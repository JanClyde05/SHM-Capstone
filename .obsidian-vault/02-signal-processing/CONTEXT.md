# Signal Processing — Backend DSP Pipeline

> Stage 02 | ICM L2 Contract  
> **Input**: Raw IMU readings (ax, ay, az in g)  
> **Output**: RMS, dominant frequency (Hz), intensity [0–1]  
> **File**: [[Calculations.h]]

## Pipeline Order (§5.0 — strict)

```
Raw → calibApply() → mafUpdate(ax,ay,az) → magnitude → RMS + FFT → intensity
```

⚠ MAF runs **per-axis BEFORE** magnitude. This is non-negotiable.

---

## 1. Calibration (`CalibState`)

**Goal**: Remove static sensor bias/drift.

| Step | Detail |
|------|--------|
| Collect | 200 stationary samples |
| Compute | Mean per axis → offset vector |
| Apply | `corrected = raw − offset` |
| Gravity | NOT removed here (done in magnitude step) |

```cpp
struct CalibState { double sumAx,sumAy,sumAz; int count; float offAx,offAy,offAz; bool done; };
calibUpdate(c, ax, ay, az);  // feed sample
calibFinish(c);               // lock offsets
calibApply(c, ax, ay, az);    // subtract offsets (in-place)
```

**Validation**: Post-calibration `|a| ≈ 1g ± 0.10g`. Failure = sensor moved during calibration.

---

## 2. Moving Average Filter (`MafState`)

**Goal**: Reduce high-frequency noise before magnitude.

| Param | Value |
|-------|-------|
| Window | `MAF_SIZE = 8` |
| Buffer | Circular, per-axis |
| Instances | 3 per sensor (ax, ay, az) |

```cpp
struct MafState { float buf[MAF_SIZE]; int idx; float sum; int fill; };
float smoothed = mafUpdate(m, sample);  // O(1) update
```

Update rule: `sum -= oldest; buf[idx] = new; sum += new; output = sum/fill`

---

## 3. Magnitude Extraction

```
mag = sqrt(fax² + fay² + faz²) − 1.0
if (mag < 0) mag = 0
```

Removes gravity baseline. Isolates dynamic vibration only.

---

## 4. RMS Feature Extraction

```
RMS = sqrt(Σx² / N)    N = RMS_WINDOW_SIZE (50)
```

Represents vibration energy. Direct structural response indicator.

---

## 5. FFT Frequency Analysis

| Step | Detail |
|------|--------|
| Window | Hamming |
| Size | 128 samples (power-of-2) |
| Library | arduinoFFT v2.x |
| Output | Dominant frequency (Hz) |

```cpp
ArduinoFFT<double> fft(vReal, vImag, FFT_SAMPLES, sampleRate);
fft.windowing(FFTWindow::Hamming, FFTDirection::Forward);
fft.compute(FFTDirection::Forward);
fft.complexToMagnitude();
float peak = fft.majorPeak();
```

---

## 6. Intensity Normalization

```
intensity = clamp(RMS / MAX_RMS_G, 0.0, 1.0)    MAX_RMS_G = 0.3g
```

Maps vibration energy to [0,1] for visualization + alerting.

---

## Tuning Constants

| Constant | Value | Controls |
|----------|-------|----------|
| `FFT_SAMPLES` | 128 | Frequency resolution |
| `RMS_WINDOW_SIZE` | 50 | Energy averaging window |
| `MAX_RMS_G` | 0.3 | Intensity ceiling |
| `CALIB_SAMPLES` | 200 | Calibration accuracy |
| `MAF_SIZE` | 8 | Filter smoothness |

## Links

- [[01-system-overview]] — where this fits in the pipeline
- [[04-firmware]] — FreeRTOS tasks that call these functions
- [[03-visualization]] — how intensity/freq drive shaders
