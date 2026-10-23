# Hardware — PCB, Wiring, Components

> Stage 05 | ICM L2 Contract  
> **Input**: Physical components  
> **Output**: Assembled SHM hardware unit

## Core Components

| Component | Spec | Qty |
|-----------|------|-----|
| MCU | ESP32-S3-WROOM-1 | 1 |
| IMU | MPU6050 (GY-521) | 3 |
| Bus | I2C @ 400kHz | 1 shared |

## Wiring Diagram

```
ESP32-S3
├── GPIO 8 ──── SDA (all IMUs)
├── GPIO 9 ──── SCL (all IMUs)
├── GPIO 4 ──── AD0 → IMU 0 (X-axis)
├── GPIO 5 ──── AD0 → IMU 1 (Y-axis)
└── GPIO 6 ──── AD0 → IMU 2 (Z-axis)

IMU Address: AD0=LOW → 0x68 | AD0=HIGH → 0x69
Only one active at a time via selectSensor().
```

## MPU6050 Register Config

| Register | Value | Meaning |
|----------|-------|---------|
| 0x6B | 0x00 | Wake from sleep |
| 0x1C | 0x00 | Accel ±2g |
| 0x1B | 0x00 | Gyro ±250°/s |
| 0x1A | 0x03 | DLPF bandwidth 44Hz |
| 0x19 | 0x04 | Sample rate divider → ~200Hz |

## PCB

- Custom PCB designed in KiCad
- Gerber files: `gerber/` directory
- Images: `images/PCB Front View.jpg`, `images/PCB Back View.jpg`

## Network

| Setting | Value |
|---------|-------|
| Mode | WiFi Access Point |
| SSID | `SHM_MONITOR` |
| Password | `bastaPassword` |
| IP | 192.168.4.1 |
| Subnet | 255.255.255.0 |

## Storage

- **LittleFS**: Stores `three.min.js` (603KB) and `shm.csv`
- **Upload tool**: `arduino-littlefs-upload-1.6.3.vsix`

## Links

- [[04-firmware]] — software that drives this hardware
- [[01-system-overview]] — where hardware fits in system
