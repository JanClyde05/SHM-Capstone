# Legacy program behavior and migration notes

This note describes the preserved source snapshot in `../firmware_legacy/`. It records what the old program attempted to do. The current contract is in `APPROVED_METHOD.md`, `HANDOFF.md` and `PROJECT_MAP.md`; numbered audit/plan documents are historical.

## Legacy files

| File | What it contains |
|---|---|
| `firmware_legacy/firmware/SHM_Main.ino` | Arduino setup, sensor reads, FreeRTOS tasks, LittleFS CSV, access point, HTTP handlers |
| `firmware_legacy/firmware/Calculations.h` | Startup calibration, per-axis moving average, RMS, short FFT, normalized intensity |
| `firmware_legacy/firmware/WebServerUI.h` | Embedded HTML/CSS/JS dashboard, Three.js fabric animation, tables, state badges |
| `firmware_legacy/data/three.min.js` | Bundled Three.js runtime served from LittleFS |
| `firmware_legacy/data/` other files | LittleFS upload/build support assets from the original project |
| `firmware_legacy/README_legacy.md` | Original high-level description of the old pipeline |

The build copy has the hard-coded access-point password replaced by a redaction marker. Compare the original reference folder only in a local environment when recovering historical intent; do not reuse that value as a credential.

## Old runtime flow

1. The ESP32 starts a Wi-Fi access point and an HTTP server.
2. Three MPU-6050 devices share an I2C bus; GPIO-controlled AD0 lines select a device. The firmware labels each device as X, Y, or Z even though every device returns three accelerometer axes (and gyro values).
3. The firmware polls sensor registers on a software period, converts acceleration to g, applies a startup offset calibration, then an 8-sample moving average.
4. It reduces the three acceleration axes to one magnitude, subtracts 1 g, and clamps negative values to zero. RMS and a 128-sample Hamming-window FFT are computed from this scalar stream; intensity is RMS scaled by a configured maximum.
5. A ten-second post-boot RMS collection becomes per-device warning thresholds. It is not a multi-session frequency baseline and has no traffic-condition labels.
6. Sensor and derived values are returned as JSON from `/data`. The browser polls the route and uses additional smoothing to animate a Three.js fabric-style visualization.
7. Processed CSV rows are appended to LittleFS. `/download` streams the CSV, then deletes and recreates the file.

## Migration decisions

- Keep the original snapshot only for historical comparison. New source belongs in `firmware/`.
- Keep the three sensors as redundant full-axis sensors. Do not preserve the old device-to-axis naming.
- Replace scalar magnitude and startup-offset removal with all nine separate sensor-axis streams and mean removal within each fixed 60-second window.
- Use the approved exact N-point FFT maximum-bin estimator, measured per-sensor window rates, symmetric Hann and ten-window session median. Pilot-confirm band and QC settings before freezing formal sessions.
- Replace the boot-time RMS thresholds with session-based dominant-frequency baseline statistics and clear review states.
- Replace the unbounded CSV workflow with session metadata, retained raw records, summaries, reason-coded QC, and explicit deletion confirmation.
- Use the current embedded dashboard's real XYZ previews, nine independent latest-window peaks, session controls and baseline tables. No decorative animation is measurement evidence; full spectra/history are not served by the current API.

## Known limitations of this description

The old code and supplied audit were read as the basis for this summary. This does not validate the old hardware or establish its frequency accuracy or build compatibility. Current primary sources and actual checks are in `VERIFIED_FIRMWARE_SOURCES.md`, `MATHEMATICAL_ALGORITHMS.md` and `IMPLEMENTATION_STATUS.md`.

