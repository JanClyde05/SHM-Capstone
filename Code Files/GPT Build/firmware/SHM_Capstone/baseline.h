#pragma once

#include <stddef.h>
#include <stdint.h>

struct BaselineAxisSummary {
    uint32_t n;
    double meanHz;
    double sampleSdHz;
    double coefficientVariationPct;
    double descriptiveLoHz;
    double descriptiveHiHz;
    double reviewLoHz;
    double reviewHiHz;
    bool sdDefined;
    bool cvDefined;
    bool practicalTargetMet; // Feasibility target only; never a power claim.
};

// Pure C++; IDs in docs/MATHEMATICAL_ALGORITHMS.md. Caller ensures each
// contribution is ONE accepted session median from matching frozen settings.
struct BaselineAccumulator {
    uint32_t n = 0;
    double meanHz = 0;
    double m2Hz2 = 0;
};

bool baselineAccumulate(BaselineAccumulator* accumulator, double sessionMedianHz);
bool baselineSummarize(const BaselineAccumulator& accumulator,
                       BaselineAxisSummary* summary, double reviewK = 2.0,
                       unsigned int practicalTarget = 5);
bool baselineOutsideReview(double sessionMedianHz, const BaselineAxisSummary& summary);

// Independent cells: group0..2, sensor0..2, axis0..2. No pooled fusion.
void baselineBegin();
bool baselineAddSession(uint8_t group, uint8_t sensor, uint8_t axis, double sessionMedianHz);
bool baselineGet(uint8_t group, uint8_t sensor, uint8_t axis,
                 BaselineAxisSummary* summary, double reviewK = 2.0,
                 unsigned int practicalTarget = 5);
