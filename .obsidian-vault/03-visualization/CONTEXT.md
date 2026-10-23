# Visualization Engine — Frontend Rendering

> Stage 03 | ICM L2 Contract  
> **Input**: JSON from `/data` endpoint (intensity, freq per axis)  
> **Output**: Real-time 3D fabric ripple + heatmap + alerts  
> **File**: [[WebServerUI.h]]

## Data Flow

```
/data → fetch@20Hz → updateScene() → LPF → LERP → shader uniforms → GPU render
```

---

## 1. Dual-Stage Smoothing

### Stage 1 — Poll-tick LPF (network level)

```js
value += 0.10 × (new_value − current_value)   // LPF_A = 0.10
```

Reduces network jitter. Applied on each `/data` response.

### Stage 2 — Frame LERP (render level)

```js
curAmp[i] += AMP_L × (targetAmp − curAmp[i])   // AMP_L = 0.05
curSpd[i] += SPD_L × (targetSpd − curSpd[i])   // SPD_L = 0.04
```

Decouples sensor rate from GPU frame rate. Cloth-like fluidity.

---

## 2. Fabric Geometry

| Property | Value |
|----------|-------|
| Plane size | 22 × 22 units |
| Resolution | 96 × 96 segments |
| Orientation | XZ plane (rotation.x = −π/2) |
| Displacement | Y-axis (local Z → world Y) |

---

## 3. IMU → Ripple Source Mapping

| IMU Axis | Origin (local XY) | Position |
|----------|-------------------|----------|
| X | (−5.5, −4.0) | Left-front |
| Y | (0.0, 0.0) | Centre |
| Z | (5.5, −4.0) | Right-front |

---

## 4. Marinacci Radial Ripple (Vertex Shader)

```glsl
dist  = length(pos.xy − origin)
angle = −uTime × speed + dist × 6.0
att   = 1.0 / (1.0 + dist × 0.18)

disp = amp × att × (
    sin(angle)
  + sin(angle×2 + t×0.3) × 0.35
  + sin(angle×3.5 + t×0.7) × 0.12
)
```

3-harmonic sum with radial attenuation. Per-source, then summed.

---

## 5. Analytical Normals (No Finite Differences)

```glsl
// Chain rule: d(ripDisp)/d(angle) × d(angle)/d(dist) × d(dist)/d(pos)
normal = normalize(−dZ/dx, −dZ/dy, 1.0)
```

Transformed to world space via `mat3(modelMatrix)`.

---

## 6. Heatmap Color Ramp (Fragment Shader)

| Heat `t` | Color | Meaning |
|-----------|-------|---------|
| 0.00 | Deep indigo | Trough |
| 0.25 | Neon teal | Below mid |
| 0.50 | Cyan-green | Zero crossing |
| 0.75 | Yellow | Above mid |
| 1.00 | Red | Crest (max energy) |

`t = 0.5 + 0.5 × (totalDisp / maxAmp)` — signed, centred at rest.

---

## 7. Lighting System

- **3 directional lights**: Key (teal), Fill (cyan), Rim (back)
- **Phong specular**: shininess 55, strength 0.70
- **Crest glow**: Neon teal additive on wave peaks
- **Trough shadow**: Darkening factor on deep troughs

---

## 8. Intensity → Visual Mapping

| Metric | Idle | Full Vibration |
|--------|------|----------------|
| Amplitude | 0.50 | 4.0 |
| Speed | 0.40 | 3.0 |

```js
targetAmp = 0.50 + intensity × 3.50
targetSpd = 0.40 + min(freq, 50) × 0.052
```

---

## 9. UI / Alert System

**Table**: Ax/Ay/Az, Gx/Gy/Gz, RMS, Freq, Intensity%, Status badge  
**HUD**: Live dot, Hz counter, max RMS/Freq, threshold display  
**States**: `OK` (green) → `WARN` (yellow) → `CRIT` (red+flash)  
**Alert trigger**: `RMS ≥ critical threshold` → flashing triangle + row highlight

---

## Links

- [[02-signal-processing]] — where intensity/freq values come from
- [[04-firmware]] — `/data` endpoint that serves JSON
- [[07-graphs]] — shader pipeline graph
