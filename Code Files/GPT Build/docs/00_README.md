> **Historical snapshot - superseded 2026-10-24.** The user approved paper v2 and authorized Arduino IDE firmware for ESP32-S3-WROOM-1-N16R8 with three MPU6050 ICs. The active FFT method, hardware map, traffic protocol and verification status are in APPROVED_METHOD.md, HANDOFF.md, PROJECT_MAP.md and IMPLEMENTATION_STATUS.md. Older Welch, PlatformIO, old GPIO, estimator-open, collection and scaffold instructions below are retained only as history.

# SHM V2 — Documentation Set (Index)

> **Latest user decisions (2026-10-24):** These decisions supersede older conflicting proposals in this document set. Use the three traffic groups NEAR_ZERO, MEDIUM, and HEAVY. Poll three triaxial sensors in order, reading one complete X/Y/Z frame from sensor 1, then 2, then 3, and repeat. Preserve each sensor stream; attach a polling-cycle ID, per-frame timestamp, and per-sensor sample index. Frames are sequential, not simultaneous. For baselines, report mean ± sample SD as a descriptive band and separately use mean ± 2 sample SD as the default heuristic review band; do not call the latter a formal 95% interval. DSP must be mathematically specified and reproducible. FFT versus Welch remains an open estimator decision; see docs/RESEARCH_ALIGNMENT_REVIEW.md for the implementation gate and paper-edit map.

**Project:** Development of a Localized Real-Time Frequency Monitoring System for Structural Health Monitoring using MEMS IMUs and ESP32
**Author:** Jan Clyde T. Talosig — BS Electronics Engineering, CSU Carig
**Site:** Buntun Bridge, Tuguegarao City, Cagayan
**Repo:** https://github.com/JanClyde05/SHM-Capstone
**Prepared:** 2026-10-23 (based on `Thesis.kicad_sch`, `Thesis.kicad_pcb`, `SHM - Formatted Thesis Paper - Reference Update.docx`, and firmware `SHM_Main.ino` / `Calculations.h` / `WebServerUI.h`)

Confidence tags used throughout: **[Certain]** = verified in a file or datasheet read during this review. **[Likely]** = strong inference. **[Guessing]** = placeholder that must be decided with pilot data.

---

## Reading order

| # | File | Purpose | Primary reader |
|---|------|---------|----------------|
| 00 | `00_README.md` | This index, decision log, open questions | JC |
| — | `AGENTS.md` | Briefing + rules for the Antigravity agents | Opus 4.6 / Gemini 3.8 High |
| 01 | `01_RESEARCH_CONTEXT.md` | What the research is, what the device does, requirement traceability | JC + agents |
| 02 | `02_AUDIT_AND_FIXES.md` | Every defect found (firmware, schematic, PCB), evidence, severity, fix | JC + agents |
| 03 | `03_FIRMWARE_FIX_INSTRUCTIONS.md` | Step-by-step firmware corrections with exact register values and code | Code agent |
| 04 | `04_CODEBASE_PLAN.md` | New repo structure, modules, data formats, API, tests, milestones | Code agent |
| 05 | `05_SCHEMATIC_PCB_V2_SPEC.md` | Revised schematic, pin map, BOM with datasheet links, layout rules, V1 rework list | Hardware agent |
| 06 | `06_DATA_COLLECTION_PROTOCOL.md` | The three traffic-level datasets (near-zero / medium / heavy), field procedure, QC, stats, thesis edits | JC |
| 07 | `07_REFERENCES.md` | All links, with verification status | everyone |

## Suggested work order (one chat/agent session per row)

1. **Pilot first** (bench noise test + short bridge recording) → freezes the analysis band and QC thresholds. See `06`.
2. **Firmware core** (`03` steps 1–6): fixes the gravity bug, timing, the selected DSP estimator after method reconciliation. Works on the *existing V1 board* with two pin changes.
3. **Session / baseline / UI** (`04` milestones M3–M5).
4. **Schematic + PCB V2** (`05`) — only after you decide rework vs respin (open question Q1).
5. **Thesis sync** (`06` §9, `02` §Thesis-sync).

## Decision log (what this document set assumes)

| ID | Decision | Why | Status |
|----|----------|-----|--------|
| D1 | Keep ESP32-S3-WROOM-1 + MPU-6050 | Thesis narrative is "low-cost MEMS"; changing sensor rewrites Chapters I–III | Proposed — revisit after pilot noise-floor result |
| D2 | Three triaxial sensors are read sequentially in round-robin order: complete XYZ frame from sensor 1, then 2, then 3. Preserve each stream and timestamp; cycle ID associates a polling pass but does not imply simultaneous acquisition or an approved averaging method. | User-confirmed; fusion rule open |
| D3 | Per-axis acceleration, **no vector magnitude** | Magnitude − 1 g rectifies and distorts the spectrum | Proposed (high confidence) |
| D4 | Sampling rate, DLPF, analysis band, and estimator settings are provisional until verified and pilot-frozen. Welch N=4096/HOP=2048/Hann is a proposal only; FFT versus Welch remains unresolved. | Placeholder; see alignment review |
| D5 | Physical bus/AD0/FIFO design must be verified against the actual hardware. Firmware must follow the confirmed sequential sensor 1→2→3 round-robin poll order. | Hardware layout proposed; sequential order user-confirmed |
| D6 | microSD for raw logs (V2) | LittleFS fills in ≈ 1 min at old logging rate | Proposed |
| D7 | Per-category baseline reports mean ± sample SD as a descriptive band; separate default review limits are mean ± 2 sample SD, a heuristic only. | Resolved by user; not a formal 95% interval |
| D8 | Three traffic groups: NEAR_ZERO, MEDIUM, HEAVY. Set simple site-local operational criteria before formal sessions; retain counts as supporting observations. | User-confirmed; criteria must be documented before collection |

## Open questions (JC must answer)

- **Q1.** Are V1 boards already assembled and tested, and does the defense date leave time for a V2 fabrication run? (Decides `05` §A rework-only vs §B respin.)
- **Q2.** Exact part number printed on your ESP32-S3-WROOM-1 module (N8? N16R8?). If it is an **R8** or **R16V** variant, IO35/IO36/IO37 are unusable [Certain — Espressif datasheet v1.8, Table 3-1 note b].
- **Q3.** Is written DPWH/LGU approval for Buntun Bridge access in hand? (No fieldwork before it — thesis §3.2/§3.7.)
- **Q4.** Where on the bridge can the sensor be mounted (span, member, side)? Needed for the mounting design in `05` and Table 1 of the thesis.

## Folder layout of this package

```
shm-v2-docs/
├─ 00_README.md
├─ AGENTS.md
├─ 01_RESEARCH_CONTEXT.md
├─ 02_AUDIT_AND_FIXES.md
├─ 03_FIRMWARE_FIX_INSTRUCTIONS.md
├─ 04_CODEBASE_PLAN.md
├─ 05_SCHEMATIC_PCB_V2_SPEC.md
├─ 06_DATA_COLLECTION_PROTOCOL.md
└─ 07_REFERENCES.md
```
Copy this folder to `SHM-Capstone/docs/` in the repo.




