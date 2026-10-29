# KiCad validation snapshot

## Final corrected PCB CAD delivery — 2026-10-29

Active artifact: `PCB Files/GPT Build - PCB/design/SHM_Node_R2.kicad_pcb`, SHA-256 `0ea352e982e6ccb87134d1d3dcef7bd3adb747efab5ba28b136cd1090f99540e`. The four final reference-label moves change the earlier promoted hash `804D5B67...`; components, pad nets, copper and outline are unchanged by those moves. Old source/report hashes are historical.

Exact evidence: `PCB Files/GPT Build - PCB/reports/reference_corrected/validation_20261029T145905461959Z/manifest.json`. KiCad 10.0.6 ERC/DRC/connectivity/parity and independent audit: zero findings; 233 numbered pads, 148 spec endpoints, firmware mappings, native USB/reserved pins, actual MPU center copper/paste and rule areas checked. Exact SHM_PCB_New 12-edge 79.50 × 50.45 mm outline. Baseline four ERC/five DRC ignored categories remain explicitly listed; no explicit exclusions/new suppressions. Report commands, timestamps and source/report hashes are retained.

Current recovery/navigation: hardware `docs/HANDOFF.md`, `CONTINUATION_PLAN.md`, `PROJECT_MAP.md`, `LAYOUT_REVIEW.md`, `RESEARCH_LEDGER.md`, `ERROR_LOG.md`, `BOM.md` and `PROTOTYPE_BRINGUP.md`. Active native files are in `design/`; staging in `design/reference_corrected/`; wrong 83 mm history in `design/superseded_wrong_83mm_outline/`. Run `tools/run_corrected_checks.py --active` for active files. Do not run legacy writers or regenerate over later manual work.

Remaining gates: fabricator stackup/USB impedance, exact remaining parts and DFM/stencil, enclosure/cable/mounting, thermal/current/USB/I2C/DRDY/FIFO, reference-frequency and field tests. No physical validation or fabrication release is claimed. Paper and firmware were not edited during this continuation. Top/bottom native renders and copper plots were visually inspected, and the existing schematic layout remains unchanged.

## Earlier snapshots (historical)

# KiCad validation snapshot

## 2026-10-28/29 reference correction - scope of this historical snapshot

The user identified only the root `PCB Files/Reference PCB (OLD Version)/Thesis/SHM_PCB_New/SHM_PCB_New.kicad_sch/.kicad_pcb` as the intended old reference. Direct geometry inspection found that the R2 PCB hash below used the larger parent Thesis outline, not that compact reference. Its shape conformity is therefore **contradicted** despite the narrow zero-active-violation results recorded here. Corrected layout work is active; this document has not yet recorded a successful check of the corrected source.

The intended reference centerline extent is79.50 x50.45mm; reference PCB SHA-256:`372996943A9C3EB3C9087C315B7C810DF9C0B70A4E0D1B47A99E9EC81B52C23F`. Exact source/edge/placement comparison is saved at `PCB Files/GPT Build - PCB/reports/reference/reference_correction_20261028.json`. Preserve the reports below as historical evidence. They do not transfer to changed geometry, mounting, component placement, routing or stackup, and do not establish fabrication readiness. Append new report/source hashes only after the corrected artifact is actually checked.

Audit date: 2026-10-26. This captures the current R2 KiCad project check from the same audit session as the hashes below. It is evidence of CAD rule-check status for the exact files checked; it is not a fabrication release or physical validation.

## Source identifiers

| File | SHA-256 |
|---|---|
| `PCB Files/GPT Build - PCB/design/SHM_Node_R2.kicad_pcb` | `DA80B01E83B4625F8C970DF54883DBA27B5402EBCA027CB8A6274129E32A0E54` |
| `PCB Files/GPT Build - PCB/design/SHM_Node_R2.kicad_sch` | `4D93FA95E3C7131072CDAC248E71C3A8D98AEA8189763AA2578037EAB57F4A94` |
| `PCB Files/GPT Build - PCB/design/circuit_spec.json` | `F5F5A56F9E9B467C1FF75795E55D94CA561EB9770ED3594DD65273EA0006B34B` |

KiCad CLI version: 10.0.6.

## Results

| Check | Report | Timestamp (local project environment) | Result |
|---|---|---|---|
| PCB DRC | [`kicad_drc_20261026_020348.json`](verification/kicad_drc_20261026_020348.json) | 2026-10-26 02:03:48 | 0 active violations, 0 unconnected items, 0 schematic parity issues. |
| Schematic ERC | [`kicad_erc_20261026_020401.json`](verification/kicad_erc_20261026_020401.json) | 2026-10-26 02:04:01 | 0 active violations. |
| PCB DRC repeat with severity exclusions | [`kicad_drc_exclusions_20261026_020514.json`](verification/kicad_drc_exclusions_20261026_020514.json) | 2026-10-26 02:05:14 | Same zero active-violation, unconnected, and parity counts; no exclusion messages emitted. |
| Schematic ERC repeat with severity exclusions | [`kicad_erc_exclusions_20261026_020527.json`](verification/kicad_erc_exclusions_20261026_020527.json) | 2026-10-26 02:05:27 | Same zero active-violation count; no exclusion messages emitted. |

Report SHA-256 values:

- DRC: `1984D72AF6696BBCA21E66AF6DD53DCAAB35903A41120E22F6942166329667AA`
- ERC: `5C37B18B3903489EFDFDA929A12F41791411D36E4891F0A0E6F7BB97F4BBB554`
- DRC repeat: `0FF13561544945F8D0F3EF940E3D1C59F612632CE0EAD7A67D79042F7482348F`
- ERC repeat: `C6E240D81AC6726998318B9C2F2B83B5F328E66508F2AC99C98404088675A9D3`

The report output does not embed the source hashes shown above. Hashes were recorded from the same audit session; if independent provenance is needed, rerun the checks and hash the source and output together. The older `PCB Files/GPT Build - PCB/docs/AUDIT_ELECTRICAL` source hash is stale; older README/HANDOFF text also reports an earlier routing state. Do not rely on those for current DRC status.

## Ignored/excluded rule categories

The DRC report enumerates five ignored categories: missing courtyard; track endpoint not centered on via; tuning-profile track geometries; footprint filters mismatch; footprint type/pads mismatch. The ERC report enumerates four ignored categories: single global label; four-way junction; SPICE model; footprint filter. These were not emitted as active violations in the snapshot. Their exclusion is not evidence that a footprint, assembly, or design is correct; inspect them when reviewing the design and before fabrication.

## Interpretation limits

The output supports only that KiCad 10.0.6's recorded rule checks reported zero active violations/unconnected/parity items for these exact CAD files under the project's configured rules/exclusions. It does not establish schematic intent, electrical margins, component availability, footprint-manufacturer correspondence, antenna performance, signal integrity, thermal behavior, enclosure fit, manufacturability, assembly quality, sensor noise, sampling accuracy, or research suitability. No board-level physical test or fabrication readiness review was performed by these checks. Rerun and preserve reports after any CAD source or rule change.

## Engineering audit follow-up — 2026-10-29

Hardware review: [engineering audit](../PCB%20Files/GPT%20Build%20-%20PCB/docs/ENGINEERING_AUDIT_20261029.md), [scope/plan](../PCB%20Files/GPT%20Build%20-%20PCB/docs/ENGINEERING_AUDIT_PLAN.md). The deeper read-only audit found issues beyond configured ERC/DRC: USB A-contact transition imbalance (4 D+ versus 2 D−), missing explicit impedance stackup, no local capacitor directly on the ESD VBUS net, J2-to-U3 nominal body separation about 5.18 mm (5.13 mm conservative F.Fab box) against the TDK 6 mm insertion-component guidance, and unresolved thermal/probe-access qualification. Nominal antenna overhang is 0.10 mm with no recorded tolerance budget. These are engineering concerns, not observed prototype failures. Active PCB remains unchanged at SHA-256 `0ea352e982e6ccb87134d1d3dcef7bd3adb747efab5ba28b136cd1090f99540e`; the earlier configured CAD pass remains bounded evidence.

The report maps ENG-01–ENG-13 to file evidence, source IDs E1–E9, equation IDs and closure steps. `tools/audit_engineering_geometry.py` measures paths, reference-fill samples, antenna geometry, test pads and insertion-component proximity; `tools/audit_engineering_math.py` records conditional power/thermal/I2C/RC arithmetic. Data is in `PCB Files/GPT Build - PCB/reports/engineering_audit/20261029/`. No physical tests or new CAD edits were performed.

