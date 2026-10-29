# SHM frequency acquisition prototype

Arduino IDE firmware for ESP32-S3-WROOM-1-N16R8 and three co-located MPU6050 ICs. The user approved paper v2 and authorized implementation on 2026-10-24.

Start with [docs/PROJECT_MAP.md](docs/PROJECT_MAP.md), [docs/HANDOFF.md](docs/HANDOFF.md), [Arduino setup](docs/ARDUINO_IDE_SETUP.md) and [hardware wiring](docs/HARDWARE_INTERFACE.md). Open firmware/SHM_Capstone/SHM_Capstone.ino in Arduino IDE. Install ArduinoJson7.4.2 and Espressif core3.3.5 (local verification target).

Use [docs/PROTOTYPE_WORKFLOW.md](docs/PROTOTYPE_WORKFLOW.md) for first operation, pilot counts, export/replay, configuration freeze and formal sessions. Astra starts at [docs/ASTRA_REVIEW_BRIEF.md](docs/ASTRA_REVIEW_BRIEF.md).

The dashboard is embedded in ui_assets.h and uses built-in HTTP WebServer with polling. No web asset upload is required. LittleFS is for raw/summary/window records. Select 16MB flash, QIO flash and OPI PSRAM; the sketch supplies its own partitions.csv.

This is implemented prototype firmware awaiting physical validation. Read the actual verification record in docs/IMPLEMENTATION_STATUS.md and reports/. The numerical algorithms have an independent audit path in docs/MATHEMATICAL_ALGORITHMS.md and tools/.

firmware_legacy and docs/01..07 retain historical reference context. Their old estimator, pin and tooling proposals are superseded by docs/APPROVED_METHOD.md. They are not the active implementation specification.
