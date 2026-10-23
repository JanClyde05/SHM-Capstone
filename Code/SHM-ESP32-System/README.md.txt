SHM System Documentation — Signal Processing + Visualization Pipeline

---

1. SYSTEM OVERVIEW

This system is a Structural Health Monitoring (SHM) platform composed of:

A. Embedded Signal Processing (ESP32)
Handled by Calculations.h
Processes IMU data into vibration metrics.

B. Web Visualization Dashboard
Handled by WebServerUI.h
Displays real-time vibration as a 3D animated fabric.

---

2. GLOBAL PIPELINE (END-TO-END FLOW)

IMU Sensors (MPU6050)
↓
Raw Acceleration Data (ax, ay, az)
↓
Calibration (offset removal)
↓
Moving Average Filter (per axis)
↓
Smoothed Acceleration
↓
Magnitude Calculation (|a| - 1g)
↓
RMS + FFT
↓
Intensity + Frequency
↓
WebServer JSON (/data)
↓
Frontend Polling (20 Hz)
↓
Two-Stage Smoothing
↓
Shader Uniform Mapping
↓
3D Fabric Ripple Visualization
↓
User Interface + Alerts

---

3. BACKEND: SIGNAL PROCESSING

3.1 CALIBRATION

Purpose:
Remove sensor bias.

Process:

* Collect ~200 samples while sensor is still
* Compute average per axis
* Store offsets
* Subtract offsets from live data

Formula:
offset = sum / count
corrected = raw - offset

Note:
Gravity is NOT removed here.

---

3.2 MOVING AVERAGE FILTER (MAF)

Purpose:
Reduce noise and smooth signal.

Structure:

* Circular buffer
* Running sum
* Window size = MAF_SIZE

Process:
sum -= oldest
replace oldest with new sample
sum += new sample
output = sum / N

Important:

* Apply per axis (ax, ay, az)
* Must run BEFORE magnitude

---

3.3 MAGNITUDE

Formula:
mag = sqrt(ax² + ay² + az²) - 1.0

Purpose:
Remove gravity and isolate vibration.

---

3.4 RMS (VIBRATION ENERGY)

Formula:
RMS = sqrt( Σ(x²) / N )

Purpose:
Represents vibration strength / energy.

---

3.5 FFT (FREQUENCY)

Process:

* Apply Hamming window
* Perform FFT
* Extract dominant peak frequency

Output:
dominant frequency in Hz

---

3.6 INTENSITY

Formula:
intensity = RMS / MAX_RMS_G

Clamped between 0 and 1.

Meaning:
0 = no vibration
1 = maximum vibration

---

4. FRONTEND: VISUALIZATION

4.1 DATA FLOW

ESP32 → /data endpoint
→ fetch() every 50ms
→ updateScene()
→ smoothing
→ shader update

---

4.2 TWO-STAGE SMOOTHING

Stage 1 (Polling LPF):
value += 0.10 * (new - value)

Stage 2 (Frame LERP):
value += rate * (target - value)

Purpose:

* Smooth transitions
* Decouple rendering from sensor rate

---

4.3 FABRIC GEOMETRY

* Plane size: 22 × 22
* Segments: 96 × 96
* Rotated into XZ plane
* Displacement along Y-axis

---

4.4 IMU → RIPPLE SOURCES

X-axis → left origin
Y-axis → center
Z-axis → right

---

4.5 RIPPLE EQUATION

dist  = distance(point, origin)
angle = -time * speed + dist * 6

disp = amplitude * attenuation *
(sin(angle)
+ sin(2*angle)*0.35
+ sin(3.5*angle)*0.12)

attenuation = 1 / (1 + dist * 0.18)

---

4.6 NORMAL CALCULATION

normal = normalize(-dZ/dx, -dZ/dy, 1)

Purpose:
Accurate lighting and shading.

---

4.7 COLOR (HEATMAP)

0.0 → deep blue (low / trough)
0.5 → cyan/green (neutral)
1.0 → red (high / crest)

---

4.8 LIGHTING

* Diffuse lighting (3 sources)
* Phong specular highlight
* Crest glow effect
* Trough darkening

---

4.9 INTENSITY → VISUAL

Amplitude:
0.5 → idle
4.0 → strong vibration

Speed:
0.4 → slow waves
3.0 → fast waves

---

4.10 UI SYSTEM

Table displays:

* Acceleration (ax, ay, az)
* Gyroscope
* RMS
* Frequency
* Intensity

Status:
OK   → normal
WARN → above warning threshold
CRIT → anomaly detected

---

4.11 ALERT SYSTEM

Trigger:
RMS ≥ critical threshold

Effects:

* Flashing warning triangle
* Highlighted table row
* Axis label display

---

5. SYSTEM BEHAVIOR

Normal:

* Small waves
* Cool colors

Warning:

* Larger waves
* Yellow tones

Critical:

* Strong ripples
* Red peaks
* Flashing alerts

---

6. DESIGN PATTERNS

* Modular processing (pipeline)
* Separation of backend/frontend
* Double smoothing system
* GPU-based rendering (shader)

---

7. MODIFICATION GUIDE

Change filter:
MAF_SIZE

Change sensitivity:
MAX_RMS_G

Change amplitude scaling:
0.50 + intensity * 3.50

Change ripple frequency:
dist * 6.0

Change smoothing:
LPF_A, AMP_L, SPD_L

---

8. CORE INSIGHT

Physical vibration
→ mathematical processing
→ normalized metrics
→ GPU simulation
→ visual interpretation

---

9. SUMMARY

The system:

* Cleans IMU data
* Extracts vibration energy and frequency
* Normalizes the data
* Drives a shader-based simulation
* Displays real-time structural behavior
* Detects and highlights anomalies

---

END OF DOCUMENT
