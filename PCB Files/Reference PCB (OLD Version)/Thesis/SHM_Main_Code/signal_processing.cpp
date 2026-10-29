/*
 * ============================================================
 * signal_processing.cpp  —  v2 (UPDATED)
 *
 * CHANGES vs v1:
 *
 *   sp_computeHeatmap()
 *     OLD: rmsScore = rms / (ANOMALY_RMS_THRESHOLD * 3.0f)
 *          → absolute normalizer saturated at real ambient 0.98 g
 *     NEW: rmsScore = (rms - baseline) / (baseline * SENSITIVITY)
 *          → score is 0 at ambient, rises only with TRUE increase
 *
 *   sp_computeNode()
 *     • Baseline bootstrap: first BASELINE_WARMUP_COUNT calls use
 *       alpha=0.15; s_rmsBaseline[i] is bootstrapped to first rms
 *       measurement so warmup starts near real ambient, not 0.06g.
 *     • Anomaly hysteresis: two-threshold system prevents chatter.
 *     • newAnomaly: set only when transitioning false→true.
 *       s_alertFired[] gate ensures one broadcast per event.
 * ============================================================
 */

#include "signal_processing.h"

// ── Per-node ring buffers ─────────────────────────────────────
static SensorBuffer s_buf[NUM_SENSORS];

// ── Shared FFT working arrays (serialised by s_fftMutex) ─────
static double            s_vReal[FFT_SAMPLES];
static double            s_vImag[FFT_SAMPLES];
static SemaphoreHandle_t s_fftMutex;

// ArduinoFFT v2 template instance
static ArduinoFFT<double> s_fft(s_vReal, s_vImag, FFT_SAMPLES, SENSOR_SAMPLE_RATE);

// ── Per-node state ────────────────────────────────────────────
static float    s_rmsBaseline [NUM_SENSORS];   // EMA ambient floor
static uint16_t s_computeCount[NUM_SENSORS];   // Tracks warmup progress
static bool     s_alertFired  [NUM_SENSORS];   // Hysteresis gate
static bool     s_inAnomaly   [NUM_SENSORS];   // Tracks current anomaly state

// ============================================================
// INITIALISATION
// ============================================================

void signal_processing_init() {
    s_fftMutex = xSemaphoreCreateMutex();
    configASSERT(s_fftMutex != NULL);

    for (int i = 0; i < NUM_SENSORS; i++) {
        memset(&s_buf[i], 0, sizeof(SensorBuffer));
        s_buf[i].mutex = xSemaphoreCreateMutex();
        configASSERT(s_buf[i].mutex != NULL);

        // Initialise to 0 — first real sample will bootstrap via
        // the "if baseline == 0 → set baseline = rms" guard below.
        s_rmsBaseline [i] = 0.0f;
        s_computeCount[i] = 0;
        s_alertFired  [i] = false;
        s_inAnomaly   [i] = false;
    }

    Serial.println("[SP] Signal processing v2 initialised.");
    Serial.printf ("[SP] Model: RELATIVE baseline | sensitivity=%.0f%% | "
                   "sigma=%.1fx | hysteresis=%.1fx\n",
                   BASELINE_SENSITIVITY * 100.0f,
                   ANOMALY_SIGMA_MULT,
                   ANOMALY_HYSTERESIS);
    Serial.printf ("[SP] FFT: %d pts @ %.0f Hz/node → %.3f Hz res | "
                   "Nyquist %.0f Hz\n",
                   FFT_SAMPLES, SENSOR_SAMPLE_RATE,
                   SENSOR_SAMPLE_RATE / FFT_SAMPLES,
                   SENSOR_SAMPLE_RATE / 2.0f);
}

// ============================================================
// PUSH SAMPLE  — from Sensor Acquisition task (Core 0)
// ============================================================

void sp_pushSample(int nodeIndex, const IMUData &data) {
    if (nodeIndex < 0 || nodeIndex >= NUM_SENSORS || !data.valid) return;

    SensorBuffer &b = s_buf[nodeIndex];

    // Non-blocking: drop sample rather than stall acquisition task
    if (xSemaphoreTake(b.mutex, pdMS_TO_TICKS(1)) != pdTRUE) return;

    // Vector magnitude — orientation-independent
    float mag = sqrtf(data.accX * data.accX +
                      data.accY * data.accY +
                      data.accZ * data.accZ);

    b.rmsBuf[b.rmsHead] = mag;
    b.rmsHead = (b.rmsHead + 1) % RMS_WINDOW;
    if (b.rmsFilled < RMS_WINDOW) b.rmsFilled++;

    // Z-axis primary for vertical deck vibration
    b.fftBuf[b.fftHead] = data.accZ;
    b.fftHead = (b.fftHead + 1) % FFT_SAMPLES;
    if (b.fftFilled < FFT_SAMPLES) b.fftFilled++;

    xSemaphoreGive(b.mutex);
}

// ============================================================
// COMPUTE RMS
// ============================================================

float sp_computeRMS(const float *data, int size) {
    if (size <= 0) return 0.0f;
    double acc = 0.0;
    for (int i = 0; i < size; i++) acc += (double)data[i] * (double)data[i];
    return (float)sqrt(acc / size);
}

// ============================================================
// COMPUTE FFT  — Hann-windowed, returns dominant frequency
// ============================================================

float sp_computeFFT(float  *timeSeries,
                    int     size,
                    float   sampleRate,
                    float  *magnitudesOut,
                    float  *peakMagOut) {

    if (size != FFT_SAMPLES) return 0.0f;

    if (xSemaphoreTake(s_fftMutex, pdMS_TO_TICKS(200)) != pdTRUE) {
        Serial.println("[SP] FFT mutex timeout — skipped");
        return 0.0f;
    }

    for (int i = 0; i < size; i++) {
        s_vReal[i] = (double)timeSeries[i];
        s_vImag[i] = 0.0;
    }

    // Hann window — suppresses spectral leakage
    s_fft.windowing(FFTWindow::Hann, FFTDirection::Forward);
    s_fft.compute(FFTDirection::Forward);
    s_fft.complexToMagnitude();

    double peakMag = 0.0;
    int    peakBin = 1;
    int    halfSize = size / 2;

    for (int k = 1; k < halfSize; k++) {
        if (magnitudesOut) magnitudesOut[k - 1] = (float)s_vReal[k];
        if (s_vReal[k] > peakMag) {
            peakMag = s_vReal[k];
            peakBin = k;
        }
    }
    if (magnitudesOut) magnitudesOut[0] = 0.0f;  // Zero DC bin in output
    if (peakMagOut)    *peakMagOut = (float)peakMag;

    float dominantFreq = (float)peakBin * sampleRate / (float)size;

    xSemaphoreGive(s_fftMutex);
    return dominantFreq;
}

// ============================================================
// COMPUTE HEATMAP  — v2: RELATIVE baseline model
//
//  rmsScore = (rms - baseline) / (baseline × SENSITIVITY)
//
//  When rms ≈ baseline (stable environment): score ≈ 0
//  When rms = baseline × (1 + SENSITIVITY):  score = 1.0
//
//  This means gravity (≈1g) or any other constant ambient
//  component is absorbed into the baseline and does NOT
//  artificially inflate the heatmap score.
//
//  freqScore: Gaussian risk bell centred at 4 Hz (bridge
//             resonance region), unchanged from v1.
// ============================================================

float sp_computeHeatmap(float rms, float freq, float baseline) {
    // ── RMS component ─────────────────────────────────────────
    float rmsScore = 0.0f;
    if (baseline > 0.001f) {
        float relativeExcess = (rms - baseline) / baseline;
        // Normalise: excess of BASELINE_SENSITIVITY = score 1.0
        rmsScore = relativeExcess / BASELINE_SENSITIVITY;
        rmsScore = constrain(rmsScore, 0.0f, 1.0f);
    }

    // ── Frequency risk component ──────────────────────────────
    // Gaussian bell centred at 4 Hz (σ ≈ 3 Hz)
    // Peaks in the structural resonance band for bridges (1–8 Hz)
    float freqScore = 0.0f;
    if (freq >= ANOMALY_FREQ_NOISE_MIN && freq <= ANOMALY_FREQ_NOISE_MAX) {
        float d = (freq - 4.0f) / 3.0f;
        freqScore = expf(-0.5f * d * d);
    }

    // Weighted combination: RMS dominates (70%), freq modulates (30%)
    return constrain(0.70f * rmsScore + 0.30f * freqScore, 0.0f, 1.0f);
}

// ============================================================
// COMPUTE NODE  — orchestrates all processing for one node
// ============================================================

bool sp_computeNode(int nodeIndex, ProcessedData &result) {
    if (nodeIndex < 0 || nodeIndex >= NUM_SENSORS) return false;

    SensorBuffer &b = s_buf[nodeIndex];

    // ── Snapshot buffers ──────────────────────────────────────
    float    rmsSnap[RMS_WINDOW]  = {};
    float    fftSnap[FFT_SAMPLES] = {};
    uint16_t rmsFilled, fftFilled;

    if (xSemaphoreTake(b.mutex, pdMS_TO_TICKS(20)) != pdTRUE) return false;

    rmsFilled = b.rmsFilled;
    fftFilled = b.fftFilled;

    for (uint16_t i = 0; i < rmsFilled; i++) {
        uint16_t idx = (b.rmsHead + RMS_WINDOW - rmsFilled + i) % RMS_WINDOW;
        rmsSnap[i] = b.rmsBuf[idx];
    }
    for (uint16_t i = 0; i < fftFilled; i++) {
        uint16_t idx = (b.fftHead + FFT_SAMPLES - fftFilled + i) % FFT_SAMPLES;
        fftSnap[i] = b.fftBuf[idx];
    }

    xSemaphoreGive(b.mutex);

    if (rmsFilled < 5) {
        result = {0.0f, 0.0f, 0.0f, false, false, {}, 0.0f, millis()};
        return false;
    }

    // ── RMS ───────────────────────────────────────────────────
    result.rms = sp_computeRMS(rmsSnap, rmsFilled);

    // ── Baseline bootstrap & EMA update ──────────────────────
    // Step 1: If baseline has never been set, seed it directly
    //         so the system doesn't start with a near-zero floor.
    if (s_rmsBaseline[nodeIndex] < 0.001f) {
        s_rmsBaseline[nodeIndex] = result.rms;
    }

    // Step 2: Two-speed EMA — fast warmup, then slow ambient tracking
    uint16_t cnt = ++s_computeCount[nodeIndex];
    float alpha  = (cnt < BASELINE_WARMUP_COUNT)
                   ? BASELINE_ALPHA_FAST
                   : BASELINE_ALPHA;

    s_rmsBaseline[nodeIndex] = alpha * result.rms +
                               (1.0f - alpha) * s_rmsBaseline[nodeIndex];

    float baseline = s_rmsBaseline[nodeIndex];

    // ── FFT ───────────────────────────────────────────────────
    memset(result.spectrum, 0, sizeof(result.spectrum));
    result.spectrumPeak = 0.0f;
    result.dominantFreq = 0.0f;

    if (fftFilled >= FFT_SAMPLES) {
        result.dominantFreq = sp_computeFFT(
            fftSnap, FFT_SAMPLES, SENSOR_SAMPLE_RATE,
            result.spectrum, &result.spectrumPeak
        );
    } else if (fftFilled >= 32) {
        // Zero-padded partial FFT — coarser resolution but functional
        float padded[FFT_SAMPLES] = {};
        memcpy(padded, fftSnap, fftFilled * sizeof(float));
        result.dominantFreq = sp_computeFFT(
            padded, FFT_SAMPLES, SENSOR_SAMPLE_RATE,
            result.spectrum, &result.spectrumPeak
        );
    }

    // ── Heatmap (relative model) ──────────────────────────────
    result.heatmap = sp_computeHeatmap(result.rms, result.dominantFreq, baseline);

    // ── Anomaly detection with hysteresis ─────────────────────
    //
    //   Two thresholds create a dead-band:
    //     SET   threshold = baseline × 2.5  (hard structural event)
    //     CLEAR threshold = baseline × 1.5  (well below trigger level)
    //
    //   This prevents a sensor borderline between thresholds from
    //   toggling the anomaly flag every processing cycle.
    //
    float setThreshold   = baseline * ANOMALY_SIGMA_MULT;   // 2.5×
    float clearThreshold = baseline * ANOMALY_HYSTERESIS;   // 1.5×

    bool rmsExceedsSet    = (result.rms > setThreshold);
    bool rmsBelowClear    = (result.rms < clearThreshold);
    bool heatmapExceeds   = (result.heatmap > ANOMALY_HEATMAP_LEVEL);

    // ── State machine ──────────────────────────────────────────
    if (!s_inAnomaly[nodeIndex]) {
        // NORMAL state: enter anomaly on SET threshold breach
        if (rmsExceedsSet || heatmapExceeds) {
            s_inAnomaly[nodeIndex] = true;
        }
    } else {
        // ANOMALY state: exit only when below CLEAR threshold (hysteresis)
        if (rmsBelowClear && !heatmapExceeds) {
            s_inAnomaly[nodeIndex] = false;
            s_alertFired[nodeIndex] = false;   // Re-arm for next event
        }
    }

    result.anomaly = s_inAnomaly[nodeIndex];

    // ── Rising-edge detection for alert broadcast ─────────────
    // newAnomaly is TRUE only on the FIRST cycle of a new anomaly.
    // main.ino's taskSignalProcessing broadcasts the WS alert ONLY
    // when newAnomaly==true, preventing popup spam.
    if (result.anomaly && !s_alertFired[nodeIndex]) {
        result.newAnomaly    = true;
        s_alertFired[nodeIndex] = true;
    } else {
        result.newAnomaly = false;
    }

    result.timestamp = millis();
    return true;
}
