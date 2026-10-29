# Approved paper to firmware sync

The user approved paper v2 on2026-10-24 and deferred further paper revisions. Do not edit the paper in this firmware task.

Firmware implements the paper's single-board three-channel XYZ scan, one station,600s sessions, concurrent count, ten60s FFT windows, per-stream medians, local pilot count groups, descriptive mean±s and separate2s review heuristic. See docs/APPROVED_METHOD.md and docs/MATHEMATICAL_ALGORITHMS.md.

Record final module N16R8, MPU6050 register settings, confirmed pin map, measured sample rate/timing tolerance, selected symmetric Hann window, analysis band, frozen traffic cutoffs, storage limitations and measured prototype performance for a later paper revision. DRDY epochs are MCU-observed output events, with latency; do not describe them as simultaneous channels or calibrated ADC timing.
