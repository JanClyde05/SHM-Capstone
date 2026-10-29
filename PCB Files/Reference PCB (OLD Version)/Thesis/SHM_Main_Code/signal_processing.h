/*
 * ============================================================
 * signal_processing.h  —  v2 (UPDATED)
 *
 * FIX ① — Intensity always ~49%
 *   Root cause: hardcoded ANOMALY_RMS_THRESHOLD (0.12 g) used as
 *   absolute normalizer. Real ambient RMS ≈ 0.98 g (gravity
 *   component) immediately saturated the score to 1.0.
 *
 *   Solution: RELATIVE baseline model.
 *     heatmap ≈ 0   →  rms ≈ ambient baseline  (stable)
 *     heatmap = 1   →  rms exceeds baseline by BASELINE_SENSITIVITY
 *   The baseline is an EMA that learns the ambient floor, so the
 *   score reflects CHANGE from normal, not absolute amplitude.
 *
 * FIX ② — Anomaly popup spam
 *   Added 'newAnomaly' flag to ProcessedData.
 *   Only true on the RISING EDGE of anomaly (first detection).
 *   ws_broadcastAlert() is called only when newAnomaly==true.
 *   Hysteresis band prevents rapid SET/CLEAR toggling.
 *
 * FIX ③ — Faster baseline bootstrap at startup
 *   BASELINE_WARMUP_COUNT: first 50 computations use alpha=0.15
 *   so the baseline reaches ambient level within ~3 seconds
 *   instead of drifting for minutes.
 * ============================================================
 */

#pragma once
#include <Arduino.h>
#include <arduinoFFT.h>
#include "imu_manager.h"

// ── Buffer dimensions ─────────────────────────────────────────
#define RMS_WINDOW              50
#define FFT_SAMPLES             128
#define FFT_HALF                (FFT_SAMPLES / 2)
#define SENSOR_SAMPLE_RATE      20.0f   // Hz per node (~180 Hz total / 9 nodes)

// ── Baseline EMA ──────────────────────────────────────────────
//   Baseline tracks ambient RMS via exponential moving average.
//   Two-speed: fast during warmup, slow after.
#define BASELINE_ALPHA          0.05f   // Slow ambient tracking (was 0.01)
#define BASELINE_ALPHA_FAST     0.15f   // Fast initial bootstrap
#define BASELINE_WARMUP_COUNT   50      // # computeNode calls before slow mode

// ── Heatmap sensitivity ───────────────────────────────────────
//   Fraction above baseline at which heatmap saturates to 1.0.
//   0.50 → 50% above baseline = max alert.
//   Raise this value to make the system LESS sensitive.
#define BASELINE_SENSITIVITY    0.50f

// ── Anomaly detection thresholds (relative to baseline) ───────
//   Hysteresis band prevents chattering:
//     SET   : rms > baseline × ANOMALY_SIGMA_MULT  (2.5×)
//     CLEAR : rms < baseline × ANOMALY_HYSTERESIS  (1.5×)
#define ANOMALY_SIGMA_MULT      2.50f
#define ANOMALY_HYSTERESIS      1.50f
#define ANOMALY_HEATMAP_LEVEL   0.65f   // Heatmap > 65% also triggers anomaly

// ── Frequency plausibility bounds ────────────────────────────
#define ANOMALY_FREQ_NOISE_MIN  0.3f    // Hz — below = quasi-static / DC drift
#define ANOMALY_FREQ_NOISE_MAX  9.5f    // Hz — above Nyquist = aliasing

// ── Ring buffer per sensor ────────────────────────────────────
struct SensorBuffer {
    float    fftBuf[FFT_SAMPLES];
    uint16_t fftHead;
    uint16_t fftFilled;

    float    rmsBuf[RMS_WINDOW];
    uint16_t rmsHead;
    uint16_t rmsFilled;

    SemaphoreHandle_t mutex;
};

// ── Per-node processing result ────────────────────────────────
struct ProcessedData {
    float    rms;                   // g   — vector magnitude RMS
    float    dominantFreq;          // Hz  — FFT peak frequency
    float    heatmap;               // 0–1 — relative anomaly severity
    bool     anomaly;               // true while anomaly condition is active
    bool     newAnomaly;            // true ONLY on rising edge (first detection)
    float    spectrum[FFT_HALF];    // Per-bin FFT magnitudes
    float    spectrumPeak;          // Max spectral magnitude
    uint32_t timestamp;             // millis()
};

// ── Public API ────────────────────────────────────────────────
void  signal_processing_init();
void  sp_pushSample(int nodeIndex, const IMUData &data);
bool  sp_computeNode(int nodeIndex, ProcessedData &result);

// Unit-testable helpers
float sp_computeRMS    (const float *data, int size);
float sp_computeFFT    (float *timeSeries, int size, float sampleRate,
                        float *magnitudesOut, float *peakMagOut);
float sp_computeHeatmap(float rms, float freq, float baseline);
