> **Historical snapshot - superseded 2026-10-24.** The user approved paper v2 and authorized Arduino IDE firmware for ESP32-S3-WROOM-1-N16R8 with three MPU6050 ICs. The active FFT method, hardware map, traffic protocol and verification status are in APPROVED_METHOD.md, HANDOFF.md, PROJECT_MAP.md and IMPLEMENTATION_STATUS.md. Older Welch, PlatformIO, old GPIO, estimator-open, collection and scaffold instructions below are retained only as history.

# 02 — Audit Register and Detailed Fixes

Severity: **S1** = invalidates the thesis result, **S2** = degrades data quality or defense credibility, **S3** = cleanup.
Evidence is cited to the exact file / function / datasheet section so an agent can re-verify.

Files audited: `firmware/SHM_Main.ino`, `firmware/Calculations.h`, `firmware/WebServerUI.h`, `Thesis.kicad_sch` (81 symbols, nets extracted), `Thesis.kicad_pcb` (36 footprints, 411 segments, 69 vias, 1 zone), manuscript .docx.

---

## A. Summary table

| ID | Area | Finding | Sev | Conf. | Fix doc |
|----|------|---------|-----|-------|---------|
| FW-01 | Firmware | Gravity removed twice → output is 0 for any motion < 1 g | **S1** | Certain | 03 §2 |
| FW-02 | Firmware | Scalar magnitude (`|a| − 1 g`, clamped ≥ 0) rectifies the signal, destroys per-axis info, doubles frequencies for lateral motion | **S1** | Certain | 03 §2 |
| FW-03 | Firmware | FFT reads ring buffer in storage order (splice at write pointer) with no lock | S2 | Certain | 03 §6 |
| FW-04 | Firmware | N = 128 at 166.7 Hz → 1.30 Hz bins, 0.77 s window; cannot resolve 1–5 Hz modes | **S1** | Certain | 03 §6 |
| FW-05 | Firmware | Software polling at 166.7 Hz vs MPU output 200 Hz (DLPF on, div 4) → duplicated/skipped samples; INT unused | S2 | Certain | 03 §3–4 |
| FW-06 | Firmware | `PWR_MGMT_1 = 0x00` → CLKSEL = 0 (internal oscillator): ±5 % initial, −15/+10 % over temperature → frequency axis error | **S1** | Certain | 03 §3–4 |
| FW-07 | Firmware | 8-tap moving average on top of 44 Hz DLPF: uncontrolled double low-pass | S3 | Certain | 03 §3 |
| FW-08 | Firmware | "Baseline" = 10 s idle RMS after boot; "CRIT = structural anomaly" contradicts thesis scope and §3.10 | S2 | Certain | 03 §8 |
| FW-09 | Firmware | No session ID, traffic tag, metadata, QC log, raw retention | **S1** | Certain | 04 §5 |
| FW-10 | Firmware | CSV ≈ 500 rows/s × ~56 B ≈ 28 KB/s; LittleFS fills in ≈ 1 min; flash writes stall sampler; download auto-deletes file | S2 | Likely (partition size assumed) | 03 §7 |
| FW-11 | Firmware | I2C pins 8/9 in code vs IO36(SDA)/IO35(SCL) on V1 PCB | S2 | Certain | 03 §1 |
| FW-12 | Firmware | "IMU X-axis / Y-axis / Z-axis" naming: each IMU measures all 3 axes | S2 | Certain | 03 §2 |
| FW-13 | Firmware | Dashboard maps frequency → ripple speed with arbitrary constants; not a measurement view; Three.js ≈ 600 KB flash | S2 | Certain | 04 §7 |
| FW-14 | Firmware | No pre-run stationary check / IMU self-test | S3 | Certain | 03 §5 |
| FW-15 | Firmware | Wi-Fi password hard-coded in source | S3 | Certain | 03 §10 |
| FW-16 | Firmware | `millis()` timestamp, same value for all 3 sensors | S3 | Certain | 03 §4 |
| HW-01 | Schematic | CPOUT capacitors C9/C12/C15 = 220 pF; datasheet requires **2.2 nF X7R 50 V** | S2 | **Certain** (MPU-6000/6050 spec §7.3) | 05 §3 |
| HW-02 | Schematic | 3 × 4.7 kΩ in parallel on each of SDA and SCL ≈ 1.57 kΩ | S3 | Certain | 05 §4 |
| HW-03 | Schematic | 6 AUX_DA/AUX_CL pull-ups (R9, R10, R13, R14, R17, R18) unused | S3 | Certain | 05 §4 |
| HW-04 | Schematic | INT pins (pin 12) of all 3 IMUs unconnected | S2 | Certain | 05 §4 |
| HW-05 | Schematic | I2C on IO35/IO36: unusable if module is R8/R16V | S1 if R8 | **Certain** (Espressif datasheet v1.8 Table 3-1 note b) | 05 §2 |
| HW-06 | Schematic | No ESD protection on USB D±, no VBUS fuse | S3 | Certain | 05 §3 |
| HW-07 | Schematic | No microSD, no status LED, no test points | S2 | Certain | 05 §3 |
| HW-08 | Schematic | AD0 driven by 3 GPIOs (time-multiplex trick) instead of fixed addresses | S3 | Certain | 05 §4 |
| HW-09 | Schematic | No VLOGIC 10 nF (datasheet C4) | S3 | Certain | 05 §3 |
| PCB-01 | PCB | **No mounting holes** (only J1 shield NPTH) — thesis §3.6 requires rigid mount | S2 | Certain | 05 §6 |
| PCB-02 | PCB | All nets 0.30 mm incl. +5V/+3V3 | S3 | Certain | 05 §6 |
| PCB-03 | PCB | I2C routed on both layers with 11 vias (SDA 7, SCL 4) → ground plane split | S3 | Likely | 05 §6 |
| PCB-04 | PCB | **Pass:** no signal vias/traces under the MPU packages (datasheet §11.4.3); single GND via near U4 | — | Certain | — |
| PCB-05 | PCB | **Pass:** ESP32 antenna keep-out rule area exists (x 111.05–159.05, y 40.75–61.75 mm) | — | Certain | — |
| PCB-06 | PCB | No axis/orientation silkscreen for bridge-axis mapping | S3 | Likely | 05 §6 |
| TH-01 | Thesis | Section 3.4 leaves sensor count/model to document; user confirmed three sequential triaxial sensor slots, exact model still to verify | S2 | User decision recorded; thesis edit remains | 06 §9 |
| TH-02 | Thesis | Traffic categories peak/off-peak in thesis vs NEAR_ZERO/MEDIUM/HEAVY in plan | S2 | Historical discrepancy; user confirmed three groups on 2026-10-24; thesis edit remains | 06 §9 |
| TH-03 | Thesis | List of Figures has two "Figure 1"; body headings 3.11–3.15 unnumbered but numbered in TOC | S3 | Certain | 06 §9 |
| TH-04 | Thesis | Two reference hyperlinks contain `?utm_source=chatgpt.com` (Cornwell 1999; Welch 1967) — strip | S3 | Certain | 06 §9 |
| TH-05 | Thesis | Section 3.10 mean ± s descriptive band versus separate mean ± 2s heuristic review band | S2 | User decision recorded; revise Section 3.10; ±2s is not a formal 95% interval | 03 §8 |

---

## B. Detailed explanations of the S1 items

### FW-01 / FW-02 — why the system only reacts to violent motion

Evidence (code path):
1. `runCalibration()` → `calibUpdate()` accumulates **raw** `ax, ay, az` (these include gravity ≈ (0, 0, 1) g when flat).
2. `calibFinish()` sets `offA* = mean(raw)` → offsets **include gravity**.
3. `readMPU6050()` → `calibApply()` subtracts the offsets → at rest the vector is ≈ (0, 0, 0).
4. `taskSensorAcquisition()` then computes `sqrtf(fax² + fay² + faz²) − 1.0f` and clamps negatives to 0.

At rest the result is `0 − 1 = −1 → 0`. For a vertical sinusoid of amplitude A g, `|a| ≤ A`, so the result is `A·|sin| − 1 < 0` unless **A > 1 g**. So RMS ≈ 0 and the FFT sees zeros except during > 1 g shocks.
(The earlier note blaming an "RMS threshold gate" is not the root cause; the gate only compounds it.)

Even with the double subtraction fixed, magnitude is the wrong quantity: for a small lateral vibration `a_x` on top of gravity along z, `|a| ≈ 1 + a_x²/(2·1 g)` — second-order, so the signal is both tiny and frequency-doubled. The thesis response variable is the **dominant frequency per axis** (Table 2: "Dominant frequency per axis").

Fix: acquire each axis separately, subtract the **session mean** per axis (this removes gravity and bias together), never form a magnitude. See `03` §2.

### FW-04 — resolution

Δf = fs/N = 166.67/128 = **1.30 Hz**. A 2 Hz mode lands in bin 1 or 2 (error up to ±0.65 Hz = ±30 %). Target Δf ≈ 0.024 Hz: fs = 100 Hz, N = 4096 (40.96 s). Frequency accuracy of the interpolated peak is better than the bin width but is bounded by SNR and fs accuracy (FW-06).

### FW-06 — the sampling clock is not what the code assumes

Code writes `PWR_MGMT_1 = 0x00` → CLKSEL = 0 → internal relaxation oscillator.
MPU-6000/6050 Product Specification Rev 3.4, Table 6.6: clock initial tolerance **±5 %** (CLK_SEL = 0, 25 °C), variation over temperature **−15 % to +10 %**; with CLK_SEL = 1, 2, 3 (gyro PLL) ±1 %. §7.15 states the gyro reference gives a more accurate clock.
Consequence: every frequency you compute is scaled by the same unknown factor (several %), and it drifts with the bridge-side temperature during a session. For a thesis whose output *is* a frequency this is S1.
Fix: set CLKSEL = 1 (X-gyro PLL) **and** measure the true sample rate against the ESP32 crystal using INT-edge timestamps (`03` §4). Use the measured fs in Δf and f_k.

---

## C. Things that are fine (do not "fix")

- USB-C CC1/CC2 5.1 kΩ pull-downs (R3, R4) — correct for a sink [Certain].
- EN pull-up 10 kΩ + 1 µF — matches Espressif's recommended RC (datasheet §9). C6 (100 nF) in parallel is redundant but harmless.
- BOOT button on IO0 with 100 Ω series — fine.
- MPU CLKIN and FSYNC tied to GND, REGOUT 100 nF — correct per datasheet §7.1–7.3.
- VDD 3.3 V within the 2.375–3.46 V window; VLOGIC ≤ VDD at all times (both on +3V3).
- All three MPUs placed with identical orientation (rotation 0°) so axes are aligned across IMUs — required for averaging.
- No routed signals/vias under the MPU footprints; footprint has no exposed-pad land (datasheet: do not solder the die pad).
- AMS1117-3.3: dropout adequate at 5 V in; 22 µF tantalum on output provides ESR for stability [Likely — confirm against AMS1117 datasheet stability section].
- Native USB (IO19/IO20) used for programming/serial — no USB-UART needed.

---

## D. Fix priority and ordering

1. **Firmware-only fixes on V1 hardware** (no board change): FW-01, 02, 03, 04, 06, 07, 08, 09, 10 (with LittleFS short sessions), 11, 12, 14, 15, 16. Pin change for FW-11 is a constant.
2. **V1 rework (soldering)**: HW-01 (3 caps), HW-02 (remove 4 of the 6 I2C pull-ups: R11, R12, R15, R16 — see `05` §A), HW-03 (remove 6 resistors), HW-04 (optional bodge-wire INT).
3. **V2 respin**: HW-04…HW-08, PCB-01…PCB-03, PCB-06.

## E. Verification of each fix

| Fix | How to prove it worked |
|---|---|
| FW-01/02 | Hand-tap the node at rest: raw per-axis trace is non-zero (mg level), mean ≈ 0 after removal, no clamping to zero |
| FW-04/06 | Synthetic sine test + spring/pendulum bench test (`04` §9 T-01, T-04): reported f within ±1 bin and ±1 % of reference |
| FW-05 | No FIFO overflow in 30-min static run; sample-interval histogram within ±0.1 ms |
| HW-01 | Measure CPOUT cap value with LCR meter before/after; gyro stable (even though gyro unused) |
| HW-04 | Scope INT pulses ≈ 100 Hz, 50 µs wide (datasheet tINT, LATCH_INT_EN = 0) |
| PCB-01 | Fit-check + vibration coupling test: tap test shows single coherent peak across all 3 IMUs |


