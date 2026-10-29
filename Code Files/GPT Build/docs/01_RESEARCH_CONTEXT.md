> **Historical snapshot - superseded 2026-10-24.** The user approved paper v2 and authorized Arduino IDE firmware for ESP32-S3-WROOM-1-N16R8 with three MPU6050 ICs. The active FFT method, hardware map, traffic protocol and verification status are in APPROVED_METHOD.md, HANDOFF.md, PROJECT_MAP.md and IMPLEMENTATION_STATUS.md. Older Welch, PlatformIO, old GPIO, estimator-open, collection and scaffold instructions below are retained only as history.

# 01 — Research Context, Device, and System Description

> **Latest user decisions (2026-10-24):** These decisions supersede older conflicting proposals in this document set. Use the three traffic groups NEAR_ZERO, MEDIUM, and HEAVY. Poll three triaxial sensors in order, reading one complete X/Y/Z frame from sensor 1, then 2, then 3, and repeat. Preserve each sensor stream; attach a polling-cycle ID, per-frame timestamp, and per-sensor sample index. Frames are sequential, not simultaneous. For baselines, report mean ± sample SD as a descriptive band and separately use mean ± 2 sample SD as the default heuristic review band; do not call the latter a formal 95% interval. DSP must be mathematically specified and reproducible. FFT versus Welch remains an open estimator decision; see docs/RESEARCH_ALIGNMENT_REVIEW.md for the implementation gate and paper-edit map.

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

## 4. What the device is intended to do

The planned sensor node uses three triaxial sensors polled sequentially in round-robin order. Each poll reads one complete X/Y/Z frame from sensor 1, then sensor 2, then sensor 3, then repeats. Preserve each sensor stream and retain a polling-cycle ID, per-frame monotonic timestamp, and per-sensor sample index. The three frames in one cycle are associated but not simultaneous. The exact sensor model and final hardware configuration must be verified against the actual board. The DSP estimator is not yet settled: the thesis describes FFT peak selection, while the engineering plan proposes Welch PSD. Do not implement or describe the final estimator until its complete mathematical definition is reconciled with the thesis. The system's intended scope remains dominant-frequency monitoring and visualization, not structural diagnosis.

## 5. Intended system flow (implementation details remain subject to verification)

Traffic / wind / ambient excitation
        ↓
Bridge member vibration and verified rigid mounting
        ↓
Three triaxial sensors: poll complete XYZ frame from 1, then 2, then 3; repeat
        ↓
Acquisition records raw per-sensor XYZ, cycle ID, per-frame timestamp, sample index, rate, skew, and gaps
        ↓
Raw retention and offline reference analysis using the same estimator as firmware
        ↓
DSP: estimator and parameters TBD after research-method reconciliation; use measured per-sensor sampling rate
        ↓
Session manager: session ID, traffic group, metadata, quality-control record
        ↓
Baseline: per-group descriptive mean ± s and separate mean ± 2s heuristic review band
        ↓
Arduino IDE firmware node and local dashboard using the adopted global UI standard

No averaging, fusion, or single node-level result is authorized until an explicit method is defined and validated. Keep individual sensor results available.

## 6. Measurement chain defined in Chapter III (what firmware must implement)

| Thesis element | Required behavior |
|---|---|
| §3.5 session = continuous record with fixed sensor placement/settings | Session manager with immutable settings snapshot per session |
| §3.5 ≥ 5 valid sessions per primary traffic condition | Session counter per traffic level; accept/reject log |
| §3.6 stationary check before each run | Pre-run 10 s still record: offset, clipping, noise gate |
| §3.9 estimator must be finalized and mathematically specified; thesis currently describes FFT while the plan proposes Welch | DSP pipeline with config-frozen band and rule |
| §3.9 Eq. (1)–(2) Δf = fs/N, f_k = k·fs/N | Use **measured** fs, not nominal (MPU clock ±1 % — see 03 Step 4) |
| §3.10 report x̄ ± s descriptively; separately use x̄ ± 2s as a heuristic review band, not a formal 95% interval | Baseline module + wording rule |
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
| FR-06 | Per-level baseline mean ± s descriptive band and mean ± 2s heuristic review band; CV and review flag | O2 | `baseline` | — | T-05 |
| FR-07 | Live spectrum, f_d trace with baseline band, session panel in browser | O3 | `web`, `data/` | Wi-Fi AP | T-08 |
| FR-08 | No damage-diagnosis wording anywhere | Scope | `web`, docs | — | review checklist |
| NFR-01 | Rigid mechanical coupling | O1 | — | 4 mounting holes + enclosure | T-09 |
| NFR-02 | Run ≥ 2 h on USB power bank | O1 | power mgmt | USB-C 5 V | T-10 |
| NFR-03 | Analysis settings frozen before baseline sessions (git tag) | O2 | `config` | — | process check |

Tests T-01…T-10 are specified in `04_CODEBASE_PLAN.md` §9 and `06_DATA_COLLECTION_PROTOCOL.md`.

### Acquisition and analysis constraints from the latest user clarification

- The traffic labels are NEAR_ZERO, MEDIUM, and HEAVY. Define a simple site-local classification rule from pilot observations before formal sessions; do not invent universal engineering thresholds.
- Each sensor frame has its own timestamp and sample index. A cycle ID associates the sequential sensor-1, sensor-2, and sensor-3 frames; it does not make their timestamps identical.
- Preserve per-sensor and per-axis data. Do not claim correlation from cycle membership alone, and do not average sensor spectra without a separately approved, validated rule.
- The one-SD descriptive baseline and two-SD review threshold are separate. The review threshold is heuristic, not a formal 95% interval.
- FFT versus Welch remains unresolved. Use the measured sampling rate in any final frequency calculation and reproduce the final firmware estimator in the offline reference.
## 8. Key terms (consistent usage)

- **Dominant frequency (f_d):** frequency of the largest valid spectral peak in the pre-declared analysis band, per axis per session. It is a *peak-picking indicator*, not automatically a true modal frequency (Hasani & Freddi, 2023; manuscript §2.2.2).
- **Baseline:** empirical, internal, condition-specific reference range of f_d from accepted sessions — not a safety limit.
- **Session:** one continuous, fixed-duration record under one traffic level with fixed hardware/firmware settings.
- **Traffic level:** one of `NEAR_ZERO`, `MEDIUM`, `HEAVY` (definitions in `06`).



