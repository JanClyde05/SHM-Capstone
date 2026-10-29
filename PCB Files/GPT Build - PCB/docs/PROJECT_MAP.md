# Project navigation map

## Engineering audit follow-up — 2026-10-29

Read [ENGINEERING_AUDIT_20261029.md](ENGINEERING_AUDIT_20261029.md) and its [plan](ENGINEERING_AUDIT_PLAN.md) before the next CAD edit. The deeper read-only audit found issues beyond configured ERC/DRC: USB A-contact transition imbalance (4 D+ versus 2 D−), missing explicit impedance stackup, no local capacitor directly on the ESD VBUS net, J2-to-U3 nominal body separation about 5.18 mm (5.13 mm conservative F.Fab box) against the TDK 6 mm insertion-component guidance, and unresolved thermal/probe-access qualification. Nominal antenna overhang is 0.10 mm with no recorded tolerance budget. These are engineering concerns, not observed prototype failures. Active PCB remains unchanged at SHA-256 `0ea352e982e6ccb87134d1d3dcef7bd3adb747efab5ba28b136cd1090f99540e`; the earlier configured CAD pass remains bounded evidence.

New evidence: `reports/engineering_audit/20261029/geometry.json`, `math.json`, and USB plane-screen SVG/PNG; reproducible tools `audit_engineering_geometry.py` and `audit_engineering_math.py`. Start with the report's ordered corrections and acceptance criteria. The audit did not change CAD, firmware or paper, and does not authorize fabrication.

## Accepted compact CAD checkpoint — 2026-10-29

**Verified for configured CAD checks:** KiCad 10.0.6 reports zero ERC violations, zero DRC violations, zero unconnected items and zero schematic-parity issues. Independent audit: zero failures; 233 numbered pads and 148 intended spec endpoints checked; exact 12-edge reference geometry retained (79.50 × 50.45 mm). This is a prototype/review design, **not a fabrication release or physical validation**.

Active PCB SHA-256: `0ea352e982e6ccb87134d1d3dcef7bd3adb747efab5ba28b136cd1090f99540e`. Evidence: `reports/reference_corrected/validation_20261029T145905461959Z/manifest.json`, with commands, source/report hashes, unchanged-source checks, rule values and disabled-category lists. Four baseline ERC categories and five baseline DRC categories remain ignored; no new suppressions or explicit exclusions were accepted. The clean result is bounded by those settings.

Current electrical source is `design/SHM_Node_R2.kicad_sch`, `.net`, `circuit_spec.json`; current board/project/local library are beside them. `design/reference_corrected/` retains reproducible staging inputs and the same final board. The old wrong 83.6 mm board is preserved in `design/superseded_wrong_83mm_outline/`. Earlier reports and hashes remain historical evidence, not current acceptance.
## Current navigation

| File / folder | Use |
|---|---|
| `design/SHM_Node_R2.kicad_pro`, `.kicad_sch`, `.kicad_pcb` | Active editable corrected project |
| `design/DESIGN_MANIFEST.json` | Exact active file hashes and current report link |
| `design/reference_corrected/` | Staging, saved inputs and final candidate; not the default editing location |
| `design/superseded_wrong_83mm_outline/`, `archive/` | Preserved superseded design and recovery snapshots |
| `tools/run_corrected_checks.py --active` | Timestamped active ERC/DRC/independent verification |
| `tools/build_corrected_board.py`, `prepare_corrected_routing.py`, `route_corrected_usb.py` | Placement/critical-route generators; not safe over unpreserved manual work |
| `tools/finish_corrected_board.py`, `polish_corrected_labels.py` | Routing import, local repairs, planes and final four reference labels |
| `tools/verify_corrected_board.py`, `measure_usb_geometry.py` | Independent consistency/geometry and bounded USB path metrics |
| `docs/HANDOFF.md`, `CONTINUATION_PLAN.md`, `LAYOUT_REVIEW.md` | Current results, next actions and engineering limits |
| `docs/RESEARCH_LEDGER.md`, `ELECTRICAL_DECISIONS.md`, `ERROR_LOG.md` | Primary sources, choices and retained failures |
| `BOM.md`, `BOM.csv`, `docs/PROTOTYPE_BRINGUP.md` | Engineering parts list and unperformed physical checks |
| `previews/00_README_ACTIVE_PREVIEWS.md` | Current visual artifact index; other preview names may be historic |

## Earlier map snapshots (historical)

# Project navigation map

Updated 2026-10-29. Paths in code spans are relative to the hardware-project root unless stated otherwise; Markdown links resolve from this document. **Current task: first document the continuation plan, then correct R2 to the user-selected compact reference `../Reference PCB (OLD Version)/Thesis/SHM_PCB_New/SHM_PCB_New.kicad_pcb` and its root schematic.** Parent Thesis and nested SHM_Proto_PCB are historical comparisons. The old larger-outline selection is superseded. Read [CONTINUATION_PLAN.md](CONTINUATION_PLAN.md) and [HANDOFF.md](HANDOFF.md) before relying on any checkpoint row below.

The 2026-10-26 zero-active-violation CAD snapshot is in `../../MD Files/14_CAD_VALIDATION_SNAPSHOT.md`, tied to old R2 PCB hash `DA80B01E...32A0E54`. That result supersedes the earlier incomplete-routing counts below as a historical state, but does not validate the corrected geometry. New geometry, placement and routing must receive fresh checks. `reports/reference/reference_correction_20261028.json` captures both old selected-reference and wrong-R2 geometry at the correction checkpoint. [ANTENNA_PLACEMENT_REVIEW.md](ANTENNA_PLACEMENT_REVIEW.md) records the official overhang guidance and measured old module position.

## Read order

For the current design review, also read [LAYOUT_REVIEW.md](LAYOUT_REVIEW.md): observed geometry, USB planar metrics, thermal/plane/mounting choices, and explicit physical limits. `tools/measure_usb_geometry.py` regenerates the endpoint graph measurements; they are not electrical-delay or impedance measurements.

1. Repository [AGENTS.md](../../../AGENTS.md), central [00_README.md](../../../MD%20Files/00_README.md), [08_PROJECT_MAP_AND_SOURCE_OF_TRUTH.md](../../../MD%20Files/08_PROJECT_MAP_AND_SOURCE_OF_TRUTH.md), [12_EXECUTION_PLAN.md](../../../MD%20Files/12_EXECUTION_PLAN.md), and [22_AI_FEEDBACK_AND_MISTAKE_LOG.md](../../../MD%20Files/22_AI_FEEDBACK_AND_MISTAKE_LOG.md) — active artifacts, evidence rules, user preferences and prior mistakes.
2. Hardware [README.md](../README.md) and [AGENTS.md](../AGENTS.md) — scope and local work constraints.
3. [CONTINUATION_PLAN.md](CONTINUATION_PLAN.md) — recovery state, source-to-decision map, ordered commands and acceptance gates. Read before running a generator.
4. [HANDOFF.md](HANDOFF.md) — current progress, next action and actual validation evidence; reconcile report timestamps with the written checkpoint.
5. [DECISION_MAP.md](DECISION_MAP.md), [REFERENCE_REVIEW.md](REFERENCE_REVIEW.md), and [ANTENNA_PLACEMENT_REVIEW.md](ANTENNA_PLACEMENT_REVIEW.md) — requirements, exact reference geometry, aesthetic choices and bounded antenna analysis.
6. [RESEARCH_LEDGER.md](RESEARCH_LEDGER.md) and [ELECTRICAL_DECISIONS.md](ELECTRICAL_DECISIONS.md) — manufacturer sources and their circuit applications.
7. [ERROR_LOG.md](ERROR_LOG.md), actual validation reports and [PROTOTYPE_BRINGUP.md](PROTOTYPE_BRINGUP.md) — CAD failure history and physical checks that have not been performed.

## Active design and superseded file map (Updated 2026-10-29)

Following user direction, the superseded 83.6mm layout and intermediate files were isolated into `design/superseded_wrong_83mm_outline/`. The corrected 79.50 × 50.45 mm 12-edge compact design was promoted to root `design/` and validated.

| Path | Role and current observed state |
| --- | --- |
| `design/SHM_Node_R2.kicad_pro` | **Active KiCad Project**. Primary project entry point for KiCad 10.0.6. |
| `design/SHM_Node_R2.kicad_sch` | **Active Schematic**. Correlated ESP32-S3 + 3× MPU-6050 schematic. ERC: 0 violations. |
| `design/SHM_Node_R2.kicad_pcb` | **Active PCB Layout**. Corrected 79.50 × 50.45 mm compact board (SHA-256: `804D5B67AF300BFD1435103EC163E99917812B64A9055980DF44E0CCA97D3EE5`). KiCad 10.0.6 DRC: 0 errors, 0 unconnected, 0 parity issues. |
| `design/circuit_spec.json`, `SHM_Node_R2.net` | **Active Circuit Definition**. Canonical net/component specification and exported XML netlist. |
| `design/fp-lib-table`, `SHM_Local.pretty/` | **Active Footprints**. Registered project-local footprint library (contains verified `ESP32-S3-WROOM-1_Overhang`). |
| `design/00_README_ACTIVE_DESIGN.md` | Human- and AI-readable master document detailing active design files, hashes, and verification commands. |
| `design/DESIGN_MANIFEST.json` | Machine-readable manifest for active design assets. |
| `design/superseded_wrong_83mm_outline/` | **Superseded Archive (DO NOT USE)**. Holds old 83.6 mm board (`SHM_Node_R2_superseded_83mm.kicad_pcb`, hash `DA80B01E...`) and intermediate placement/preroute files, with a clear warning notice. |
| `design/reference_corrected/` | Working sandbox directory preserved for build/routing script provenance. |
| `previews/active_pcb_3d_top.png`, `active_pcb_3d_bottom.png` | Fresh raytraced 3D visual renders of the active board. |
| `previews/active_schematic.png`, `SHM_Node_R2_schematic.pdf` | Fresh high-resolution 2D renders of the active schematic. |

## Historical artifact ownership and relationships

| Path | Purpose | Historical October26 early checkpoint status; current correction noted above |
| --- | --- | --- |
| `design/SHM_Node_R2.kicad_pro` | Native KiCad project and board settings | Created |
| `design/SHM_Node_R2.kicad_sch` | New correlated schematic | Created; active edits require fresh ERC |
| `design/SHM_Node_R2.kicad_pcb` | New board with imported routing and planes | Created; routing correction and final checks pending |
| `design/circuit_spec.json` | Shared component/net specification used for correlation | Created |
| `design/SHM_Node_R2.net` | Schematic-exported netlist | Created; regenerate after schematic edits |
| `design/SHM_Local.pretty/MPU6050_QFN24_NoCenterPad.kicad_mod` | Local MPU footprint matching no-center-pad strategy | Created; manufacturer/DRC review required |
| `design/fp-lib-table` | Project-local footprint library registration | Created |
| `tools/build_board.py` | Board-generation source; inspect before running because it can replace generated board outputs | Created |
| `tools/build_schematic.py` | Reproducible schematic and circuit-spec generation | Created |
| `tools/prepare_routing.py` | Preroute preparation and interchange generation | Created |
| `design/SHM_Node_R2_placement.*` and `_preroute.*` | Intermediate board/project snapshots | Created; not final design files |
| `reports/SHM_Node_R2.dsn` and `.ses` | Autorouter input and saved routing session | Created; router finished with16 unrouted/18 internal violations |
| `reports/routing.log` | Autorouter and optimizer history for last run | Created; process completion is not acceptance |
| `docs/RESEARCH_LEDGER.md` | Verified primary-source log | Created |
| `docs/ELECTRICAL_DECISIONS.md` | Pin map, components, equations and review limits | Created |
| `docs/PROTOTYPE_BRINGUP.md` | Physical test procedure and blank evidence table | Created; no tests performed |
| `docs/ERROR_LOG.md` | Actual tool/CAD failures, fixes and pending rechecks | Created |
| `docs/REFERENCE_REVIEW.md` | Old design and aesthetic audit | Completed read-only review |
| `reports/reference/reference_inventory.json` | Exact source hashes, edge geometry, footprints and pad-net tables from three old boards | Created |
| `reports/reference/SHM_PCB_New.svg` | Current old schematic exported by KiCad | Created and visually reviewed via PNG |
| `reports/reference/SHM_PCB_New-schematic.png` | Raster of current old schematic | Created and visually reviewed |
| `reports/reference/SHM_PCB_New-top.svg` and `.png` | Old front copper, silkscreen and outline | Created and visually reviewed |
| `reports/reference/old-schematic-pdf.png` | Raster of old existing PDF, useful for historical layout comparison | Created and visually reviewed |
| `reports/erc_initial.json`, `erc_current.json` | Schematic-rule history | Latest inspectedOct25 report has0 listed violations, four ignored-check categories; later edits need rerun |
| `reports/drc_placement.json`, `drc_preroute.json` | Intermediate board-rule history | Preroute report has0 listed errors,24 warnings,115 unconnected items; post-route validation pending |
| `previews/SHM_Node_R2_schematic.pdf`, `.png`, `SHM_Node_R2.svg` | New schematic review exports | Created; regenerate after edits |
| `previews/placement.svg`, `.png` | New placement preview | Created; not proof of finished routing |

## Related project locations

| Location relative to this folder | Authority/use |
| --- | --- |
| `../../Code Files/GPT Build/firmware/SHM_Capstone/hardware_profile.h` | Firmware GPIO/controller/address source of truth |
| `../../Code Files/GPT Build/docs/HARDWARE_INTERFACE.md` | Acquisition electrical/timing contract, bare-IC scope and bench evidence requirements |
| `../../Code Files/GPT Build/docs/APPROVED_METHOD.md` | Approved research-method summary |
| `../../Code Files/GPT Build/docs/MATHEMATICAL_ALGORITHMS.md` | DSP equation registry; hardware work must preserve data requirements |
| `../Reference PCB (OLD Version)/Thesis/SHM_PCB_New/SHM_PCB_New.kicad_sch` and `.kicad_pcb` | **Only intended old reference**, confirmed by user2026-10-28; compact79.50 x50.45mm centerline outline |
| Parent `Thesis/Thesis.*` and nested `SHM_PCB_New/SHM_Proto_PCB/` | Historical comparisons only; do not select as reference defaults |
| `../../MD Files/00_README.md`, `08`–`22` and verification records | Current project navigation, evidence, plans and persistent preferences/mistakes; read the index for exact filenames and current statuses |
| `../../MD Files/01`–`07` | Historical proposals; do not override current human requirements, approved method or active firmware |
| `../../Documents/The Real Research Paper/GPT Paper/` | Approved edited paper and its own handoff; no paper revision is part of this task |

## Design chain

Current human constraints + firmware interface -> verified manufacturer requirements -> circuit/net definition -> schematic -> footprints/placement -> four-layer routing and planes -> ERC/DRC + connectivity comparison -> visual/manual engineering review -> fabrication review package -> physical prototype evidence.

Validation outputs must identify the actual source version or hashes. Any schematic/net/footprint edit invalidates dependent board and report assumptions until reconciled.
