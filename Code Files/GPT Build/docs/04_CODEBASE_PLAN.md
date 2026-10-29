> **Historical snapshot - superseded 2026-10-24.** The user approved paper v2 and authorized Arduino IDE firmware for ESP32-S3-WROOM-1-N16R8 with three MPU6050 ICs. The active FFT method, hardware map, traffic protocol and verification status are in APPROVED_METHOD.md, HANDOFF.md, PROJECT_MAP.md and IMPLEMENTATION_STATUS.md. Older Welch, PlatformIO, old GPIO, estimator-open, collection and scaffold instructions below are retained only as history.

# 04 — New Codebase Plan (SHM-Capstone v2)

> **Latest user decisions (2026-10-24):** These decisions supersede older conflicting proposals in this document set. Use the three traffic groups NEAR_ZERO, MEDIUM, and HEAVY. Poll three triaxial sensors in order, reading one complete X/Y/Z frame from sensor 1, then 2, then 3, and repeat. Preserve each sensor stream; attach a polling-cycle ID, per-frame timestamp, and per-sensor sample index. Frames are sequential, not simultaneous. For baselines, report mean ± sample SD as a descriptive band and separately use mean ± 2 sample SD as the default heuristic review band; do not call the latter a formal 95% interval. DSP must be mathematically specified and reproducible. FFT versus Welch remains an open estimator decision; see docs/RESEARCH_ALIGNMENT_REVIEW.md for the implementation gate and paper-edit map.

> **Local user amendment:** Build and open firmware with Arduino IDE; do not use PlatformIO. Follow ARDUINO_IDE_AND_UI_STANDARD.md. The user confirmed three sequential triaxial sensor slots and traffic groups NEAR_ZERO/MEDIUM/HEAVY. The baseline reports mean ± s descriptively and uses mean ± 2s as a separate heuristic review band. Preserve per-sensor streams and timestamps; do not assume synchronous samples or average/fuse without a validated method. The exact estimator (FFT or Welch) is the only research-method decision still open; see RESEARCH_ALIGNMENT_REVIEW.md.

Goal: a repository where every thesis claim in Chapter III maps to a module, a test, and a stored artifact. Use Arduino IDE with the ESP32 Arduino core. Offline analysis in Python.

## 1. Repository structure

```
SHM-Capstone/
├─ README.md
├─ AGENTS.md                         # agent briefing (copy from docs/)
├─ docs/                             # this documentation set (00…07)
├─ firmware/
│  └─ SHM_Capstone/                  # Open this folder's matching .ino in Arduino IDE
│     ├─ SHM_Capstone.ino            # setup() and loop() only
│     ├─ app.cpp / app.h             # module composition and update order
│     ├─ hardware_profile.h          # revision selection; verified pin map added later
│     ├─ config.h                    # analysis settings and freeze marker
│     ├─ version.h                   # SHM_FW_VERSION and later CONFIG_HASH
│     ├─ imu_mpu6050.cpp / .h        # driver: begin(), drainFifo(), selfTest()
│     ├─ acquisition.cpp / .h        # drain scheduler, rings, fs estimator, gap tracking
│     ├─ dsp.cpp / .h                # selected estimator, peak picker, SNR/QC, live preview
│     ├─ session.cpp / .h            # state machine, metadata, precheck, QC verdict
│     ├─ storage.cpp / .h            # raw writer, JSON writers, file index
│     ├─ baseline.cpp / .h            # per-level + pooled stats, flagging
│     ├─ timebase.cpp / .h            # monotonic time, browser epoch mapping
│     ├─ wifi_manager.cpp / .h        # SoftAP and credentials
│     ├─ web_server.cpp / .h          # HTTP routes and streaming downloads
│     └─ data/                        # offline LittleFS UI: HTML, CSS, JavaScript
├─ tools/                            # Python (offline)
│  ├─ requirements.txt               # numpy scipy pandas matplotlib statsmodels scikit-posthocs
│  ├─ decode_shmb.py                 # binary -> numpy / CSV
│  ├─ analyze_session.py             # reference estimator -> must match the selected firmware method within tolerance
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
| acquisition | Round-robin reads (one XYZ frame from sensor 1, then 2, then 3), per-frame timestamp/index/cycle ID, rings, measured per-sensor rate/skew, gap log | start(), stop(), pop(sensor, Sample3*, n), fsEstimate(sensor), gaps(sensor) | Spectral analysis |
| dsp | Finalized FFT or Welch estimator, peak rule, units, QC, preview; must match the thesis and Python reference | Interface chosen after estimator definition | I/O, Wi-Fi |
| `session` | State machine, metadata, QC verdict | `begin(meta)`, `tick()`, `abort(reason)`, `result()` | Raw sample handling |
| `storage` | Files, formats | `RawWriter::open(sessionId)`, `write(block)`, `close()`, `listSessions()` | Deleting without confirm |
| `baseline` | Stats per level + pooled, flags | `add(sessionSummary)`, `get(level)`, `classify(f_d)` | Damage wording |
| `timebase` | Monotonic timestamps and browser epoch mapping | `nowUs()`, `setEpoch(epoch)` | Sampling scheduling |
| `wifi_manager` | SoftAP lifecycle and credentials | `begin()`, `isReady()` | HTTP routes and session business logic |
| `web_server` | Static UI, HTTP, JSON | route table in §7 | Session business logic |

Dependencies point downward only: `web_server → {session, storage, baseline}`; `session → {acquisition, dsp, storage, timebase}`; `acquisition → imu_mpu6050`. `wifi_manager` owns the AP and is called by the application composition layer. `dsp` and `baseline` have **no Arduino includes** so they can run in native tests.

## 3. Task/core layout (ESP32-S3, 2 cores)

| Task | Core | Prio | Period | Notes |
|---|---|---|---|---|
| acquisition task | 1 | 5 | round-robin cycle | Sequentially reads one XYZ frame from sensor 1, then 2, then 3; stamps every frame; updates per-sensor rate/skew and gap state |
| DSP task | 1 | 3 | event (analysis input ready) | Runs only the estimator selected and fully defined in the research method; updates peak/QC outputs |
| `store` | 1 | 2 | event | Drains raw queue to SD/LittleFS, 16–32 KB buffers |
| `web` | 0 | 2 | — | WebServer; Wi-Fi support tasks use core 0 |
| `session` | 0 | 2 | 100 ms | State machine, timers |

Queues: `rawQ` (acq → store), `segQ` (acq → dsp). Sizing rule: ≥ 3 s of data for `rawQ` so an SD stall cannot cause loss. Shared results use a mutex-protected snapshot struct (fixes FW-03).

## 4. Configuration (all analysis choices remain provisional until method selection and pilot freeze)

```cpp
#define FS_NOMINAL_HZ      100
#define DLPF_CFG           4         // ~21 Hz accel bandwidth (verify in register map)
#define ACCEL_RANGE_G      2
#define WELCH_N            4096  // proposal only; use only if Welch is selected
#define WELCH_HOP          2048  // proposal only; use only if Welch is selected
#define WINDOW_TYPE        "hann"  // proposal only; define normalization if selected
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

> Summary records must preserve the result for each sensor and axis. Do not emit an averaged node result until an aggregation method is explicitly defined and validated. The example summary fields below are illustrative only; revise them to include cycle/time metadata and the selected estimator.

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
  "settings": {"fs_nominal": 100, "analysis_method": "TBD", "analysis_parameters": "record exact frozen parameters"},
  "weather": {"note": "", "temp_c": null, "humidity_pct": null, "wind": ""},
  "traffic_observation": {"method": "manual_tally|video", "veh_per_min": null, "heavy_vehicle_count": null, "notes": ""}
}
```
`summary.json` written at finalize:
```json
{
  "session_id": "...", "duration_s": 600.0, "valid": true, "qc_reason": [],
  "imu": [{"id":1,"fs_est":100.03,"gaps":0,"clip_count":0,"fd":{"x":0.0,"y":0.0,"z":0.0}}, {...}, {...}],
  "session_level_aggregation": null, "aggregation_status": "NOT_DEFINED",
  "vertical_axis": "z", "cycle_count": 0
}
```
QC reason codes: `PRECHECK_FAIL`, `CLIPPING`, `FIFO_GAP`, `FS_OUT_OF_TOL`, `NO_VALID_PEAK` (informational, not an exclusion by itself), `SENSOR_DETACH`, `COMM_FAIL`, `OPERATOR_ABORT`, `OTHER_<text>`. Every excluded session keeps its files and a reason (thesis §3.13).

## 6. Raw file format concept (final binary layout is not frozen)

Use a versioned session file with a header containing magic/version, verified hardware and firmware identifiers, sensor count, axis count, nominal configuration, per-sensor measured-rate metadata, session start mapping, and configuration hash. Store independently timestamped frame records containing at minimum: sensor ID, cycle ID, per-sensor sample index, monotonic timestamp, X/Y/Z values, and quality/gap flags. Record units and scaling in the format metadata. Define byte order, field widths, CRC scope, gap semantics, and decoder together before implementation. Round-trip decoder validation is required when the format is implemented.

The earlier fixed 64-byte header/block proposal is not final because it does not yet define the user's required cycle association and timestamp semantics.


## 7. REST API (served by `web_server` over the AP managed by `wifi_manager`)

| Method | Path | Body / returns |
|---|---|---|
| GET | `/api/status` | state, time, fw, hw, free storage, per-IMU health |
| POST | `/api/time` | `{epoch}` from browser (also sent inside `session/start`) |
| POST | `/api/session/precheck` | runs Step-5 checks, returns verdict |
| POST | `/api/session/start` | meta fields in §5 → `session_id` |
| POST | `/api/session/stop` | finalize now |
| GET | /api/live | preview plus per-sensor/per-axis results and timestamps; no aggregate result until a method is defined |
| GET | /api/sessions | list with traffic level, valid flag, per-sensor/per-axis summary reference, size |
| GET | /api/sessions | list with traffic level, valid flag, per-sensor/per-axis summary reference, size |
| GET | /api/sessions | list with traffic level, valid flag, per-sensor/per-axis summary reference, size |
| DELETE | `/api/sessions/<id>?confirm=<token>` | explicit delete only |
| GET | /api/baseline | per-level per-sensor/per-axis descriptive x̄ ± s, separate x̄ ± 2s heuristic review limits; pooled summary optional |

## 8. Web UI (replaces Three.js ripple)

Static files in `firmware/SHM_Capstone/data/`, no CDN dependency (AP has no internet). The current scaffold uses a small canvas spectrum preview and does not bundle uPlot. This list describes the WP4 target; the current front end does not yet have a live API, frequency-history trace, baseline shading, or a working session backend. Screens:
1. **Live:** spectrum preview (log-y), per-sensor dominant-frequency readout, f_d trace showing descriptive and review bands (`x̄ ± s` and `x̄ ± 2s`), per-sensor availability and timestamp-skew display; any agreement/correlation metric requires a defined time-alignment method.
2. **Session:** form (traffic level buttons NEAR_ZERO/MEDIUM/HEAVY, weather, notes), Precheck result, Start/Stop, countdown, QC flags.
3. **Records:** session list, download raw/summary, explicit delete.
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
| M0 | Repo restructure, README, legacy moved | any | Arduino IDE sketch organization complete; build acceptance recorded only after an IDE build |
| M1 | `imu_mpu6050` + `acquisition` (FIFO, fs_est, gaps) | V1 | T-02, T-03 |
| M2 | `dsp` + native tests + Python reference | none/V1 | T-01 |
| M3 | `session` + `storage` + `.shmb` | V1 (LittleFS) | T-06, 1 full 10-min session stored |
| M4 | `baseline` + `net` + UI | V1 | T-05, T-07, T-08 |
| M5 | Bench validation, noise floor, **pilot at bridge** → freeze band/QC | V1 | `analysis-freeze-v1` git tag |
| M6 | V2 firmware profile (INT, 2 buses, SD) | V2 | T-02 on V2, T-10 |
| M7 | Campaign scripts, figures for Chapter IV | any | reproduces `summary.json` stats from raw |

## 11. Definition of done for the codebase
- Every Chapter III step maps to a module (table in `01` §6) and has a passing test.
- A third person can open the matching `.ino` in Arduino IDE, build and flash for the verified module, and reproduce a session summary from a provided raw file using `tools/analyze_session.py` (replicability, thesis Ch. III intro).
- No forbidden wording; no secrets; CI green.






