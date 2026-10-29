# Corrected compact PCB engineering review

Updated 2026-10-29, Asia/Manila. This document distinguishes CAD facts from unmeasured hardware behavior. Read CONTINUATION_PLAN and the latest HANDOFF for current completion status.

## Scope and sources

User-selected geometry is the root SHM_PCB_New board, not the parent Thesis or nested SHM_Proto_PCB project. The reference is read-only. Current electrical definition is circuit_spec.json plus the Eeschema XML netlist, correlated to hardware_profile.h. The manuscript and firmware are unchanged during this layout correction.

Manufacturer source locations and limitations are recorded in RESEARCH_LEDGER: SRC-01 MPU support/land pattern; SRC-02 module pinout; SRC-04 layer/USB/module positioning guidance; SRC-06 regulator pinout/thermal conditions; SRC-07 ESD flow-through pins; SRC-10 connector mechanics. The 2026-10-29 web recheck covered SRC-04 USB requirements and SRC-07 functional pin diagram.

## Observed design and engineering choices

| Concern | CAD evidence / choice | Scope and remaining gate |
|---|---|---|
| Outline | Exact 12-edge silhouette, 79.50 by 50.45 mm edge-centerline extent | Final independent audit must compare each edge to the unmodified reference |
| Controller | N16R8 module, native USB GPIO19/20, two I2C buses, three interrupt inputs | Pad/net agreement does not establish purchased-module identity or assembled function |
| Sensor identity | U2=IMU1 bus0/address0x68; U3=IMU2 bus0/0x69; U4=IMU3 bus1/0x68; all at 0 degrees | Three complete triaxial channels at one station; no synchronized-clock or spatial-array claim |
| MPU land pattern | 24 peripheral pads, no center copper/paste pad; center track/via exclusion with ground planes allowed | Source-backed geometry; stencil/assembly and real packages still need review |
| Sensor capacitors | Four required support connections per MPU are locked short routes before autorouting; pad 1 faces the IC | CAD geometry, not measured noise or frequency accuracy; final ground returns reviewed separately |
| USB connector and ESD | Side-entry USB4105-GF-A; mirrored data pins joined locally; USBLC6 pin1/6 D-, pin3/4 D+, short GND return | Cable/enclosure clearance and physical ESD/USB tests remain open |
| USB routing | 0.20 mm track width; approximately 0.20 mm vertical pair edge gap and 0.1536 mm diagonal gap; explicit layer return vias | Provisional geometry only. Supplier stackup must establish 90 ohm differential impedance within the manufacturer's stated tolerance; no impedance result exists |
| USB length review | Saved v5 preroute graph: signed planar mismatch +0.074840 mm (A contacts), -0.078714 mm (B contacts), including MCU-side traces | Excludes via depth, pad and resistor internals. A-side D+ has two more transitions; this is not matched electrical delay. Recheck final imported board |
| Power | Locked 0.65 mm main trunks with paired layer-change vias; local supply branches routed separately | Width does not establish current/thermal margin. USB source capability, inrush and burst droop require measurements |
| Regulator | AP7361C-33E-13, grounded tab; finisher adds collision-checked tab vias and solid GND connection | Actual filled copper and via count must be recorded after finishing. No temperature guarantee; buck redesign remains a contingent option if testing fails |
| Layers | Four copper layers; both inner layers GND references; signals on outer layers | Chosen construction, not inherited two-layer reference. Plane presence alone does not prove return continuity |
| Antenna | Module center (138.9,60.20); footprint antenna beyond top baseboard edge; explicit all-layer exclusion | Final enclosure and RF tests still required; generic preview is not RF evidence |
| Mounting | Three proposed 3.2 mm NPTH holes H1-H3 with 3.3 mm radius copper keepouts | Fastener/enclosure dimensions and rigid coupling to the roadway deck are not validated |
| Preview | Native KiCad 3D render shows all three sensor packages and the selected silhouette | MPU STEP is generic package visualization, not a verified manufacturer mechanical model |

## Review sequence and acceptance

Before general routing, `preroute_usb_v5_support_drc.json` reports zero errors, 21 silk warnings and 90 unconnected items. These are intentionally incomplete routing facts. Failed v1/v2/v4 reports remain preserved. The final board must pass schematic parity/connectivity, explicit geometry/net/constraint checks, and visual top/bottom copper and silkscreen review. Import must preserve placements and locked tracks. Actual final report paths, hashes and residual issues belong in HANDOFF and the validation manifest.

Supplier stackup, passive/switch/header MPN selection, DFM/stencil review, assembly inspection, supply/thermal/USB/I2C measurements, sensor timing/calibration and field performance remain open. A clean CAD result cannot close these gates.

## Accepted compact CAD checkpoint — 2026-10-29

**Verified for configured CAD checks:** KiCad 10.0.6 reports zero ERC violations, zero DRC violations, zero unconnected items and zero schematic-parity issues. Independent audit: zero failures; 233 numbered pads and 148 intended spec endpoints checked; exact 12-edge reference geometry retained (79.50 × 50.45 mm). This is a prototype/review design, **not a fabrication release or physical validation**.

Active PCB SHA-256: `0ea352e982e6ccb87134d1d3dcef7bd3adb747efab5ba28b136cd1090f99540e`. Evidence: `reports/reference_corrected/validation_20261029T145905461959Z/manifest.json`, with commands, source/report hashes, unchanged-source checks, rule values and disabled-category lists. Four baseline ERC categories and five baseline DRC categories remain ignored; no new suppressions or explicit exclusions were accepted. The clean result is bounded by those settings.

Current electrical source is `design/SHM_Node_R2.kicad_sch`, `.net`, `circuit_spec.json`; current board/project/local library are beside them. `design/reference_corrected/` retains reproducible staging inputs and the same final board. The old wrong 83.6 mm board is preserved in `design/superseded_wrong_83mm_outline/`. Earlier reports and hashes remain historical evidence, not current acceptance.
Final visual scope: inspected top/bottom copper plots, latest 1600×1100 top/bottom native 3D renders and the unchanged full schematic export. No crossing/overlap was inferred from images alone; actual connectivity and clearance checks are in the manifest. Eight regulator tab vias and the four visible reference-label corrections are present. Selected stackup, actual impedance, mounting/cable envelope and physical thermal/measurement qualification remain open.

## Engineering audit follow-up — 2026-10-29

Read [ENGINEERING_AUDIT_20261029.md](ENGINEERING_AUDIT_20261029.md) and its [plan](ENGINEERING_AUDIT_PLAN.md) before the next CAD edit. The deeper read-only audit found issues beyond configured ERC/DRC: USB A-contact transition imbalance (4 D+ versus 2 D−), missing explicit impedance stackup, no local capacitor directly on the ESD VBUS net, J2-to-U3 nominal body separation about 5.18 mm (5.13 mm conservative F.Fab box) against the TDK 6 mm insertion-component guidance, and unresolved thermal/probe-access qualification. Nominal antenna overhang is 0.10 mm with no recorded tolerance budget. These are engineering concerns, not observed prototype failures. Active PCB remains unchanged at SHA-256 `0ea352e982e6ccb87134d1d3dcef7bd3adb747efab5ba28b136cd1090f99540e`; the earlier configured CAD pass remains bounded evidence.

New evidence: `reports/engineering_audit/20261029/geometry.json`, `math.json`, and USB plane-screen SVG/PNG; reproducible tools `audit_engineering_geometry.py` and `audit_engineering_math.py`. Start with the report's ordered corrections and acceptance criteria. The audit did not change CAD, firmware or paper, and does not authorize fabrication.

