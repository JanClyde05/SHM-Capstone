# Engineering bill of materials

Reconciled 2026-10-29 against `design/circuit_spec.json` and all 49 CSV references/quantities. Source SHA256: `f5f5a56f9e9b467c1ff75795e55d94ca561eb9770ed3594dd65273ea0006b34b`. Earlier header hash was stale; component content was unchanged.

**Status: prototype engineering list, not a released purchasing list.** Exact verified MPNs are recorded where selected. Blank MPNs intentionally mean a part has not been selected; they are not an invitation to assume any component with the same nominal value will fit. No prices, stock or supplier authenticity claims are made.

There are **38 assembled schematic components** and **11 PCB test-pad features**. CSV quantities cover all49 schematic references exactly once. The corrected compact candidate has three board mounting holes H1-H3 (updated 2026-10-29); they are mechanical features, not additional electrical components. The superseded larger board had four holes.

| References | Qty | Value/function | Manufacturer / MPN | Package / selection status |
| --- | ---: | --- | --- | --- |
| U2, U3, U4 | 3 | MPU-6050 | TDK InvenSense / MPU-6050 | MPU6050_QFN24_NoCenterPad |
| C6, C8, C10, C12, C14, C16, C4 | 7 | 100nF | Not selected | C_0603_1608Metric |
| C7, C11, C15 | 3 | 10nF | Not selected | C_0603_1608Metric |
| C9, C13, C17 | 3 | 2.2nF | Not selected | C_0603_1608Metric |
| J1 | 1 | USB4105-GF-A | GCT / USB4105-GF-A | USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal |
| R1, R2 | 2 | 5.1k 1% | Not selected | R_0603_1608Metric |
| U6 | 1 | USBLC6-2SC6 | STMicroelectronics / USBLC6-2SC6 | SOT-23-6 |
| F1 | 1 | 0.75A HOLD | Littelfuse / 1206L075/16WR | Fuse_1206_3216Metric |
| U5 | 1 | AP7361C-33E-13 | Diodes Incorporated / AP7361C-33E-13 | SOT-223-3_TabPin2 |
| C1 | 1 | 4.7uF | Not selected | C_0805_2012Metric |
| C2, C3 | 2 | 10uF | Not selected | C_0805_2012Metric |
| U1 | 1 | ESP32-S3-WROOM-1-N16R8 | Espressif Systems / ESP32-S3-WROOM-1-N16R8 | ESP32-S3-WROOM-1_Overhang |
| J2 | 1 | UART DEBUG 3V3 | Not selected | PinHeader_1x03_P2.54mm_Vertical |
| R5, R6 | 2 | 10k | Not selected | R_0603_1608Metric |
| C5 | 1 | 1uF | Not selected | C_0603_1608Metric |
| SW1, SW2 | 2 | Momentary pushbutton, normally open | Not selected | SW_SPST_TL3342 |
| R7, R8, R9, R10 | 4 | 2.2k | Not selected | R_0603_1608Metric |
| R3, R4 | 2 | 22R | Not selected | R_0603_1608Metric |
| TP1, TP2, TP3, TP4, TP5, TP6, TP7, TP8, TP9, TP10, TP11 | 11 | PCB test pad | PCB feature | TestPoint_Pad_D1.0mm |

## Procurement and assembly requirements

- **MPU local capacitors:** C6-C17 retain X7R and10% or tighter tolerance. C9/C13/C17 require50V at2.2nF. Other voltage fields and capacitor values are preserved in [BOM.csv](BOM.csv); qualify DC-bias capacitance, especially the LDO input/output and1uF EN capacitor.
- **Resistors:** R1/R2 are5.1kOhm1% USB-C sink terminations. The1%/0.1W specification for the remaining0603 resistors is an engineering purchasing recommendation; those details are not yet explicit in every schematic field.
- **Switches:** the drawing uses the KiCad TL3342 family footprint; choose an exact switch only after checking pad dimensions and actuator height against its manufacturer drawing. No exact TL3342 suffix has been invented.
- **Header J2:** choose a1x3 vertical2.54mm header compatible with the PCB drill/pad geometry and enclosure. It carries GND/TX/RX at3.3V logic, with no extra supply input.
- **PCB:** one four-layer board per assembly, with actual stackup and impedance requirements finalized with the fabricator. The PCB material, finish, thickness and assembly process must match the final fabrication notes; this list does not silently select a fabricator.
- **Mechanical items:** three M3 clearance holes are in the corrected compact candidate. Screws, washers, standoffs, rigid mounting base and enclosure remain to be dimensioned and selected for the actual roadway-deck fixture. Fasteners must not intrude into antenna clearance. This proposed hole pattern does not establish mounting rigidity or vibration transfer.
- **External items:** USB-C data cable, compatible5V source, mounting hardware and prototype instruments are not part of the38-component count. Their required current and mechanical fit must be established from prototype evidence.

## Evidence and outstanding gates

Part sources are in the CSV and [research ledger](docs/RESEARCH_LEDGER.md). Read [electrical decisions](docs/ELECTRICAL_DECISIONS.md) and [independent electrical audit](docs/AUDIT_ELECTRICAL.md) before substituting a part. The SOT223 regulator must pass actual thermal/load testing. Native USB current/inrush, routing impedance and ESD performance remain qualification tasks. Firmware and schematic agree on the two I2C buses and individual DRDY inputs.

F1 was corrected from the unsupported `1206L075/16YR` suffix to manufacturer-listed `1206L075/16WR`; do not restore the former from an older export. The MPU center pad must remain unsoldered. The ESP32 module center ground pad follows its own distinct manufacturer guidance.

## Refreshing this list

After any circuit edit, regenerate the grouped list from the current `circuit_spec.json`, compare every reference and quantity against the exported schematic netlist, and update this source hash. Test pads and mounting holes must remain marked as PCB features. Add an exact passive/switch/header MPN only after manufacturer footprint and electrical verification, then record its URL and selection date.
