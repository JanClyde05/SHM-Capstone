# System Overview — SHM Capstone

> Stage 01 | ICM L2 Contract  
> **Input**: None (entry point)  
> **Output**: Architectural understanding of full SHM system

## What This System Is

Real-time Structural Health Monitoring platform.  
Two subsystems, tightly coupled via JSON over HTTP.

### Backend — ESP32-S3

- **File**: `Calculations.h` + `SHM_Main.ino`
- **Job**: Acquire → calibrate → filter → extract → stream
- **Hardware**: 3× MPU6050 IMUs, AD0 multiplexed on shared I2C bus
- **RTOS**: 3 FreeRTOS tasks pinned to dual cores

### Frontend — Web Dashboard

- **File**: `WebServerUI.h` (PROGMEM HTML/CSS/JS)
- **Job**: Poll → smooth → shader → render → alert
- **Engine**: Three.js r128 (custom ShaderMaterial, not Phong injection)
- **Geometry**: 96×96 PlaneGeometry, XZ-oriented, Y-displacement

## End-to-End Pipeline

```
MPU6050 → Raw accel → Calibrate → MAF → Magnitude(−1g)
→ RMS + FFT → Intensity → JSON /data → fetch@20Hz
→ LPF → LERP → Shader uniforms → GPU ripple → UI + alerts
```

## Key Numbers

| Parameter | Value | Note |
|-----------|-------|------|
| IMU count | 3 | X, Y, Z axes |
| Sample rate | ~167 Hz | 6ms period per sensor |
| Processing rate | 20 Hz | 50ms period |
| Poll rate | 20 Hz | Frontend fetch |
| WiFi | AP mode | SSID: `SHM_MONITOR` |
| IP | 192.168.4.1 | Fixed |

## Links

- [[02-signal-processing]] — calibration, filters, feature extraction
- [[03-visualization]] — shaders, smoothing, heatmap
- [[04-firmware]] — FreeRTOS task architecture
- [[07-graphs]] — visual dependency maps
