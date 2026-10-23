# Firmware Architecture — FreeRTOS + I2C + CSV

> Stage 04 | ICM L2 Contract  
> **Input**: Hardware peripherals (I2C, WiFi, LittleFS)  
> **Output**: Running SHM system with web server + data logging  
> **File**: [[SHM_Main.ino]]

## Boot Sequence (`setup()`)

```
Serial → I2C init → AD0 GPIO → Init MPUs → WiFi AP → Calibration
→ HTTP routes → LittleFS → CSV open → Mutexes → Zero buffers
→ Baseline init → Launch 3 FreeRTOS tasks
```

⚠ WiFi AP starts **BEFORE** calibration. Ensures network reachable regardless of IMU state.

---

## Task Architecture

| Task | Core | Priority | Period | Job |
|------|------|----------|--------|-----|
| SensorAcquisition | 0 | 3 (highest) | 6ms | I2C read → calib → MAF → mag → buffers → CSV |
| Processing | 1 | 2 | 50ms | RMS + FFT + intensity + baseline |
| WebServer | 1 | 1 (lowest) | 50ms | `server.handleClient()` |

---

## Sensor Acquisition Pipeline (per cycle)

```
for each IMU (0..2):
  selectSensor(i)      // AD0 multiplex
  readMPU6050(i)       // I2C → calibApply() → gNodes
  snapshot ax,ay,az    // mutex-protected
  fax = mafUpdate(ax)  // per-axis MAF
  fay = mafUpdate(ay)
  faz = mafUpdate(az)
  mag = sqrt(fax²+fay²+faz²) − 1g
  push mag → gRmsBuf[i], gFftBuf[i]
  append CSV row       // non-blocking (skip if file busy)
```

---

## I2C Multiplexing (AD0 Scheme)

- All 3 MPU6050s share SDA/SCL bus
- AD0 pin per IMU controlled via GPIO 4, 5, 6
- Active IMU: AD0 → LOW (address 0x68)
- Inactive IMUs: AD0 → HIGH (address 0x69)

---

## Dynamic Baseline (§10)

| Param | Value |
|-------|-------|
| Collection window | 10 seconds post-boot |
| WARN threshold | baseline_rms + 0.05g |
| CRIT threshold | baseline_rms + 0.10g |
| Minimum samples | 5 |

Locks per-axis thresholds after collection. Falls back to 0.08/0.15g until locked.

---

## CSV Logging

- **Path**: `/shm.csv` on LittleFS
- **Format**: `timestamp,axis,ax,ay,az,rms,freq,intensity`
- **Flush**: Every 1KB written OR every 3 seconds
- **Download**: `GET /download` → stream → auto-delete → recreate w/ header
- **Protected by**: `gFileMutex` (non-blocking in sensor task)

---

## HTTP Endpoints

| Route | Method | Response |
|-------|--------|----------|
| `/` | GET | Full HTML dashboard (PROGMEM) |
| `/data` | GET | JSON: `{nodes:[{id,axis,acc,gyro,rms,freq,intensity,warn,crit,baseline_done}]}` |
| `/download` | GET | CSV file attachment |
| `/three.js` | GET | Three.js r128 from LittleFS |

---

## Shared State + Synchronisation

| Mutex | Protects | Timeout |
|-------|----------|---------|
| `gDataMutex` | `gNodes[]` reads/writes | 2–10ms |
| `gFileMutex` | `gCsvFile` writes/download | 0ms (non-blocking) or 500ms (download) |

---

## Hardware Config

| Pin | Function |
|-----|----------|
| GPIO 4 | AD0 → IMU 0 (X-axis) |
| GPIO 5 | AD0 → IMU 1 (Y-axis) |
| GPIO 6 | AD0 → IMU 2 (Z-axis) |
| GPIO 8 | SDA (shared) |
| GPIO 9 | SCL (shared) |

I2C clock: 400 kHz. MPU6050 config: ±2g accel, ±250°/s gyro, DLPF 44Hz, ~200Hz output.

---

## Links

- [[01-system-overview]] — architectural context
- [[02-signal-processing]] — DSP functions called by tasks
- [[03-visualization]] — HTML served by `/` route
- [[05-hardware]] — PCB and wiring
