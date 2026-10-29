# Implementation status - 2026-10-24

The user approved paper v2 and authorized this Arduino IDE prototype for ESP32-S3-WROOM-1-N16R8 and three MPU6050 ICs. The active estimator is exact N-point FFT maximum-bin selection; the earlier Welch/scaffold gate is superseded.

## Implemented

| Area | Current implementation | Evidence / remaining boundary |
|---|---|---|
| Arduino project | Matching .ino entry point and peer C++ modules | Integrated Arduino compile passed; see reports/FIRMWARE_PROTOTYPE_20261024.md |
| Sensor acquisition | Two I2C controllers, addresses 0x68/0x69/0x68, complete XYZ FIFO reads in sensor order 1,2,3, three DRDY queues | Register sources verified; electrical behavior and exact FIFO/edge association need bench evidence |
| Timing / QC | Per-sensor DRDY epochs, sample/scan indices, clipping, continuity, measured rate, interval and endpoint checks | Software paths implemented; physical ISR latency and tolerance need measurement |
| DSP | Mean removal, symmetric Hann, Bluestein exact N-point FFT, largest positive in-band magnitude bin, ten-window median | Native C++ versus independent NumPy spectrum/invalid-input checks passed; no device accuracy claim |
| Baselines | Separate traffic/sensor/axis session-level mean, sample SD, CV, descriptive +/-s and separate +/-2s review heuristic | Native statistics checks passed; real accepted formal sessions are not available |
| Session / storage | Fixed 600 s, ten 60 s windows, PSRAM capture, raw/CSV/JSON retention, payload CRC32, frozen setting hash | Synthetic replay/QC checks passed; full physical recording and power-interruption recovery remain |
| Traffic workflow | Concurrent manual tally, pilot nearest-rank cutoffs, frozen formal context, count finalization including retained pending records after reboot | Tools reject collapsed/empty groups and mixed context; no numeric field cutoffs invented |
| Dashboard | Adopted global dark UI, embedded HTTP assets, REST/polling, real readings, nine stream results | JS syntax/DOM source checks passed; no live-device browser test yet |
| Offline tools | Session replay, campaign statistics, traffic-cutoff derivation, independent numerical verification | Commands and scope in tools/README.md |
| Future hardware | Firmware pin/interface handoff only | User assigned schematic/PCB to Astra after prototype; BOM to Sol after hardware review |

## Actual verification

- Integrated source compiled with Arduino CLI 1.1.1, Espressif core 3.3.5 and ArduinoJson 7.4.2, generic ESP32-S3, 16 MB QIO flash, OPI PSRAM and custom partitions. Exact final sizes and source manifest are recorded in the report.
- Native MSVC C++ linked the actual dsp.cpp/baseline.cpp. Sixteen spectral/input cases passed against NumPy 2.3.5, plus scalar/statistics checks. Maximum normalized full-spectrum complex error was about 1.10e-7 under the 2e-6 numerical tolerance. See reports/math_verification.json.
- Synthetic 600-second raw replay and deliberate CRC, jitter and index-gap cases were checked; pilot cutoff/context checks were also run. These fixtures are not field data.
- No device was flashed, no physical electrical/known-frequency/600-second measurement was performed, and no research result or hardware accuracy is claimed.

## Prototype limits and next work

The principal PSRAM allocations total 6,688,144 bytes before other allocations. Capture remains in RAM until completion and persistence: a reset or power loss before then loses the session. At nominal rate, each raw payload is 5,760,000 bytes. Back up all three files before explicit raw purging; summaries remain for baseline replay. Automatic formatting/deletion is disabled.

The 0.5-20 Hz band, 100 Hz nominal rate, 500 us timing tolerance, +/-3% rate tolerance, all-ten-valid-window rule and five-session baseline display target are engineering/protocol settings requiring pilot evaluation. Five sessions is not a power calculation. Mean +/-2s is a review heuristic.

Start with PROTOTYPE_WORKFLOW.md and HARDWARE_INTERFACE.md. Astra's independent audit starts at ASTRA_REVIEW_BRIEF.md. Update this status and the verification report from actual prototype observations.
