#include <Arduino.h>
#include <atomic>
#include "acquisition.h"
#include "imu_mpu6050.h"
#include "config.h"
namespace {
AcquisitionStatus status{};
portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;
AcquisitionSink sink = nullptr;
std::atomic<bool> pauseRequested{false}, pauseAck{false};
TaskHandle_t handle = nullptr;
void task(void *) {
    uint32_t cycle = 0;
    for (;;) {
        if (pauseRequested) {
            pauseAck = true;
            vTaskDelay(1);
            continue;
        }
        pauseAck = false;
        for (unsigned s = 0; s < 3; ++s) {
            RawRecord r{};
            auto result = imuReadFrame(s, &r);
            if (result == ImuRead::Fault) {
                portENTER_CRITICAL(&mux);
                status.ready = false;
                status.error = imuLastError();
                portEXIT_CRITICAL(&mux);
                pauseRequested = true;
                break;
            }
            if (result != ImuRead::Frame)
                continue;
            r.cycleId = cycle;
            for (int a = 0; a < 3; ++a)
                if (abs(int(r.xyz[a])) >= SHM_CLIP_COUNTS)
                    r.flags |= 1;
            portENTER_CRITICAL(&mux);
            ++status.counts[s];
            if (r.flags)
                ++status.clips[s];
            if (!status.firstUs[s])
                status.firstUs[s] = r.timestampUs;
            status.lastUs[s] = r.timestampUs;
            for (int a = 0; a < 3; ++a)
                status.latest[s][a] = r.xyz[a];
            // EQ-RATE-01 live preview only, DRDY count/elapsed since boot.
            if (status.counts[s] > 1)
                status.fsEstimateHz[s] = double(status.counts[s] - 1) * 1e6 /
                                         double(status.lastUs[s] - status.firstUs[s]);
            portEXIT_CRITICAL(&mux);
            if (sink)
                sink(r);
        }
        ++cycle;
        vTaskDelay(1);
    }
}
} // namespace
bool acquisitionBegin(AcquisitionSink callback) {
    sink = callback;
    status.error = "";
    status.ready = imuBeginAll();
    if (!status.ready) {
        status.error = imuLastError();
        return false;
    }
    if (xTaskCreatePinnedToCore(task, "shm-acquisition", 4096, nullptr, 18, &handle, 1) != pdPASS) {
        status.ready = false;
        status.error = "acquisition task allocation";
    }
    return status.ready;
}
AcquisitionStatus acquisitionGetStatus() {
    portENTER_CRITICAL(&mux);
    auto copy = status;
    portEXIT_CRITICAL(&mux);
    return copy;
}

void acquisitionSuspend() {
    if (!handle)
        return;
    pauseRequested = true;
    while (!pauseAck)
        vTaskDelay(1);
    imuStopAll();
}
bool acquisitionResume() {
    bool ok = imuBeginAll();
    portENTER_CRITICAL(&mux);
    status = {};
    status.ready = ok;
    status.error = ok ? "" : imuLastError();
    portEXIT_CRITICAL(&mux);
    if (ok && !handle) {
        if (xTaskCreatePinnedToCore(task, "shm-acquisition", 4096, nullptr, 18, &handle, 1) !=
            pdPASS) {
            ok = false;
            status.ready = false;
            status.error = "acquisition task allocation";
        }
    }
    if (ok) {
        pauseAck = false;
        pauseRequested = false;
    }
    return ok;
}
