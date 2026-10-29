/*
 * ============================================================
 *  SHM_Main.ino — Structural Health Monitoring Firmware v3
 *  Target  : ESP32-S3-WROOM-1
 *  Board   : esp32 (Espressif) ≥ v2.0 in Arduino IDE
 *
 *  Libraries (install via Library Manager):
 *    • arduinoFFT  ≥ v2.0
 *
 *  ⚠  IMPORTANT INCLUDE ORDER:
 *     #include <WebServer.h>  must appear BEFORE
 *     #include "WebServerUI.h"
 *
 *  Wiring (3-axis config):
 *    ESP32-S3 GPIO 4  → AD0 of IMU 0  (X-axis)
 *    ESP32-S3 GPIO 5  → AD0 of IMU 1  (Y-axis)
 *    ESP32-S3 GPIO 6  → AD0 of IMU 2  (Z-axis)
 *    All IMUs share SDA (GPIO 8) and SCL (GPIO 9)
 *
 *  Network:
 *    SSID : SHM_MONITOR
 *    PASS : REDACTED_IN_ARCHIVE
 *    IP   : 192.168.4.1
 *    Open browser → http://192.168.4.1
 *
 *  CSV log stored in LittleFS at /shm.csv
 *  Auto-reset (delete + recreate with header) on download
 *
 *  Signal pipeline (v3 — per SHM_Details_V2):
 *    readMPU6050() → calibApply() → magnitude → mafUpdate()
 *    → gRmsBuf / gFftBuf → computeRMS() / computeFFT()
 *    → intensity → JSON → Web UI + CSV
 * ============================================================
 */

// ── Includes (order matters — see note above) ──────────────────
#include <LittleFS.h>
#include <WiFi.h>
#include <WebServer.h>      // ESP32 library (angle-brackets)
#include <Wire.h>
#include "Calculations.h"   // signal processing (calib, MAF, RMS, FFT)
#include "WebServerUI.h"    // dashboard HTML (quotes)

// ═════════════════════════════════════════════════════════════
//  NETWORK CONFIGURATION
// ═════════════════════════════════════════════════════════════
static const char* AP_SSID = "SHM_MONITOR";
static const char* AP_PASS = "REDACTED_IN_ARCHIVE";
static const IPAddress AP_IP(192, 168, 4, 1);
static const IPAddress AP_GW(192, 168, 4, 1);
static const IPAddress AP_SN(255, 255, 255, 0);

// ═════════════════════════════════════════════════════════════
//  HARDWARE CONSTANTS
// ═════════════════════════════════════════════════════════════
#define NUM_NODES      3
#define MPU_ADDR_LOW   0x68    // AD0 = LOW → I2C address

const int AD0_PINS[NUM_NODES] = { 4, 5, 6 };

// Axis labels used in CSV, JSON, and Serial output
static const char* AXIS_NAME[NUM_NODES] = { "X", "Y", "Z" };

// I2C pins — adjust to your board variant
#define SHM_SDA  8
#define SHM_SCL  9

// ═════════════════════════════════════════════════════════════
//  PROCESSING CONSTANTS
// ═════════════════════════════════════════════════════════════
#define SENSOR_PERIOD_MS   6     // ~167 Hz per sensor
#define PROC_PERIOD_MS    50     // 20 Hz
#define SERVER_PERIOD_MS  50     // 20 Hz

static const float SENSOR_SAMPLE_RATE = 1000.0f / SENSOR_PERIOD_MS;

// ═════════════════════════════════════════════════════════════
//  CSV LOGGING via LittleFS
//
//  Strategy: keep file open globally; flush every FLUSH_BYTES_THRESH
//  bytes OR every FLUSH_INTERVAL_MS ms — whichever comes first.
//  On download: flush → close → streamFile → delete → recreate+header.
// ═════════════════════════════════════════════════════════════
#define FLUSH_INTERVAL_MS   3000   // max ms between flushes
#define FLUSH_BYTES_THRESH  1024   // flush after ~1 KB written

static File              gCsvFile;
static SemaphoreHandle_t gFileMutex    = nullptr;
static uint32_t          gFlushTimer   = 0;
static uint32_t          gBytesWritten = 0;

// ═════════════════════════════════════════════════════════════
//  SHARED DATA STRUCTURES
// ═════════════════════════════════════════════════════════════
struct SensorNode {
    float ax, ay, az;   // calibrated acceleration (g)
    float gx, gy, gz;   // gyro (°/s)
    float rms;          // RMS of filtered vibration magnitude
    float freq;         // dominant frequency (Hz)
    float intensity;    // normalised vibration [0–1]
};

static volatile SensorNode gNodes[NUM_NODES];
static SemaphoreHandle_t   gDataMutex = nullptr;

// ── RMS sliding-window buffers ─────────────────────────────────
static float gRmsBuf[NUM_NODES][RMS_WINDOW_SIZE];
static int   gRmsIdx[NUM_NODES]   = {};
static bool  gRmsReady[NUM_NODES] = {};

// ── FFT time-domain buffers ────────────────────────────────────
static float gFftBuf[NUM_NODES][FFT_SAMPLES];
static int   gFftIdx[NUM_NODES] = {};

// ▶ per-node calibration state (§4.4)
static CalibState gCalib[NUM_NODES];

// ▶ per-axis MAF filter state (§4.2.1, §5.0)
//   gMaf[node][axis]  where axis: 0=ax  1=ay  2=az
//   MAF is applied to each calibrated axis component BEFORE
//   magnitude calculation (correct §5.0 pipeline order).
static MafState gMaf[NUM_NODES][3];

// ▶ Dynamic anomaly baseline (§10)
//   Idle RMS is collected for BASELINE_PERIOD_MS after boot.
//   WARN and CRIT thresholds are derived as baseline + margin.
#define BASELINE_PERIOD_MS    10000UL  // 10 s collection window
#define BASELINE_WARN_MARGIN  0.05f    // g above baseline → WARN
#define BASELINE_CRIT_MARGIN  0.10f    // g above baseline → CRIT

struct BaselineState {
    double sumRms = 0.0;
    int    count  = 0;
    float  rms    = 0.0f;   // locked idle RMS
    float  warn   = 0.08f;  // fallback until baseline locked
    float  crit   = 0.15f;
    bool   done   = false;
};
static BaselineState gBaseline[NUM_NODES];
static uint32_t      gBaselineStart = 0;  // set just before tasks launch

// ═════════════════════════════════════════════════════════════
//  WEB SERVER
// ═════════════════════════════════════════════════════════════
static WebServer server(80);

// ═════════════════════════════════════════════════════════════
//  FORWARD DECLARATIONS
// ═════════════════════════════════════════════════════════════
static void selectSensor  (int idx);
static void initMPU6050   (int idx);
static void readMPU6050   (int idx);   // reads + calibApply; no buffer push
static void runCalibration();          // ▶ NEW — blocking startup routine

static void taskSensorAcquisition(void* pv);
static void taskProcessing        (void* pv);
static void taskWebServer         (void* pv);

static void handleRoot    ();
static void handleData    ();
static void handleDownload();

// ═════════════════════════════════════════════════════════════
//  SETUP
// ═════════════════════════════════════════════════════════════
void setup() {
    Serial.begin(115200);
    while (!Serial && millis() < 3000) {}
    Serial.println("\n[SHM] Booting…");

    // ── I2C ──────────────────────────────────────────────────
    Wire.begin(SHM_SDA, SHM_SCL);
    Wire.setClock(400000UL);

    // ── AD0 GPIO setup ────────────────────────────────────────
    for (int i = 0; i < NUM_NODES; i++) {
        pinMode(AD0_PINS[i], OUTPUT);
        digitalWrite(AD0_PINS[i], HIGH);   // default HIGH → 0x69 (deselected)
    }

    // ── Initialise each MPU6050 ───────────────────────────────
    for (int i = 0; i < NUM_NODES; i++) {
        selectSensor(i);
        delay(5);
        initMPU6050(i);
    }

    // ── WiFi Access Point ─────────────────────────────────────
    //   ⚠ Brought BEFORE calibration deliberately:
    //     runCalibration() is a blocking loop (~3 s). If an IMU is
    //     slow or missing the loop takes longer. Starting the AP first
    //     means it is always reachable regardless of IMU state.
    //
    //   ⚠ Correct ESP32-S3 softAP order:
    //     1. WiFi.mode()
    //     2. WiFi.softAP()       — starts the AP radio
    //     3. delay(100)          — let the AP come up fully
    //     4. WiFi.softAPConfig() — apply custom IP (must be AFTER softAP)
    WiFi.mode(WIFI_AP);
    if (!WiFi.softAP(AP_SSID, AP_PASS)) {
        Serial.println("[SHM] ⚠ WiFi.softAP() FAILED — check power / antenna");
    }
    delay(100);   // required: AP radio must be up before reconfiguring IP
    WiFi.softAPConfig(AP_IP, AP_GW, AP_SN);
    Serial.print("[SHM] AP IP: ");
    Serial.println(WiFi.softAPIP());   // should print 192.168.4.1

    // ── Static calibration (§4.4) ────────────────────────────
    //   Runs after AP is up so the network is available immediately.
    //   Keep the structure motionless during this phase (~3 s).
    runCalibration();

    // ── HTTP routes ───────────────────────────────────────────
    server.on("/",         HTTP_GET, handleRoot);
    server.on("/data",     HTTP_GET, handleData);
    server.on("/download", HTTP_GET, handleDownload);

    // ── LittleFS ──────────────────────────────────────────────
    if (!LittleFS.begin(true)) {
        Serial.println("[SHM] LittleFS mount failed!");
    }

    // Serve three.js from flash storage
    server.on("/three.js", HTTP_GET, []() {
        File f = LittleFS.open("/three.min.js", "r");
        if (!f) { server.send(404, "text/plain", "three.min.js not found"); return; }
        server.streamFile(f, "application/javascript");
        f.close();
    });

    // Open CSV log in append mode; write header if file is new/empty
    gCsvFile = LittleFS.open("/shm.csv", "a");
    if (gCsvFile) {
        if (gCsvFile.size() == 0) {
            gCsvFile.print("timestamp,axis,ax,ay,az,rms,freq,intensity\r\n");
            gCsvFile.flush();
            Serial.println("[SHM] CSV created with header");
        } else {
            Serial.printf("[SHM] CSV log resumed (%u bytes)\n", gCsvFile.size());
        }
    } else {
        Serial.println("[SHM] WARNING: CSV log open FAILED");
    }

    server.begin();
    Serial.println("[SHM] HTTP server started");

    // ── Mutexes ───────────────────────────────────────────────
    gDataMutex = xSemaphoreCreateMutex();
    gFileMutex = xSemaphoreCreateMutex();
    gFlushTimer = millis();

    // ── Zero shared buffers ───────────────────────────────────
    memset((void*)gNodes, 0, sizeof(gNodes));
    memset(gRmsBuf,   0, sizeof(gRmsBuf));
    memset(gFftBuf,   0, sizeof(gFftBuf));
    memset(gMaf,      0, sizeof(gMaf));       // 2D MAF array
    memset(gBaseline, 0, sizeof(gBaseline));  // baseline state
    // Restore fallback thresholds zeroed by memset
    for (int i = 0; i < NUM_NODES; i++) {
        gBaseline[i].warn = 0.08f;
        gBaseline[i].crit = 0.15f;
    }

    gBaselineStart = millis();   // baseline window starts now

    // ── FreeRTOS Tasks ────────────────────────────────────────
    xTaskCreatePinnedToCore(taskSensorAcquisition, "SensorTask", 8192, nullptr, 3, nullptr, 0);
    xTaskCreatePinnedToCore(taskProcessing,         "ProcTask",   8192, nullptr, 2, nullptr, 1);
    xTaskCreatePinnedToCore(taskWebServer,          "WebTask",    8192, nullptr, 1, nullptr, 1);

    Serial.println("[SHM] All tasks launched — system running.");
}

void loop() { vTaskDelay(pdMS_TO_TICKS(1000)); }

// ═════════════════════════════════════════════════════════════
//  SENSOR HELPERS
// ═════════════════════════════════════════════════════════════

/**
 * selectSensor — activate one IMU via AD0 multiplexing.
 * Sets the target IMU's AD0 LOW (→ 0x68) and all others HIGH (→ 0x69).
 */
static void selectSensor(int idx) {
    for (int j = 0; j < NUM_NODES; j++) {
        digitalWrite(AD0_PINS[j], (j == idx) ? LOW : HIGH);
    }
}

/**
 * initMPU6050 — wake + configure one IMU.
 * Assumes selectSensor(idx) has already been called.
 */
static void initMPU6050(int idx) {
    Wire.beginTransmission(MPU_ADDR_LOW);
    Wire.write(0x6B); Wire.write(0x00);   // PWR_MGMT_1: wake
    if (Wire.endTransmission(true) != 0) {
        Serial.printf("[SHM] ⚠ IMU %d (%s-axis) not found — check wiring\n",
                      idx, AXIS_NAME[idx]);
        return;
    }
    delay(10);

    // Accel ±2 g
    Wire.beginTransmission(MPU_ADDR_LOW); Wire.write(0x1C); Wire.write(0x00); Wire.endTransmission(true);
    // Gyro ±250 °/s
    Wire.beginTransmission(MPU_ADDR_LOW); Wire.write(0x1B); Wire.write(0x00); Wire.endTransmission(true);
    // DLPF 44 Hz
    Wire.beginTransmission(MPU_ADDR_LOW); Wire.write(0x1A); Wire.write(0x03); Wire.endTransmission(true);
    // Sample-rate divider → ~200 Hz output
    Wire.beginTransmission(MPU_ADDR_LOW); Wire.write(0x19); Wire.write(0x04); Wire.endTransmission(true);

    Serial.printf("[SHM] IMU %d (%s-axis) OK\n", idx, AXIS_NAME[idx]);
}

/**
 * readMPU6050 — read 14 bytes from the active IMU, convert to
 * physical units, apply calibration offsets, and store in gNodes.
 *
 * ▶ CHANGED (v3):
 *   - calibApply() now corrects ax/ay/az before storing in gNodes.
 *   - Magnitude calculation and buffer push are REMOVED from here;
 *     they now happen in taskSensorAcquisition AFTER the MAF step.
 *     This preserves the correct pipeline order:
 *       read → calib → magnitude → MAF → buffer
 */
static void readMPU6050(int idx) {
    Wire.beginTransmission(MPU_ADDR_LOW);
    Wire.write(0x3B);
    Wire.endTransmission(false);
    uint8_t n = Wire.requestFrom((uint8_t)MPU_ADDR_LOW, (uint8_t)14, (uint8_t)true);
    if (n < 14) return;

    auto r16 = []() -> int16_t {
        return ((int16_t)Wire.read() << 8) | Wire.read();
    };

    int16_t axR = r16(), ayR = r16(), azR = r16();
    r16();   // temperature — discard
    int16_t gxR = r16(), gyR = r16(), gzR = r16();

    // Convert to physical units
    float ax = axR / 16384.0f;
    float ay = ayR / 16384.0f;
    float az = azR / 16384.0f;
    float gx = gxR /   131.0f;
    float gy = gyR /   131.0f;
    float gz = gzR /   131.0f;

    // ▶ NEW: Apply per-axis calibration offsets (§4.4)
    //   calibApply is safe to call even before calibFinish —
    //   offsets default to 0 so it is a no-op during warm-up.
    calibApply(gCalib[idx], ax, ay, az);

    // Store calibrated values in the shared struct
    if (xSemaphoreTake(gDataMutex, pdMS_TO_TICKS(2)) == pdTRUE) {
        gNodes[idx].ax = ax;  gNodes[idx].ay = ay;  gNodes[idx].az = az;
        gNodes[idx].gx = gx;  gNodes[idx].gy = gy;  gNodes[idx].gz = gz;
        xSemaphoreGive(gDataMutex);
    }
    // Magnitude, MAF, and buffer push happen in taskSensorAcquisition.
}

// ═════════════════════════════════════════════════════════════
//  CALIBRATION ROUTINE  (▶ NEW — §4.4, §2 MASTER FLOW)
// ═════════════════════════════════════════════════════════════

/**
 * runCalibration — blocking static calibration at startup.
 *
 * For each sensor:
 *   1. Select the IMU.
 *   2. Collect CALIB_SAMPLES raw readings.
 *   3. Feed each to calibUpdate().
 *   4. Call calibFinish() to lock per-axis offsets.
 *
 * Runs synchronously in setup() BEFORE FreeRTOS tasks start,
 * so there is no I2C bus contention and no mutex required.
 *
 * Keep the monitored structure motionless during this period
 * (~1 second total at 5 ms per sample × 200 samples × 3 nodes).
 */
static void runCalibration() {
    Serial.println("[SHM] ── Calibration start — keep structure STILL ──");

    for (int i = 0; i < NUM_NODES; i++) {
        Serial.printf("[SHM] Calibrating %s-axis IMU (%d/%d)…\n",
                      AXIS_NAME[i], i + 1, NUM_NODES);

        selectSensor(i);
        delay(20);   // allow multiplexer to settle

        int collected = 0;
        int retries   = 0;
        const int MAX_RETRIES = CALIB_SAMPLES * 4;   // bail out after 4x quota

        while (collected < CALIB_SAMPLES && retries < MAX_RETRIES) {
            // Direct I2C read — mirrors readMPU6050 but without side effects
            Wire.beginTransmission(MPU_ADDR_LOW);
            Wire.write(0x3B);
            Wire.endTransmission(false);
            uint8_t n = Wire.requestFrom((uint8_t)MPU_ADDR_LOW, (uint8_t)14, (uint8_t)true);
            if (n < 14) {
                retries++;
                delay(2);
                continue;   // retry; guard above prevents infinite spin
            }

            auto r16 = []() -> int16_t {
                return ((int16_t)Wire.read() << 8) | Wire.read();
            };

            float ax = r16() / 16384.0f;
            float ay = r16() / 16384.0f;
            float az = r16() / 16384.0f;
            r16();           // temperature — discard
            r16(); r16(); r16();   // gyro — discard

            calibUpdate(gCalib[i], ax, ay, az);
            collected++;
            delay(5);   // ~200 Hz equivalent spacing
        }

        if (collected < CALIB_SAMPLES) {
            // IMU unreachable — offsets stay 0, live data flows uncorrected
            Serial.printf("[SHM] \u26a0 %s-axis IMU unreachable — calibration SKIPPED\n",
                          AXIS_NAME[i]);
        } else {
            calibFinish(gCalib[i]);
            Serial.printf("[SHM] %s-axis offsets -> ax=%.4f  ay=%.4f  az=%.4f\n",
                          AXIS_NAME[i],
                          gCalib[i].offAx,
                          gCalib[i].offAy,
                          gCalib[i].offAz);

            // ── Gravity validation (§4.4) ──────────────────────────────────
            // After removing offset bias, the magnitude of the mean vector
            // should equal ~1g.  Significant deviation means the sensor was
            // moving during calibration and the offsets are unreliable.
            float gMag = sqrtf(gCalib[i].offAx * gCalib[i].offAx
                             + gCalib[i].offAy * gCalib[i].offAy
                             + gCalib[i].offAz * gCalib[i].offAz);
            float gErr = fabsf(gMag - 1.0f);
            if (gErr > 0.10f) {
                Serial.printf("[SHM] \u26a0 %s-axis gravity check FAILED "
                              "(|a|=%.3fg, expected 1.0g \u00b1 0.10g) "
                              "— was sensor moving during calibration?\n",
                              AXIS_NAME[i], gMag);
            } else {
                Serial.printf("[SHM] %s-axis gravity OK  |a|=%.3fg\n",
                              AXIS_NAME[i], gMag);
            }
        }
    }

    Serial.println("[SHM] -- Calibration complete --");
}

// ═════════════════════════════════════════════════════════════
//  FREERTOS TASKS
// ═════════════════════════════════════════════════════════════

/**
 * Task 1 — Sensor Acquisition (Core 0, priority 3)
 *
 * Cycles through all 3 IMUs every SENSOR_PERIOD_MS (~167 Hz/sensor).
 *
 * Pipeline per IMU per cycle (v3):
 *   1. selectSensor() — AD0 multiplexing
 *   2. readMPU6050()  — I2C read + unit conversion + calibApply()
 *   3. Snapshot calibrated ax/ay/az from gNodes
 *   4. Compute vibration magnitude = |a| − 1 g  (gravity removed)
 *   5. mafUpdate()    — moving-average smoothing (§4.2.1)
 *   6. Push FILTERED magnitude to gRmsBuf and gFftBuf
 *   7. Append CSV row to LittleFS (non-blocking; skips if file busy)
 */
static void taskSensorAcquisition(void* pv) {
    TickType_t lastWake = xTaskGetTickCount();
    const TickType_t period = pdMS_TO_TICKS(SENSOR_PERIOD_MS);

    for (;;) {
        uint32_t ts = millis();

        for (int i = 0; i < NUM_NODES; i++) {
            // ── Step 1-2: select IMU and read (calib applied inside) ──
            selectSensor(i);
            delayMicroseconds(80);
            readMPU6050(i);

            // ── Step 3: snapshot calibrated accel from shared struct ──
            float ax = 0.0f, ay = 0.0f, az = 0.0f;
            if (xSemaphoreTake(gDataMutex, pdMS_TO_TICKS(2)) == pdTRUE) {
                ax = gNodes[i].ax;
                ay = gNodes[i].ay;
                az = gNodes[i].az;
                xSemaphoreGive(gDataMutex);
            }

            // ── Step 4: MAF per-axis BEFORE magnitude (§5.0 correct order) ──
            //   Filter each calibrated axis component independently.
            //   gMaf[node][0..2] = ax/ay/az filters respectively.
            float fax = mafUpdate(gMaf[i][0], ax);
            float fay = mafUpdate(gMaf[i][1], ay);
            float faz = mafUpdate(gMaf[i][2], az);

            // ── Step 5: magnitude from filtered axes (§4.3) ──────────
            //   mag = |a_filtered| − 1g  (removes gravity)
            float filtered = sqrtf(fax * fax + fay * fay + faz * faz) - 1.0f;
            if (filtered < 0.0f) filtered = 0.0f;

            // ── Step 6: push filtered magnitude to DSP buffers ────────
            gRmsBuf[i][gRmsIdx[i]] = filtered;
            gRmsIdx[i] = (gRmsIdx[i] + 1) % RMS_WINDOW_SIZE;
            if (gRmsIdx[i] == 0) gRmsReady[i] = true;

            gFftBuf[i][gFftIdx[i]] = filtered;
            gFftIdx[i] = (gFftIdx[i] + 1) % FFT_SAMPLES;

            // ── Step 7: append CSV row (non-blocking) ─────────────────
            if (xSemaphoreTake(gFileMutex, 0) == pdTRUE) {
                if (gCsvFile) {
                    // Snapshot processed values for the log row
                    float rms = 0.0f, freq = 0.0f, intensity = 0.0f;
                    if (xSemaphoreTake(gDataMutex, 0) == pdTRUE) {
                        rms       = gNodes[i].rms;
                        freq      = gNodes[i].freq;
                        intensity = gNodes[i].intensity;
                        xSemaphoreGive(gDataMutex);
                    }

                    // CSV format: timestamp,axis,ax,ay,az,rms,freq,intensity
                    char row[128];
                    int len = snprintf(row, sizeof(row),
                        "%lu,%s,%.4f,%.4f,%.4f,%.4f,%.2f,%.4f\r\n",
                        (unsigned long)ts, AXIS_NAME[i],
                        ax, ay, az, rms, freq, intensity
                    );
                    gCsvFile.print(row);
                    gBytesWritten += (uint32_t)len;

                    // Flush on threshold — avoids constant tiny writes
                    uint32_t now = millis();
                    if (gBytesWritten >= FLUSH_BYTES_THRESH ||
                        (now - gFlushTimer) >= FLUSH_INTERVAL_MS) {
                        gCsvFile.flush();
                        gBytesWritten = 0;
                        gFlushTimer   = now;
                    }
                }
                xSemaphoreGive(gFileMutex);
            }
        }

        vTaskDelayUntil(&lastWake, period);
    }
}

/**
 * Task 2 — Signal Processing (Core 1, priority 2)
 *
 * Computes RMS, FFT dominant frequency, and intensity
 * for each axis node at PROC_PERIOD_MS (20 Hz).
 * Reads from gRmsBuf / gFftBuf written by Task 1.
 */
static void taskProcessing(void* pv) {
    TickType_t lastWake = xTaskGetTickCount();
    const TickType_t period = pdMS_TO_TICKS(PROC_PERIOD_MS);

    for (;;) {
        for (int i = 0; i < NUM_NODES; i++) {
            int rmsLen = gRmsReady[i] ? RMS_WINDOW_SIZE : gRmsIdx[i];
            if (rmsLen < 2) continue;

            float rms       = computeRMS(gRmsBuf[i], rmsLen);
            float freq      = computeFFT(gFftBuf[i], FFT_SAMPLES, SENSOR_SAMPLE_RATE);
            float intensity = computeIntensity(rms);

            // ── Dynamic baseline accumulation (§10) ─────────────────
            if (!gBaseline[i].done) {
                gBaseline[i].sumRms += (double)rms;
                gBaseline[i].count++;
                if (millis() - gBaselineStart >= BASELINE_PERIOD_MS
                    && gBaseline[i].count >= 5) {
                    gBaseline[i].rms  = (float)(gBaseline[i].sumRms / gBaseline[i].count);
                    gBaseline[i].warn = gBaseline[i].rms + BASELINE_WARN_MARGIN;
                    gBaseline[i].crit = gBaseline[i].rms + BASELINE_CRIT_MARGIN;
                    gBaseline[i].done = true;
                    Serial.printf("[SHM] %s-axis baseline locked: "
                                  "idle=%.4fg  WARN=%.4fg  CRIT=%.4fg\n",
                                  AXIS_NAME[i],
                                  gBaseline[i].rms,
                                  gBaseline[i].warn,
                                  gBaseline[i].crit);
                }
            }

            if (xSemaphoreTake(gDataMutex, pdMS_TO_TICKS(5)) == pdTRUE) {
                gNodes[i].rms       = rms;
                gNodes[i].freq      = freq;
                gNodes[i].intensity = intensity;
                xSemaphoreGive(gDataMutex);
            }
        }

        vTaskDelayUntil(&lastWake, period);
    }
}

/**
 * Task 3 — Web Server (Core 1, priority 1)
 * Handles HTTP client requests at SERVER_PERIOD_MS (20 Hz).
 */
static void taskWebServer(void* pv) {
    TickType_t lastWake = xTaskGetTickCount();
    const TickType_t period = pdMS_TO_TICKS(SERVER_PERIOD_MS);

    for (;;) {
        server.handleClient();
        vTaskDelayUntil(&lastWake, period);
    }
}

// ═════════════════════════════════════════════════════════════
//  HTTP ROUTE HANDLERS
// ═════════════════════════════════════════════════════════════

static void handleRoot() {
    server.send_P(200, "text/html", index_html);
}

/**
 * GET /data — JSON snapshot for all 3 axis nodes.
 * Returns calibrated ax/ay/az and processed rms/freq/intensity.
 */
static void handleData() {
    // 3 nodes × ~280 chars + envelope — under 1100 bytes
    static char buf[1100];
    int pos = 0;

    pos += snprintf(buf + pos, sizeof(buf) - pos, "{\"nodes\":[");

    if (xSemaphoreTake(gDataMutex, pdMS_TO_TICKS(10)) == pdTRUE) {
        for (int i = 0; i < NUM_NODES; i++) {
            const SensorNode& n = (const SensorNode&)gNodes[i];
            pos += snprintf(buf + pos, sizeof(buf) - pos,
                "%s{\"id\":%d,\"axis\":\"%s\","
                "\"acc\":[%.4f,%.4f,%.4f],"
                "\"gyro\":[%.4f,%.4f,%.4f],"
                "\"rms\":%.4f,"
                "\"freq\":%.2f,"
                "\"intensity\":%.4f,"
                "\"warn\":%.4f,"
                "\"crit\":%.4f,"
                "\"baseline_done\":%s}",
                (i > 0) ? "," : "",
                i, AXIS_NAME[i],
                n.ax, n.ay, n.az,
                n.gx, n.gy, n.gz,
                n.rms, n.freq, n.intensity,
                gBaseline[i].warn, gBaseline[i].crit,
                gBaseline[i].done ? "true" : "false"
            );
        }
        xSemaphoreGive(gDataMutex);
    }

    pos += snprintf(buf + pos, sizeof(buf) - pos, "]}");
    server.send(200, "application/json", buf);
}

/**
 * GET /download — stream the CSV file directly from LittleFS.
 *
 * Flow: lock → flush+close → streamFile → delete → recreate+header → unlock
 * Protected by gFileMutex to block concurrent sensor-task writes.
 */
static void handleDownload() {
    if (xSemaphoreTake(gFileMutex, pdMS_TO_TICKS(500)) != pdTRUE) {
        server.send(503, "text/plain", "File busy — try again in a moment");
        return;
    }

    // Flush and close the write handle so the reader sees all data
    if (gCsvFile) {
        gCsvFile.flush();
        gCsvFile.close();
    }

    File f = LittleFS.open("/shm.csv", "r");
    if (!f || f.size() == 0) {
        if (f) f.close();
        gCsvFile = LittleFS.open("/shm.csv", "a");
        xSemaphoreGive(gFileMutex);
        server.send(404, "text/plain", "No data logged yet");
        return;
    }

    // Stream directly from flash — no heap allocation needed
    server.sendHeader("Content-Disposition", "attachment; filename=shm_data.csv");
    server.sendHeader("Cache-Control",       "no-cache");
    server.streamFile(f, "text/csv");
    f.close();

    // Auto-reset: delete and recreate with a fresh header
    LittleFS.remove("/shm.csv");
    gCsvFile = LittleFS.open("/shm.csv", "a");
    if (gCsvFile) {
        gCsvFile.print("timestamp,axis,ax,ay,az,rms,freq,intensity\r\n");
        gCsvFile.flush();
        Serial.println("[SHM] CSV reset after download");
    } else {
        Serial.println("[SHM] WARNING: CSV recreate FAILED after download");
    }

    gBytesWritten = 0;
    gFlushTimer   = millis();

    xSemaphoreGive(gFileMutex);
}
