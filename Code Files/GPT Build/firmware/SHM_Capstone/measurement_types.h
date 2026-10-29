#pragma once
#include <stdint.h>
// Little-endian SHMRAW2; docs/DATA_FORMAT.md.
struct __attribute__((packed)) RawRecord {
    uint64_t timestampUs;     // MCU DRDY rising edge, not ADC aperture
    uint64_t readTimestampUs; // FIFO receipt; not used as sample epoch
    uint32_t sampleIndex, cycleId;
    int16_t xyz[3];
    uint8_t sensorId, flags; // sensor1..3; flag bit0=near rail
};
static_assert(sizeof(RawRecord) == 32, "RawRecord schema changed");
struct __attribute__((packed)) RawHeader {
    char magic[8];
    uint32_t schema, recordBytes;
    uint64_t startUs;
    uint32_t durationS, sensors;
};
static_assert(sizeof(RawHeader) == 32, "RawHeader schema changed");
