#pragma once
#include "measurement_types.h"
enum class ImuRead { Empty, Frame, Fault };
bool imuBeginAll();
ImuRead imuReadFrame(unsigned sensor, RawRecord *output);
const char *imuLastError();

void imuStopAll();
