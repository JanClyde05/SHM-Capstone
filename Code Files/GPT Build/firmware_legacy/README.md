# Preserved legacy firmware

This folder is a reference copy of the old Arduino project. It contains the original firmware headers/sketch and LittleFS assets, plus the old README. It exists to explain the previous implementation and support migration. New work belongs in `../firmware/`.

The copy was sourced from `../../Reference File (OLD Version)/SHM-ESP32-System/`. That source folder was not modified. The copied `.ino` has its hard-coded access-point password replaced with `REDACTED_IN_ARCHIVE`; use the original only for local historical comparison, never as a live credential. See `../docs/LEGACY_BEHAVIOR.md` for behavior and known defects.

Do not flash this snapshot as the new firmware or build on its behavior without resolving the audit items in `../docs/02_AUDIT_AND_FIXES.md` and implementation rules in `../docs/03_FIRMWARE_FIX_INSTRUCTIONS.md`.
