# Independent electrical audit

Audit date: 2026-10-25. Scope: current schematic/exported netlist, circuit specification and placement/preroute boards. This review does not certify the later routed PCB; rerun pad/net correlation and inspect its actual routing after the final board is generated.

## Result

The reviewed power, native USB and three MPU-6050 circuits agree with the primary-source pin connections in [ELECTRICAL_DECISIONS.md](ELECTRICAL_DECISIONS.md). One definite procurement metadata error and one incomplete assembly specification were identified and sent to the schematic owner. Final routing, source-current compliance and thermal suitability remain unresolved at this audit snapshot.

## Checks actually performed

1. Read `design/circuit_spec.json`, `design/SHM_Node_R2.net`, the local MPU footprint, `tools/build_board.py`, `tools/prepare_routing.py`, and `reports/erc_current.json`.
2. Parsed the Eeschema XML export and compared **148 specified package-pin endpoints** against the independent circuit specification: **zero endpoint/net mismatches after removing the root-sheet slash**.
3. Loaded both `SHM_Node_R2_placement.kicad_pcb` and `SHM_Node_R2_preroute.kicad_pcb` through installed KiCad10 `pcbnew`; every specified pad had the intended net, including duplicated connector power/ground pads. This checks assignments, not routed continuity.
4. Checked all three MPU footprints: exactly24 pads, no pad25, orientation0° on all three. The copper land geometry follows manufacturer0.5mm pitch,0.35mm width,0.80/0.85mm radial length and4.80mm outer extent. Each board contains the three die no-track/no-via rule areas and antenna clearance area.
5. Confirmed four copper layers and two inner ground zones. At the snapshot, placement had0 track objects and preroute had12; neither is a completed routed board.
6. Read actual ERC output: no errors/warnings among enabled checks. The report also lists the standard disabled check categories; do not describe it as all conceivable electrical checks enabled.

## Findings requiring closure

| ID | Finding | Required resolution / status at review |
| --- | --- | --- |
| AUD-E-01 | F1 field uses `1206L075/16YR`; manufacturer ordering table specifies **1206L075/16WR**. | Correct generator, schematic metadata and circuit spec; regenerate netlist/render. The source family URL alone does not validate an invented suffix. Owner notified. |
| AUD-E-02 | MPU capacitors have voltage and X7R fields but no tolerance field. | Record10% or tighter for the four manufacturer-specified local capacitors per IC, especially C9/C13/C17 (2.2nF50V). Owner notified. |
| AUD-E-03 | LDO power dissipation has not been qualified on this board. | AP7361C SOT223 can dissipate0.85W at0.5A from5V. Datasheet minimal-layout thetaJA110°C/W implies a93.5°C rise; actual copper can change this. Provide direct tab-to-ground heat spreading/vias and measure worst-case load/ambient. Do not call the finished power path a1A continuous supply based only on its silicon rating. |
| AUD-E-04 | Passive CC resistors do not measure source current capability. | Verify prototype load/inrush and use a documented suitable source. Device does not thereby gain permission to draw1A from arbitrary USB hosts. |
| AUD-E-05 | Schematic root-sheet labels export `/GND`, `/+3V3`, etc.; generated board uses `GND`, `+3V3`, etc. | Electrical node grouping matches, but normalize names or explain expected rename before KiCad Update PCB from Schematic. No hidden connectivity defect was found from this difference. |
| AUD-E-06 | Final USB topology, ground returns, thermal copper and final DRC are outside the preroute snapshot. | Inspect actual final route: connector duplicated data pins join at connector, ESD path flows through U6,22Ω resistors remain near U1, pair is routed together over intact ground, die keepouts and antenna keepout honored. Generic autorouting does not prove differential impedance. |

## Verified circuit details

- **U5 AP7361C-33E-13:** pad1 input, pad2/tab ground, pad3 output. C1=4.7µF input and C2=10µF output are nominally above datasheet minima; actual effective ceramic capacitance awaits selected parts. C3/C4 provide local module bulk/bypass. No1117 pin swap was found.
- **U2/U3/U4:** VLOGIC and VDD are3V3, CLKIN/FSYNC ground, REGOUT gets100nF only, CPOUT gets2.2nF50V only. AD0 is low/high/low. Reserved19/21/22 and unused auxiliary pins remain isolated. Each INT reaches its separate GPIO. Center pad is absent, consistent with the MPU-specific no-solder instruction.
- **J1/U6:** CC1/CC2 each have5.1kΩ1% to ground; neither is shorted to the other. D+ maps toGPIO20 and D− toGPIO19 through22Ω. USBLC6 pins1/6 useD−,3/4 useD+,2ground,5VBUS. Connector SBU pins are open.
- **U1:** N16R8 reservedGPIO35/36/37 remain unconnected. EN has10kΩ/1µF and reset-to-ground; GPIO0 has10kΩ and boot-to-ground. UART header is signal/ground only, avoiding an accidental second supply source.

## Sources checked during this audit

Main source IDs resolve through [RESEARCH_LEDGER.md](RESEARCH_LEDGER.md): SRC-01 MPU product specification pp21–23 and41–43; SRC-02 module datasheet Table3-1 and§9; SRC-03/SRC-04 Espressif schematic/layout guidance; SRC-06 regulator pp1–2,6,11–13; SRC-07 USBLC6 diagram; SRC-08 USB-C CC tables; SRC-10 GCT drawing.

Additional primary source: [Littelfuse1206L datasheet, revised2024-02-26](https://www.littelfuse.com/assetdocs/littelfuse-ptc-1206l-datasheet?assetguid=2b6a1515-d4ee-4c83-8bd4-152b4901b8f5), five pages, read online. Printedp4 lists1206L075/16WR; p1 gives0.75A hold at20°C and1.5A trip; p2 gives hold-current derating (0.59A at50°C,0.54A at60°C). The fuse selection is plausible for a prototype, but local heat/load must be measured and the0.75A label is not a temperature-independent current guarantee.

## Closure record

The main agent should append each correction and final report path here after regenerating artifacts. Preserve this distinction between the initial audit snapshot and a later verified result; do not silently rewrite a failed finding as if it had never occurred.

### 2026-10-26 verified corrections

- **AUD-E-01 closed:** regenerated `circuit_spec.json` records F1=`1206L075/16WR`, using the exact manufacturer PDF URL. The schematic owner regenerated the native schematic and exported XML.
- **AUD-E-02 closed:** all C6-C17 now have `Tolerance: 10% or better`; C9/C13/C17 retain50V/X7R. All other capacitors also received the tolerance field.
- Recompared148 intended endpoints with the regenerated XML after normalization: zero mismatches. No signal topology changed in these corrections.
- U1 now uses a project-local `ESP32-S3-WROOM-1_Overhang` footprint. Its intended change is antenna artwork moving from silkscreen to fabrication layer; final board comparison must verify identical electrical pads.
- Created the engineering [BOM CSV](../BOM.csv) and [BOM guide](../BOM.md):49 schematic references,38 purchased/assembled component placements,11 PCB test pads. Passive/header/switch MPNs remain explicitly unselected; source-backed exact parts are listed without stock claims.
- Rechecked every cited source URL; see the dated accessibility log in the research ledger. Direct-client failures were retried successfully through the web reader.

AUD-E-03/04 remain physical qualification gates. AUD-E-05/06 must be evaluated against the final routed board and its current reports; the initial audit does not imply those are resolved.

### 2026-10-26 routed-board snapshot

Loaded `design/SHM_Node_R2.kicad_pcb`, SHA256 `9b5d68a3ce51608f286420743634933aa854b52f3d73f104391bffcad9e46f6d`. It contained455 track/via objects, including36 ground vias. All148 intended endpoints have the correct assigned net. An additional comparison of exact names against the current Eeschema XML found **zero mismatches without normalization**, closing **AUD-E-05** for this snapshot.

The project-local U1 footprint and installed stock WROOM footprint have identical62 pad objects when comparing number, position, size, shape and copper/paste/mask layer sets. This verifies the overhang artwork edit did not change pad geometry. All three MPU footprints still have24 pads and identical0° orientation.

This snapshot verifies package/net assignments and footprint geometry. It does not replace final routed-connectivity/DRC reports or a USB signal-integrity review. AUD-E-06 closes only after those final routing checks are documented. Later file hashes require renewed comparison.

Audit tool note: an initial `LIB_ID.Format()` call failed due to the installed SWIG binding's overload handling; reading `GetLibItemName()` succeeded. The preceding endpoint comparison had completed, and the remaining footprint inspection was rerun successfully. No board mutation was performed by these read-only checks.

## Engineering audit follow-up — 2026-10-29

Read [ENGINEERING_AUDIT_20261029.md](ENGINEERING_AUDIT_20261029.md) and its [plan](ENGINEERING_AUDIT_PLAN.md) before the next CAD edit. The deeper read-only audit found issues beyond configured ERC/DRC: USB A-contact transition imbalance (4 D+ versus 2 D−), missing explicit impedance stackup, no local capacitor directly on the ESD VBUS net, J2-to-U3 nominal body separation about 5.18 mm (5.13 mm conservative F.Fab box) against the TDK 6 mm insertion-component guidance, and unresolved thermal/probe-access qualification. Nominal antenna overhang is 0.10 mm with no recorded tolerance budget. These are engineering concerns, not observed prototype failures. Active PCB remains unchanged at SHA-256 `0ea352e982e6ccb87134d1d3dcef7bd3adb747efab5ba28b136cd1090f99540e`; the earlier configured CAD pass remains bounded evidence.

New evidence: `reports/engineering_audit/20261029/geometry.json`, `math.json`, and USB plane-screen SVG/PNG; reproducible tools `audit_engineering_geometry.py` and `audit_engineering_math.py`. Start with the report's ordered corrections and acceptance criteria. The audit did not change CAD, firmware or paper, and does not authorize fabrication.

