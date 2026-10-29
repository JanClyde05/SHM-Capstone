# 04 — New Codebase Plan (SHM-Capstone v2)

Goal: a repository where every thesis claim in Chapter III maps to a module, a test, and a stored artifact. Build on PlatformIO (Arduino-ESP32 + ESP-DSP). Offline analysis in Python.

## 1. Repository structure

```
SHM-Capstone/
├─ README.md
├─ AGENTS.md                         # agent briefing (copy from docs/)
├─ docs/                             # this documentation set (00…07)
├─ firmware/
│  ├─ platformio.ini
│  ├─ partitions.csv
│  ├─ include/
│  │  ├─ hw_profile.h                # pin maps for HW rev 1 / 2
│  │  ├─ config.h                    # FROZEN analysis settings (fs, N, hop, band, QC thresholds)
│  │  └─ version.h                   # SHM_FW_VERSION, CONFIG_HASH
│  ├─ src/
│  │  └─ main.cpp                    # setup(): init modules, create tasks. No logic here.
│  ├─ lib/
│  │  ├─ imu_mpu6050/                # driver: begin(), drainFifo(), selfTest(), selectSensor()
│  │  ├─ acquisition/                # task, FIFO drain scheduler, ring buffer, fs estimator, gap tracking
│  │  ├─ dsp/                        # hann, welch accumulator, peak picker, snr, live preview
│  │  ├─ session/                    # state machine, metadata, precheck, QC verdict
│  │  ├─ storage/                    # raw writer (SD or LittleFS), json writers, file index
│  │  ├─ baseline/                   # per-level + pooled stats, flagging
│  │  ├─ timebase/                   # esp_timer, epoch from phone, sample index <-> time
│  │  ├─ net/                        # SoftAP, WebServer, REST handlers, streaming download
│  │  └─ util/                       # crc32, ring_buffer, logging, result codes
│  ├─ data/                          # web UI (served from LittleFS): index.html, app.js, style.css, uplot.min.js
│  └─ test/
│     ├─ test_dsp_native/            # Unity tests on PC: synthetic sines, band/peak/interp
│     ├─ test_baseline_native/
│     └─ test_session_native/
├─ tools/                            # Python (offline)
│  ├─ requirements.txt               # numpy scipy pandas matplotlib statsmodels scikit-posthocs
│  ├─ decode_shmb.py                 # binary -> numpy / CSV
│  ├─ analyze_session.py             # reference Welch -> must match firmware within tolerance
│  ├─ analyze_campaign.py            # all sessions -> baseline stats, ANOVA / Kruskal-Wallis, figures
│  ├─ make_synthetic.py              # test vectors with known frequencies
│  └─ qc_report.py                   # per-session QC table (reason codes)
├─ hardware/
│  ├─ rev1/                          # existing KiCad files + gerbers (frozen)
│  ├─ rev2/                          # new KiCad project (see 05)
│  ├─ bom/                           # BOM csv + datasheet links
│  └─ mechanical/                    # enclosure / mount drawings
├─ field/
│  ├─ log_sheet_template.csv         # traffic + weather + vehicle count + notes
│  └─ session_checklist.md
└─ thesis/
   └─ chapter3_sync.md               # list of manuscript edits driven by the final design
```

## 2. Module responsibilities and interfaces

| Module | Owns | Public interface (sketch) | Never does |
|---|---|---|---|
| `imu_mpu6050` | Register access, FIFO drain, AD0 gating (V1) | `bool begin(i)`, `size_t drain(i, Sample3*, max, bool& overflow)`, `bool selfTest(i)` | DSP, timing policy |
| `acquisition` | Scheduling of drains, ring buffers, gap log, `fs_est` per IMU | `start()`, `stop()`, `pop(i, Sample3*, n)`, `fsEstimate(i)`, `gaps(i)` | Spectral analysis |
| `dsp` | Welch, peak pick, SNR, preview | `WelchAccum::push(seg)`, `Peak pick(psd, df, band)`, `Preview::update()` | I/O, Wi-Fi |
| `session` | State machine, metadata, QC verdict | `begin(meta)`, `tick()`, `abort(reason)`, `result()` | Raw sample handling |
| `storage` | Files, formats | `RawWriter::open(sessionId)`, `write(block)`, `close()`, `listSessions()` | Deleting without confirm |
| `baseline` | Stats per level + pooled, flags | `add(sessionSummary)`, `get(level)`, `classify(f_d)` | Damage wording |
| `net` | AP, HTTP, JSON | route table in §7 | Business logic |

Dependencies point downward only: `net → session → {acquisition, dsp, storage, baseline} → imu/util`. `dsp` and `baseline` have **no Arduino includes** so they can run in native tests.

## 3. Task/core layout (ESP32-S3, 2 cores)

| Task | Core | Prio | Period | Notes |
|---|---|---|---|---|
| `acq` | 1 | 5 | 200–250 ms | Drains 3 FIFOs, updates `fs_est`; stack 4 KB |
| `dsp` | 1 | 3 | event (segment ready) | Welch update, peak pick, live preview |
| `store` | 1 | 2 | event | Drains raw queue to SD/LittleFS, 16–32 KB buffers |
| `net` | 0 | 2 | — | WebServer + Wi-Fi (default Wi-Fi tasks live on core 0) |
| `session` | 0 | 2 | 100 ms | State machine, timers |

Queues: `rawQ` (acq → store), `segQ` (acq → dsp). Sizing rule: ≥ 3 s of data for `rawQ` so an SD stall cannot cause loss. Shared results use a mutex-protected snapshot struct (fixes FW-03).

## 4. `config.h` — frozen analysis settings (copied into every session)

```cpp
#define FS_NOMINAL_HZ      100
#define DLPF_CFG           4         // ~21 Hz accel bandwidth (verify in register map)
#define ACCEL_RANGE_G      2
#define WELCH_N            4096
#define WELCH_HOP          2048
#define WINDOW_TYPE        "hann"
#define BAND_LO_HZ         0.5f      // PLACEHOLDER - freeze after pilot, then git tag analysis-freeze-v1
#define BAND_HI_HZ         20.0f     // PLACEHOLDER
#define SNR_MIN_DB         6.0f      // PLACEHOLDER
#define NOISE_RMS_MAX_G    0.02f     // PLACEHOLDER (bench)
#define CLIP_RAW_LIMIT     32000
#define FS_TOL_FRACTION    0.03f
#define SESSION_LEN_S      600       // may change after pilot
#define BASELINE_K         2.0f
#define MIN_SESSIONS_FINAL 5         // thesis §3.5
```
`CONFIG_HASH = CRC32(all of the above + firmware version)`; stored in every session.

## 5. Session lifecycle and metadata

States: `IDLE → PRECHECK → ARMED → RECORDING → FINALIZING → DONE` (+ `ABORTED`).
`meta.json` written at start (immutable):
```json
{
  "session_id": "S-20261104-0630-N",
  "traffic_level": "NEAR_ZERO",
  "start_epoch_utc": 1793764200,
  "start_epoch_source": "browser",
  "operator": "JC",
  "site": "Buntun Bridge",
  "mount": {"member": "TBD", "span": "TBD", "orientation": "X=longitudinal,Y=transverse,Z=vertical"},
  "hw_rev": 1, "fw_version": "v2.0.0-<git>", "config_hash": "0x1A2B3C4D",
  "settings": {"fs_nominal": 100, "dlpf_cfg": 4, "range_g": 2, "welch_n": 4096, "hop": 2048,
               "band_hz": [0.5, 20.0], "snr_min_db": 6.0},
  "weather": {"note": "", "temp_c": null, "humidity_pct": null, "wind": ""},
  "traffic_observation": {"method": "manual_tally|video", "veh_per_min": null, "heavy_vehicle_count": null, "notes": ""}
}
```
`summary.json` written at finalize:
```json
{
  "session_id": "...", "duration_s": 600.0, "valid": true, "qc_reason": [],
  "imu": [{"id":1,"fs_est":100.03,"gaps":0,"clip_count":0,"fd":{"x":0.0,"y":0.0,"z":0.0}}, {...}, {...}],
  "node": {"axis": {"x": {"f_d": 0.0, "snr_db": 0.0, "valid_peak": true},
                    "y": {...}, "z": {...}}},
  "vertical_axis": "z", "n_segments": 28, "peak_agreement_hz": 0.03
}
```
QC reason codes: `PRECHECK_FAIL`, `CLIPPING`, `FIFO_GAP`, `FS_OUT_OF_TOL`, `NO_VALID_PEAK` (informational, not an exclusion by itself), `SENSOR_DETACH`, `COMM_FAIL`, `OPERATOR_ABORT`, `OTHER_<text>`. Every excluded session keeps its files and a reason (thesis §3.13).

## 6. Raw file format `.shmb` (little-endian)

```
File header (64 B):
  magic "SHMB" | u16 version=1 | u16 header_len | u8 hw_rev | u8 n_imu=3 | u8 axes=3 | u8 bytes_per_sample=2
  f32 fs_nominal | f32 fs_est[3] | u64 start_epoch_us | u32 config_hash | char session_id[24] | reserved
Block (repeated):
  u32 block_magic 0xB10C | u8 imu_id | u8 flags (bit0 = gap_before) | u16 n_samples
  u64 t_us_first (esp_timer) | u32 sample_index_first | i16 data[n_samples*3]  (ax,ay,az)
  u32 crc32
```
`tools/decode_shmb.py` must round-trip it (test T-06).

## 7. REST API (served by `net`)

| Method | Path | Body / returns |
|---|---|---|
| GET | `/api/status` | state, time, fw, hw, free storage, per-IMU health |
| POST | `/api/time` | `{epoch}` from browser (also sent inside `session/start`) |
| POST | `/api/session/precheck` | runs Step-5 checks, returns verdict |
| POST | `/api/session/start` | meta fields in §5 → `session_id` |
| POST | `/api/session/stop` | finalize now |
| GET | `/api/live` | preview spectrum (≤ 256 points), current `f_d`, trace of last 120 `f_d`, per-IMU status |
| GET | `/api/sessions` | list with level, valid flag, f_d, size |
| GET | `/api/sessions/<id>/summary` | summary.json |
| GET | `/api/sessions/<id>/raw` | streamed `.shmb`, `Content-Length` set |
| DELETE | `/api/sessions/<id>?confirm=<token>` | explicit delete only |
| GET | `/api/baseline` | stats per level + pooled, state label |

## 8. Web UI (replaces Three.js ripple)

Static files in `data/`, no CDN dependency (AP has no internet). Charting: **uPlot** (small, MIT) copied into `data/`. Screens:
1. **Live:** spectrum preview (log-y), dominant-frequency readout, f_d trace with baseline band shaded (`x̄ ± s` and `x̄ ± k·s`), per-IMU agreement indicator.
2. **Session:** form (traffic level buttons NEAR_ZERO/MEDIUM/HEAVY, weather, notes), Precheck result, Start/Stop, countdown, QC flags.
3. **Data:** session list, download raw/summary, explicit delete.
4. **Baseline:** table per level (n, mean, s, CV) with `PROVISIONAL (n<5)` labels.
Wording rule from `03` Step 8 applies. Optional (later): keep a 3-D "node tilt/attitude" visual only if clearly labeled decorative.

## 9. Test plan

| ID | Test | Where | Pass criterion |
|---|---|---|---|
| T-01 | Synthetic sines (1.0, 2.5, 7.3 Hz) + white noise at SNR 0/6/12 dB through `dsp` | native Unity + Python reference | `f_d` error ≤ 0.5·Δf (≈ 0.012 Hz) at SNR ≥ 6 dB; identical to `analyze_session.py` within 1e-3 Hz |
| T-02 | FIFO drain with injected overflow | HW / mock | gap flagged, segments overlapping gap excluded |
| T-03 | 30-min static recording | HW | 0 gaps; `fs_est` within ±3 % of 100 Hz; noise floor PSD recorded as the **noise-floor reference** |
| T-04 | Known-frequency bench source: IMU on spring/pendulum (≈ 1–3 Hz) and small motor/speaker source (≈ 5–15 Hz) with reference by video or tachometer | bench | `f_d` within ±1 % of reference; 10 repeats → CV reported (supports thesis §3.12) |
| T-05 | Baseline math on synthetic session sets | native | mean/s/CV match NumPy; classification boundaries correct |
| T-06 | `.shmb` round-trip + CRC corruption | native + Python | decode == original; corrupted block detected |
| T-07 | UI form validation, traffic level required | browser | cannot start without level |
| T-08 | Live page renders on phone (Android Chrome / iOS Safari) over the AP | field | updates ≥ 0.5 Hz, no console errors |
| T-09 | Mount coupling: tap test | HW | all 3 IMUs show the same dominant tap-decay frequency (±1 bin) |
| T-10 | Power: 2 h on a power bank | HW | no reset; bank does not auto-shut-off |
| T-11 | Wording lint | CI | grep for forbidden strings = 0 |

## 10. Milestones (each ends in a tagged commit and a short test report)

| M | Deliverable | Hardware | Acceptance |
|---|---|---|---|
| M0 | Repo restructure, README, legacy moved | any | builds empty skeleton |
| M1 | `imu_mpu6050` + `acquisition` (FIFO, fs_est, gaps) | V1 | T-02, T-03 |
| M2 | `dsp` + native tests + Python reference | none/V1 | T-01 |
| M3 | `session` + `storage` + `.shmb` | V1 (LittleFS) | T-06, 1 full 10-min session stored |
| M4 | `baseline` + `net` + UI | V1 | T-05, T-07, T-08 |
| M5 | Bench validation, noise floor, **pilot at bridge** → freeze band/QC | V1 | `analysis-freeze-v1` git tag |
| M6 | V2 firmware profile (INT, 2 buses, SD) | V2 | T-02 on V2, T-10 |
| M7 | Campaign scripts, figures for Chapter IV | any | reproduces `summary.json` stats from raw |

## 11. Definition of done for the codebase
- Every Chapter III step maps to a module (table in `01` §6) and has a passing test.
- A third person can clone the repo, run `pio run`, flash, and reproduce a session summary from a provided raw file using `tools/analyze_session.py` (replicability, thesis Ch. III intro).
- No forbidden wording; no secrets; CI green.
