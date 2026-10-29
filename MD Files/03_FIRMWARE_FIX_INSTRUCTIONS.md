# 03 — Firmware Fix Instructions (step by step)

Audience: the code agent. Do the steps **in order**; each ends with an acceptance test. Snippets are reference sketches — compile and test them; do not assume they are drop-in.

**Rules**
- Any register value marked *(verify)* comes from the MPU-6000/6050 Register Map (not fetched during the audit). Check it against the document before flashing: https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Register-Map1.pdf
- Values marked *(datasheet)* were read in the MPU-6000/6050 Product Specification Rev 3.4 (PS-MPU-6000A-00).
- Never reintroduce: vector magnitude, MAF smoothing, `MAX_RMS_G` intensity, startup offset calibration, "CRIT/anomaly" wording, auto-delete on download.

---

## Step 0 — Repo hygiene
1. Move current code to `firmware_legacy/` (read-only reference). New code goes to `firmware/` per `04_CODEBASE_PLAN.md`.
2. Add `.gitignore` entries: `.pio/`, `.vscode/`, `secrets.h`, `*.shmb`, `data_local/`.
3. Add `README.md` at repo root: purpose, build, hardware rev table, link to `docs/`.
4. Remove `.obsidian-vault/` from the **public** repo history or confirm it contains no private notes/keys (it was visible in the public tree).

## Step 1 — Hardware profile and pin map

Create `include/hw_profile.h` with two profiles selected by `-DSHM_HW_REV=1|2`.

```cpp
#pragma once
#if SHM_HW_REV == 1            // V1 board as built (Thesis.kicad_pcb)
  // Check module variant first: IO35/IO36 are NOT usable on R8 / R16V modules.
  #define PIN_SDA0   36
  #define PIN_SCL0   35
  #define N_I2C_BUSES 1
  #define IMU_USE_AD0_GATING 1                   // 3 IMUs on one bus, AD0 from GPIO
  static const int PIN_AD0[3]  = {4, 5, 6};      // U2->IO4, U4->IO5, U5->IO6 (see netlist)
  #define HAS_INT_LINES 0                        // INT not routed on V1
  #define HAS_SDCARD    0
#else                          // V2 board (see 05_SCHEMATIC_PCB_V2_SPEC.md)
  #define PIN_SDA0    8
  #define PIN_SCL0    9
  #define PIN_SDA1   15
  #define PIN_SCL1   16
  #define N_I2C_BUSES 2
  #define IMU_USE_AD0_GATING 0                   // AD0 hard-strapped
  static const int PIN_INT[3] = {4, 5, 6};
  #define HAS_INT_LINES 1
  #define HAS_SDCARD    1
  #define PIN_SD_CS   10
  #define PIN_SD_MOSI 11
  #define PIN_SD_SCK  12
  #define PIN_SD_MISO 13
  #define PIN_SD_CD   14
  #define PIN_LED_REC 38
#endif
```
V1 IMU mapping from the netlist: U2 AD0 → IO4 (`IMU-AD0X1`), U4 AD0 → IO5 (`IMU-AD0Y1`), U5 AD0 → IO6 (`IMU-AD0Z1`). Rename logically to IMU1/IMU2/IMU3 — **not** X/Y/Z (FW-12).

Acceptance: boot log prints rev, I2C scan, `WHO_AM_I == 0x68` for all 3 IMUs.

## Step 2 — Acquire per-axis acceleration; delete the magnitude path

Delete from the legacy code: `calibUpdate/Finish/Apply`, `mafUpdate`, the `sqrtf(fax²+…) − 1.0f` block, `computeIntensity`, `MAX_RMS_G`, `gRmsBuf`.

New data model (per IMU, per axis): `int16_t` raw counts, converted to g only in DSP (`/16384.0f` at ±2 g — *datasheet*).

```cpp
struct Sample3 { int16_t ax, ay, az; };    // 6 bytes — same layout as the MPU FIFO
```
Mean/gravity removal happens **per Welch segment, per axis** (Step 6). No global offset. The vertical axis is identified from the stationary pre-run (Step 5), only for labeling.

Acceptance: static board on a table → per-axis mean after removal ≈ 0 and RMS ≈ 2–4 mg (noise), never clamped.

## Step 3 — MPU-6050 configuration (FIFO, correct clock, defined filter)

Fixes FW-05, FW-06, FW-07. Sequence per IMU (select via AD0 on V1):

```cpp
static bool wr(uint8_t a, uint8_t r, uint8_t v){ Wire.beginTransmission(a); Wire.write(r); Wire.write(v); return Wire.endTransmission()==0; }
static bool rd(uint8_t a, uint8_t r, uint8_t* b, size_t n){
  Wire.beginTransmission(a); Wire.write(r); if (Wire.endTransmission(false)!=0) return false;
  if (Wire.requestFrom((int)a,(int)n,(int)true)!=(int)n) return false;
  for(size_t i=0;i<n;i++) b[i]=Wire.read(); return true; }

bool mpuBegin(uint8_t a){
  wr(a,0x6B,0x80); delay(100);        // PWR_MGMT_1: DEVICE_RESET
  wr(a,0x68,0x07); delay(100);        // SIGNAL_PATH_RESET (register 0x68, not the I2C address) (verify)
  wr(a,0x6B,0x01); delay(20);         // wake, CLKSEL=1 (X-gyro PLL) — NOT 0x00  (FW-06) (datasheet §7.15, Table 6.6)
  uint8_t who=0; if(!rd(a,0x75,&who,1) || who!=0x68) return false;   // WHO_AM_I
  wr(a,0x1A,0x04);                    // CONFIG: DLPF_CFG=4 -> accel BW ~21 Hz (verify)
  wr(a,0x19,9);                       // SMPLRT_DIV=9 -> 1 kHz/(1+9)=100 Hz with DLPF on (datasheet Table 6.6)
  wr(a,0x1C,0x00);                    // ACCEL_CONFIG: +/-2 g, 16384 LSB/g (datasheet Table 6.2)
  wr(a,0x23,0x00);                    // FIFO_EN: all off
  wr(a,0x6A,0x04);                    // USER_CTRL: FIFO_RESET (verify)
  wr(a,0x23,0x08);                    // FIFO_EN: ACCEL_FIFO_EN only (6 bytes/sample) (verify)
  wr(a,0x6A,0x40);                    // USER_CTRL: FIFO_EN (verify)
#if HAS_INT_LINES
  wr(a,0x37,0x00);                    // INT_PIN_CFG: active-high, push-pull, 50 us pulse
  wr(a,0x38,0x11);                    // INT_ENABLE: DATA_RDY(bit0)+FIFO_OFLOW(bit4) (verify)
#endif
  return true; }
```
Why each choice:
- **Gyros stay powered** and CLKSEL=1: the datasheet says the gyro-referenced clock is more accurate than the internal oscillator (CLKSEL=0: ±5 % initial, −15/+10 % over temperature; CLKSEL 1–3: ±1 %). Gyro current (3.6 mA) is irrelevant for a USB-powered node. Gyro data is simply not put into the FIFO.
- **DLPF ≈ 21 Hz + 100 Hz output** replaces the MAF. Do not add another low-pass.
- If you later change range/filter/rate, the change must go through `config` and be written into every session file (thesis §3.12).

Acceptance: `FIFO_COUNT` increases by ≈ 600 bytes/s (100 Hz × 6 B) per IMU.

## Step 4 — Timing: FIFO bursts + measured sampling rate

**Do not poll registers at 166.7 Hz.** Drain each IMU's FIFO every 200–250 ms (≤ 1024 B = 170 samples ≈ 1.7 s capacity).

Drain procedure (per IMU):
1. (V1) `selectSensor(i)` — AD0 LOW for the target, HIGH for others, wait ≥ 80 µs.
2. Read `FIFO_COUNT_H/L` (0x72/0x73). `n = (count/6)*6`.
3. Read `INT_STATUS` (0x3A); bit 4 = FIFO overflow → **mark a gap**, reset FIFO (`0x6A=0x04` then `0x40`), discard overlapping Welch segments.
4. Read `n` bytes from `FIFO_R_W` (0x74) in chunks ≤ 126 B (Arduino `Wire` buffer is 128 B by default; chunk = 21 samples).
5. Push `Sample3[]` into the acquisition ring with the batch's `esp_timer_get_time()` and cumulative sample index.

**Measured fs (fixes FW-06 residual error):** for each IMU keep `(t_us, produced)` pairs where `produced = consumed + remaining_in_FIFO/6` at the instant `FIFO_COUNT` was read. Least-squares slope of `produced` vs `t` over the session = true fs (ESP32 module crystal is ±10 ppm, per Espressif schematic). Use this `fs_est` in Δf = fs/N and f_k = k·fs/N (thesis Eq. 1–2). Report `fs_est` per IMU in `summary.json`; QC rule: `|fs_est − 100|/100 ≤ 3 %` else investigate.

V2 (INT wired): additionally timestamp DATA_RDY edges in an IRAM ISR (`esp_timer_get_time()`), use for jitter statistics; FIFO still carries the data.

Replace `millis()` timestamps with `esp_timer` µs and a sample index.

Acceptance: 30-min static run → zero overflow gaps; `fs_est` stable to better than ±0.05 Hz between runs [Likely achievable; confirm].

## Step 5 — Pre-run checks (thesis §3.6)

Before every session, `PRECHECK` state, 10 s stationary record per IMU:
- `WHO_AM_I` OK, FIFO alive, no overflow.
- Clipping: `|raw| ≥ 32000` count = 0.
- Mean vector magnitude within 1 g ± 0.15 g (sanity only — mounting tilt/bias allowed). Vertical axis = axis with the largest |mean|. Store gravity vector.
- Noise RMS per axis below a ceiling (`NOISE_RMS_MAX_G`, **placeholder 0.02 g — set from bench test**).
- Optional: MPU self-test registers (0x0D–0x10) per Product Spec §7.12 / Register Map; log pass/fail.
Result stored in `precheck.json`. Failure blocks session start (operator may override with a logged reason).

## Step 6 — DSP: Welch PSD, per axis, per IMU

Parameters (frozen in `config.h`, copied into every session): `FS_NOMINAL=100`, `WELCH_N=4096`, `WELCH_HOP=2048`, window = Hann, `BAND_LO_HZ=0.5` and `BAND_HI_HZ=20.0` (**placeholders — freeze after pilot**, thesis §3.9 requires the band to be fixed before analysis).

Per completed segment (4096 samples, no gap inside):
```
x[i] = raw[i] / 16384.0f           // g
x   -= mean(x)                      // removes gravity + bias per axis (thesis §3.9 "removal of the DC component")
x[i]*= hann[i]
X    = FFT(x)                       // esp-dsp fc32 radix-2, in place
Pxx[k] = |X[k]|^2 / (fs_est * sum(w^2))        // one-sided: multiply 1..N/2-1 by 2
acc[imu][axis][k] += Pxx[k]; nseg[imu][axis]++
```
Use the **ESP-DSP** library (https://github.com/espressif/esp-dsp; `dsps_fft2r_init_fc32`, `dsps_fft2r_fc32`, `dsps_bit_rev_fc32` — confirm exact names/signatures in its docs). Do not use `arduinoFFT` with `double` at N=4096 (≈ 64 KB per array, slow). Cost: 9 FFTs per hop (20.5 s) — trivial.

Node spectrum per axis: `P_axis[k] = mean over the 3 IMUs of (acc/nseg)`. **Average power spectra, not time signals** — the three IMUs have independent sample clocks (not synchronized), so time-domain averaging is invalid without alignment.

Peak pick (fixed rule, thesis §3.9): `k* = argmax P_axis[k]` for `k` with `BAND_LO ≤ k·Δf ≤ BAND_HI` (bin 0 excluded). Parabolic interpolation on log power:
```
α=log10(P[k*-1]) β=log10(P[k*]) γ=log10(P[k*+1])
δ = 0.5*(α-γ)/(α-2β+γ);   f_d = (k*+δ)·Δf,   Δf = fs_est/N
```
Also output: `peak_snr_db = 10·log10(P[k*] / median(P[band]))`, per-IMU `f_d`, `n_segments`. QC: if `peak_snr_db < SNR_MIN_DB` (**placeholder 6 dB**) → `f_d` flagged `NO_VALID_PEAK` (expected during near-zero traffic; record, don't hide).

Live preview (not for the thesis result): sliding Welch N=1024 (Δf ≈ 0.1 Hz), update every ≈ 2 s; UI labels it "preview".

Acceptance: T-01 (synthetic sines) and T-04 (bench oscillator) in `04_CODEBASE_PLAN.md` §9.

## Step 7 — Logging and storage (fixes FW-10)

- **Never write CSV rows per sample.** Write binary blocks (`04` §6): header + `Sample3[]`, 16–32 KB buffered, written by a separate low-priority task so flash/SD stalls cannot delay the sampler (the FIFO is the shock absorber).
- V2: microSD (`/sessions/<id>/raw.shmb`, `meta.json`, `summary.json`, `qc.json`).
- V1 (no SD): LittleFS with a custom partition table (Q2: confirm flash size). Example for **8 MB** flash:
```
# Name,    Type, SubType, Offset,   Size
nvs,       data, nvs,     0x9000,   0x5000
phy_init,  data, phy,     0xe000,   0x1000
factory,   app,  factory, 0x10000,  0x200000
littlefs,  data, spiffs,  0x210000, 0x5F0000
```
Raw volume: 100 Hz × 3 IMU × 6 B = 1.8 KB/s ≈ 1.08 MB per 10-min session → V1 holds ~5 sessions between downloads. Export after every field day.
- `/api/sessions/<id>/raw` streams the file with `Content-Length`; **deletion only via an explicit `DELETE` endpoint with a confirm token**. Never auto-delete on download.

## Step 8 — Baseline and wording (fixes FW-08, TH-05)

- Remove the 10-second idle-RMS "baseline". Baseline = aggregation of **accepted sessions' f_d** per axis: `n`, mean `x̄`, sample SD `s` (n−1), `CV = s/x̄·100`, min, max — per traffic level and pooled (thesis Eq. 3–4).
- Flag rule: report both `x̄ ± s` (descriptive, thesis Eq. 3) and an alert band `x̄ ± k·s` with configurable `k` (default 2). Rationale: under normality `x̄ ± s` contains only ≈ 68 % of ordinary readings, so ≈ 32 % of normal sessions would be flagged [Certain, arithmetic].
- UI states, exactly: `NO BASELINE YET`, `PROVISIONAL (n<5)`, `WITHIN BASELINE`, `OUTSIDE BASELINE – REVIEW`. Forbidden strings anywhere in firmware/UI: `CRIT`, `critical`, `damage`, `anomaly`, `failure`, `unsafe`, `safe`. Add a CI grep check.
- Outliers are never auto-removed; only technical-cause exclusions with a reason code (thesis §3.13).

## Step 9 — Session state machine

`IDLE → PRECHECK → ARMED → RECORDING → FINALIZING → DONE` (+ `ABORTED`). `RECORDING` length fixed (`SESSION_LEN_S`, default 600; pilot may adjust). Inputs from the web UI: traffic level (`NEAR_ZERO|MEDIUM|HEAVY`), vehicle count method/value (manual entry after the session), weather note, operator, free-text event note, and the **phone's epoch time** (the AP has no internet; the node sets its clock from the browser). Details: `04` §5.

## Step 10 — Config, security, build

- Wi-Fi SSID/password in NVS (default SSID `SHM-<last 4 of MAC>`, WPA2, password generated and printed on serial at first boot). No credentials in git.
- `platformio.ini` (starting point; verify board/flash settings for your module — *Likely*):
```ini
[env:shm]
platform = espressif32
board = esp32-s3-devkitc-1
framework = arduino
board_build.filesystem = littlefs
board_build.partitions = partitions.csv
board_upload.flash_size = 8MB
monitor_speed = 115200
build_flags = -DSHM_HW_REV=1 -DARDUINO_USB_MODE=1 -DARDUINO_USB_CDC_ON_BOOT=1 -DCORE_DEBUG_LEVEL=1
lib_deps = bblanchon/ArduinoJson
```
- Firmware version string `SHM_FW_VERSION` (git describe) written to every session; `config_hash` = CRC32 of frozen settings.

## Keep / drop summary

| Keep (idea only) | Drop |
|---|---|
| ESP32 SoftAP + local web server | Three.js ripple fabric and its arbitrary freq→speed mapping |
| FreeRTOS tasks pinned per core | Vector magnitude, MAF, intensity, RMS-gated alarms |
| JSON `/data`-style live endpoint (new schema) | CSV-per-sample logging, auto-delete on download |
| LittleFS as V1 fallback storage | Startup offset calibration, 10-s idle "baseline" |
