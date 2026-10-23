#pragma once
/*
 * ============================================================
 *  Calculations.h — SHM Signal Processing (v4)
 *  Provides calibration, moving-average filtering, RMS, FFT,
 *  and intensity normalization for the SHM system.
 *
 *  Target  : ESP32-S3 | Library: arduinoFFT v2.x
 *
 *  Pipeline (§5.0 — exact order):
 *    Raw Signal → Calibration (offset removal per axis)
 *              → Moving-Average Filter (per axis: ax, ay, az)
 *              → Magnitude: mag = |a_filtered| − 1g
 *              → RMS + FFT → Intensity
 *
 *  Types / functions:
 *    CalibState  — per-sensor calibration state
 *      calibUpdate()   — feed one raw sample during static phase
 *      calibFinish()   — compute offsets; validates gravity (§4.4)
 *      calibApply()    — subtract offsets from a live reading
 *      calibIsReady()  — true once calibration is done
 *
 *    MafState    — per-axis moving-average filter state
 *      mafUpdate()     — push one axis sample, returns smoothed value
 *      NOTE: Instantiate one MafState per AXIS (3 per sensor node).
 *            Apply to ax, ay, az individually BEFORE magnitude calc.
 *
 *    computeRMS(), computeFFT(), computeIntensity() — unchanged
 * ============================================================
 */

#include <arduinoFFT.h>
#include <math.h>

// ---- Tuning constants ----------------------------------------
#define FFT_SAMPLES      128      // Must be power-of-2
#define RMS_WINDOW_SIZE   50      // Sliding-window size for RMS
#define MAX_RMS_G         0.3f   // g-force that maps to intensity = 1.0

// ▶ NEW: Calibration + filter sizes (§4.2.1, §4.4)
#define CALIB_SAMPLES    200      // Static samples averaged at startup
#define MAF_SIZE           8      // Moving-average window length (5–10 per doc)
// --------------------------------------------------------------


// ================================================================
//  CALIBRATION  (§4.4 — Static Calibration)
//
//  One CalibState per sensor node.
//  Phase 1 (setup): feed CALIB_SAMPLES raw readings via calibUpdate(),
//                   then call calibFinish() to lock offsets.
//  Phase 2 (live):  call calibApply() on every converted sample.
//
//  Gravity bias note:
//    Gravity (~1 g on one axis) is removed later in the magnitude
//    calculation step (mag = |a| − 1), so we zero all three axis
//    means here without any per-axis gravity compensation.
// ================================================================
struct CalibState {
    // Accumulation sums (only used during calibration phase)
    double sumAx = 0.0, sumAy = 0.0, sumAz = 0.0;
    int    count = 0;

    // Locked offsets (set once by calibFinish)
    float offAx = 0.0f, offAy = 0.0f, offAz = 0.0f;

    // True after calibFinish() succeeds
    bool done = false;
};

// ----------------------------------------------------------------
//  calibUpdate
//  Feed one raw converted sample (in g) during the static phase.
//  Silently ignored if calibration is already done.
// ----------------------------------------------------------------
inline void calibUpdate(CalibState& c, float ax, float ay, float az) {
    if (c.done) return;
    c.sumAx += (double)ax;
    c.sumAy += (double)ay;
    c.sumAz += (double)az;
    c.count++;
}

// ----------------------------------------------------------------
//  calibFinish
//  Compute mean offsets from accumulated sums and mark done.
//  Must be called after feeding at least 2 samples.
// ----------------------------------------------------------------
inline void calibFinish(CalibState& c) {
    if (c.count < 2 || c.done) return;
    c.offAx = (float)(c.sumAx / c.count);
    c.offAy = (float)(c.sumAy / c.count);
    c.offAz = (float)(c.sumAz / c.count);
    c.done  = true;
}

// ----------------------------------------------------------------
//  calibApply
//  Subtract per-axis offsets from a live converted reading.
//  Values are corrected in-place.  Safe to call before done —
//  offsets are zero-initialised so the call becomes a no-op.
// ----------------------------------------------------------------
inline void calibApply(const CalibState& c, float& ax, float& ay, float& az) {
    ax -= c.offAx;
    ay -= c.offAy;
    az -= c.offAz;
}

// ----------------------------------------------------------------
//  calibIsReady
//  Returns true once calibFinish() has been called successfully.
// ----------------------------------------------------------------
inline bool calibIsReady(const CalibState& c) {
    return c.done;
}


// ================================================================
//  MOVING-AVERAGE FILTER  (§4.2.1 — Signal Stabilization)
//
//  One MafState per AXIS per sensor node (3 per node: ax, ay, az).
//  Applied to each calibrated axis component BEFORE the magnitude
//  calculation — this is the correct §5.0 pipeline order:
//    calibApply(ax,ay,az) → mafUpdate(ax) / (ay) / (az)
//    → mag = sqrt(fax²+fay²+faz²) − 1g
//
//  Window = MAF_SIZE samples (≈ 5–10 per documentation).
//  Output ramps up naturally during the first MAF_SIZE calls.
// ================================================================
struct MafState {
    float buf[MAF_SIZE] = {};   // circular sample store
    int   idx  = 0;             // next write position
    float sum  = 0.0f;          // running sum of valid entries
    int   fill = 0;             // number of valid entries (0 → MAF_SIZE)
};

// ----------------------------------------------------------------
//  mafUpdate
//  Push a new sample into the filter and return the smoothed mean.
// ----------------------------------------------------------------
inline float mafUpdate(MafState& m, float sample) {
    // Subtract the oldest slot before overwriting it
    m.sum -= m.buf[m.idx];

    // Write new sample
    m.buf[m.idx] = sample;
    m.sum        += sample;

    // Advance circular index
    m.idx = (m.idx + 1) % MAF_SIZE;

    // Track how many valid samples exist (caps at MAF_SIZE)
    if (m.fill < MAF_SIZE) m.fill++;

    return m.sum / (float)m.fill;
}


// ================================================================
//  computeRMS  (unchanged)
//  Root-Mean-Square of an arbitrary float array.
//  Designed for the circular RMS sliding-window buffer;
//  call once the buffer contains at least 2 valid entries.
// ================================================================
float computeRMS(float* data, int size) {
    if (size <= 0) return 0.0f;
    float sum = 0.0f;
    for (int i = 0; i < size; i++) {
        sum += data[i] * data[i];
    }
    return sqrtf(sum / (float)size);
}


// ================================================================
//  computeFFT  (unchanged)
//  Applies a Hamming window to 'size' time-domain samples,
//  runs an FFT, and returns the dominant frequency in Hz.
//
//  @param data        Filtered vibration magnitude samples
//  @param size        Valid sample count (≤ FFT_SAMPLES)
//  @param sampleRate  Per-sensor acquisition rate (Hz)
// ================================================================
float computeFFT(float* data, int size, float sampleRate) {
    // Static double buffers — avoids repeated stack allocation inside a task
    static double vReal[FFT_SAMPLES];
    static double vImag[FFT_SAMPLES];

    int n = (size < FFT_SAMPLES) ? size : FFT_SAMPLES;

    for (int i = 0; i < n; i++) {
        vReal[i] = (double)data[i];
        vImag[i] = 0.0;
    }
    // Zero-pad the remainder so FFT operates on a full power-of-2 frame
    for (int i = n; i < FFT_SAMPLES; i++) {
        vReal[i] = 0.0;
        vImag[i] = 0.0;
    }

    // arduinoFFT v2.x template API
    ArduinoFFT<double> fft(vReal, vImag, (uint16_t)FFT_SAMPLES, (double)sampleRate);
    fft.windowing(FFTWindow::Hamming, FFTDirection::Forward);
    fft.compute(FFTDirection::Forward);
    fft.complexToMagnitude();

    double peak = fft.majorPeak();
    return (peak > 0.0) ? (float)peak : 0.0f;
}


// ================================================================
//  computeIntensity  (unchanged)
//  Maps RMS (g) to a normalised [0.0 … 1.0] intensity value.
//  Clamped: values above MAX_RMS_G → 1.0, below 0 → 0.0.
// ================================================================
float computeIntensity(float rms) {
    float v = rms / MAX_RMS_G;
    if (v > 1.0f) v = 1.0f;
    if (v < 0.0f) v = 0.0f;
    return v;
}
