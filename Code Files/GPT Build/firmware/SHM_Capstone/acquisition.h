#pragma once
#include "measurement_types.h"
struct AcquisitionStatus {
    bool ready;
    uint32_t counts[3], clips[3];
    uint64_t firstUs[3], lastUs[3];
    double fsEstimateHz[3];
    int16_t latest[3][3];
    const char *error;
};
using AcquisitionSink = void (*)(const RawRecord &);
bool acquisitionBegin(AcquisitionSink sink);
AcquisitionStatus acquisitionGetStatus();

void acquisitionSuspend();
bool acquisitionResume();
