#include "dsp.h"
#include <math.h>
#include <string.h>

namespace {
constexpr double PI = 3.14159265358979323846264338327950288;
bool isFinite(double x) { return isfinite(x); }
DspComplex multiply(DspComplex a, DspComplex b) {
    return {a.re * b.re - a.im * b.im, a.re * b.im + a.im * b.re};
}
double magnitude(DspComplex a) { return hypot(double(a.re), double(a.im)); }

// EQ-FFT-02: radix-2 Cooley-Tukey, forward unscaled, inverse / M.
// Used for Bluestein convolution; this does not change the N-point bin grid.
void fft(DspComplex* data, size_t n, bool inverse) {
    for (size_t i = 1, j = 0; i < n; ++i) {
        size_t bit = n >> 1;
        for (; j & bit; bit >>= 1) j ^= bit;
        j ^= bit;
        if (i < j) { DspComplex t = data[i]; data[i] = data[j]; data[j] = t; }
    }
    for (size_t len = 2; len <= n; len <<= 1) {
        double angle = (inverse ? 2.0 : -2.0) * PI / double(len);
        const double stepRe = cos(angle), stepIm = sin(angle);
        for (size_t start = 0; start < n; start += len) {
            double wr = 1.0, wi = 0.0;
            for (size_t j = 0; j < len / 2; ++j) {
                DspComplex even = data[start + j];
                DspComplex odd = data[start + j + len / 2];
                double tr = odd.re * wr - odd.im * wi;
                double ti = odd.re * wi + odd.im * wr;
                data[start + j] = {float(even.re + tr), float(even.im + ti)};
                data[start + j + len / 2] = {float(even.re - tr), float(even.im - ti)};
                double nextWr = wr * stepRe - wi * stepIm;
                wi = wr * stepIm + wi * stepRe; wr = nextWr;
            }
        }
        if (len == n) break; // Prevent size_t wrap at its maximum bit.
    }
    if (inverse) for (size_t i = 0; i < n; ++i) {
        data[i].re /= float(n); data[i].im /= float(n);
    }
}

bool reject(DspAxisResult* r, DspStatus status) {
    r->status = status; r->validPeak = false; r->dominantFrequencyHz = NAN;
    return false;
}
} // namespace

size_t dspWorkspaceLength(size_t count) {
    if (count < 4 || count > SIZE_MAX / 2) return 0;
    size_t target = 2 * count - 1, m = 1;
    while (m < target) { if (m > SIZE_MAX / 2) return 0; m <<= 1; }
    if (m > SIZE_MAX / sizeof(DspComplex)) return 0;
    return m;
}

bool dspAnalyzeAxis(const float* samples, size_t count, double fs,
                    const DspSettings& s, DspWorkspace* w, DspAxisResult* r) {
    if (!r) return false;
    *r = {}; r->dominantFrequencyHz = NAN; r->status = DspStatus::InvalidParameters;
    r->sampleCount = count; r->fsEstimateHz = fs;
    size_t m = dspWorkspaceLength(count);
    if (!samples || !m || !isFinite(fs) || fs <= 0 ||
        !isFinite(s.bandLoHz) || !isFinite(s.bandHiHz) || s.bandLoHz <= 0 ||
        s.bandHiHz <= s.bandLoHz || s.bandHiHz >= fs / 2 ||
        !isFinite(s.relativeTieTolerance) || s.relativeTieTolerance < 0 ||
        s.relativeTieTolerance >= 1 || !isFinite(s.clipAbs) || s.clipAbs < 0)
        return false;
    r->binSpacingHz = fs / double(count); // EQ-BIN-01: delta f = fs / N.
    if (!w || !w->a || !w->b || w->a == w->b || w->capacity < m)
        return reject(r, DspStatus::WorkspaceTooSmall);
    double sum = 0;
    for (size_t i = 0; i < count; ++i) {
        if (!isFinite(samples[i])) return reject(r, DspStatus::NonFiniteInput);
        if (s.clipAbs > 0 && fabs(samples[i]) >= s.clipAbs)
            return reject(r, DspStatus::ClippedInput);
        sum += samples[i];
    }
    double mean = sum / double(count); // EQ-MEAN-01: current window's mean.
    memset(w->a, 0, m * sizeof(DspComplex)); memset(w->b, 0, m * sizeof(DspComplex));
    double centeredEnergy = 0;
    for (size_t i = 0; i < count; ++i) {
        double centered = samples[i] - mean;
        centeredEnergy += centered * centered;
        // EQ-HANN-01: symmetric Hann w[n]=.5-.5*cos(2*pi*n/(N-1)).
        double windowed = centered * (0.5 - 0.5 * cos(2.0 * PI * double(i) / double(count - 1)));
        // EQ-BLUESTEIN-01: reduce phase modulo 2*N before trig evaluation.
        double phase = PI * fmod(double(i) * double(i), 2.0 * double(count)) / double(count);
        DspComplex positiveChirp = {float(cos(phase)), float(sin(phase))};
        w->a[i] = {float(windowed * positiveChirp.re), float(-windowed * positiveChirp.im)};
        w->b[i] = positiveChirp;
        if (i) w->b[m - i] = positiveChirp;
    }
    if (!(centeredEnergy > 0)) return reject(r, DspStatus::ZeroSignal);
    // EQ-DFT-01 computed via EQ-BLUESTEIN-01, without changing actual N.
    fft(w->a, m, false); fft(w->b, m, false);
    for (size_t i = 0; i < m; ++i) w->a[i] = multiply(w->a[i], w->b[i]);
    fft(w->a, m, true);
    for (size_t k = 0; k < count; ++k) {
        double phase = PI * fmod(double(k) * double(k), 2.0 * double(count)) / double(count);
        w->a[k] = multiply(w->a[k], {float(cos(phase)), float(-sin(phase))});
    }
    // EQ-PEAK-01: bins strictly between 0 and Nyquist, in closed fixed band.
    // Max search is ascending and uses >, so exact ties choose lowest index.
    size_t lo = 0, hi = 0;
    for (size_t k = 1; k <= (count - 1) / 2; ++k) {
        double f = double(k) * r->binSpacingHz;
        if (f >= s.bandLoHz && f <= s.bandHiHz) { if (!lo) lo = k; hi = k; }
    }
    if (!lo) return reject(r, DspStatus::NoBandBins);
    size_t winner = lo; double maximum = -1;
    for (size_t k = lo; k <= hi; ++k) {
        double v = magnitude(w->a[k]);
        if (!isFinite(v)) return reject(r, DspStatus::NumericalError);
        if (v > maximum) { maximum = v; winner = k; }
    }
    r->peakBin = winner; r->peakMagnitude = maximum;
    if (!(maximum > 0)) return reject(r, DspStatus::ZeroSignal);
    double tieThreshold = maximum * (1.0 - s.relativeTieTolerance);
    for (size_t k = lo; k <= hi; ++k)
        if (k != winner && magnitude(w->a[k]) >= tieThreshold) r->nearTie = true;
    r->bandEdgePeak = winner == lo || winner == hi; // Diagnostic; never reject.
    r->dominantFrequencyHz = double(winner) * fs / double(count); // EQ-BIN-02.
    r->validPeak = true; r->status = DspStatus::Valid;
    return true;
}

const char* dspStatusName(DspStatus s) {
    switch (s) {
    case DspStatus::Valid: return "VALID";
    case DspStatus::InvalidParameters: return "INVALID_PARAMETERS";
    case DspStatus::WorkspaceTooSmall: return "WORKSPACE_TOO_SMALL";
    case DspStatus::NonFiniteInput: return "NONFINITE_INPUT";
    case DspStatus::ClippedInput: return "CLIPPED_INPUT";
    case DspStatus::ZeroSignal: return "ZERO_SIGNAL";
    case DspStatus::NoBandBins: return "NO_BAND_BINS";
    case DspStatus::NumericalError: return "NUMERICAL_ERROR";
    }
    return "UNKNOWN";
}

double dspEstimateRateHz(size_t n, uint64_t first, uint64_t last) {
    if (n < 2 || last <= first) return NAN;
    return double(n - 1) * 1e6 / double(last - first); // EQ-RATE-01.
}

bool dspMedian(float* v, size_t n, double* out) {
    if (!v || !out || !n) return false;
    for (size_t i = 0; i < n; ++i) if (!isFinite(v[i]) || v[i] <= 0) return false;
    for (size_t i = 1; i < n; ++i) {
        float item = v[i]; size_t j = i;
        while (j && v[j - 1] > item) { v[j] = v[j - 1]; --j; }
        v[j] = item;
    }
    *out = n % 2 ? v[n / 2] : (double(v[n / 2 - 1]) + v[n / 2]) / 2.0; // EQ-MEDIAN-01.
    return true;
}


