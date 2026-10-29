#pragma once
#include <stdint.h>
// PROPOSED prototype map for N16R8. Verify wiring; not the old board map.
#define SHM_HW_REV 2
constexpr int SHM_SDA[2] = {8, 10}, SHM_SCL[2] = {9, 11}, SHM_INT[3] = {4, 5, 6};
constexpr uint8_t SHM_BUS[3] = {0, 0, 1}, SHM_ADDRESS[3] = {0x68, 0x69, 0x68};
constexpr uint32_t SHM_I2C_HZ = 400000;
// GPIO35/36/37 reserved by R8 PSRAM; GPIO19/20 reserved for native USB.
