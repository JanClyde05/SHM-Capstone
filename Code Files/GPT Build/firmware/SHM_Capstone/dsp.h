#pragma once

#include <stddef.h>
#include <stdint.h>

// Pure numerical module. IDs are mapped in docs/MATHEMATICAL_ALGORITHMS.md.
// Settings are study choices: freeze after pilot, not claims of calibration.
struct DspSettings {
    double bandLoHz = 0.5;
    double bandHiHz = 20.0;
    double relativeTieTolerance = 1e-4; // Diagnostic only: does not reject/alter peak.
    double clipAbs = 0.0;               // 0 disables; raw counts require a raw-count limit.
};

enum class DspStatus : uint8_t {
    Valid,
    InvalidParameters,
    WorkspaceTooSmall,
    NonFiniteInput,
    ClippedInput,
    ZeroSignal,
    NoBandBins,
    NumericalError
};

struct DspAxisResult {
    double dominantFrequencyHz;
    double fsEstimateHz;
    double binSpacingHz;
    double peakMagnitude; // Unnormalized |DFT|; not PSD/calibrated amplitude.
    size_t sampleCount;
    size_t peakBin;
    bool validPeak;
    bool nearTie;      // Other in-band bin within relativeTieTolerance of maximum.
    bool bandEdgePeak; // Maximum is first/last included bin: review band in pilot.
    DspStatus status;
};

struct DspComplex {
    float re;
    float im;
};
struct DspWorkspace {
    DspComplex *a;
    DspComplex *b;
    size_t capacity; // Complex elements in EACH array, never bytes.
};

// Caller owns workspace memory, e.g. PSRAM on ESP32. No heap allocations here.
// N=6000 => M=16384 => 262144 bytes for both arrays, excluding input.
size_t dspWorkspaceLength(size_t sampleCount);
bool dspAnalyzeAxis(const float *samples, size_t count, double fsEstimateHz,
                    const DspSettings &settings, DspWorkspace *workspace, DspAxisResult *result);
// After transform a[0..count-1] holds the N-point DFT. Input validation can
// return before populating it; never use stale output from a prior window.
const char *dspStatusName(DspStatus status);

// EQ-RATE-01: real sample epochs, never FIFO burst/poll receipt times.
double dspEstimateRateHz(size_t count, uint64_t firstSampleUs, uint64_t lastSampleUs);
// EQ-MEDIAN-01: caller supplies only valid finite positive frequencies.
// Sorts values in-place. Even count => mean of the two central values.
bool dspMedian(float *values, size_t count, double *median);
