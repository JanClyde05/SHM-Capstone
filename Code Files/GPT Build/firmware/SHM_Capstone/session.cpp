#include <Arduino.h>
#include <ArduinoJson.h>
#include <LittleFS.h>
#include <Preferences.h>
#include <esp_heap_caps.h>
#include <mbedtls/sha256.h>
#include <math.h>
#include "session.h"
#include "config.h"
#include "version.h"
#include "hardware_profile.h"
#include "timebase.h"
#include "storage.h"
#include "acquisition.h"
#include "dsp.h"
#include "baseline.h"
namespace {
struct WindowResult {
    DspAxisResult fft{};
    bool timing = false;
    uint64_t first = 0, last = 0;
};
struct Job {
    uint32_t window, endIndex;
};
AnalysisConfig config, snapshot;
String frozenStation, frozenOrientation, hash, snapshotHash, id, mode, operatorName, weather,
    station, orientation;
String state = "IDLE", message = "Run a ten-second precheck before a session.";
Preferences prefs;
RawRecord *raw = nullptr;
float *scratch = nullptr;
DspWorkspace workspace{};
QueueHandle_t jobs = nullptr;
SemaphoreHandle_t resultMutex = nullptr;
WindowResult results[10][3][3]{};
uint32_t completed = 0, sealed = 0, recordCount = 0, rawCrc = 0, vehicleCount = 0, qcMask = 0;
String acquisitionError;
uint64_t startUs = 0, epochStart = 0, actualDuration = 0, precheckAt = 0;
AcquisitionStatus precheckSnapshot{};
bool capture = false;
bool capacityExceeded = false;
bool technicalValid = true, finalized = false, prechecked = false, aborted = false,
     rawSaved = false;
bool workerReady = false;
int group = -1;
double medians[3][3];
String reviewStates[3][3];
portMUX_TYPE captureMux = portMUX_INITIALIZER_UNLOCKED;
const char *axisNames[3] = {"x", "y", "z"};
const char *groupNames[3] = {"NEAR_ZERO", "MEDIUM", "HEAVY"};
String encode(JsonDocument &d) {
    String s;
    serializeJson(d, s);
    return s;
}
void number(JsonVariant v, double value) {
    if (isfinite(value))
        v.set(value);
    else
        v.set(nullptr);
}
bool parseDouble(const String &s, double &value) {
    if (s.isEmpty())
        return false;
    char *e = nullptr;
    value = strtod(s.c_str(), &e);
    return e && *e == 0 && isfinite(value);
}
bool parseCount(const String &s, uint32_t &v) {
    double n;
    if (!parseDouble(s, n) || n < 0 || n > 1000000 || floor(n) != n)
        return false;
    v = uint32_t(n);
    return true;
}
String configHash(const AnalysisConfig &c) {
    // EQ-HASH-01 SHA256 of explicit canonical settings; no struct padding.
    String s =
        "SHM2|" + String(SHM_FW_VERSION) + "|N16R8|MPU6050|100|DLPF4|DIV9|RANGE2|FIFO6|DRDY|";
    s += "two-bus8,9;10,11|INT4,5,6|600|60|HANN-SYMMETRIC|FFT-BLUESTEIN|MAX-BIN|";
    s += String(c.bandLo, 12) + "|" + String(c.bandHi, 12) + "|" + String(c.timingToleranceUs) +
         "|" + String(c.cutoff1) + "|" + String(c.cutoff2);
    s += "|clip" + String(SHM_CLIP_COUNTS) + "|fsTolerance" + String(SHM_FS_TOLERANCE, 12) +
         "|minWindows" + String(SHM_MIN_VALID_WINDOWS) + "|k" + String(SHM_REVIEW_K, 12) + "|tie" +
         String(SHM_RELATIVE_TIE_TOLERANCE, 12);
    unsigned char digest[32];
    mbedtls_sha256(reinterpret_cast<const unsigned char *>(s.c_str()), s.length(), digest, 0);
    char output[65];
    for (int i = 0; i < 32; ++i)
        snprintf(output + 2 * i, 3, "%02x", digest[i]);
    return String(output);
}
void settingsJson(JsonObject o, const AnalysisConfig &c) {
    o["nominal_fs_hz"] = SHM_NOMINAL_FS;
    o["session_s"] = SHM_SESSION_SECONDS;
    o["window_s"] = SHM_WINDOW_SECONDS;
    o["band_lo_hz"] = c.bandLo;
    o["band_hi_hz"] = c.bandHi;
    o["timing_tolerance_us"] = c.timingToleranceUs;
    o["fs_tol_fraction"] = SHM_FS_TOLERANCE;
    o["cutoff1"] = c.cutoff1;
    o["cutoff2"] = c.cutoff2;
    o["relative_tie_tolerance"] = SHM_RELATIVE_TIE_TOLERANCE;
    o["clip_raw_limit"] = SHM_CLIP_COUNTS;
    o["min_valid_windows"] = SHM_MIN_VALID_WINDOWS;
    o["window"] = "symmetric_hann";
    o["peak_rule"] = "largest_positive_in_band_bin";
    o["review_k"] = SHM_REVIEW_K;
    o["dlpf_cfg"] = 4;
    o["smplrt_div"] = 9;
    o["counts_per_g"] = SHM_COUNTS_PER_G;
}
uint32_t currentCount() {
    portENTER_CRITICAL(&captureMux);
    uint32_t n = recordCount;
    portEXIT_CRITICAL(&captureMux);
    return n;
}
bool bufferExceeded() {
    portENTER_CRITICAL(&captureMux);
    bool exceeded = capacityExceeded;
    portEXIT_CRITICAL(&captureMux);
    return exceeded;
}
void stopCapture() {
    portENTER_CRITICAL(&captureMux);
    capture = false;
    portEXIT_CRITICAL(&captureMux);
}
void worker(void *) {
    Job job;
    for (;;) {
        if (xQueueReceive(jobs, &job, portMAX_DELAY) != pdTRUE)
            continue;
        const uint64_t lo = startUs + uint64_t(job.window) * SHM_WINDOW_SECONDS * 1000000ULL,
                       hi = lo + SHM_WINDOW_SECONDS * 1000000ULL;
        for (unsigned s = 0; s < 3; ++s) {
            uint32_t n = 0;
            uint64_t first = 0, last = 0, previous = 0;
            bool continuity = true;
            uint32_t priorIndex = 0;
            for (uint32_t i = 0; i < job.endIndex; ++i) {
                const auto &r = raw[i];
                if (r.sensorId != s + 1 || r.timestampUs < lo || r.timestampUs >= hi)
                    continue;
                if (r.flags)
                    continuity = false;
                if (!n)
                    first = r.timestampUs;
                else if (r.timestampUs <= previous || r.sampleIndex != priorIndex + 1)
                    continuity = false;
                previous = r.timestampUs;
                priorIndex = r.sampleIndex;
                last = r.timestampUs;
                ++n;
            }
            double fs = dspEstimateRateHz(n, first, last),
                   period = n > 1 ? double(last - first) / double(n - 1) : 0;
            bool timing = continuity && n >= 2 && n <= SHM_MAX_WINDOW_SAMPLES && isfinite(fs) &&
                          fabs(fs / SHM_NOMINAL_FS - 1) <= SHM_FS_TOLERANCE;
            // EQ-TIMING-01 coverage and interval residuals against measured mean period.
            timing = timing && double(first - lo) <= 2 * period && double(hi - last) <= 2 * period;
            timing = timing &&
                     n >= SHM_NOMINAL_FS * SHM_WINDOW_SECONDS * (1 - SHM_FS_TOLERANCE) - 2 &&
                     n <= SHM_NOMINAL_FS * SHM_WINDOW_SECONDS * (1 + SHM_FS_TOLERANCE) + 2;
            previous = 0;
            for (uint32_t i = 0; i < job.endIndex && timing; ++i) {
                const auto &r = raw[i];
                if (r.sensorId != s + 1 || r.timestampUs < lo || r.timestampUs >= hi)
                    continue;
                if (previous &&
                    fabs(double(r.timestampUs - previous) - period) > snapshot.timingToleranceUs)
                    timing = false;
                previous = r.timestampUs;
            }
            for (unsigned a = 0; a < 3; ++a) {
                WindowResult out{};
                out.first = first;
                out.last = last;
                out.timing = timing;
                if (timing) {
                    uint32_t j = 0;
                    for (uint32_t i = 0; i < job.endIndex; ++i) {
                        const auto &r = raw[i];
                        if (r.sensorId == s + 1 && r.timestampUs >= lo && r.timestampUs < hi)
                            scratch[j++] = r.xyz[a];
                    }
                    DspSettings settings;
                    settings.relativeTieTolerance = SHM_RELATIVE_TIE_TOLERANCE;
                    settings.bandLoHz = snapshot.bandLo;
                    settings.bandHiHz = snapshot.bandHi;
                    dspAnalyzeAxis(scratch, n, fs, settings, &workspace, &out.fft);
                } else {
                    out.fft.validPeak = false;
                    out.fft.status = DspStatus::InvalidParameters;
                    out.fft.sampleCount = n;
                    out.fft.fsEstimateHz = fs;
                    out.fft.dominantFrequencyHz = NAN;
                    out.fft.binSpacingHz = n ? fs / n : NAN;
                }
                xSemaphoreTake(resultMutex, portMAX_DELAY);
                results[job.window][s][a] = out;
                xSemaphoreGive(resultMutex);
                vTaskDelay(1);
            }
        }
        xSemaphoreTake(resultMutex, portMAX_DELAY);
        ++completed;
        xSemaphoreGive(resultMutex);
    }
}
String windowsCsv() {
    String s = "window_index,sensor_id,axis,sample_count,first_us,last_us,fs_est_hz,bin_spacing_hz,"
               "peak_bin,frequency_hz,valid_peak,status,timing_valid,near_tie,band_edge\n";
    s.reserve(22000);
    for (unsigned w = 0; w < sealed; ++w)
        for (unsigned c = 0; c < 3; ++c)
            for (unsigned a = 0; a < 3; ++a) {
                auto &r = results[w][c][a];
                auto &f = r.fft;
                s += String(w) + "," + String(c + 1) + "," + axisNames[a] + "," +
                     String(f.sampleCount) + "," + String(r.first) + "," + String(r.last) + ",";
                s += (isfinite(f.fsEstimateHz) ? String(f.fsEstimateHz, 10) : "") + String(",") +
                     (isfinite(f.binSpacingHz) ? String(f.binSpacingHz, 12) : "") + ",";
                s += String(f.peakBin) + "," +
                     (f.validPeak ? String(f.dominantFrequencyHz, 12) : "") + "," +
                     String(f.validPeak ? 1 : 0) + ",";
                s += String(dspStatusName(f.status)) + "," + String(r.timing ? 1 : 0) + "," +
                     String(f.nearTie ? 1 : 0) + "," + String(f.bandEdgePeak ? 1 : 0) + "\n";
            }
    return s;
}
unsigned validWindows(unsigned s, unsigned a) {
    unsigned n = 0;
    for (unsigned w = 0; w < sealed; ++w)
        if (results[w][s][a].fft.validPeak && results[w][s][a].timing)
            ++n;
    return n;
}
String makeSummary() {
    JsonDocument d;
    d["schema_version"] = 2;
    d["firmware_version"] = SHM_FW_VERSION;
    d["session_id"] = id;
    d["mode"] = mode;
    d["config_hash"] = snapshotHash;
    d["config_frozen"] = snapshot.frozen;
    d["station_id"] = station;
    d["orientation"] = orientation;
    d["operator"] = operatorName;
    d["weather_note"] = weather;
    d["start_us"] = startUs;
    d["epoch_seconds"] = epochStart;
    d["duration_s"] = double(actualDuration) / 1e6;
    d["record_count"] = currentCount();
    d["finalized"] = finalized;
    d["technical_valid"] = technicalValid;
    d["aborted"] = aborted;
    d["raw_saved"] = rawSaved;
    char hex[9];
    snprintf(hex, sizeof(hex), "%08x", rawCrc);
    d["raw_crc32_hex"] = hex;
    if (finalized)
        d["vehicle_count"] = vehicleCount;
    else
        d["vehicle_count"] = nullptr;
    d["traffic_level"] = group >= 0 ? groupNames[group] : "UNCLASSIFIED";
    d["qc_mask"] = qcMask;
    d["acquisition_error"] = acquisitionError;
    auto reasons = d["qc_reasons"].to<JsonArray>();
    const char *codes[] = {"CLIPPING",
                           "SAMPLE_INDEX_GAP",
                           "WINDOW_TIMING",
                           "OPERATOR_OR_ACQUISITION_ABORT",
                           "RAW_CAPACITY",
                           "ACQUISITION_INTEGRITY",
                           "INCOMPLETE_WINDOW_SET",
                           "PERSISTENCE_INCOMPLETE"};
    for (unsigned q = 0; q < 8; ++q)
        if (qcMask & (1u << q))
            reasons.add(codes[q]);
    d["completed_windows"] = completed;
    d["message"] = message;
    settingsJson(d["settings"].to<JsonObject>(), snapshot);
    auto streams = d["streams"].to<JsonArray>();
    for (unsigned s = 0; s < 3; ++s)
        for (unsigned a = 0; a < 3; ++a) {
            auto r = streams.add<JsonObject>();
            r["sensor_id"] = s + 1;
            r["axis"] = axisNames[a];
            r["valid_windows"] = validWindows(s, a);
            number(r["median_hz"], medians[s][a]);
            r["baseline_state"] = reviewStates[s][a];
        }
    return encode(d);
}
void summarize() {
    uint32_t previous[3] = {};
    bool seen[3] = {};
    const uint32_t total = currentCount();
    for (uint32_t i = 0; i < total; ++i) {
        const auto &r = raw[i];
        unsigned s = r.sensorId - 1;
        if (s > 2) {
            technicalValid = false;
            qcMask |= 2;
            continue;
        }
        if (r.flags) {
            technicalValid = false;
            qcMask |= 1;
        }
        if (seen[s] && r.sampleIndex != previous[s] + 1) {
            technicalValid = false;
            qcMask |= 2;
        }
        previous[s] = r.sampleIndex;
        seen[s] = true;
    }
    for (unsigned s = 0; s < 3; ++s)
        for (unsigned a = 0; a < 3; ++a) {
            float frequencies[10];
            unsigned n = 0;
            for (unsigned w = 0; w < sealed; ++w) {
                if (!results[w][s][a].timing) {
                    technicalValid = false;
                    qcMask |= 4;
                }
                if (results[w][s][a].fft.validPeak)
                    frequencies[n++] = results[w][s][a].fft.dominantFrequencyHz;
            }
            medians[s][a] = NAN;
            if (n >= SHM_MIN_VALID_WINDOWS)
                dspMedian(frequencies, n, &medians[s][a]); // EQ-MEDIAN-01
        }
}
String baselineState(unsigned s, unsigned a, double value, int level) {
    if (level < 0)
        return "NO BASELINE YET";
    BaselineAxisSummary b{};
    baselineGet(level, s, a, &b);
    if (!b.n)
        return "NO BASELINE YET";
    if (b.n < SHM_MIN_BASELINE_SESSIONS || !b.sdDefined)
        return "PROVISIONAL (n<5)";
    if (!isfinite(value))
        return "BASELINE_READY"; // static baseline availability; no current comparison
    return baselineOutsideReview(value, b) ? "OUTSIDE_BASELINE_REVIEW" : "WITHIN BASELINE";
}
void saveFinished() {
    summarize();
    if (sealed != 10 || completed != 10) {
        technicalValid = false;
        qcMask |= 64;
    }
    if (aborted) {
        technicalValid = false;
        qcMask |= 8;
    }
    if (bufferExceeded()) {
        technicalValid = false;
        qcMask |= 16;
    }
    acquisitionSuspend();
    uint32_t crc = 0;
    bool ok = storageCreateSession(id) && storageSaveRaw(id, raw, currentCount(), startUs, &crc);
    rawSaved = ok;
    rawCrc = crc;
    if (ok)
        ok = storageWriteText(id, "windows.csv", windowsCsv());
    if (!ok) {
        technicalValid = false;
        qcMask |= 128;
        message = "Recording persistence incomplete. Retain power and recover available files.";
        state = "ERROR";
    } else {
        state = "AWAITING_COUNT";
        message = "Recording stored. Enter the concurrent vehicle tally to finalize.";
    }
    if (!storageWriteText(id, "summary.json", makeSummary())) {
        state = "ERROR";
        message = "Summary could not be saved.";
    }
    acquisitionResume();
    prechecked = false;
}
} // namespace
void sessionOnSample(const RawRecord &r) {
    portENTER_CRITICAL(&captureMux);
    if (capture && r.timestampUs >= startUs &&
        r.timestampUs < startUs + SHM_SESSION_SECONDS * 1000000ULL) {
        if (recordCount < SHM_MAX_RAW_RECORDS)
            raw[recordCount++] = r;
        else {
            capacityExceeded = true;
            capture = false;
        }
    }
    portEXIT_CRITICAL(&captureMux);
}
bool sessionBusy() {
    return state == "PRECHECK" || state == "ARMED" || state == "RECORDING" || state == "PROCESSING";
}
void sessionBegin() {
    prefs.begin("shm-study2", false);
    config.bandLo = prefs.getDouble("lo", .5);
    config.bandHi = prefs.getDouble("hi", 20);
    config.timingToleranceUs = prefs.getUInt("tol", 500);
    config.cutoff1 = prefs.getUInt("c1", 0);
    config.cutoff2 = prefs.getUInt("c2", 0);
    config.frozen = prefs.getBool("frozen", false);
    frozenStation = prefs.getString("station");
    frozenOrientation = prefs.getString("orient");
    hash = configHash(config);
    raw = static_cast<RawRecord *>(heap_caps_malloc(SHM_MAX_RAW_RECORDS * sizeof(RawRecord),
                                                    MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
    scratch = static_cast<float *>(heap_caps_malloc(SHM_MAX_WINDOW_SAMPLES * sizeof(float),
                                                    MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
    workspace.capacity = dspWorkspaceLength(SHM_MAX_WINDOW_SAMPLES);
    workspace.a = static_cast<DspComplex *>(heap_caps_malloc(
        workspace.capacity * sizeof(DspComplex), MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
    workspace.b = static_cast<DspComplex *>(heap_caps_malloc(
        workspace.capacity * sizeof(DspComplex), MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
    resultMutex = xSemaphoreCreateMutex();
    jobs = xQueueCreate(10, sizeof(Job));
    if (raw && scratch && workspace.a && workspace.b && resultMutex && jobs)
        workerReady =
            xTaskCreatePinnedToCore(worker, "shm-dsp", 8192, nullptr, 1, nullptr, 0) == pdPASS;
    if (!workerReady)
        message = "PSRAM or worker allocation unavailable; check OPI PSRAM settings.";
    for (unsigned s = 0; s < 3; ++s)
        for (unsigned a = 0; a < 3; ++a) {
            medians[s][a] = NAN;
            reviewStates[s][a] = "NO BASELINE YET";
        }
    sessionReloadBaseline();
}
void sessionReloadBaseline() {
    baselineBegin();
    if (!storageReady() || !config.frozen)
        return;
    auto root = LittleFS.open("/");
    for (auto dir = root.openNextFile(); dir; dir = root.openNextFile()) {
        if (!dir.isDirectory())
            continue;
        String path = String(dir.path()) + "/summary.json";
        auto f = LittleFS.open(path, "r");
        if (!f)
            continue;
        JsonDocument d;
        if (deserializeJson(d, f))
            continue;
        if (String(d["mode"] | "") != "formal" || !d["finalized"].as<bool>() ||
            !d["technical_valid"].as<bool>() || String(d["config_hash"] | "") != hash ||
            String(d["station_id"] | "") != frozenStation ||
            String(d["orientation"] | "") != frozenOrientation)
            continue;
        String level = d["traffic_level"] | "";
        int g = -1;
        for (int i = 0; i < 3; ++i)
            if (level == groupNames[i])
                g = i;
        if (g < 0)
            continue;
        for (auto r : d["streams"].as<JsonArray>()) {
            int s = r["sensor_id"].as<int>() - 1;
            String axis = r["axis"] | "";
            int a = -1;
            for (int i = 0; i < 3; ++i)
                if (axis == axisNames[i])
                    a = i;
            if (s >= 0 && s < 3 && a >= 0 && !r["median_hz"].isNull() &&
                r["valid_windows"].as<unsigned>() >= SHM_MIN_VALID_WINDOWS)
                baselineAddSession(g, s, a, r["median_hz"].as<double>());
        }
    }
}
void sessionUpdate() {
    uint64_t now = timebaseNowUs();
    auto acq = acquisitionGetStatus();
    if (state == "PRECHECK" && now - precheckAt >= SHM_PRECHECK_SECONDS * 1000000ULL) {
        prechecked = acq.ready;
        for (int s = 0; s < 3; ++s) {
            const uint32_t n = acq.counts[s] - precheckSnapshot.counts[s];
            if (n < SHM_NOMINAL_FS * SHM_PRECHECK_SECONDS * .97 ||
                n > SHM_NOMINAL_FS * SHM_PRECHECK_SECONDS * 1.03 ||
                acq.clips[s] != precheckSnapshot.clips[s] || now - acq.lastUs[s] > 100000)
                prechecked = false;
        }
        state = "IDLE";
        message = prechecked
                      ? "Precheck complete. Confirm the fixed mounting before starting."
                      : "Precheck rejected. Check wiring, data-ready lines, clipping and timing.";
    }
    if (state == "ARMED" && now >= startUs)
        state = "RECORDING";
    if (state == "RECORDING") {
        if (!acq.ready || bufferExceeded()) {
            technicalValid = false;
            aborted = true;
            qcMask |= acq.ready ? 16 : 32;
            acquisitionError = acq.ready ? "" : String(acq.error);
            message = acq.ready ? "Raw buffer capacity reached." : acq.error;
            stopCapture();
            actualDuration = now > startUs ? now - startUs : 0;
            state = "PROCESSING";
        } else {
            while (sealed < 10) {
                uint64_t boundary =
                    startUs + uint64_t(sealed + 1) * SHM_WINDOW_SECONDS * 1000000ULL;
                if (now < boundary)
                    break;
                bool passed = true;
                for (unsigned s = 0; s < 3; ++s)
                    if (acq.lastUs[s] < boundary)
                        passed = false;
                if (!passed) {
                    if (now > boundary + 1000000) {
                        technicalValid = false;
                        aborted = true;
                        stopCapture();
                        state = "PROCESSING";
                        actualDuration = now - startUs;
                    }
                    break;
                }
                Job j{sealed, currentCount()};
                if (xQueueSend(jobs, &j, 0) != pdTRUE) {
                    technicalValid = false;
                    aborted = true;
                    stopCapture();
                    state = "PROCESSING";
                    break;
                }
                ++sealed;
            }
            if (sealed == 10) {
                stopCapture();
                actualDuration = SHM_SESSION_SECONDS * 1000000ULL;
                state = "PROCESSING";
                message = "Final window processing and record persistence.";
            }
        }
    }
    if (state == "PROCESSING") {
        xSemaphoreTake(resultMutex, portMAX_DELAY);
        bool done = completed == sealed;
        xSemaphoreGive(resultMutex);
        if (done)
            saveFinished();
    }
}
String sessionGetJson(const String &route) {
    JsonDocument d;
    auto acq = acquisitionGetStatus();
    if (route == "/api/status") {
        d["state"] = state;
        d["fw_version"] = SHM_FW_VERSION;
        d["hw_rev"] = SHM_HW_REV;
        d["session_id"] = id;
        d["elapsed_s"] = startUs && timebaseNowUs() > startUs
                             ? min(double(timebaseNowUs() - startUs) / 1e6, 600.0)
                             : 0;
        uint64_t countdownNow = timebaseNowUs();
        d["starts_in_s"] =
            state == "ARMED" && countdownNow < startUs ? double(startUs - countdownNow) / 1e6 : 0;
        d["hardware_ready"] = acq.ready;
        d["psram_ready"] = workerReady;
        d["storage_ready"] = storageReady();
        d["free_bytes"] = storageFreeBytes();
        d["precheck_ready"] = prechecked;
        d["message"] = message;
    } else if (route == "/api/config") {
        d["frozen"] = config.frozen;
        d["hash"] = hash;
        d["band_lo"] = config.bandLo;
        d["band_hi"] = config.bandHi;
        d["timing_tolerance_us"] = config.timingToleranceUs;
        d["cutoff1"] = config.cutoff1;
        d["cutoff2"] = config.cutoff2;
        d["station_id"] = frozenStation;
        d["orientation"] = frozenOrientation;
    } else if (route == "/api/live") {
        if (!resultMutex) {
            d["message"] = "Numerical worker unavailable";
            return encode(d);
        }
        d["state"] = state;
        d["session_id"] = id;
        d["traffic_level"] = group >= 0 ? groupNames[group] : "UNCLASSIFIED";
        xSemaphoreTake(resultMutex, portMAX_DELAY);
        d["windows_complete"] = completed;
        d["total_windows"] = 10;
        auto sensors = d["sensors"].to<JsonArray>();
        for (unsigned s = 0; s < 3; ++s) {
            auto sensor = sensors.add<JsonObject>();
            sensor["id"] = s + 1;
            number(sensor["fs_est_hz"], acq.fsEstimateHz[s]);
            d["fs_est_hz"][String("imu") + String(s + 1)] = acq.fsEstimateHz[s];
            // EQ-SCALE-01 nominal +/-2g conversion for preview; raw counts feed the FFT.
            auto xyz = sensor["xyz_g"].to<JsonArray>();
            for (unsigned a = 0; a < 3; ++a)
                xyz.add(double(acq.latest[s][a]) / SHM_COUNTS_PER_G);
            for (unsigned a = 0; a < 3; ++a) {
                auto ax = sensor["axes"][axisNames[a]].to<JsonObject>();
                bool valid = completed && results[completed - 1][s][a].fft.validPeak;
                ax["valid_peak"] = valid;
                number(ax["f_d_hz"],
                       valid ? results[completed - 1][s][a].fft.dominantFrequencyHz : NAN);
                ax["baseline_state"] = finalized ? reviewStates[s][a] : "NO BASELINE YET";
            }
        }
        xSemaphoreGive(resultMutex);
    } else if (route == "/api/baseline") {
        auto sensors = d["sensors"].to<JsonArray>();
        for (unsigned s = 0; s < 3; ++s) {
            auto sensor = sensors.add<JsonObject>();
            sensor["id"] = s + 1;
            for (unsigned a = 0; a < 3; ++a) {
                auto ax = sensor["axes"][axisNames[a]].to<JsonObject>();
                ax["state"] = baselineState(s, a, NAN, group);
                for (int g = 0; g < 3; ++g) {
                    BaselineAxisSummary b{};
                    baselineGet(g, s, a, &b);
                    auto l = ax["levels"][groupNames[g]].to<JsonObject>();
                    l["n"] = b.n;
                    number(l["mean_hz"], b.n ? b.meanHz : NAN);
                    number(l["sd_hz"], b.sdDefined ? b.sampleSdHz : NAN);
                    number(l["cv_pct"], b.cvDefined ? b.coefficientVariationPct : NAN);
                    number(l["descriptive_lo_hz"], b.sdDefined ? b.descriptiveLoHz : NAN);
                    number(l["descriptive_hi_hz"], b.sdDefined ? b.descriptiveHiHz : NAN);
                    number(l["review_lo_hz"], b.sdDefined ? b.reviewLoHz : NAN);
                    number(l["review_hi_hz"], b.sdDefined ? b.reviewHiHz : NAN);
                    l["state"] = baselineState(s, a, NAN, g);
                }
            }
        }
    } else if (route == "/api/sessions") {
        auto sessions = d["sessions"].to<JsonArray>();
        if (storageReady() && !sessionBusy()) {
            auto root = LittleFS.open("/");
            unsigned limit = 0;
            for (auto dir = root.openNextFile(); dir && limit < 64; dir = root.openNextFile()) {
                if (!dir.isDirectory())
                    continue;
                auto f = LittleFS.open(String(dir.path()) + "/summary.json", "r");
                if (!f)
                    continue;
                JsonDocument stored;
                if (deserializeJson(stored, f))
                    continue;
                auto o = sessions.add<JsonObject>();
                o["session_id"] = stored["session_id"];
                o["mode"] = stored["mode"];
                o["traffic_level"] = stored["traffic_level"];
                o["valid"] = stored["technical_valid"];
                o["duration_s"] = stored["duration_s"];
                o["vehicle_count"] = stored["vehicle_count"];
                o["finalized"] = stored["finalized"];
                ++limit;
            }
        }
    } else {
        d["message"] = "Unknown endpoint";
    }
    return encode(d);
}
bool sessionPost(const String &route, const WebForm &f, String &reply, int &status) {
    JsonDocument d;
    status = 200;
    auto respond = [&](const char *m, int code) {
        d["message"] = m;
        status = code;
        reply = encode(d);
        return true;
    };
    if (route == "/api/session/precheck") {
        if (sessionBusy() || state == "AWAITING_COUNT")
            return respond("Finish the current session first.", 409);
        acquisitionSuspend();
        acquisitionResume();
        precheckSnapshot = acquisitionGetStatus();
        precheckAt = timebaseNowUs();
        prechecked = false;
        state = "PRECHECK";
        message = "Ten-second acquisition precheck in progress.";
        return respond(message.c_str(), 200);
    }
    if (route == "/api/config/freeze") {
        if (sessionBusy() || state == "AWAITING_COUNT")
            return respond("Configuration is locked during a session.", 409);
        AnalysisConfig proposed;
        double tol;
        if (f.confirm != "FREEZE" || !parseDouble(f.bandLo, proposed.bandLo) ||
            !parseDouble(f.bandHi, proposed.bandHi) || !parseDouble(f.timingToleranceUs, tol) ||
            tol < 50 || tol > 2000 || floor(tol) != tol ||
            !parseCount(f.cutoff1, proposed.cutoff1) || !parseCount(f.cutoff2, proposed.cutoff2) ||
            proposed.cutoff2 <= proposed.cutoff1 || proposed.bandLo <= 0 ||
            proposed.bandHi <= proposed.bandLo ||
            proposed.bandHi >= SHM_NOMINAL_FS * (1 - SHM_FS_TOLERANCE) / 2 ||
            f.stationId.isEmpty() || f.orientation.isEmpty())
            return respond(
                "Enter verified pilot settings, distinct count cutoffs, station and orientation.",
                400);
        proposed.timingToleranceUs = uint32_t(tol);
        proposed.frozen = true;
        acquisitionSuspend();
        config = proposed;
        frozenStation = f.stationId;
        frozenOrientation = f.orientation;
        prefs.putDouble("lo", config.bandLo);
        prefs.putDouble("hi", config.bandHi);
        prefs.putUInt("tol", config.timingToleranceUs);
        prefs.putUInt("c1", config.cutoff1);
        prefs.putUInt("c2", config.cutoff2);
        prefs.putString("station", frozenStation);
        prefs.putString("orient", frozenOrientation);
        prefs.putBool("frozen", true);
        hash = configHash(config);
        sessionReloadBaseline();
        acquisitionResume();
        prechecked = false;
        return respond("Pilot settings frozen; run a new precheck before formal acquisition.", 200);
    }
    if (route == "/api/session/start") {
        if (sessionBusy() || state == "AWAITING_COUNT")
            return respond("Finish the current session first.", 409);
        if (!prechecked || !acquisitionGetStatus().ready || !workerReady || !storageReady())
            return respond("Precheck, sensors, PSRAM and storage must be ready.", 409);
        if (f.mode != "pilot" && f.mode != "formal")
            return respond("Choose pilot or formal.", 400);
        if (f.stationId.isEmpty() || f.orientation.isEmpty())
            return respond("Record the station and board orientation.", 400);
        if (f.mode == "formal" &&
            (!config.frozen || f.stationId != frozenStation || f.orientation != frozenOrientation))
            return respond("Formal sessions require frozen matching station and orientation.", 409);
        if (storageFreeBytes() < SHM_MAX_RAW_RECORDS * sizeof(RawRecord) + 262144)
            return respond("Insufficient space. Back up and explicitly purge an old raw record.",
                           507);
        acquisitionSuspend();
        uint32_t sequence = prefs.getUInt("sequence", 0) + 1;
        do {
            id = "S" + String(sequence++);
        } while (LittleFS.exists("/" + id));
        prefs.putUInt("sequence", sequence - 1);
        acquisitionResume();
        if (!acquisitionGetStatus().ready)
            return respond("Acquisition restart rejected; inspect wiring.", 409);
        snapshot = config;
        snapshotHash = hash;
        mode = f.mode;
        station = f.stationId;
        orientation = f.orientation;
        operatorName = f.operatorName;
        weather = f.weatherNote;
        double epoch;
        if (parseDouble(f.epoch, epoch) && epoch > 0)
            timebaseSetEpoch(uint64_t(epoch));
        startUs = timebaseNowUs() + 5000000;
        const uint64_t calendar = timebaseEpochSeconds();
        epochStart = calendar ? calendar + 5 : 0;
        actualDuration = 0;
        qcMask = 0;
        acquisitionError = "";
        recordCount = 0;
        completed = 0;
        sealed = 0;
        vehicleCount = 0;
        rawCrc = 0;
        finalized = false;
        aborted = false;
        capacityExceeded = false;
        technicalValid = true;
        rawSaved = false;
        group = -1;
        prechecked = false;
        memset(results, 0, sizeof(results));
        for (unsigned s = 0; s < 3; ++s)
            for (unsigned a = 0; a < 3; ++a) {
                medians[s][a] = NAN;
                reviewStates[s][a] = "NO BASELINE YET";
            }
        portENTER_CRITICAL(&captureMux);
        capture = true;
        portEXIT_CRITICAL(&captureMux);
        state = "ARMED";
        message = "Five-second countdown; tally vehicles for the same 600-second interval.";
        return respond(message.c_str(), 200);
    }
    if (route == "/api/session/stop") {
        if (state != "ARMED" && state != "RECORDING")
            return respond("No active recording.", 409);
        stopCapture();
        aborted = true;
        technicalValid = false;
        actualDuration = timebaseNowUs() > startUs ? timebaseNowUs() - startUs : 0;
        state = "PROCESSING";
        message = "Operator stopped the recording; retained as an incomplete record.";
        return respond(message.c_str(), 200);
    }
    if (route == "/api/session/finalize") {
        // Recover count finalization after a reboot, using the retained snapshot.
        if (state != "AWAITING_COUNT" || f.sessionId != id) {
            if (sessionBusy() || !storageValidId(f.sessionId))
                return respond("Stored session is not available for count entry.", 409);
            fs::File storedFile;
            if (!storageOpen(f.sessionId, "summary", storedFile))
                return respond("Stored summary unavailable.", 404);
            JsonDocument stored;
            if (deserializeJson(stored, storedFile) || stored["finalized"].as<bool>())
                return respond("Summary unreadable or already finalized.", 409);
            uint32_t count;
            if (!parseCount(f.vehicleCount, count))
                return respond("Enter an integer tally.", 400);
            const bool frozen = stored["config_frozen"].as<bool>();
            const uint32_t c1 = stored["settings"]["cutoff1"].as<uint32_t>(),
                           c2 = stored["settings"]["cutoff2"].as<uint32_t>();
            // EQ-TRAFFIC-03 uses the retained frozen cutoffs, including after reboot.
            int savedGroup = frozen ? (count <= c1 ? 0 : count <= c2 ? 1 : 2) : -1;
            stored["vehicle_count"] = count;
            stored["traffic_level"] = savedGroup >= 0 ? groupNames[savedGroup] : "UNCLASSIFIED";
            stored["finalized"] = true;
            bool compare = stored["technical_valid"].as<bool>() &&
                           String(stored["mode"] | "") == "formal" &&
                           String(stored["config_hash"] | "") == hash &&
                           String(stored["station_id"] | "") == frozenStation &&
                           String(stored["orientation"] | "") == frozenOrientation;
            for (auto stream : stored["streams"].as<JsonArray>()) {
                int sensor = stream["sensor_id"].as<int>() - 1;
                String axis = stream["axis"] | "";
                int a = -1;
                for (int i = 0; i < 3; ++i)
                    if (axis == axisNames[i])
                        a = i;
                stream["baseline_state"] =
                    compare && sensor >= 0 && sensor < 3 && a >= 0 && !stream["median_hz"].isNull()
                        ? baselineState(sensor, a, stream["median_hz"].as<double>(), savedGroup)
                        : String("NO BASELINE YET");
            }
            acquisitionSuspend();
            bool ok = storageWriteText(f.sessionId, "summary.json", encode(stored));
            if (ok)
                sessionReloadBaseline();
            acquisitionResume();
            prechecked = false;
            return respond(ok ? "Stored session count finalized." : "Summary write incomplete.",
                           ok ? 200 : 500);
        }
        if (state != "AWAITING_COUNT" || f.sessionId != id ||
            !parseCount(f.vehicleCount, vehicleCount))
            return respond("Enter the current stored session ID and a nonnegative integer tally.",
                           400);
        finalized = true;
        // EQ-TRAFFIC-03 frozen nearest-rank thresholds, count inclusive at lower boundaries.
        group = snapshot.frozen ? (vehicleCount <= snapshot.cutoff1   ? 0
                                   : vehicleCount <= snapshot.cutoff2 ? 1
                                                                      : 2)
                                : -1;
        for (unsigned s = 0; s < 3; ++s)
            for (unsigned a = 0; a < 3; ++a)
                reviewStates[s][a] = technicalValid && mode == "formal" && snapshotHash == hash &&
                                             station == frozenStation &&
                                             orientation == frozenOrientation &&
                                             isfinite(medians[s][a])
                                         ? baselineState(s, a, medians[s][a], group)
                                         : "NO BASELINE YET";
        acquisitionSuspend();
        message = "Session finalized and retained.";
        bool ok = storageWriteText(id, "summary.json", makeSummary());
        if (ok)
            sessionReloadBaseline();
        acquisitionResume();
        state = ok ? "COMPLETE" : "ERROR";
        return respond(ok ? "Session finalized. Back up raw, windows and summary."
                          : "Summary persistence incomplete.",
                       ok ? 200 : 500);
    }
    return false;
}
void sessionInvalidatePrecheck() {
    prechecked = false;
}
