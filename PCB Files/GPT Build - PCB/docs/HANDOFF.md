# Hardware continuation handoff

## Engineering audit follow-up — 2026-10-29

Read [ENGINEERING_AUDIT_20261029.md](ENGINEERING_AUDIT_20261029.md) and its [plan](ENGINEERING_AUDIT_PLAN.md) before the next CAD edit. The deeper read-only audit found issues beyond configured ERC/DRC: USB A-contact transition imbalance (4 D+ versus 2 D−), missing explicit impedance stackup, no local capacitor directly on the ESD VBUS net, J2-to-U3 nominal body separation about 5.18 mm (5.13 mm conservative F.Fab box) against the TDK 6 mm insertion-component guidance, and unresolved thermal/probe-access qualification. Nominal antenna overhang is 0.10 mm with no recorded tolerance budget. These are engineering concerns, not observed prototype failures. Active PCB remains unchanged at SHA-256 `0ea352e982e6ccb87134d1d3dcef7bd3adb747efab5ba28b136cd1090f99540e`; the earlier configured CAD pass remains bounded evidence.

New evidence: `reports/engineering_audit/20261029/geometry.json`, `math.json`, and USB plane-screen SVG/PNG; reproducible tools `audit_engineering_geometry.py` and `audit_engineering_math.py`. Start with the report's ordered corrections and acceptance criteria. The audit did not change CAD, firmware or paper, and does not authorize fabrication.

Updated 2026-10-29T23:03:32+08:00 (Asia/Manila).

## Accepted compact CAD checkpoint — 2026-10-29

**Verified for configured CAD checks:** KiCad 10.0.6 reports zero ERC violations, zero DRC violations, zero unconnected items and zero schematic-parity issues. Independent audit: zero failures; 233 numbered pads and 148 intended spec endpoints checked; exact 12-edge reference geometry retained (79.50 × 50.45 mm). This is a prototype/review design, **not a fabrication release or physical validation**.

Active PCB SHA-256: `0ea352e982e6ccb87134d1d3dcef7bd3adb747efab5ba28b136cd1090f99540e`. Evidence: `reports/reference_corrected/validation_20261029T145905461959Z/manifest.json`, with commands, source/report hashes, unchanged-source checks, rule values and disabled-category lists. Four baseline ERC categories and five baseline DRC categories remain ignored; no new suppressions or explicit exclusions were accepted. The clean result is bounded by those settings.

Current electrical source is `design/SHM_Node_R2.kicad_sch`, `.net`, `circuit_spec.json`; current board/project/local library are beside them. `design/reference_corrected/` retains reproducible staging inputs and the same final board. The old wrong 83.6 mm board is preserved in `design/superseded_wrong_83mm_outline/`. Earlier reports and hashes remain historical evidence, not current acceptance.

## Completed and checked

- Correct reference silhouette, four copper layers, three MPU6050 devices with common orientation, exact current firmware net contract, native USB-C and N16R8 module.
- Locked main power/USB and 12 local sensor support-capacitor connections. Eight regulator tab vias with 0.60 mm top links, approximately 2.2–2.6 mm long, join ground planes. These dimensions do not establish thermal margin.
- Finished local supply/interrupt gaps, ground fills and silk clearance. Final visual pass moved R1/R8/U1/J1 labels out from under component bodies. Native top/bottom renders and 2D plots were reviewed; the schematic remains the checked, orderly repeated-block layout.
- USB endpoint planar mismatch +0.074839 mm (A contacts), -0.078715 mm (B contacts), including module-side copper. D- has two transitions; D+ has four for A contacts and two for B contacts. This excludes via barrel, pad and component effects and does not establish electrical delay or impedance. See `reports/reference_corrected/usb_active_final_geometry.json`.
- Final candidate and active validation both passed. Exact active files were checked with `tools/run_corrected_checks.py --active`; no manual source change occurred during checks.

## Start here next time

1. Read project AGENTS and MD00/08/12/22; then CONTINUATION_PLAN, this handoff, LAYOUT_REVIEW, RESEARCH_LEDGER and ERROR_LOG. Current user instructions override historic plans.
2. Open `design/SHM_Node_R2.kicad_pro`. Confirm the manifest/source hashes before editing. Do not open the archived wrong-outline project as current.
3. For read-only verification run KiCad Python on `tools/run_corrected_checks.py --active`. Reports are timestamped; preserve failures. Do not rerun generators merely to view the board.
4. For reproduction, preserve manual work first. Build/prepare corrected placement; route the saved DSN; finish the SES using a matching project sidecar. The accepted correction lineage also retains `SHM_Node_R2_before_final_gap.kicad_pcb` plus `.kicad_pro`; finishing that input with `--skip-ses`, followed by `polish_corrected_labels.py`, reproduces the last geometric operations. Rerun all appropriate checks after any regeneration; regenerated UUIDs or router paths need not be byte-identical. Never use the legacy larger-outline writers.
5. Resolve supplier stackup/USB impedance, remaining passive/switch/header MPNs, stencil/DFM, cable/enclosure/fastener clearance and mounting interface before a fabrication release. Then follow PROTOTYPE_BRINGUP for actual assembly/power/thermal/USB/I2C/DRDY/FIFO/noise/frequency-reference evidence.

## Checks not performed and assumptions

No powered hardware, fabricator DFM, controlled-impedance calculation/measurement, ESD/USB compliance, thermal load test, sensor calibration, mechanical transfer or field test was performed. No purchasing or fabrication submission occurred. Four layers, regulator/support parts and three-hole mounting pattern are documented engineering choices; supplier and fixture details remain open. Generic MPU 3D bodies are approximate visual models. Paper, firmware and original reference CAD were not edited in this continuation.

No CAD generation or routing process is intentionally left running at this handoff. Failed checks and tool defects are preserved in ERROR_LOG and MD22; do not interpret an earlier failed status as the current result or erase it after a pass.

## Preserved earlier checkpoints

# Hardware continuation handoff

## Current checkpoint — 2026-10-29

**Read `CONTINUATION_PLAN.md` first.** It contains the authoritative continuation sequence, source map, commands and acceptance gates requested by the owner. The old root R2 board still uses the wrong reference outline; the corrected work is isolated in `design/reference_corrected/` until final integration. No fabrication release exists.

Completed this continuation:

- Preserved the wrong-reference work and failed reports; bound the correct root SHM_PCB_New board by exact path/hash.
- Rebuilt the exact 12-edge, 79.50 x 50.45 mm compact outline. Moved module center to (138.9,60.20) for antenna overhang; three proposed mounting holes; backside test pads.
- Fixed J2/SW2 and H1/SW1 placement overlaps. Actual `preroute_placement_fixed.json`: **0 errors, 22 silkscreen warnings, 113 unconnected items**. This is an incomplete routing checkpoint.
- `definition_geometry_audit_20261029.json` confirms exact reference edge equality, all 148 intended spec-to-XML connected pin assignments, and the explicit firmware bus/address/interrupt constants. It does not prove completed routing.
- Added persistent mistake entries and a comprehensive continuation plan. Extended the independent verifier's source to check spec net values and firmware constants; its full final-board run remains pending.

Next: finish and check manual USB routing, regenerate placement after the logged sensor-bypass orientation correction, recheck critical power/USB copper, then route remaining nets and execute the finisher/independent verification. The new USB helper is still in progress; never interpret its absence as a completed step. Inspect files before resuming, since source/report timestamps may advance during work.

Current relevant scripts: `build_corrected_board.py`, `prepare_corrected_routing.py`, `finish_corrected_board.py`, `verify_corrected_board.py`. Legacy root board writers are not the current path. Required physical/supplier gates (stackup/USB, power/thermal, assembly, mounting, timing, frequency reference) remain open. Paper, firmware and old reference artifacts remain unchanged.

---

# Historical checkpoints (superseded where the current checkpoint differs)

# Hardware continuation handoff

Updated 2026-10-28. **State: corrected-reference geometry revision; not fabrication release.**

## Current correction and acceptance boundary

The user corrected the intended reference to **only `PCB Files/Reference PCB (OLD Version)/Thesis/SHM_PCB_New/`**. Its root `.kicad_sch` and `.kicad_pcb` are authoritative for the requested old aesthetic. Do not select the parent `Thesis.kicad_pcb` or nested `SHM_Proto_PCB` as default source.

Read-only inspection with KiCad10 pcbnew on2026-10-28 confirms the selected reference has12 edge primitives and a79.50 x50.45mm centerline extent. Reference PCB SHA-256:`372996943A9C3EB3C9087C315B7C810DF9C0B70A4E0D1B47A99E9EC81B52C23F`; schematic SHA-256:`FDEC6C2144BB29514277FDE18DD1DFC94389EF3B5C5ED57F76D1D258EDDD6D97`. The R2 PCB inspected at this checkpoint, SHA-256:`DA80B01E83B4625F8C970DF54883DBA27B5402EBCA027CB8A6274129E32A0E54`, still has the16-primitive larger outline. Exact paths/coordinates are saved in `reports/reference/reference_correction_20261028.json`.

**Status of the old R2's shape conformity: contradicted.** The prior larger-outline selection is superseded. The2026-10-26 snapshot in `../../MD Files/14_CAD_VALIDATION_SNAPSHOT.md` records zero active DRC/ERC violations for that exact old board under its configured checks. This does not establish conformity to the newly clarified reference, and no prior clearance/routing/mounting acceptance transfers automatically to the corrected outline.

Authorized corrective action: rebuild/remap layout from the selected reference geometry while retaining the current validated-by-source firmware net contract. Acceptance requires a recorded comparison to the intended outline (or explicitly approved deviation), readable reference-style schematic, firmware/pad-net consistency, footprint/fastener/antenna review, renewed source-hash-linked ERC/DRC, and honest unresolved stackup/thermal/physical limits. Root integration owns CAD/scripts and the central MD verification records; this review changed documentation and saved read-only comparison evidence only.

## Immediate continuation order

1. Use the root `SHM_PCB_New` board's exact edge geometry. Its measured old placements are reference anchors, not verified placements for the added R2 parts.
2. Re-place components and mounting holes; do not simply clip or shrink the existing83mm layout. Review USB connector reach, local decoupling, antenna exclusion, fastener access and all three sensor axes.
3. Regenerate routing/planes and applicable previews, then rerun geometry, connectivity and configured KiCad checks on the corrected source. Preserve dated reports and distinguish the old clean report from the new result.
4. Refresh `docs/PROJECT_MAP.md`, this handoff, error log, and central MD inventory/verification ledger after integration. Record any change to dimensions and its authorization.

The following sections are **historical checkpoints from2026-10-25/26**, preserved for provenance. Their workflow/status statements do not override this correction. In particular, the early autorouter incompleteness was later resolved to the narrow CAD result recorded in MD14, and the larger-outline decision is no longer current.

## Human request and scope

The user explicitly requested the correlated schematic and PCB now, after the prior firmware work. This overrides the older "after prototype" planning gate in firmware documents. They confirmed ESP32-S3-WROOM-1-N16R8 and three bare MPU-6050 ICs, one board, USB-C for external power and programming, research-supported decisions, careful schematic formatting, a similar old board aesthetic, error correction and complete AI-readable mapping.

## Work already evidenced

- Inspected three old KiCad boards read-only through KiCad10 pcbnew. Saved source SHA-256 hashes, geometry, footprints and pad/net inventory in `reports/reference/reference_inventory.json`.
- Visually reviewed existing old PCB image, exported current old schematic/PCB SVG and PNG, and rasterized the historical schematic PDF.
- Compared old net assignments and historical hardware proposals against current firmware. The active mapping is bus0 GPIO8/9, bus1 GPIO10/11, individual INT GPIO4/5/6, addresses 0x68/0x69/0x68 on buses0/0/1.
- Created navigation/constraint/decision documents, primary-source ledger, electrical decisions, error log and a prototype bring-up procedure. Physical results remain unmeasured.
- Created native schematic, project, circuit specification/netlist and intermediate placement/preroute boards. Latest inspectedOct25 ERC has zero listed violations with four ignored-check categories; later schematic edits require fresh validation.
- Corrected identified C2/C3 power-route pad orientation and J2/SW2 placement conflicts. The replacement preroute DRC atOct25 12:48:16 has zero listed errors,24 warnings and115 unconnected items. This is an intermediate result, not final board acceptance.
- Freerouting finishedOct25 12:59:27 with16 unrouted connections and18 internal violations and saved `reports/SHM_Node_R2.ses`. Root imported that session into the native board onOct26; actual KiCad post-import validation/correction is in progress.

## Historical construction strategy - superseded2026-10-28

Root integration selected the **larger top-level Thesis outline**, approximately 83.6 x 83.1 mm including its stroke, as the geometry source to provide room for mounting and the revised electronics while retaining the rounded three-lobe aesthetic. Only outline geometry is to be copied; old circuits/traces are obsolete. This differs deliberately from the reference reviewer initially preferring the smaller 79.5 x 50.45 mm version on appearance alone. Four copper layers are the current routing strategy; manufacturer stackup remains a review item.

Schematic source is `design/SHM_Node_R2.kicad_sch`; shared definition is `design/circuit_spec.json`, generated through `tools/build_schematic.py`. Board files use matching `.kicad_pro`/`.kicad_pcb`; `tools/build_board.py` and `tools/prepare_routing.py` create intermediate inputs. Regenerating a placement/preroute board can discard imported/manual routing; inspect script outputs and preserve needed edits before running. See PROJECT_MAP for the full file chain.

## Historical next actions at the October26 early checkpoint

1. Inspect the imported routed board with actual KiCad DRC, fix remaining connectivity/clearance problems, and preserve each final report rather than equating router process completion with acceptance.
2. Re-export schematic netlist and rerun ERC after current schematic edits; compare component pad/net assignments against firmware and manufacturer pinouts.
3. Review schematic readability and board silkscreen; regenerate stale previews after changes.
4. Manually review mounting clearances, antenna exclusion, USB pair/return geometry and power/thermal construction; record manufacturer stackup assumptions and unresolved physical limits.
5. Retain final source hashes, ERC/DRC/net-comparison outputs and clear remaining limitations. Update this document and PROJECT_MAP to the actual delivered state.

Physical bring-up still requires supply/ripple/transient and temperature measurements, USB enumeration/programming, dual-bus I2C rise-time checks, all three DRDY/FIFO timing checks, mechanical-coupling inspection and frequency-reference measurements. Neither old renders nor passing CAD checks establishes those results.
