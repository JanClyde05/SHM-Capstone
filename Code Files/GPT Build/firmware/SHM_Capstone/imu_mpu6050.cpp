#include <Arduino.h>
#include <Wire.h>
#include <esp_timer.h>
#include "imu_mpu6050.h"
#include "hardware_profile.h"
// REG-* identifiers map to docs/HARDWARE_INTERFACE.md.
namespace {
constexpr uint8_t RATE = 0x19, CONFIG = 0x1a, GYRO = 0x1b, ACCEL = 0x1c, FIFO_SOURCE = 0x23;
constexpr uint8_t INT_CONFIG = 0x37, INT_ENABLE = 0x38, INT_STATUS = 0x3a, USER = 0x6a,
                  POWER = 0x6b, POWER2 = 0x6c;
constexpr uint8_t FIFO_COUNT = 0x72, FIFO_DATA = 0x74, IDENTITY = 0x75;
struct Device {
    QueueHandle_t edges = nullptr;
    volatile uint32_t lost = 0;
    uint32_t index = 0;
    uint64_t mismatchSince = 0;
} dev[3];
TwoWire bus0(0), bus1(1);
TwoWire *buses[2] = {&bus0, &bus1};
const char *lastError = "not initialized";
bool writeReg(unsigned s, uint8_t r, uint8_t v) {
    auto &b = *buses[SHM_BUS[s]];
    b.beginTransmission(SHM_ADDRESS[s]);
    b.write(r);
    b.write(v);
    return b.endTransmission() == 0;
}
bool readReg(unsigned s, uint8_t r, uint8_t *p, size_t n) {
    auto &b = *buses[SHM_BUS[s]];
    b.beginTransmission(SHM_ADDRESS[s]);
    b.write(r);
    if (b.endTransmission(false) != 0 || b.requestFrom(SHM_ADDRESS[s], n, true) != n)
        return false;
    for (size_t i = 0; i < n; ++i)
        p[i] = static_cast<uint8_t>(b.read());
    return true;
}
void ARDUINO_ISR_ATTR readyEdge(void *arg) {
    auto *d = static_cast<Device *>(arg);
    const uint64_t t = esp_timer_get_time();
    BaseType_t wake = pdFALSE;
    if (xQueueSendFromISR(d->edges, &t, &wake) != pdTRUE)
        ++d->lost;
    if (wake)
        portYIELD_FROM_ISR();
}
bool configure(unsigned s) {
    uint8_t id = 0;
    if (!readReg(s, IDENTITY, &id, 1) || id != 0x68) {
        lastError = "WHO_AM_I mismatch or bus unavailable";
        return false;
    }
    if (!writeReg(s, POWER, 0x80))
        return false;
    delay(100); // REG-POWER-01 reset
    // Sleep while aligning FIFO and edge queue; retain gyros for X PLL.
    if (!writeReg(s, POWER, 0x41) || !writeReg(s, POWER2, 0) || !writeReg(s, INT_ENABLE, 0) ||
        !writeReg(s, FIFO_SOURCE, 0) || !writeReg(s, USER, 0) || !writeReg(s, CONFIG, 4) ||
        !writeReg(s, RATE, 9) || !writeReg(s, GYRO, 0) || !writeReg(s, ACCEL, 0) ||
        !writeReg(s, INT_CONFIG, 0) || !writeReg(s, USER, 4))
        return false;
    delay(2); // FIFO_RESET only while USER_CTRL.FIFO_EN=0.
    xQueueReset(dev[s].edges);
    pinMode(SHM_INT[s], INPUT);
    attachInterruptArg(SHM_INT[s], readyEdge, &dev[s], RISING);
    uint8_t discard;
    if (!readReg(s, INT_STATUS, &discard, 1) || !writeReg(s, FIFO_SOURCE, 8) ||
        !writeReg(s, USER, 0x40) || !writeReg(s, INT_ENABLE, 1) || !writeReg(s, POWER, 1))
        return false;
    // REG-CLOCK-01 CLKSEL1 = X gyro PLL. REG-FIFO-01 accel XYZ only.
    const uint8_t regs[] = {CONFIG, RATE, ACCEL, FIFO_SOURCE, USER, INT_ENABLE, POWER};
    const uint8_t vals[] = {4, 9, 0, 8, 0x40, 1, 1};
    for (unsigned i = 0; i < sizeof(regs); ++i) {
        uint8_t v = 0;
        if (!readReg(s, regs[i], &v, 1) || v != vals[i])
            return false;
    }
    return true;
}
} // namespace
bool imuBeginAll() {
    for (unsigned b = 0; b < 2; ++b) {
        if (!buses[b]->begin(SHM_SDA[b], SHM_SCL[b], SHM_I2C_HZ)) {
            lastError = "I2C begin rejected";
            return false;
        }
        buses[b]->setTimeOut(10);
    }
    for (auto &d : dev) {
        if (!d.edges)
            d.edges = xQueueCreate(128, sizeof(uint64_t));
        d.lost = 0;
        d.mismatchSince = 0;
        if (!d.edges) {
            lastError = "IRQ queue allocation";
            return false;
        }
    }
    for (unsigned s = 0; s < 3; ++s)
        if (!configure(s)) {
            if (strcmp(lastError, "not initialized") == 0)
                lastError = "MPU register verification";
            return false;
        }
    lastError = "";
    return true;
}
ImuRead imuReadFrame(unsigned s, RawRecord *out) {
    auto &d = dev[s];
    if (d.lost) {
        lastError = "DRDY queue overflow";
        return ImuRead::Fault;
    }
    uint8_t status = 0, count[2];
    if (!readReg(s, INT_STATUS, &status, 1)) {
        lastError = "I2C status read incomplete";
        return ImuRead::Fault;
    }
    const unsigned before = uxQueueMessagesWaiting(d.edges);
    if (!readReg(s, FIFO_COUNT, count, 2)) {
        lastError = "I2C count read incomplete";
        return ImuRead::Fault;
    }
    const unsigned queued = uxQueueMessagesWaiting(d.edges),
                   bytes = (unsigned(count[0]) << 8) | count[1], frames = bytes / 6;
    if ((status & 0x10) || bytes >= 1024) {
        lastError = "FIFO overflow";
        return ImuRead::Fault;
    }
    // A conversion arriving during the snapshot requires a new snapshot.
    // Never tolerate a permanent one-frame offset or pair while counts disagree.
    if (before != queued || frames != queued || bytes % 6) {
        if (!d.mismatchSince)
            d.mismatchSince = esp_timer_get_time();
        if (uint64_t(esp_timer_get_time()) - d.mismatchSince > 100000) {
            lastError = "FIFO/DRDY count mismatch";
            return ImuRead::Fault;
        }
        return ImuRead::Empty;
    }
    d.mismatchSince = 0;
    if (!frames)
        return ImuRead::Empty;
    uint8_t raw[6];
    uint64_t timestamp;
    if (!readReg(s, FIFO_DATA, raw, 6) || xQueueReceive(d.edges, &timestamp, 0) != pdTRUE) {
        lastError = "FIFO/DRDY pairing rejected";
        return ImuRead::Fault;
    }
    *out = {};
    out->timestampUs = timestamp;
    out->readTimestampUs = esp_timer_get_time();
    out->sampleIndex = d.index++;
    out->sensorId = s + 1;
    for (unsigned a = 0; a < 3; ++a)
        out->xyz[a] = static_cast<int16_t>((unsigned(raw[a * 2]) << 8) | raw[a * 2 + 1]);
    return ImuRead::Frame;
}
const char *imuLastError() {
    return lastError;
}

void imuStopAll() {
    for (unsigned s = 0; s < 3; ++s) {
        writeReg(s, INT_ENABLE, 0);
        writeReg(s, POWER, 0x41);
        writeReg(s, FIFO_SOURCE, 0);
        writeReg(s, USER, 0);
    }
}
