# SHM SYSTEM DOCUMENTATION (LLM STYLE)

## Structural Health Monitoring — Signal Processing + Visualization Pipeline

##### BY: JAN CLYDE T. TALOSIG

---

# 1. SYSTEM OVERVIEW

This system is a real-time Structural Health Monitoring (SHM) platform composed of two tightly coupled subsystems:

### A. Embedded Signal Processing Layer (ESP32)

Implemented in `Calculations.h`

Responsibilities:

* Acquire IMU data (MPU6050)
* Calibrate raw sensor readings
* Filter and stabilize signals
* Compute vibration metrics (RMS, FFT, intensity)

---

### B. Visualization Layer (Web Dashboard)

Implemented in `WebServerUI.h`

Responsibilities:

* Fetch processed data via ESP32 WebServer `/data`
* Render real-time 3D structural simulation
* Map vibration metrics into GPU shader motion
* Display alerts and system state

---

# 2. END-TO-END DATA PIPELINE

## Core System Flow

IMU Sensors (MPU6050)
→ Raw Acceleration (ax, ay, az)
→ Calibration (bias removal)
→ Moving Average Filter (per axis smoothing)
→ Gravity-compensated magnitude
→ RMS + FFT feature extraction
→ Intensity + Frequency outputs
→ JSON streaming via WebServer (/data)
→ Frontend polling (20 Hz)
→ Dual-stage smoothing (LPF + LERP)
→ Shader uniform updates
→ 3D fabric ripple simulation
→ UI rendering + anomaly alerts

---

# 3. BACKEND — SIGNAL PROCESSING (Calculations.h)

---

## 3.1 CALIBRATION MODULE

### Objective

Remove static sensor bias and drift.

### Method

* Collect ~200 stationary samples
* Compute mean per axis
* Store offset vector
* Subtract offset from live readings

### Model

offset = average(raw_samples)
corrected_signal = raw_signal - offset

### Constraint

Gravity is NOT removed during calibration phase.

---

## 3.2 MOVING AVERAGE FILTER (MAF)

### Objective

Reduce high-frequency noise and stabilize IMU readings.

### Architecture

* Circular buffer per axis
* Running sum accumulator
* Fixed window size (MAF_SIZE)

### Update Rule

sum -= oldest_sample
insert new_sample
sum += new_sample
output = sum / window_size

### Constraint

Must be applied:

* per axis (ax, ay, az)
* BEFORE magnitude computation

---

## 3.3 MAGNITUDE EXTRACTION

### Objective

Convert 3-axis acceleration into vibration-only scalar.

### Equation

mag = sqrt(ax² + ay² + az²) - 1g

### Interpretation

* Removes gravity baseline
* Isolates dynamic vibration components

---

## 3.4 RMS FEATURE EXTRACTION

### Objective

Quantify vibration energy.

### Equation

RMS = sqrt( (Σ x²) / N )

### Meaning

* Represents structural energy response
* Direct indicator of vibration intensity

---

## 3.5 FFT FREQUENCY ANALYSIS

### Objective

Extract dominant vibration frequency.

### Process

* Apply Hamming window
* Execute FFT transform
* Identify peak frequency bin

### Output

dominant_frequency (Hz)

---

## 3.6 INTENSITY NORMALIZATION

### Objective

Map vibration energy into normalized scale.

### Equation

intensity = RMS / MAX_RMS_G

### Constraints

* Clamped between 0.0 and 1.0
* Used for visualization and alerts

---

# 4. FRONTEND — VISUALIZATION ENGINE

---

## 4.1 DATA FLOW PIPELINE

ESP32 WebServer (/data)
→ fetch() at 20 Hz
→ updateScene()
→ LPF smoothing
→ LERP interpolation
→ shader uniform update
→ GPU rendering

---

## 4.2 DUAL-STAGE SMOOTHING MODEL

### Stage 1 — Low Pass Filter (Network Level)

value += 0.10 × (new_value - current_value)

Purpose:

* Reduce network jitter
* Stabilize incoming data stream

---

### Stage 2 — Frame Interpolation (Render Level)

value += rate × (target - current_value)

Purpose:

* Ensure smooth animation
* Decouple sensor rate from render FPS

---

## 4.3 FABRIC GEOMETRY MODEL

* Plane size: 22 × 22 units
* Resolution: 96 × 96 segments
* Orientation: XZ plane
* Deformation axis: Y-axis displacement

---

## 4.4 IMU TO VISUAL MAPPING

Axis-to-source mapping:

X-axis → Left ripple origin
Y-axis → Center ripple origin
Z-axis → Right ripple origin

---

## 4.5 RIPPLE GENERATION MODEL

### Core Equation

dist  = distance(point, origin)
angle = -time × speed + dist × 6

disp = amplitude × attenuation ×
(sin(angle)
+ 0.35·sin(2·angle)
+ 0.12·sin(3.5·angle))

### Attenuation Model

attenuation = 1 / (1 + dist × 0.18)

---

## 4.6 NORMAL VECTOR COMPUTATION

normal = normalize(-∂z/∂x, -∂z/∂y, 1)

Purpose:

* Enables physically correct lighting response
* Improves realism of fabric deformation

---

## 4.7 HEATMAP COLOR MODEL

Mapping:

0.0 → deep blue (low vibration)
0.5 → cyan / green (stable region)
1.0 → red (high stress region)

---

## 4.8 LIGHTING SYSTEM

Components:

* Multi-source diffuse lighting (3 lights)
* Phong specular highlights
* Crest glow enhancement
* Trough shadow deepening

---

## 4.9 INTENSITY → VISUAL BEHAVIOR MAPPING

Amplitude scaling:

* 0.5 → idle state
* 4.0 → high vibration state

Speed scaling:

* 0.4 → slow oscillation
* 3.0 → rapid wave propagation

---

## 4.10 UI SYSTEM

### Displayed Metrics

* Acceleration (ax, ay, az)
* Gyroscope values
* RMS vibration energy
* Dominant frequency
* Normalized intensity

### System States

OK   → stable operation
WARN → elevated vibration
CRIT → structural anomaly detected

---

## 4.11 ALERT SYSTEM

Trigger Condition:

RMS ≥ critical threshold

### Response Behavior

* Flashing warning indicator
* Highlighted data rows
* Axis-level anomaly labeling

---

# 5. SYSTEM BEHAVIOR MODES

---

## NORMAL STATE

* Low amplitude wave motion
* Cool color palette (blue/green)
* Stable UI feedback

---

## WARNING STATE

* Increased amplitude oscillation
* Yellow/orange transitions
* Elevated RMS values

---

## CRITICAL STATE

* High amplitude chaotic ripples
* Red dominant visualization
* Flashing alerts and emphasis markers

---

# 6. ARCHITECTURAL DESIGN PATTERNS

* Modular pipeline architecture
* Clear backend/frontend separation
* Dual-stage smoothing system
* GPU-accelerated simulation layer

---

# 7. SYSTEM TUNING PARAMETERS

Filter tuning:
MAF_SIZE → smoothing strength

Sensitivity:
MAX_RMS_G → detection threshold scaling

Visual amplitude:
0.50 + intensity × 3.50

Ripple frequency:
dist × 6.0

Smoothing control:
LPF_A, AMP_L, SPD_L

---

# 8. CORE SYSTEM INSIGHT

Physical vibration signal
→ statistical processing
→ normalized feature extraction
→ GPU-based simulation mapping
→ real-time visual structural interpretation

---

# 9. FINAL SUMMARY

This system:

* Converts raw IMU data into structured vibration metrics
* Extracts energy (RMS) and frequency (FFT)
* Normalizes structural response
* Drives a real-time GPU-based simulation
* Visualizes structural health dynamically
* Detects and flags anomalies in real time

---

END OF DOCUMENT
