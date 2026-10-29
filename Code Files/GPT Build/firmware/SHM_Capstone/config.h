#pragma once
#include <stdint.h>
// Scientific defaults are PILOT settings until explicitly frozen in the UI.
constexpr uint32_t SHM_SESSION_SECONDS = 600, SHM_WINDOW_SECONDS = 60, SHM_NOMINAL_FS = 100;
constexpr uint32_t SHM_WINDOW_COUNT = 10, SHM_MAX_RAW_RECORDS = 200000,
                   SHM_MAX_WINDOW_SAMPLES = 6500;
constexpr int SHM_CLIP_COUNTS = 32000;
constexpr double SHM_COUNTS_PER_G = 16384.0, SHM_FS_TOLERANCE = .03, SHM_REVIEW_K = 2.0;
constexpr uint32_t SHM_PRECHECK_SECONDS = 10;
constexpr double SHM_RELATIVE_TIE_TOLERANCE = 1e-4;
constexpr unsigned SHM_MIN_BASELINE_SESSIONS = 5, SHM_MIN_VALID_WINDOWS = 10;
struct AnalysisConfig {
    double bandLo = .5, bandHi = 20;
    uint32_t timingToleranceUs = 500, cutoff1 = 0, cutoff2 = 0;
    bool frozen = false;
};
