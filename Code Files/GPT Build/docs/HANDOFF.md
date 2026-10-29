# Firmware handoff — 2026-10-24

User approved paper v2 and authorized the firmware. Exact module is ESP32-S3-WROOM-1-N16R8; exact sensors are three MPU6050 ICs. Read PROJECT_MAP.md, APPROVED_METHOD.md, MATHEMATICAL_ALGORITHMS.md and the current implementation/verification report.

Active sketch firmware/SHM_Capstone implements two I2C buses, three DRDY edge queues, sequential six-byte XYZ FIFO retrieval, a600s PSRAM recording with ten60s FFT jobs, raw/CSV/JSON retention, pilot/formal controls, frozen local traffic cutoffs, nine independent channel-axis baselines and embedded offline HTTP dashboard. Arduino IDE only.

Current defaults are prototype settings and need pilot confirmation. Unknown wiring/site approval/bridge coordinates have not been invented. Formal mode requires frozen station/orientation/settings. Do not silently change window, estimator, raw scaling, FFT grid, timing tolerance, cutoff version or baseline membership.

Numerical audit: native C++ versus NumPy full complex spectrum, scalar/baseline checks and synthetic full-session reconstruction exist under tools/. reports/math_verification.json records actual source hashes and results. Integrated Arduino compilation and physical validation status belong in IMPLEMENTATION_STATUS.md; never infer a bench pass from a successful compile.

Known prototype limitations: raw remains in PSRAM until capture ends; power loss beforehand loses it.16MB flash holds only a small number of complete recordings; explicit backup/purge is required. DRDY epochs include MCU interrupt latency and sensor output delay. Sensors are independently clocked and are not phase synchronized. There is no calibrated reference validation, field dataset or physical FIFO/IRQ trace yet.

Historical docs01..07 describe the earlier Welch/PlatformIO proposal and old hardware. Current approved FFT method and N16R8 map supersede those conflicts. Do not edit the source paper or Reference File folder.

Next human step: follow PROTOTYPE_WORKFLOW.md, ARDUINO_IDE_SETUP.md and HARDWARE_INTERFACE.md, wire the proposed prototype, run precheck, collect pilot data, export raw/windows/summary and independently analyze them. Resolve physical timing/IRQ continuity, maximum sustained DSP runtime, filesystem retention, known-frequency bench response and traffic-count reliability before formal sessions. Record all actual outcomes.

Astra starts independent review at ASTRA_REVIEW_BRIEF.md; stable EQ-* labels identify exact code and formulas. Pilot count derivation uses tools/derive_traffic_cutoffs.py with actual exported summaries.

Future user assignment: after prototyping, GPT6 Astra researches and produces KiCad schematic/PCB and audits mathematical algorithms; GPT6.1 Sol prepares the BOM from the reviewed hardware design. This firmware turn does not fabricate that future schematic or BOM.
