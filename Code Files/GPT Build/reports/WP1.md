> Historical scaffold milestone. Current firmware implementation and verification are recorded in FIRMWARE_PROTOTYPE_20261024.md.

# WP1 — Repository structure and handoff

## Result

[Certain] `GPT Build` now has the planned top-level organization, copied project specifications, an explicitly minimal firmware scaffold, and handoff documentation for future agents. [Certain] The legacy source folder was left unchanged; its code/assets were copied to `firmware_legacy/`, with the hard-coded access-point password redacted in the copied sketch.

## Changed areas

- Added root `README.md`, `AGENTS.md` clarification, and `.gitignore`.
- Copied the eight numbered project documents into `docs/`.
- Added architecture, legacy behavior, handoff, implementation-status, and milestone-report documentation.
- Initially created a PlatformIO skeleton, then replaced it per the user's follow-up with the Arduino IDE sketch and peer-module layout in `firmware/SHM_Capstone/`.
- Added the SHM static dashboard under `firmware/SHM_Capstone/data/` using the global design rules from the user's Danger Monitoring System V2 project.
- Copied the legacy firmware and LittleFS assets into `firmware_legacy/`.
- Sorted supplied Rev 1 Gerber/drill files and images under `hardware/rev1/`; the supplied source did not contain KiCad project files.
- Added area README guides, offline-tool dependencies, field-log template, and thesis-sync placeholder.

## Verification

[Certain] File structure and source-copy contents were inspected. [Certain] No build, test, flash, hardware check, datasheet check, or field run was performed for this report.

## Deviations

[Certain] The original M0 plan's empty-skeleton build acceptance remains unverified because no build was run. [Certain] No hardware pins or sensor register writes were added because the module part number and register-map checks remain unresolved. [Certain] The copied legacy `.ino` is not byte-identical: its hard-coded access-point password was replaced with a redaction marker. [Certain] The static dashboard has no active device/API implementation.

## Unverified items

- [Certain] Arduino IDE board/core selection and firmware compilation.
- [Certain] Physical ESP32-S3 module variant and V1 pin availability (Q2).
- [Certain] Sensor-register values against the linked register map and product specification.
- [Certain] Board operation, measured sampling rate, storage capacity, dashboard behavior, and all field permissions/site details.
- [Certain] The separate public-history review mentioned in the supplied repo-hygiene spec was not performed; this task stayed inside `GPT Build` and did not alter unrelated workspace files.
