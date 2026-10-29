# 01 — Research Context, Device, and System Description

Source of truth: the manuscript *SHM – Formatted Thesis Paper – Reference Update.docx* (Chapters I–III written; IV–V are template text) and the repo `JanClyde05/SHM-Capstone`.

## 1. Problem (Chapter I)

- Region 2 (Cagayan Valley) bridges are managed by periodic visual inspection and reactive action. Two failures within one year illustrate the gap: Cabagan–Sta. Maria Bridge (Feb 27, 2025) and Piggatan Bridge, Alcala (Oct 6, 2025).
- **Buntun Bridge** (opened 1969, 1,369 m, Cagayan River) is the only direct crossing between Tuguegarao City and Solana. It has documented steel-truss fatigue and deck cracking, a 15-ton load restriction since March 2025, and flood closures (Typhoons Uwan/Tino, Nov 2025). **No instrumented vibration record of it exists.**
- Frequency-based SHM is established (natural frequency depends on mass and stiffness), but available systems are imported and expensive.

## 2. Objectives (Chapter I §1.3)

1. Develop a real-time monitoring system that acquires and processes structural vibration data from Buntun Bridge.
2. Extract and establish a **baseline range of dominant structural frequencies** from the acquired signals under varying traffic conditions.
3. Develop a real-time visualization interface for structural vibration characteristics and frequency behavior.

## 3. Scope limits you wrote (must be respected by firmware wording and UI labels)

- Frequency monitoring only — **no damage diagnosis, damage classification, load-capacity analysis, or repair recommendations.**
- Single site (Buntun Bridge); results not claimed to generalize.
- Baseline is **internal** (built with the same device; no external reference sensor / ground truth).
- Environmental factors (temperature, humidity, EMI) not fully modeled.
- Therefore the UI must **not** say "CRIT / structural anomaly". Use "OUTSIDE BASELINE – REVIEW".

## 4. What the device does (one paragraph)

A sensor node is rigidly attached to a Buntun Bridge member. Traffic-induced ambient vibration moves the structure; three MEMS accelerometers (MPU-6050) on the node record the acceleration. The ESP32-S3 acquires samples at a fixed, timestamped rate, removes the mean, computes a Welch-averaged spectrum per axis, and selects the **dominant frequency** inside a pre-declared analysis band using a fixed peak-picking rule. It stores the raw record and a per-session summary, compares the result with the baseline range, and serves a web dashboard over its own Wi-Fi access point so the operator can watch the spectrum live in the field.

## 5. How the system works (end to end)

```
Traffic / wind / ambient excitation
        │
        ▼
Bridge member vibrates  (rigid mount: bolts/magnet/epoxy plate)
        │
        ▼
3× MPU-6050 (accel ±2 g, DLPF ≈ 21 Hz, 100 Hz output, DATA-READY INT)
        │  I2C (2 buses in V2)             │ INT lines → timestamps (ESP32 crystal)
        ▼                                  ▼
ESP32-S3: FIFO burst read → int16 samples + true-fs estimate
        │
        ├─► raw logger (microSD, binary) ───────────────► offline Python analysis (ANOVA / Kruskal–Wallis)
        │
        ▼
DSP: mean removal → Hann window → Welch PSD (N=4096, 50 % overlap)
        → average 3 IMUs per axis → peak pick in band + parabolic interpolation
        → dominant frequency f_d, peak prominence (SNR), QC flags
        │
        ▼
Session manager: ID, traffic level tag, metadata, summary.json
        │
        ▼
Baseline module: mean ± s, CV across accepted sessions (per level + pooled)
        │
        ▼
Wi-Fi AP + web dashboard: live spectrum, f_d trace vs baseline band, session panel, CSV/binary download
```

## 6. Measurement chain defined in Chapter III (what firmware must implement)

| Thesis element | Required behavior |
|---|---|
| §3.5 session = continuous record with fixed sensor placement/settings | Session manager with immutable settings snapshot per session |
| §3.5 ≥ 5 valid sessions per primary traffic condition | Session counter per traffic level; accept/reject log |
| §3.6 stationary check before each run | Pre-run 10 s still record: offset, clipping, noise gate |
| §3.9 mean/DC removal, optional detrend, window, FFT, exclude DC bin and out-of-band bins, fixed peak rule | DSP pipeline with config-frozen band and rule |
| §3.9 Eq. (1)–(2) Δf = fs/N, f_k = k·fs/N | Use **measured** fs, not nominal (MPU clock ±1 % — see 03 Step 4) |
| §3.10 baseline x̄ ± s, CV (Eq. 3–4); flag outside, never call it damage | Baseline module + wording rule |
| §3.12 repeatability (hold settings constant; log any change) | Settings hash in every session file; firmware version string |
| §3.13 QC: exclude clipping/saturation/corruption with logged reason; no cherry-picking | QC log with reason codes; outliers kept unless technical cause |
| §3.7 save processed result + raw/retained time series + metadata | microSD session folder |
| §3.11 ANOVA (α = 0.05), Kruskal–Wallis fallback | Offline Python tool (not on ESP32) |

## 7. Requirement traceability matrix

| Req ID | Requirement | Objective | Firmware module | Hardware item | Verification |
|---|---|---|---|---|---|
| FR-01 | Sample 3 IMUs at fixed rate, timestamped, no dropped samples | O1 | `imu_mpu6050`, `acquisition` | INT lines routed (V2 / bodge V1) | T-02, T-03 |
| FR-02 | Per-axis acceleration with gravity/mean removed correctly | O1 | `dsp` | — | T-01 |
| FR-03 | Dominant frequency per axis per session with fixed band and rule | O1, O2 | `dsp`, `session` | — | T-01, T-04 |
| FR-04 | Raw + summary stored per session; downloadable; no auto-delete | O1, O2 | `storage`, `web` | microSD (V2) | T-06 |
| FR-05 | Traffic level tag (near-zero / medium / heavy) + vehicle count recorded | O2 | `session`, `web` | — | T-07 |
| FR-06 | Baseline mean ± s, CV per level and pooled; outside-baseline flag | O2 | `baseline` | — | T-05 |
| FR-07 | Live spectrum, f_d trace with baseline band, session panel in browser | O3 | `web`, `data/` | Wi-Fi AP | T-08 |
| FR-08 | No damage-diagnosis wording anywhere | Scope | `web`, docs | — | review checklist |
| NFR-01 | Rigid mechanical coupling | O1 | — | 4 mounting holes + enclosure | T-09 |
| NFR-02 | Run ≥ 2 h on USB power bank | O1 | power mgmt | USB-C 5 V | T-10 |
| NFR-03 | Analysis settings frozen before baseline sessions (git tag) | O2 | `config` | — | process check |

Tests T-01…T-10 are specified in `04_CODEBASE_PLAN.md` §9 and `06_DATA_COLLECTION_PROTOCOL.md`.

## 8. Key terms (consistent usage)

- **Dominant frequency (f_d):** frequency of the largest valid spectral peak in the pre-declared analysis band, per axis per session. It is a *peak-picking indicator*, not automatically a true modal frequency (Hasani & Freddi, 2023; manuscript §2.2.2).
- **Baseline:** empirical, internal, condition-specific reference range of f_d from accepted sessions — not a safety limit.
- **Session:** one continuous, fixed-duration record under one traffic level with fixed hardware/firmware settings.
- **Traffic level:** one of `NEAR_ZERO`, `MEDIUM`, `HEAVY` (definitions in `06`).
