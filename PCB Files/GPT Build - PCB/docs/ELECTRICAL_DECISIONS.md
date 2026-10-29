# Electrical design decisions and verification boundaries

Date: 2026-10-25. Read [RESEARCH_LEDGER.md](RESEARCH_LEDGER.md) for verified manufacturer links and document locations. These are design inputs to the generated KiCad artifacts; actual ERC/DRC and netlist reports determine which have been implemented and checked.

## User requirements and design choices

The user confirmed one PCB, ESP32-S3-WROOM-1-N16R8, three bare MPU-6050 ICs and external USB-C power/programming. The firmware fixes the bus/interrupt table below. Exact USB connector, regulator, passive values, stackup, holes and enclosure are engineering selections, not previously confirmed user requirements. Preserve the rounded three-lobe appearance where antenna clearance, routing, mounting and mechanical rigidity permit.

## E-01 — Firmware-to-module net contract

| Net | ESP32 GPIO | WROOM-1 module pad | Sensor endpoint |
| --- | --- | --- | --- |
| I2C0_SDA | 8 | 12 | IMU1 + IMU2 pin24 |
| I2C0_SCL | 9 | 17 | IMU1 + IMU2 pin23 |
| I2C1_SDA | 10 | 18 | IMU3 pin24 |
| I2C1_SCL | 11 | 19 | IMU3 pin23 |
| IMU1_INT | 4 | 4 | IMU1 pin12 |
| IMU2_INT | 5 | 5 | IMU2 pin12 |
| IMU3_INT | 6 | 6 | IMU3 pin12 |
| USB_DN | 19 | 13 | USB D− through series resistor |
| USB_DP | 20 | 14 | USB D+ through series resistor |
| UART_TX | 43 | 37 | Optional diagnostic header |
| UART_RX | 44 | 36 | Optional diagnostic header |
| EN | — | 3 | Reset RC/button |
| BOOT | 0 | 27 | Boot button/pull-up |
| 3V3 | — | 2 | Regulated supply |
| GND | — | 1, 40, 41 | Ground; pad41 is module EPAD |

Source: firmware `hardware_profile.h` plus SRC-02 Table3-1. GPIO numbers must not be used as module pad numbers. Leave module pads28/29/30 (GPIO35/36/37) unused for N16R8 because octal PSRAM occupies those signals. Sensor wiring does not use strapping GPIO0/3/45/46. All three sensor orientations must be explicit and preferably identical; host polling order is not simultaneous conversion or phase synchronization.

## E-02 — Bare MPU-6050 circuits

The following applies separately to each IC. Source: SRC-01 pp21–23.

| Pin | Connection |
| --- | --- |
| 1 CLKIN | GND |
| 8 VLOGIC | 3V3; local 10nF X7R to GND |
| 9 AD0 | GND on IMU1/3 (0x68); 3V3 on IMU2 (0x69) |
| 10 REGOUT | Local 100nF X7R to GND only |
| 11 FSYNC | GND |
| 12 INT | Individual MCU GPIO above |
| 13 VDD | 3V3; local 100nF X7R to GND |
| 18 GND | GND |
| 20 CPOUT | Local 2.2nF X7R, ±10%, **50V** to GND only |
| 23 / 24 | SCL / SDA on the assigned bus |
| 6 / 7 | Unused AUX_DA / AUX_CL, no external connection |
| 19 / 21 / 22 | Reserved; no connection |
| 2–5 / 14–17 | NC; leave open in this design |

VDD must stay within 2.375–3.46V and VLOGIC within 1.71V–VDD. Both use the same 3V3 rail. Scope monotonic power rise; VLOGIC 10–90% rise must meet the specified ≤3ms condition. REGOUT and CPOUT are not extra supply inputs.

**Footprint exception:** QFN24, 4×4mm, 0.5mm pitch. The exposed center is not soldered or electrically connected. Omit center copper/paste; prohibit active traces/vias under the exposed die area. The manufacturer land guidance gives 0.35mm width and 0.80mm length (0.85mm for corner lands), 4.80mm outer extent. Evaluate manufacturing mask-sliver limits for that pitch. Source: SRC-01 pp41–43. Mechanical stress and board flex require mounting validation; a decorative lobe is not evidence of accurate deck coupling.

## E-03 — I2C pull-ups

Use one pull-up per SDA/SCL line on each of the two buses. Starting selection: 2.2kΩ, 1%, to 3V3. No parallel duplicate pull-ups on each IMU.

**HW-EQ-PULLUP-01:** `Rmin = (VDD − VOL,max) / IOL`.

**HW-EQ-PULLUP-02:** `tr(30–70%) = 0.8473 × Rp × Cbus`.

At 3.3V, a 2.2kΩ pull-up draws about 1.32mA when the line is at 0.4V. At the 400kHz fast-mode rise-time limit of 300ns, the calculated capacitance ceiling is approximately 161pF. These are calculations, not measured bus capacitance or compliance. Scope both buses with the assembled board and intended probes before accepting 400kHz. Sources: SRC-09 equations1/5/6; SRC-01 electrical/timing tables.

## E-04 — 3V3 regulation and thermal gate

Proposed exact part: **AP7361C-33E-13**, fixed3.3V, SOT223. Pin1 IN; pin2 and tab GND; pin3 OUT. E and ER differ. Use a matching symbol and footprint pin mapping, not a generic1117 circuit. Select input/output capacitance with effective values above the manufacturer minima after DC-bias derating. The example circuit uses4.7µF; minimum input1µF/output2.2µF. Local module bulk and bypass capacitance should also be provided. Sources: SRC-06 pp1–2,11,13; SRC-02 §9; SRC-03 power section.

**HW-EQ-THERMAL-01:** `PLDO ≈ (VIN − VOUT) × IOUT`.

**HW-EQ-THERMAL-02:** `TJ ≈ TA + PLDO × thetaJA`.

At5V→3.3V and0.5A, dissipation is0.85W; at1A it is1.70W. Datasheet SOT223 thetaJA=110°C/W describes its stated minimal pad test board, giving indicative rises93.5°C/187°C. The 1A electrical rating therefore does not demonstrate1A continuous operation in this application. Large grounded tab copper, thermal vias and separation from the IMUs are required; actual ambient/load/temperature measurements decide suitability. A buck regulator or larger thermal solution must replace the LDO if those measurements fail. Do not hide this uncertainty by citing only the current rating.

The USB power source and its advertised current are not confirmed. The board must remain at nominal5V input; no PD voltage negotiation is implemented. A 5.1kΩ CC resistor is not authorization to draw1A from every PC USB port. Measure startup/inrush and sustained/radio-burst load against the actual host/supply capability. Capacitor loading on rawVBUS also requires USB inrush review.

## E-05 — Native USB-C, ESD and routing

Proposed exact connector: **GCT USB4105-GF-A** (standard0.95mm shell stakes). Its family footprint must match SRC-10, not an arbitrary USB-C socket.

- A1/A12/B1/B12 and shell→GND; A4/A9/B4/B9→VBUS.
- A5 CC1 and B5 CC2 each get their own5.1kΩ,1% resistor toGND. Do not short CC1 andCC2 together.
- A6/B6 join asD+ and A7/B7 asD− immediately at the connector. A8/B8 SBU remain unconnected.
- Use **USBLC6-2SC6** near the connector: pin2GND,pin5VBUS,pins1/6one protected data line,pins3/4the other. Route through its paired I/O pins, with a short ground return. It does not provide USB power negotiation or a regulator overvoltage cutoff.
- Initial22Ω series resistors sit near the ESP32 module onGPIO19/20. Reserve DNP shunt capacitor footprints if practical. Tune only with waveform/USB evidence.
- Route the differential pair together, over a continuous adjacent ground reference, away from stubs and unrelated vias. Nominal90Ω differential impedance requires the fabricator's actual stackup/copper geometry; an arbitrary trace width is not a verified impedance result.

Sources: SRC-07 pin diagram/layout; SRC-08 CC/USB2 sections; SRC-03 USB section; SRC-04 USB layout; SRC-10 connector drawing. The manufacturer reference schematic SRC-05 confirms native USB can connect to the S3; no USB-UART bridge is required for this path. BOOT/RESET controls and optional UART fallback remain useful for recovery.

## E-06 — Startup and antenna

EN has10kΩ to3V3 and1µF toGND, with a reset button toGND. BOOT GPIO0 has a pull-up and a button toGND. Verify actual rail/reset waveforms; the RC is an initial manufacturer recommendation. Sources: SRC-02 §9 and SRC-03 reset/straps. Boot sequence must satisfy GPIO46 strap requirements; avoid external drive on unused straps.

Place the module at the upper board edge with its PCB antenna extending beyond the base-board copper/material where possible. Keep all copper layers, traces and components out of the antenna area. Housing and mounting metal need the manufacturer's recommended15mm surrounding clearance. The rounded lobe silhouette may be adjusted to preserve this. Source: SRC-04 module placement section. Do not apply the bare-chip antenna matching circuit outside this complete WROOM module.

## E-07 — Remaining confirmations and acceptance evidence

Before committing a fabrication order, record the actual chosen fabricator/stackup, soldermask capabilities, component supply/authenticity, enclosure/mounting dimensions and available USB supply. Verify generated schematic-to-PCB net correlation, every footprint pad mapping, and clean ERC/DRC with explicit exclusions explained. Then prototype and measure USB power/inrush, thermal rise, I2C rise times, all three DRDY signals, orientation, stationary noise and known-frequency response. Datasheet-backed design plus clear rule checks still does not establish research measurement accuracy.

## USB v5 pre-routing checkpoint — 2026-10-29

After the local support-capacitor tracks and USB refinement, `preroute_usb_v4_support_drc.json` reported one clearance error: a new GND return via at (130.20,78.65) had 0.145 mm clearance to VBUS against the unchanged 0.150 mm rule. Moving that via 0.05 mm right resolved it. Actual `preroute_usb_v5_support_drc.json`: zero errors, 21 silk warnings, 90 unconnected items. The earlier failed report is retained. USB v4's standalone reroute failed through KiCad's loaded-track removal path; `usb_v4_drc.json` checked stale input and is explicitly invalid as v4 acceptance. The helper now refuses existing USB copper; regenerate from placement.

Read-only graph measurements on the saved v5 preroute are in `usb_v5_geometry.json`: endpoint planar mismatch +0.074840 mm for A contacts and -0.078714 mm for B contacts, including module-side copper but excluding via barrels, pads and resistor internals. D- uses two transitions; D+ uses four for A contacts and two for B contacts. Four D+ vias remain versus five previously. This is improved planar geometry, not electrical-delay matching or USB compliance. Return vias were added at the connector crossover; final filled-plane review remains required. `measure_usb_geometry.py` reproduces this bounded measurement.
