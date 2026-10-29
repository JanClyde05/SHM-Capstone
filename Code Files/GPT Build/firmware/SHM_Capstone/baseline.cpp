#include "baseline.h"
#include <math.h>

namespace {
BaselineAccumulator cells[3][3][3];
bool indices(uint8_t group, uint8_t sensor, uint8_t axis) {
    return group < 3 && sensor < 3 && axis < 3;
}
}

bool baselineAccumulate(BaselineAccumulator* a, double value) {
    if (!a || !isfinite(value) || value <= 0 || a->n == UINT32_MAX) return false;
    // EQ-STATS-01: Welford recurrence, algebraically equal to sum squared
    // deviations. Accumulate in double; sample variance later uses n-1.
    uint32_t n = a->n + 1;
    double delta = value - a->meanHz;
    double mean = a->meanHz + delta / n;
    double m2 = a->m2Hz2 + delta * (value - mean);
    if (!isfinite(mean) || !isfinite(m2) || m2 < 0) return false;
    a->n = n; a->meanHz = mean; a->m2Hz2 = m2;
    return true;
}

bool baselineSummarize(const BaselineAccumulator& a, BaselineAxisSummary* s,
                       double reviewK, unsigned int target) {
    if (!s) return false;
    *s = {}; s->sampleSdHz = NAN; s->coefficientVariationPct = NAN;
    s->descriptiveLoHz = s->descriptiveHiHz = s->reviewLoHz = s->reviewHiHz = NAN;
    if (!a.n || !isfinite(a.meanHz) || a.meanHz <= 0 || !isfinite(a.m2Hz2) ||
        a.m2Hz2 < 0 || !isfinite(reviewK) || reviewK <= 0 || !target) return false;
    s->n = a.n; s->meanHz = a.meanHz; s->practicalTargetMet = a.n >= target;
    if (a.n < 2) return true; // Mean defined; sample spread/review interval undefined.
    s->sampleSdHz = sqrt(a.m2Hz2 / double(a.n - 1)); // EQ-SD-01: sample s.
    s->sdDefined = true;
    // EQ-CV-01. Positive frequencies have meaningful zero; no near-zero guard
    // threshold invented. Any finite >0 mean is allowed; report its CV honestly.
    s->coefficientVariationPct = 100.0 * s->sampleSdHz / s->meanHz;
    s->cvDefined = isfinite(s->coefficientVariationPct);
    // EQ-BAND-01: descriptive mean +/- s. EQ-BAND-02: separate review heuristic.
    s->descriptiveLoHz = s->meanHz - s->sampleSdHz;
    s->descriptiveHiHz = s->meanHz + s->sampleSdHz;
    s->reviewLoHz = s->meanHz - reviewK * s->sampleSdHz;
    s->reviewHiHz = s->meanHz + reviewK * s->sampleSdHz;
    return true;
}

bool baselineOutsideReview(double value, const BaselineAxisSummary& s) {
    // EQ-REVIEW-01. Evaluate against PREVIOUS baseline before any update.
    return isfinite(value) && value > 0 && s.sdDefined && s.practicalTargetMet &&
           isfinite(s.reviewLoHz) && isfinite(s.reviewHiHz) &&
           (value < s.reviewLoHz || value > s.reviewHiHz);
}

void baselineBegin() {
    for (unsigned g = 0; g < 3; ++g)
        for (unsigned s = 0; s < 3; ++s)
            for (unsigned a = 0; a < 3; ++a) cells[g][s][a] = {};
}

bool baselineAddSession(uint8_t group, uint8_t sensor, uint8_t axis, double value) {
    return indices(group, sensor, axis) && baselineAccumulate(&cells[group][sensor][axis], value);
}

bool baselineGet(uint8_t group, uint8_t sensor, uint8_t axis, BaselineAxisSummary* s,
                 double reviewK, unsigned int target) {
    if (!indices(group, sensor, axis)) { if (s) *s = {}; return false; }
    return baselineSummarize(cells[group][sensor][axis], s, reviewK, target);
}
