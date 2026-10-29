# Approved research method mapped to firmware

Paper: Documents/The Real Research Paper/GPT Paper/SHM_Research_Aligned_Revision_Draft_v2.docx; approved by the user2026-10-24. Paper content is not changed by firmware development.

| Research method | Implementation |
|---|---|
| One fixed roadway-deck station, single PCB/three co-located MPU6050s | frozen station/orientation fields and two-bus prototype pin map |
| Sequential channel1 XYZ,2 XYZ,3 XYZ | acquisition task drains one six-byte FIFO frame from each channel in ascending order per scan cycle |
| Traceable sample time | per-sensor DRDY ISR epoch plus separate FIFO-read epoch, sample index and scan-cycle ID |
| Fixed600s with concurrent tally | five-second ARMED countdown, then half-open [start,start+600s) DRDY intervals; automatic timer stop; manual stop invalidates |
| Three traffic groups | observed integer count with pilot-frozen c1/c2; NEAR_ZERO C<=c1, MEDIUM c1<C<=c2, HEAVY C>c2 |
| Ten60s windows | immutable raw span queued only after all sensor streams pass each time boundary |
| Per-axis FFT | mean removal, symmetric Hann, exact arbitrary-N DFT by Bluestein; measured per-window fs; maximum positive in-band bin |
| Session result | median of ten valid window results per channel/axis; fewer valid windows -> null session frequency |
| Baseline | Welford sample mean/SD across valid finalized formal sessions only, per group/channel/axis and matching config/station/orientation |
| Review | descriptive mean±s plus separate default mean±2s heuristic; compare before adding current session |
| Prototype performance | raw continuity, clipping, DRDY/FIFO integrity, interval variability, online/offline FFT agreement, web logging |
| Evidence retention | raw.shmb, windows.csv, summary.json with settings/hash and raw CRC32; no deletion on download |

Defaults100Hz, DLPF4 (21Hz acceleration bandwidth),±2g, symmetric Hann,0.5–20Hz band and500us interval tolerance are declared prototype choices. They require pilot assessment; they are not automatically validated research settings. Freeze records the operator's selected band, tolerance, count cutoffs, station and orientation in NVS. No numeric vehicle cutoffs are invented.

DSP excludes DC and searches positive-frequency bins within the frozen band, strictly below measured Nyquist. Near-tie and band-edge diagnostics retain the maximum-bin result. No interpolation or Welch estimate is performed. Bluestein's internal zero padding accelerates the exact N-point transform and does not add measurement resolution.

The DRDY edge is an MCU-observed output event, not an exact ADC aperture timestamp. Constant sensor-filter latency and interrupt latency remain. Sampling-rate estimation uses DRDY epochs, never burst-read timestamps. Separate sensors are not phase synchronized.

Recording remains in a6.4MB PSRAM allocation during capture. Ten-window DSP runs concurrently on older immutable records. LittleFS persistence happens after capture with acquisition paused, avoiding flash writes in the measurement interval. A reset/power interruption before persistence loses that in-memory recording. This prototype strategy must be evaluated before formal field collection.

Five sessions per traffic group is a practical campaign target, not proof of statistical power. Firmware does no hypothesis testing. The Python campaign tool reports descriptive statistics. Formal inference remains subject to the approved paper's sample-size/assumption conditions.
