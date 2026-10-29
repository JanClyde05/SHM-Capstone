# Mathematical algorithm audit map

Updated 2026-10-24 after the user approved the v2 paper and confirmed ESP32-S3-WROOM-1-N16R8 and three MPU-6050 ICs. [Certain] The approved estimator is FFT magnitude peak selection. The old Welch proposals in documents 00–07 are historical and do not define the active implementation.

Read `firmware/SHM_Capstone/dsp.h/.cpp`, `baseline.h/.cpp`, `tools/reference_math.py`, and `tools/analyze_session.py` together. Search the stable equation IDs below in code. `tools/verify_math.py` compares the actual compiled C++ to NumPy's separate FFT implementation; it does not merely run a translated version of our transform.

## Inputs, unit of observation, and policy

- Retain three independent sensor streams, each with X/Y/Z raw signed ADC counts. Each FFT consumes one axis from one sensor in one fixed 60-second time window. There is no XYZ vector magnitude, sensor averaging, startup offset subtraction, extra smoothing filter, Welch averaging, interpolation, or frequency-bin interpolation.
- Firmware treats sensor 1→2→3 FIFO reads as sequential. A scan-cycle ID associates read order. A DRDY timestamp is MCU interrupt arrival time, an approximation to sensor output time; it is not an externally calibrated ADC aperture timestamp. Read timestamps are separate. Constant filter delay, ISR latency and sensor-clock error need bench characterization.
- A session is 600 seconds, partitioned into ten half-open 60-second intervals `[start + 60j, start + 60(j+1))`, `j=0..9`. Boundary membership uses each sensor's DRDY timestamp. Actual sample counts can differ from nominal 6000 and from other sensors.
- The session result for a sensor-axis requires all ten windows to have usable timing and a defined spectral maximum. Its value is their median. This conservative implementation policy is recorded explicitly; ten windows are not ten independent field sessions. Missing estimates remain documented and are not replaced by zero.
- Timing tolerance, analysis band, clip limit, DLPF/range/rate settings, and pilot traffic cutoffs must be frozen in the configuration before formal collection. Defaults are prototype settings, not validated bridge parameters. A configuration hash identifies the actual settings.

## Equation index

Use zero-based within-window sample index `n`, actual count `N`, DFT index `k`, windowed count-valued series `y`, measured rate `f_s`, and session-level frequency observations `f_i`.

| Stable code ID | Equation and purpose | Implementation |
|---|---|---|
| `EQ-SCALE-01` | Live display only: `a_g=raw_counts/16384` for the configured ±2g accelerometer range. This is nominal sensitivity scaling, not a measured calibration. | Session `/api/live` XYZ display; `SHM_COUNTS_PER_G` in `config.h` |
| `EQ-RATE-01` | `f_s = (N−1)·10^6/(t_(N−1)−t_0)` Hz, timestamps in µs. N sample epochs span N−1 intervals. | `dspEstimateRateHz`; `reference_math.estimate_rate` |
| `EQ-MEAN-01` | `x̄_window = (1/N)Σ_(n=0)^(N−1)x[n]`; `u[n]=x[n]−x̄_window`. This removes the current window's constant component. | `dspAnalyzeAxis`; `reference_math.analyze_axis` |
| `EQ-HANN-01` | Symmetric Hann `w[n]=1/2−(1/2)cos(2πn/(N−1))`, `0≤n<N`; `y[n]=u[n]w[n]`. Both endpoints are zero, apart from arithmetic roundoff. | Same two functions. Explicit denominator **N−1**, not the periodic Hann's N. |
| `EQ-DFT-01` | `Y[k]=Σ_(n=0)^(N−1)y[n]exp(−i2πnk/N)`. Forward transform is unnormalized. | C++ Bluestein; independent NumPy `fft(y)` |
| `EQ-BLUESTEIN-01` | With `c[n]=exp(iπn²/N)`, set `a[n]=y[n]/c[n]`, `b[n]=c[n]`, and mirrored `b[M−n]=c[n]` for `1≤n<N`; all other entries zero. `Y[k]=exp(−iπk²/N)·IFFT_M(FFT_M(a)FFT_M(b))[k]`. Choose `M` as next power of two ≥`2N−1`. | `dspAnalyzeAxis`, `dspWorkspaceLength` |
| `EQ-FFT-02` | Radix-2 butterflies evaluate each auxiliary M-point forward DFT; the inverse uses positive exponent and divides by M. | Private C++ `fft` |
| `EQ-BIN-01` | `Δf=f_s/N`. This is frequency-bin spacing, not a complete spectral resolving-power or accuracy claim. | `DspAxisResult.binSpacingHz` |
| `EQ-BIN-02` | `f_k=k f_s/N`; return the selected bin's frequency with no fitted fractional-bin estimate. | `DspAxisResult.dominantFrequencyHz` |
| `EQ-PEAK-01` | `K={k:1≤k≤floor((N−1)/2), f_lo≤k f_s/N≤f_hi}`. `k*=argmax_(k∈K)|Y[k]|`; exact numerical ties select the lowest k because traversal is ascending and updates use strict `>`. | `dspAnalyzeAxis`, independent NumPy `argmax` |
| `EQ-MEDIAN-01` | Sort the ten valid frequencies; for even length L use `(f_(L/2−1)+f_(L/2))/2` with zero-based indices. | `dspMedian`; NumPy `median` in offline session tool |
| `EQ-STATS-01` | Session mean `f̄=(1/m)Σf_i`. Welford recurrence: `δ=f_i−mean_old`, `mean_new=mean_old+δ/m`, `M2_new=M2_old+δ(f_i−mean_new)`. | `baselineAccumulate`; independent NumPy batch mean/SD |
| `EQ-SD-01` | Sample `s=sqrt[M2/(m−1)] = sqrt[Σ(f_i−f̄)²/(m−1)]`, defined for `m≥2`. | `baselineSummarize`; NumPy `std(ddof=1)` |
| `EQ-CV-01` | `CV%=100s/f̄`, for positive finite mean and defined s. | `baselineSummarize` |
| `EQ-BAND-01` | Descriptive observed-spread band `[f̄−s, f̄+s]`. | `BaselineAxisSummary.descriptiveLoHz/HiHz` |
| `EQ-BAND-02` | Separate review heuristic `[f̄−k_review s, f̄+k_review s]`, default `k_review=2`. | `BaselineAxisSummary.reviewLoHz/HiHz` |
| `EQ-REVIEW-01` | Review only when a new result is strictly below/above the prior review bounds and the practical target is met. Equal endpoints are within bounds. | `baselineOutsideReview` |
| `EQ-TRAFFIC-01` | Vehicle rate `r=C/10` vehicles/minute for the fixed 10-minute session. Stop on time, never on a vehicle-count target. | Offline `analyze_session`; firmware stores raw C and fixed duration |
| `EQ-TRAFFIC-02` | From sorted m pilot counts, `c1=C_(ceil(m/3))`, `c2=C_(ceil(2m/3))`, using one-based order-statistic indices. | `reference_math.pilot_cutoffs`; operator tool `derive_traffic_cutoffs.derive` |
| `EQ-TRAFFIC-03` | NEAR_ZERO if `C≤c1`; MEDIUM if `c1<C≤c2`; HEAVY if `C>c2`. | `reference_math.traffic_group`; session `sessionPost` finalize and recovered-finalize branches |
| `EQ-TIMING-01` | Mean sample period `(last−first)/(N−1)`; bound each interval's absolute residual, frequency/count deviation, and boundary coverage as described below. | Session `worker`; offline `analyze_session` |
| `EQ-HASH-01` | SHA-256 over the explicit canonical configuration string, including firmware/algorithm/sensor settings; not over padded C++ struct bytes. | Session `configHash` |
| `EQ-CRC-01` | CRC-32/ISO-HDLC of payload records: initialize `0xffffffff`, reflected polynomial `0xedb88320`, final XOR `0xffffffff`. The header is excluded. | Storage `storageSaveRaw`; offline `zlib.crc32(payload)` |

The FFT's auxiliary zero padding implements a convolution identity. It does **not** pad the measurement to M observations or make bin spacing `f_s/M`: the returned grid remains the true N-point DFT. For nominal N=6000 and measured `f_s=100 Hz`, `Δf≈0.0166667 Hz`; M=16384. Two complex-float work arrays need 262144 bytes, reused axis by axis. Actual window N and measured rate must be reported; do not infer true accuracy from the displayed decimals.

The FFT itself consumes raw counts. The UI's counts-to-g scaling is separate; it neither subtracts 1 g nor changes the Fourier preprocessing. Multiplying an entire axis by a positive constant changes spectrum magnitude and leaves the maximum-bin index unchanged apart from finite-precision edge cases. The displayed g value retains the static component, whereas the FFT removes each current window's mean. No m/s² conversion or calibration correction is implemented.

## Checks, flags, and ambiguous results

The numerical module rejects null/too-short input, nonfinite samples/settings, invalid band/rate, insufficient workspace, configured clipping, exactly constant input, empty included-bin set, or nonfinite spectrum. A valid numerical maximum is **not** proof that signal exceeds the sensor noise floor or is a verified structural natural mode. There is no undocumented SNR gate.

For even N the Nyquist bin is excluded; for odd N the highest positive-frequency bin is allowed. DC is always excluded. The fixed band has closed bounds. No band is widened to rescue an estimate. The largest in-band bin is retained even when it lies at a band edge; `bandEdgePeak` records this diagnostic. Another included bin within `relativeTieTolerance` of the maximum sets `nearTie`. The default `1e−4` is a numerical diagnostic setting, not a rejection threshold or significance test. Exact ties select the lowest numerical maximum. Very close peaks can swap order between float32 C++ and float64 reference arithmetic; inspect flagged windows rather than claim identical physical estimates from an ill-conditioned maximum.

The current firmware records `relative_tie_tolerance` in the settings snapshot and configuration hash; the offline session tool reads that value. Historical records lacking it use the original 1e−4 default. Changing this diagnostic setting changes flags, not the selected maximum, window validity or median. The synthetic pipeline check confirms that behavior and rejects an invalid tolerance ≥1.

Timing QC is outside the Fourier transform. The active acquisition checks require monotonic epochs, no missing sample indices/queue–FIFO mismatch, no clipping or record flags, `|f_s/f_nominal−1|≤fs_tol_fraction`, every interval within `timing_tolerance_us` of its window's mean interval, coverage to within two measured periods of each window boundary, and sample count within nominal 60-second count×`(1±fs_tol_fraction)` allowing two boundary samples. Prototype tolerances require bench/pilot confirmation. Passing a mean-rate check alone cannot validate uniform sampling.

FIFO/DRDY pairing requires a stable queue-length snapshot and exact equality between complete six-byte FIFO frame count and queued sample epochs before popping the oldest pair. Queue changes during the count-register read cause a retry. Any persistent mismatch, including one frame, is an error; a one-frame offset must never be silently tolerated. A nonmultiple-of-six FIFO byte count also causes a retry and persistent-mismatch rejection. This protects association; it still requires real hardware verification.

Do not substitute FIFO burst read times for sample epochs, interpolate gaps, or use nominal100 Hz when a measured stream rate is missing. Raw timestamps, read timestamps and quality indicators remain available for audit. The offline tool verifies the payload CRC32, schema, per-stream chronology/index continuity, read order within scan cycles and the above timing rules. A device-reported technical issue remains an issue even if surviving records alone look regular.

## Baseline rules and statistical limits

Keep separate baseline cells for each of three groups × three sensors × three axes. Add one positive finite **session median** per accepted formal session per cell, after technical QC and traffic assignment. The session manager must ensure unique session IDs and equal configuration hashes. Do not count windows, axes or co-located sensors as independent session replicates. Pilot and formal modes remain separate.

At m=1 only the mean is defined; s/CV/bounds are undefined and serialized as null. At m≥2 the descriptive spread is calculable. A five-session completion target is feasibility guidance and does not establish statistical power. The review helper requires that practical target before comparing, but five sessions do not validate coverage. For identical observations s=0 and the bands collapse; any unequal new value is outside the heuristic. Negative lower bounds are retained mathematically rather than silently clamped.

The two-SD band is not a confidence interval, prediction interval, calibrated limit or diagnosis. Compare a new result with the prior baseline before considering whether it is eligible for a future baseline update. Frozen campaign membership should be documented. No inferential test is run by these tools. CV uses frequency's meaningful zero; undefined/nonfinite outputs remain null, and unusually large CV near zero must not be hidden by an invented denominator threshold.

## Raw-buffer ownership and acquisition context

[Certain] Source inspection: the session retains up to 200000 immutable 32-byte raw records in PSRAM: 6400000 bytes. The axis scratch holds 6500 floats (26000 bytes), and two M=16384 complex-float arrays require another 262144 bytes. These principal buffers total 6688144 bytes; queues, stacks, networking, JSON and other allocations are additional. This arithmetic is a memory plan, not a measured free-memory/runtime result on the N16R8 unit.

The acquisition callback appends records under the capture lock. A window is queued only after every sensor has passed its end boundary, with a published raw end-index snapshot. The worker reads only those older immutable records while acquisition continues appending. Results use a mutex. The next session does not reset/reuse buffers until the current queued jobs finish. Capture stops before persistence; raw files are written after acquisition, avoiding per-record flash writes during the 600-second capture. Source review found no need to change the defined N-point FFT or retain only a shortened power-of-two segment.

The final summary checks frame flags and per-sensor sample-index continuity across window boundaries as well as each window's timing. Thus a gap exactly between two individually regular windows is not accepted. Baseline reconstruction selects formal, finalized, technically accepted summaries with matching configuration hash, station and orientation. The current session's comparison is computed before adding its summary to the reconstructed baseline. These are inspected control-flow properties; MCU execution and fault injection remain pending.

Pilot cutoffs require local equal-duration counts. Collapsed cutoffs/empty groups require a revised or extended pilot before freezing; zero counts are permitted and NEAR_ZERO can contain nonzero counts. Formal data must not determine the cutoffs after frequency outcomes are seen.

`tools/derive_traffic_cutoffs.py` applies that rule to exported finalized pilot summaries. It requires distinct session IDs, full 600-second intervals, matching station/orientation and integer vehicle counts; aborted, shorter, formal or unfinished sessions are rejected. `--require-technical-valid` additionally requires accepted device QC. Otherwise an intact traffic observation can contribute even when vibration QC was rejected, and that QC status is retained explicitly. The output preserves the input IDs/counts, sorted counts, selected one-based ranks, cutoffs and resulting group counts. These are local operational groups, not engineering loading classes.

## Verified primary references

- [NumPy DFT conventions](https://numpy.org/doc/stable/reference/routines.fft.html): forward sign, unnormalized transform, bin ordering and even/odd Nyquist treatment. Opened 2026-10-24.
- [AMD rocFFT Bluestein design](https://rocm.docs.amd.com/projects/rocFFT/en/docs-6.1.5/design/bluestein.html): chirp convolution identity and M≥2N−1. Opened 2026-10-24. This source supports the algorithm identity; our C++ implementation and embedded runtime are independently checked, not inherited from rocFFT.
- [SciPy Hann window documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.windows.hann.html): symmetric Hann definition and distinction from periodic form. Search retrieval verified 2026-10-24; a subsequent direct fetch timed out. Link is the official documentation, and the exact convention used here is stated above.
- [NIST measures of scale](https://www.itl.nist.gov/div898/handbook/eda/section3/eda356.htm): sample variance denominator m−1 and its square-root SD. Opened 2026-10-24.
- [NIST coefficient of variation](https://itl.nist.gov/div898/software/dataplot/refman2/auxillar/coefvari.htm): sample SD relative to mean and ratio-scale interpretation. Search retrieval verified 2026-10-24.
- The approved paper and its `REVISION_PLAN.md` retain the FHWA fixed-interval/manual-count sources and the contextual one-minute bridge-window precedent. Neither provides universal numeric traffic cutoffs, a validated spectral band, nor proof of the chosen pilot tolerances.

## Actual verification and remaining work

[Certain] On 2026-10-24, native C++ built using Microsoft Visual C++ 14.50.35717 `/O2 /W4 /std:c++17` and executed. All 16 C++/NumPy cases passed, including the full complex spectrum for N31,64,257,6000,6001,6200, DC plus noise, an off-grid tone, a stronger out-of-band tone, band-edge and equal-peak diagnostics, constant/clipped/nonfinite input, invalid Nyquist band and empty-bin band. Maximum normalized complex-spectrum error across valid cases was approximately `1.10×10^−7` against a `2×10^−6` numerical check threshold. Numerical check tolerance is not a measurement-accuracy specification. See `reports/math_verification.json`.

[Certain] Native scalar checks exercised N−1 timing intervals, odd/even medians, sample SD/Bessel correction, CV, separate descriptive/review bands, invalid contributions, and independent group/sensor/axis cells. The synthetic raw-pipeline check decoded 180000 SHMRAW2 records into 90 axis-windows, recovered nine expected ten-window medians, rejected mismatched CRC32, and flagged an injected 700 µs interval disturbance and a sample-index gap with otherwise regular timestamps; a stream with nine valid windows did not obtain a session median. Unfrozen pilot cutoffs0,0 correctly retained an unclassified result. This fixture is generated mathematical data, not an acquired recording.

[Certain] `verify_traffic_workflow.py` checked synthetic pilot counts `[0,1,2,3,4,5]` yielding cutoffs 1 and 3 with two observations per group; it rejected 12 invalid pilot cases, enforced the optional device-QC requirement, accepted a matching formal campaign, and rejected different stations/orientations despite identical configuration hashes. This validates input handling and arithmetic; the counts are not proposed field thresholds.

[Not verified] ESP32 runtime/memory under concurrent Wi-Fi, real DRDY timing/FIFO matching, spectral/noise behavior of actual MPU6050 ICs, external frequency calibration, pilot-frozen settings, traffic cutoffs, field deployment and thesis results. GPT6 Astra should inspect both source and these limits before hardware design, and reproduce the recorded checks before asserting algorithm correctness.
