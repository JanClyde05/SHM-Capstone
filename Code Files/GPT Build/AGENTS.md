# Active firmware contract

Latest human decision: paper v2 approved on 2026-10-24; firmware development authorized. Target ESP32-S3-WROOM-1-N16R8 and three MPU6050 ICs. These decisions supersede conflicting historical MD Files/copies, including Welch, interpolation, sensor fusion, old GPIO35/36, and PlatformIO examples.

Read docs/HANDOFF.md, docs/PROJECT_MAP.md, docs/APPROVED_METHOD.md, docs/MATHEMATICAL_ALGORITHMS.md, docs/HARDWARE_INTERFACE.md and docs/ARDUINO_IDE_SETUP.md first. Numerical code and baseline remain independent of Arduino headers.

Use Arduino IDE peer .cpp/.h modules in firmware/SHM_Capstone. Follow the adopted global UI standard. Serve embedded offline assets with built-in HTTP WebServer; LittleFS stores research records. HTTP/WebSocket transport and filesystem asset placement are independent choices.

Retain all nine channel-axis streams, exact timestamps/counts and QC. No vector magnitude, startup-offset subtraction, smoothing, Welch, spectral fusion, sub-bin interpolation or synthetic display data. Use measured DRDY rate per window. The three sensors are co-located, sequentially read, independently clocked.

Use pilot mode until the operator freezes settings and numeric traffic cutoffs. Formal sessions require the same frozen station/orientation/config. One session600s, ten60s windows, per-window exact N-point FFT max positive in-band magnitude. Session result requires ten valid windows and is their median. Baselines use independent formal session medians and separate group/sensor/axis cells.

Label equation code with EQ-* identifiers and keep the mathematical registry and independent tools synchronized. Sources must be primary and verified. Report actual checks and unverified physical behavior; use [Certain]/[Likely]/[Guessing] in reports. Do not claim hardware frequency accuracy from a software test.

Never automatically format or delete recordings. Preserve original paper, reference program and old KiCad source. Do not commit credentials. Record downloads do not delete files. Raw purging/formatting requires explicit Serial commands.

Scope: frequency indicators and prototype performance. Operator labels use NO BASELINE YET, PROVISIONAL (n<5), WITHIN BASELINE, OUTSIDE BASELINE – REVIEW. These are review states, with no structural diagnosis.

Current work is firmware prototyping. User assigned later schematic/PCB research to GPT6 Astra after prototype work, and BOM preparation to GPT6.1 Sol after hardware definition. Do not create a speculative final BOM or PCB now.
