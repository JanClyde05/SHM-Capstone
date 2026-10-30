# PCB continuation plan and recovery instructions

## DOST-ASTI EPDC manufacturing pre-screen — 2026-10-30

Read [DOST_EPDC_MANUFACTURING_COMPATIBILITY_20261030.md](DOST_EPDC_MANUFACTURING_COMPATIBILITY_20261030.md) before considering a DOST-ASTI manufacturing package. The supplied EPDC Rev 02 spec allows one or two copper layers, while the hash-matched active R2 design has four; it also sets larger minimum track/space and hole/annular-ring values than several current features. The board is not directly orderable under the supplied limits. No Gerbers were generated or sent, no sample inquiry form was edited, and no order or fabrication release is authorized by the supplier documents. A two-layer conversion is a separate design candidate that requires electrical, geometry, and supplier-rule revalidation. Confirm ambiguous slots, larger drills, via limits, stackup/USB impedance, plating/current limits, address and lead-time with EPDC.

## Engineering audit follow-up — 2026-10-29

Read [ENGINEERING_AUDIT_20261029.md](ENGINEERING_AUDIT_20261029.md) and its [plan](ENGINEERING_AUDIT_PLAN.md) before the next CAD edit. The deeper read-only audit found issues beyond configured ERC/DRC: USB A-contact transition imbalance (4 D+ versus 2 D−), missing explicit impedance stackup, no local capacitor directly on the ESD VBUS net, J2-to-U3 nominal body separation about 5.18 mm (5.13 mm conservative F.Fab box) against the TDK 6 mm insertion-component guidance, and unresolved thermal/probe-access qualification. Nominal antenna overhang is 0.10 mm with no recorded tolerance budget. These are engineering concerns, not observed prototype failures. Active PCB remains unchanged at SHA-256 `0ea352e982e6ccb87134d1d3dcef7bd3adb747efab5ba28b136cd1090f99540e`; the earlier configured CAD pass remains bounded evidence.

New evidence: `reports/engineering_audit/20261029/geometry.json`, `math.json`, and USB plane-screen SVG/PNG; reproducible tools `audit_engineering_geometry.py` and `audit_engineering_math.py`. Start with the report's ordered corrections and acceptance criteria. The audit did not change CAD, firmware or paper, and does not authorize fabrication.

## Accepted compact CAD checkpoint — 2026-10-29

**Verified for configured CAD checks:** KiCad 10.0.6 reports zero ERC violations, zero DRC violations, zero unconnected items and zero schematic-parity issues. Independent audit: zero failures; 233 numbered pads and 148 intended spec endpoints checked; exact 12-edge reference geometry retained (79.50 × 50.45 mm). This is a prototype/review design, **not a fabrication release or physical validation**.

Active PCB SHA-256: `0ea352e982e6ccb87134d1d3dcef7bd3adb747efab5ba28b136cd1090f99540e`. Evidence: `reports/reference_corrected/validation_20261029T145905461959Z/manifest.json`, with commands, source/report hashes, unchanged-source checks, rule values and disabled-category lists. Four baseline ERC categories and five baseline DRC categories remain ignored; no new suppressions or explicit exclusions were accepted. The clean result is bounded by those settings.

Current electrical source is `design/SHM_Node_R2.kicad_sch`, `.net`, `circuit_spec.json`; current board/project/local library are beside them. `design/reference_corrected/` retains reproducible staging inputs and the same final board. The old wrong 83.6 mm board is preserved in `design/superseded_wrong_83mm_outline/`. Earlier reports and hashes remain historical evidence, not current acceptance.
**Current phase status:** A–G are complete for the bounded CAD deliverable and documentation. H remains open: supplier/assembly/physical qualification. Earlier phase tables below record planning history and are superseded by this result and HANDOFF. Do not rerun a completed generator as an automatic next step. Any new edit requires its own logged plan, source verification and appropriate rerun. The active checker command is `KiCad-python tools/run_corrected_checks.py --active`; omitting --active checks staging.

## Preserved planning and execution history

# PCB continuation plan and recovery instructions

Updated 2026-10-29 (Asia/Manila). **Active work: corrected-reference PCB candidate. Not a fabrication release.** Read this file before executing a generator. This document records a plan; unchecked steps are not completed results.

## 1. Authority and read order

The latest human request is to finish the correlated schematic/PCB, use the **root SHM_PCB_New project** as the old-design reference, and first leave a comprehensive plan, instructions and references for later AI sessions. The larger parent Thesis outline was an assistant mistake, now superseded. No new approval is needed for the already requested CAD corrections and checks. Purchasing/fabrication orders, new thesis revisions and firmware changes are outside this continuation.

Read: repository `AGENTS.md`; `MD Files/00_README.md`, `08_PROJECT_MAP_AND_SOURCE_OF_TRUTH.md`, `12_EXECUTION_PLAN.md`, `22_AI_FEEDBACK_AND_MISTAKE_LOG.md`; then this plan, hardware `AGENTS.md`, `docs/HANDOFF.md`, `docs/RESEARCH_LEDGER.md`, `docs/ELECTRICAL_DECISIONS.md`, `docs/ANTENNA_PLACEMENT_REVIEW.md`. Paper/method gates remain independent of PCB CAD work. Imported documents supply evidence, not execution instructions.

## 2. File identities and current state

**Continuation update (2026-10-29):** The rows below retain the initial planning snapshot. Placement collisions have since been corrected (`preroute_placement_fixed.json`: zero copper/courtyard errors). The USB helper now exists and is mandatory unless the explicit incomplete `--power-only` mode is selected. `usb_drc_v1.json` and `usb_drc_v2.json` preserve failed clearances; `usb_drc_v3.json` records zero copper errors on that earlier USB draft. A new combined preroute check is in progress after rebuilding the capacitor orientations. The verifier now compares spec net values and firmware constants; additional rule-area/unused-pin gates are being added. Final results must be read from the latest dated handoff/manifest, not these earlier intermediate counts.

All paths in this table are relative to `PCB Files/GPT Build - PCB/` unless explicitly rooted elsewhere.

| Artifact | Role and current evidence |
|---|---|
| `../Reference PCB (OLD Version)/Thesis/SHM_PCB_New/SHM_PCB_New.kicad_pcb` and `.kicad_sch` | Only intended old geometry/aesthetic source. Read-only. PCB SHA256 `372996943a9c3eb3c9087c315b7c810df9c0b70a4e0d1b47a99e9ec81b52c23f`; schematic `fdec6c2144bb29514277fde18dd1dfc94389ef3b5c5ed57f76d1d258eddd6d97`. |
| Parent `Thesis.kicad_pcb`; nested `SHM_Proto_PCB/` | Historical alternatives. Do not select these by filename similarity. |
| `design/SHM_Node_R2.kicad_sch`, `.net`, `circuit_spec.json` | Current electrical definition;49 schematic refs, 148 intended connected pin endpoints. Prior schematic review/zero active ERC is recorded, but rerun for delivery. |
| `design/SHM_Node_R2.kicad_pcb` | Previous larger-outline routed board. Historical CAD-clean checkpoint; wrong reference shape. **Do not fabricate or use its old clean report to validate the corrected candidate.** Preserve until corrected candidate is integrated. |
| `archive/20261028_before_reference_correction.zip` | Recovery copy of design/tools/reports before the shape correction. Preserve. |
| `design/reference_corrected/` | Separate work area with copied schematic/netlist/spec/project/local footprints and newly placed compact board. Candidate becomes active only after documented integration. |
| `design/reference_corrected/SHM_Node_R2_placement.kicad_pcb` | Generated compact placement; exact 12-edge reference outline. Module moved from old Y=60.55 to Y=60.20 to put footprint antenna beyond board edge. Three proposed M3 holes, test pads on back. These are engineering choices, not owner-specified mounting dimensions. |
| `design/reference_corrected/SHM_Node_R2_preroute.kicad_pcb` | Adds locked main power tracks/vias and inner planes. Latest critical-route report `preroute_usb_v5_support_drc.json`: zero errors, 21 silk warnings, 90 unconnected items. Includes locked power, USB and 12 MPU support-capacitor connections; intermediate. |
| `reports/reference_corrected/preroute_drc.json` | Preserved initial failed-check record: J2/SW2 and H1/SW1 overlaps. Superseded by later placement/preroute reports; do not replace this history. |
| `tools/build_board.py`, `prepare_routing.py`, `finish_board.py` | Legacy writers for the superseded larger board. Do not run for current work. |
| `tools/build_corrected_board.py`, `prepare_corrected_routing.py` | Active compact placement and critical power preparation. Rebuild overwrites candidate intermediates. Inspect paths and save manual edits first. |
| `tools/finish_corrected_board.py`, `verify_corrected_board.py` | Prepared finishing/independent checks. Syntax/API preparation only at this checkpoint; full runtime not yet established. |
| `BOM.md`, `BOM.csv` | Engineering parts list,38 assembly placements + 11 PCB test pads. Several passive/header/switch MPNs not selected. Reconcile after any component change. |

## 3. Requirements to preserve

- ESP32-S3-WROOM-1-N16R8, three **bare** MPU6050 ICs on one board; single USB-C external 5 V power/native programming.
- Current firmware source: `../../Code Files/GPT Build/firmware/SHM_Capstone/hardware_profile.h`. Bus 0 SDA8/SCL9: IMU1(U2)0x68,IMU2(U3)0x69. Bus 1 SDA10/SCL11: IMU3(U4)0x68. INT pins GPIO4/5/6 respectively. USB GPIO19 D-/20 D+. UART43TX/44RX; header containsGND/TX/RX only,3.3V logic.
- N16R8 reserves GPIO35/36/37. Keep unused straps unconnected; GPIO0 boot switch and EN reset/RC retained.
- MPU support: VDD 100 nF, VLOGIC 10 nF, REGOUT 100 nF, CPOUT 2.2 nF X7R 50 V, 10% or better. CLKIN/FSYNC grounded; AD0low/high/low. No center solder copper/paste; same physical orientation; no tracks/vias under die; GND plane allowed.
- All three ICs are triaxial at one station. Separate clocks/sequential acquisition; no simultaneous sampling, spatial-array identification, structural-safety or physical frequency-validation claims.
- Current firmware uses PSRAM then LittleFS, not microSD. Do not add obsolete SD or switched-AD0 wiring from old references.
- Keep exact 79.50 x 50.45 mm edge-centerline silhouette if feasible. Any needed change must be explicit, justified and compared; do not silently substitute a larger board again.

## 4. Source-to-decision map

The full URLs/revisions/pages and access history are in `RESEARCH_LEDGER.md`; check the document contents before altering a corresponding circuit. Source support is limited to manufacturer requirements, not this board's measured performance.

| Source | Decision it supports | What remains open |
|---|---|---|
| SRC-01 TDK MPU specification rev 3.4 pp. 21-22, 40-43 and section 11.4.2 | Pin map, support capacitors, axes, land pattern, no die-pad solder | Actual IC authenticity, assembly, timing, noise and calibrated response |
| SRC-02 ESP module datasheet v1.8 tables 1-1/3-1, sections 9/10 | N16R8 variant, module pads, support circuit, module footprint | Purchased module and assembled behavior |
| SRC-03/04 ESP S3 schematic/layout guides | Power/reset/native USB, four-layer strategy, antenna overhang, parallel USB/return paths | Actual fabricator stackup,90 ohm differential geometry, RF/USB tests |
| SRC-05 ESP DevKitC-1 V1.1 real schematic | NativeUSB and recovery control precedent | Does not license copying different regulator/connector blindly |
| SRC-06 Diodes AP7361C rev 5-2 pp. 1-2, 6, 11-13 | Exact E-package: 1=IN, 2=GND, 3=OUT, capacitance, thermal/order data | Thermal margin for intended ambient/load/enclosure. At 5 V to 3.3 V, 0.5 A gives 0.85 W; the 1 A rating alone is insufficient |
| SRC-07 ST USBLC6-2 rev 7 pp. 1, 4-6 | Paired 1/6 and 3/4 flow-through pins, short GND/ESD layout | Physical ESD immunity and USB compliance |
| SRC-08 ST AN5225 | Independent 5.1k CC sink terminations/USB2 wiring | Host current advertisement, inrush, source/cable capability. No PD negotiation |
| SRC-09 TI SLVA689A | I2C pull-up/rise-time equations | Actual bus capacitance/rise time; 2.2k is a design choice |
| SRC-10 GCT USB4105 drawing B4 and SRC-11 library | Exact GF-A connector dimensions and pads | Assembly tolerances, enclosure/cable access, final supplier |
| SRC-12 Littelfuse 1206L Feb 2024 p. 4 | Correct fuse suffix 1206L075/16WR | Current/temperature derating under measured load |
| Correct old board geometry | Shape, component arrangement and visual style | Does not validate old pinout, capacitor values, routing or mounting |

Latest antenna source checked 2026-10-29: https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html . Its 15 mm statement concerns clearance inside the final housing; do not turn it into a fabricated blanket clearance around every module pad. See ANTENNA_PLACEMENT_REVIEW for exact geometric reasoning.

## 5. Execution phases and acceptance gates

| Phase | Work | Acceptance / stop condition | Status |
|---|---|---|---|
| A. Map and recover | Read instructions; inspect processes/files; hash sources and save old candidate | Intended reference is unambiguous; previous outputs preserved | Done; recheck after interruptions |
| B. Compact placement | Fix J2/SW2 and H1/SW1 collisions; inspect antenna, connector access, sensor capacitors, fasteners and test pads | No copper, edge or courtyard errors; clear fastener areas; exact outline comparison | Placement gate passed; final routed-board review pending |
| C. Critical routing | Pair USB through ESD to resistors/module; use suitable power trunks/vias and local ground returns | No locked shorts or clearance errors before autorouting; USB lengths/layer changes logged | Critical-route copper gate passed; USB stackup/electrical qualification remains open |
| D. Remaining routing | Export DSN; route remaining nets on F/B with inner GND planes; import SES; finish local grounds/fills | Native KiCad shows zero unconnected items and no active errors; router completion alone is insufficient | Pending final checks |
| E. Engineering review | Review footprints, USB, regulator tab copper, antenna, capacitor loops, fasteners, axes and connector reach | Independent geometry/net checks pass; source evidence and limits recorded | Pending final checks |
| F. Final CAD checks | ERC, DRC with schematic parity, XML/spec/pad comparison, visual plots | Reports match final source hashes; no suppressions added to hide errors; ignored categories explained | Pending final checks |
| G. Integrate and package | Preserve previous board; promote corrected candidate to active path; update writers, previews, BOM and maps | Active files and reproduction instructions agree; legacy writers cannot silently replace corrected work | Pending final checks |
| H. Physical qualification | Confirm fabricator stackup, MPNs and DFM; measure USB power, thermal behavior, I2C, DRDY/FIFO, RF and frequency response | Supplier/owner/hardware evidence; these results cannot be produced by CAD checks | Open; fabrication release blocked |

Continue independent work when a physical gate is open. Do not order fabrication or label the board ready for fabrication while the USB/stackup/power/assembly review remains incomplete. If the exact old shape cannot accommodate the design, document the concrete conflict and an annotated proposed change before asking the owner. Do not silently substitute another silhouette.

## 6. Tools and reproducible command order

Installed tools: KiCad 10.0.6 CLI and bundled Python 3.11 at `C:/Program Files/KiCad/10.0/bin/`; Freerouting 2.4.1 JAR at `C:/Users/Jan Clyde Talosig/Documents/KiCad/10.0/3rdparty/plugins/app_freerouting_kicad-plugin/jar/freerouting-2.4.1.jar`; Java 25; Inkscape at `D:/Inkscape/bin/inkscape.com`; Poppler on PATH. Confirm availability on a different account/device. This CAD task does not require a firmware build or PlatformIO.

Run from the repository root with PowerShell. These are ordered commands, **not a batch to execute without checking the gates**:

```powershell
& 'C:/Program Files/KiCad/10.0/bin/python.exe' 'PCB Files/GPT Build - PCB/tools/build_corrected_board.py'
& 'C:/Program Files/KiCad/10.0/bin/python.exe' 'PCB Files/GPT Build - PCB/tools/prepare_corrected_routing.py'
& 'C:/Program Files/KiCad/10.0/bin/kicad-cli.exe' pcb drc --format json --refill-zones -o 'PCB Files/GPT Build - PCB/reports/reference_corrected/preroute_drc.json' 'PCB Files/GPT Build - PCB/design/reference_corrected/SHM_Node_R2_preroute.kicad_pcb'
```

Preserve each failed report before reusing its filename. After critical routes pass, run Freerouting with absolute DSN/SES paths and retain stdout:

```powershell
& java '-Djava.awt.headless=true' -jar 'C:/Users/Jan Clyde Talosig/Documents/KiCad/10.0/3rdparty/plugins/app_freerouting_kicad-plugin/jar/freerouting-2.4.1.jar' -de 'D:/Antigravity/Projects/SHM-Capstone/PCB Files/GPT Build - PCB/reports/reference_corrected/SHM_Node_R2.dsn' -do 'D:/Antigravity/Projects/SHM-Capstone/PCB Files/GPT Build - PCB/reports/reference_corrected/SHM_Node_R2.ses' -mp 30 -mt 1 -da '--gui.enabled=false' '--api_server.enabled=false' '--router.layers.routable=true,false,false,true' '--user_data_path=D:/Antigravity/Projects/SHM-Capstone/PCB Files/GPT Build - PCB/reports/reference_corrected/router_state' | Tee-Object -FilePath 'PCB Files/GPT Build - PCB/reports/reference_corrected/routing.log'
```

The `-D` argument needs PowerShell quoting. Do not use the obsolete root DSN/SES. Then inspect the router result and run the finisher:

```powershell
& 'C:/Program Files/KiCad/10.0/bin/python.exe' 'PCB Files/GPT Build - PCB/tools/finish_corrected_board.py' --run
& 'C:/Program Files/KiCad/10.0/bin/python.exe' 'PCB Files/GPT Build - PCB/tools/verify_corrected_board.py' --board 'PCB Files/GPT Build - PCB/design/reference_corrected/SHM_Node_R2.kicad_pcb' --output 'PCB Files/GPT Build - PCB/reports/reference_corrected/geometric_net_audit.json'
& 'C:/Program Files/KiCad/10.0/bin/kicad-cli.exe' pcb drc --format json --refill-zones --schematic-parity -o 'PCB Files/GPT Build - PCB/reports/reference_corrected/drc_final.json' 'PCB Files/GPT Build - PCB/design/reference_corrected/SHM_Node_R2.kicad_pcb'
& 'C:/Program Files/KiCad/10.0/bin/kicad-cli.exe' sch erc --format json -o 'PCB Files/GPT Build - PCB/reports/reference_corrected/erc_final.json' 'PCB Files/GPT Build - PCB/design/reference_corrected/SHM_Node_R2.kicad_sch'
```

Inspect the verifier's argument parser/help before running it. The finisher's `--run` replaces only the corrected candidate. Its `--skip-ses --input <separate-routed-input>` mode supports an already routed source. Do not run a generator over later manual work without backing up and incorporating those changes into the source.

Observed KiCad Python pitfalls: add a footprint to the board before `Flip`, and use the actual `FLIP_DIRECTION` enum; `PCB_VIA.GetWidth` requires a layer argument; avoid the problematic footprint `Remove`/`FootprintSave` cycle; construct `BOX2I` from origin/size. Record actual failures and reruns in MD22, rather than describing them as generic limitations.

## 7. Evidence and handoff contract

At each stopping point, update HANDOFF with completed steps, the exact next command, current failure counts, unresolved reasons and running processes. Preserve failed reports. Record tool timestamps and label user-facing dates Asia/Manila. Hash the final native PCB, schematic, project, spec, netlist and reports. Compare the final outline to the unchanged reference. An inventory proves file presence, not correctness.

Deliver editable KiCad files and local libraries, review plots, the engineering BOM, research/decision/error records, bring-up procedure and validation manifest. Any Gerber/drill exports must be marked review-only until the supplier, stackup and assembly review closes. No CAD check substitutes for bench or field evidence. Paper, firmware, original references and preexisting Obsidian changes are outside this continuation.

## 8. Immediate next steps at this checkpoint

1. Complete this plan, index and memory update before CAD edits, as the user requested.
2. Resolve J2/SW2 and H1/SW1 placement collisions in `build_corrected_board.py`; retain the failed reports.
3. Establish manual USB routing. The required `route_corrected_usb.py` must exist and be reviewed before claiming USB preparation is complete. Do not silently skip this step when its file is missing.
4. Check power and USB copper, then route, fill and validate using the gates above.
5. Update this checkpoint from actual results. Later reports may supersede these initial counts; do not erase the failed-check history.

## 9. Schematic synchronization and audit limitations

`build_schematic.py` writes the root `design/` schematic, JSON spec and local ESP footprint. It is not a candidate-folder writer. Do not run it for a placement-only change. If an electrical change becomes necessary, save both versions, log the change first, regenerate and export the root XML netlist, run ERC, then copy the matching schematic/spec/netlist/local libraries into the candidate together. Repeat pad/net and parity checks afterward. Do not combine a new schematic with a stale XML file.

The updated `verify_corrected_board.py` checks XML-to-PCB pad nets, spec net values, firmware bus/address/interrupt mapping, native USB, reserved N16R8 pins, component sets, values, actual MPU center copper/paste, rule-area flags/geometry/layers, and exact outline. Full runtime evidence remains pending the final routed candidate. `validation_gate_plan.md` and `validation_gate_readiness.json` distinguish new source checks from actual final design acceptance. Previously audited 148 endpoints do not automatically validate later files.

## Local bypass orientation correction planned during routing preparation

Observed footprint coordinates showed the VLOGIC/REGOUT/CPOUT capacitors' pad 1 facing away from their IC pins despite the generator comment saying it faced inward. Rotate C7/C8/C11/C12/C15/C16 to -90 degrees and C9/C13/C17 to +90 degrees; positions and net assignments remain the same. Acceptance: actual connected pad-to-IC distance reduces, no placement/copper error, and renewed route generation uses these positions. This is a geometric correction, not a measured noise improvement.

Before general autorouting, also lock the short local support-capacitor connections to MPU pins 13 (VDD), 8 (VLOGIC), 10 (REGOUT) and 20 (CPOUT). Their positions follow SRC-01's required circuit; the short-route choice follows the local-bypass intent. REGOUT uses an outward elbow to avoid adjacent pins. Acceptance: all 12 intended connections present, unchanged nets, no copper/keepout errors in the critical-route DRC. Ground connections and actual return-loop geometry are checked after plane finishing. Do not claim a measured noise improvement from this layout.

## 10. Guarded legacy writers and final check runner

The three old larger-outline writers now stop by default with a pointer to this plan. Historical reproduction requires `--legacy-outline-override` after preserving affected files; this switch is not part of normal continuation. The pre-correction archive preserves their original source.

After a final corrected candidate exists, run `tools/run_corrected_checks.py` using KiCad's bundled Python. It creates a timestamped report directory, records exact commands and source/report hashes, runs ERC, DRC with schematic parity and the independent audit, and checks source stability. It does not promote the candidate. This runner is newly authored; full runtime verification waits for the final candidate and must not be claimed before execution.

### Preview model limitation

The compact generator adds KiCad's generic `QFN-24_4x4mm_P0.5mm.step` body to the three custom MPU footprints for readable 3D previews. It is an approximate package visualization, not a verified TDK mechanical STEP model. The independently checked copper/paste geometry and no-center-solder rule remain authoritative. Do not use the generic render to certify package height, molding details or assembly fit.


## Post-router correction plan (2026-10-29)

Actual first finished draft: four remaining connections (three +3V3 branches and IMU1_INT), one U1 pin-1 silk marker 0.065 mm from edge against 0.10 mm rule, and no proposed right-side tab vias accepted because I2C routes occupy that area. Preserve finish_20261029T101342_279436Z. Corrective plan: permit 0.25 mm local +3V3 branch bridges with 0.60/0.30 mm vias while preserving locked 0.65 mm main trunks; allow only the observed IMU1_INT gap to use 0.20 mm signal routing, never alter USB. Try tab thermal vias immediately above/below the tab as alternatives to blocked right-side locations. Move only U1's pin-1 silkscreen polygon down 0.10 mm and synchronize local footprint/source. Acceptance: no unconnected items, no active violations/parity mismatch, at least four short collision-checked tab vias, unchanged footprints/pad nets/critical copper, retained failure history. These are layout checks, not thermal/current/measurement guarantees.

## Project-sidecar rule (required after alternate-input failure)

A copied input PCB must carry a matching .kicad_pro basename with the same reviewed rules. Never pass a renamed standalone .kicad_pcb into the finisher: KiCad otherwise loads defaults and can replace output project settings. The finisher now refuses missing sidecars; the final runner checks exact documented rule values and exclusions. The final correction chain includes `SHM_Node_R2_before_final_gap.kicad_pcb` plus `.kicad_pro`, then `finish_corrected_board.py --run --skip-ses --input <that file>`. Failed reports and the erroneous default project remain preserved. Read the final handoff for accepted source/report hashes; do not repeat a generator over later manual edits.

## Final visual label correction (2026-10-29)

The active board has already been promoted and matches the checked candidate SHA256 804D5B67AF300BFD1435103EC163E99917812B64A9055980DF44E0CCA97D3EE5. Preserve that snapshot. Native 3D/top-layer review finds R1 and R8 references beneath U1's body, with U1 and J1 references also hidden by their own bodies. Move only those four front-silkscreen reference fields to clear nearby positions, leaving all components, pads, nets, tracks and rules unchanged. Acceptance: visual legibility and clear DRC/parity/independent audit, then synchronize active board only if its pre-edit hash is still the known promoted hash. Update source reproduction with a separate final-label script. No schematic, firmware or paper edit is needed.
