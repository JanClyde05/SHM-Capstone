# GPT6 Astra mathematical review brief

Updated 2026-10-24. This brief prepares an independent audit; it does not record an Astra review or approval that has not occurred.

## Scope and current research contract

The user approved `Documents/The Real Research Paper/GPT Paper/SHM_Research_Aligned_Revision_Draft_v2.docx` and authorized firmware development. The confirmed hardware is ESP32-S3-WROOM-1-N16R8 with three MPU-6050 ICs on one intended sensing PCB. The active sketch is `Code Files/GPT Build/firmware/SHM_Capstone/SHM_Capstone.ino`, built for Arduino IDE. Read `AGENTS.md`, `docs/HANDOFF.md`, and `docs/MATHEMATICAL_ALGORITHMS.md` before interpreting the older engineering-plan documents. Their unresolved-estimator and Welch proposals have been superseded by the approved FFT method.

Measure per-axis dominant vibration-frequency indicators at one fixed roadway-deck station. Preserve three sensor streams and X/Y/Z separately. Sequential FIFO read order is sensor 1→2→3; it does not establish simultaneous physical sampling or authorize sensor fusion. There is no implemented mode-shape identification, structural diagnosis, load-capacity estimate or external frequency calibration.

## Implemented estimator to reproduce

Each session is 600 seconds with ten consecutive half-open 60-second windows. Use actual N and measured per-sensor DRDY epochs in each window. For one sensor-axis: verify timing and raw QC, subtract that window's mean, apply the **symmetric Hann with denominator N−1**, compute the exact N-point DFT by Bluestein convolution, and select the largest magnitude bin in the fixed positive-frequency band. Exclude DC and even-N Nyquist. Return the selected bin frequency `k*f_s/N` without interpolating a fractional bin. Band-edge and near-tie diagnostics do not reject or alter the largest-bin choice. A constant/nonfinite/unusable window has no valid estimate.

The session median requires all ten valid window estimates for that sensor-axis. Firmware stores window frequencies as float when preparing the median, then returns a double median; offline NumPy retains float64. This small representation difference is not a changed estimator and must be distinguished from an actual bin mismatch. The protocol does not permit windows or onboard channels to become independent session replicates.

For each traffic group/sensor/axis, a baseline accumulates one accepted formal session median. Report mean ± sample SD descriptively; retain a separate mean ± 2 sample SD review heuristic. The five-session target is practical completion guidance. No power calculation, 95% coverage or inferential test follows from those settings.

## Code and equation navigation

All code paths below are relative to `Code Files/GPT Build/`. Exact equations and edge rules are in `docs/MATHEMATICAL_ALGORITHMS.md`.

| Path / function | Equation IDs / audit question |
|---|---|
| `firmware/SHM_Capstone/dsp.cpp`: `dspEstimateRateHz` | `EQ-RATE-01`: N sample epochs span N−1 intervals; rate is Hz with µs timestamps. |
| `dsp.cpp`: `dspAnalyzeAxis` preprocessing | `EQ-MEAN-01`, `EQ-HANN-01`: per-window demeaning followed by symmetric Hann; raw axis counts retained as input. |
| `dsp.cpp`: `dspWorkspaceLength`, `dspAnalyzeAxis`, private `fft` | `EQ-DFT-01`, `EQ-BLUESTEIN-01`, `EQ-FFT-02`: chirp signs, mirrored kernel indices, M≥2N−1, inverse normalization and transform correctness for non-power-of-two N. |
| `dsp.cpp`: `dspAnalyzeAxis` selection | `EQ-BIN-01`, `EQ-BIN-02`, `EQ-PEAK-01`: grid uses actual N, measured rate and fixed closed band. Ascending strict maximum chooses lowest exact numerical tie. |
| `dsp.cpp`: `dspMedian`; `session.cpp`: `summarize` | `EQ-MEDIAN-01`: even-length central-pair mean, all-ten policy and missing-result behavior. |
| `baseline.cpp`: `baselineAccumulate` | `EQ-STATS-01`: double Welford recurrence over session medians, isolated group/sensor/axis cells. |
| `baseline.cpp`: `baselineSummarize` | `EQ-SD-01`, `EQ-CV-01`, `EQ-BAND-01`, `EQ-BAND-02`: Bessel denominator m−1, undefined spread at m<2, positive-frequency CV, separate descriptive and review bounds. |
| `baseline.cpp`: `baselineOutsideReview`; `session.cpp`: `baselineState`, finalize paths | `EQ-REVIEW-01`: compare before current session enters baseline; require matching acquisition context and technical eligibility. |
| `session.cpp`: `worker` | `EQ-TIMING-01`: monotonic epochs/indices, interval residuals, rate/count tolerances and two-period edge coverage. |
| `session.cpp`: `/api/live` | `EQ-SCALE-01`: display-only nominal counts/16384 g conversion for±2g. FFT uses raw counts and per-window mean removal. |
| `session.cpp`: `configHash` | `EQ-HASH-01`: explicit canonical configuration, including algorithm, window, band, tolerances, clip limit and diagnostic tie setting. |
| `storage.cpp`: `storageSaveRaw` | `EQ-CRC-01`: reflected CRC32 of payload records; offline `zlib.crc32` checks integrity. |
| `tools/reference_math.py`: `pilot_cutoffs`, `traffic_group`; `tools/derive_traffic_cutoffs.py`: `derive`; session finalize | `EQ-TRAFFIC-02`, `EQ-TRAFFIC-03`: nearest-rank local pilot-count tertiles, then frozen count classification. |
| `tools/analyze_session.py`: `analyze` | `EQ-TRAFFIC-01`: C/10 vehicles/minute. Firmware stores integer C and the fixed duration. |
| `imu_mpu6050.cpp`: `readyEdge`, `imuReadFrame`; `acquisition.cpp`: `task` | Physical timing association: record MCU DRDY arrival separately from FIFO read completion; pair only stable equal FIFO/IRQ counts. These require bench evidence. |

The auxiliary M-point zero padding implements convolution; it does not produce M measured observations or justify `f_s/M` bin spacing. At nominal N=6000 and 100 Hz, Δf≈0.016667 Hz with M=16384. The principal PSRAM buffers total 6688144 bytes before networking, queues and stacks. Confirm actual available memory and runtime on the N16R8 hardware.

## Independent evidence and repeatable commands

[Certain] Native C++ was compiled and executed with Microsoft Visual C++ 14.50.35717 `/O2 /W4 /std:c++17`. `reports/math_verification.json` records NumPy 2.3.5, seed 20261024, source SHA256 hashes, 16 cases and numerical residuals. The full complex spectrum was compared with independently computed NumPy float64 FFTs, including N=31,64,257,6000,6001,6200. Worst normalized maximum complex error was approximately 1.10×10⁻⁷ versus the chosen 2×10⁻⁶ software check threshold. The threshold is not a device-accuracy specification.

The C++ driver also checks timing intervals, odd/even medians, sample SD/CV/bounds, invalid contributions and cell isolation. Additional generated fixtures verify a 180000-record/90-axis-window session, CRC corruption, injected timing disturbance, sample-index gaps, missing-ten-window medians, metadata-driven tie diagnostics, unfrozen pilot classification, pilot input rules and campaign context separation. These are mathematical fixtures, not hardware measurements.

From `Code Files/GPT Build/tools/`, using an x64 Visual Studio Native Tools prompt:

```bat
cl /nologo /EHsc /std:c++17 /O2 /W4 native_math_check.cpp ..\firmware\SHM_Capstone\dsp.cpp ..\firmware\SHM_Capstone\baseline.cpp /Fe:native_math_check.exe
```

Then use the Python environment containing NumPy:

```powershell
python verify_math.py --native ./native_math_check.exe --report ../reports/math_verification.json
python verify_raw_pipeline.py
python verify_traffic_workflow.py
```

Prefer a temporary build directory for compiled objects/executable. `tools/README.md` also documents a g++ alternative, which was not executed in this session. Compare the current numerical source hashes with the saved report before relying on old results; rebuild and rerun when numerical changes justify it.

For an **actual exported prototype record**, reproduce all windows before interpreting a session:

```powershell
python analyze_session.py S1_raw.shmb --summary S1_summary.json --windows S1_windows.csv --output offline_S1.json
python analyze_campaign.py --output campaign.json offline_S1.json offline_S2.json
```

Inspect missing CSV rows, bin/validity/timing disagreements and near ties. A nonmatching bin must be investigated; a pure numerical check passing does not validate sensor timing, analog response or structural interpretation. The campaign tool rejects duplicate IDs and mismatched settings/stations/orientations and excludes pilot or technically rejected sessions.

Use actual finalized 600-second pilot summaries with `derive_traffic_cutoffs.py`, as documented in `tools/README.md`, to derive numeric cutoffs before formal collection. Synthetic test cutoffs 1 and 3 are test fixtures and must never become field defaults.

## Pending physical verification and review deliverable

- Verify the physical module marking, PSRAM behavior, bus/AD0 and DRDY wiring before using the prototype pin plan for KiCad.
- Capture DRDY alongside I²C transactions with appropriate bench instrumentation; test whether FIFO frame counts and ISR timestamps remain paired over a 600-second run with Wi-Fi/UI activity. Inject disconnects, missed edges, overflow and clipping; retain the rejected raw files and exact reasons.
- Confirm uniform sample timing, IRQ latency/jitter and counts. MCU ISR arrival is not exact ADC aperture time; constant DLPF delay and clock error are not eliminated by software timestamping. A measured average rate cannot correct arbitrary timing jitter.
- Compare an appropriate known-frequency input and external reference, document uncertainty, and characterize actual MPU6050 noise/response before asserting physical accuracy. FFT bin spacing and numerical residuals are not calibration evidence.
- Pilot-confirm mounting/orientation, usable band, timing/clip settings, fixed interval adequacy and local count cutoffs; preserve station and configuration metadata. Do not fill research results from generated signals.

The requested Astra deliverable is an independent issue list with equation IDs, module/functions, derivations or counterexamples, reproduced checks, severity and unresolved physical assumptions. Preserve accepted research scope when proposing fixes. Hardware schematic/PCB work follows prototype evidence; this brief does not claim that work or an Astra audit has already happened.
