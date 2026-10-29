# 05 — Revised Schematic and PCB Specification (HW Rev 2) + V1 Rework

Audience: the hardware agent (KiCad recreation) and JC. Source V1 files: `Thesis.kicad_sch`, `Thesis.kicad_pcb`.
Link status legend: ✅ opened and read during this review · 🔗 well-known URL from memory, **not opened** (verify before relying on it).

---

## 0. Decide first: Rework-only (§A) or Respin (§B)? — open question Q1

| | A. V1 rework + new firmware | B. V2 respin |
|---|---|---|
| Fixes | CPOUT caps, pull-ups, AUX cleanup, firmware (FIFO needs no INT) | Everything incl. mounting holes, INT, SD, 2 buses, ESD, test points |
| Cost/time | Hours, parts < ₱100 | New fab + assembly, ~1–2 weeks lead |
| Remaining risk | No mounting holes (needs edge-clamp enclosure); IO35/36 problem if R8 module | Low |
| Recommendation | **Do A now** to unblock firmware/pilot; **do B in parallel** if the schedule allows | |

[Likely] A is enough to get valid data; B improves reliability/defensibility. Decide after the pilot (M5).

---

## A. V1 rework list (soldering on existing boards)

| # | Action | Refs | Reason | Evidence |
|---|--------|------|--------|----------|
| A1 | Replace 220 pF with **2.2 nF X7R, ≥ 50 V**, same footprint | C9, C12, C15 | CPOUT value per datasheet | MPU-6000/6050 Spec §7.3 ✅ |
| A2 | Remove 4 pull-ups, keep one pair | remove R11, R12, R15, R16 (keep R7 = SDA, R8 = SCL, 4.7 kΩ) | 3 in parallel = 1.57 kΩ | netlist |
| A3 | Remove 6 AUX pull-ups (optional, harmless to leave) | R9, R10, R13, R14, R17, R18 | AUX bus unused | netlist |
| A4 | Verify module part number; if **R8/R16V**: cut IO35/IO36 traces and wire SDA/SCL to module pads IO8 (pin 12) / IO9 (pin 17); change `hw_profile.h` | U1 | IO35–37 reserved for octal PSRAM | Espressif datasheet v1.8 Table 3-1 note b ✅ |
| A5 | INT bodge (optional; firmware V1 profile does not need it) | U2/U4/U5 pin 12 → spare GPIO | timestamps for jitter stats | — |
| A6 | Mechanical: no holes — build an **edge-clamp frame** (clamp along board edges away from components) bolted to a rigid base plate; do not hang the board by a connector | enclosure | thesis §3.6 rigid coupling | PCB-01 |
| A7 | Fit a USB TVS dongle/inline ESD protector or accept risk | — | no ESD parts | HW-06 |

After A1–A3, re-test: I2C scan finds 3 IMUs; static noise run (T-03).

---

## B. Rev 2 schematic

### B.1 Design principles
1. Three MPU-6050 are **redundant sensors on one rigid node** (not X/Y/Z).
2. Hard-strapped I2C addresses on **two buses**; no GPIO address switching.
3. INT of each IMU to its own GPIO (jitter statistics, future DRDY mode).
4. Raw data to microSD.
5. Every IMU circuit exactly per the datasheet typical circuit (§7.2/7.3).
6. Test points and mounting holes for field use.

### B.2 ESP32-S3-WROOM-1 pin map (Rev 2)

Module pin numbers from Espressif datasheet v1.8 Table 3-1 ✅.

| Function | GPIO | Module pin | Net | Notes |
|---|---|---|---|---|
| I2C bus A SDA | IO8 | 12 | `SDA0` | default I2C0 pins; IMU1 + IMU2 |
| I2C bus A SCL | IO9 | 17 | `SCL0` | |
| I2C bus B SDA | IO15 | 8 | `SDA1` | IMU3 |
| I2C bus B SCL | IO16 | 9 | `SCL1` | |
| IMU1 INT | IO4 | 4 | `IMU1_INT` | reuses V1 AD0 route |
| IMU2 INT | IO5 | 5 | `IMU2_INT` | |
| IMU3 INT | IO6 | 6 | `IMU3_INT` | |
| SD CS | IO10 | 18 | `SD_CS` | SPI2 (FSPI) |
| SD MOSI | IO11 | 19 | `SD_MOSI` | |
| SD SCK | IO12 | 20 | `SD_SCK` | |
| SD MISO | IO13 | 21 | `SD_MISO` | 10 kΩ pull-up |
| SD card-detect | IO14 | 22 | `SD_CD` | |
| REC LED | IO38 | 31 | `LED_REC` | 1 kΩ to LED |
| Boot | IO0 | 27 | `BOOT` | button to GND (strapping) |
| EN | EN | 3 | `EN` | 10 kΩ pull-up + 1 µF to GND + reset button |
| USB D− / D+ | IO19 / IO20 | 13 / 14 | `USB_DN` / `USB_DP` | native USB |
| UART0 TX/RX | IO43 / IO44 | 37 / 36 | `TXD0`/`RXD0` | test pads |
| **Do not use** | IO35, IO36, IO37 | 28–30 | — | reserved on R8/R16V modules; leave NC |
| **Leave floating** | IO45, IO46, IO3 | 26, 16, 15 | — | strapping pins (VDD_SPI, boot/ROM log, JTAG select) |
| Spare (header) | IO1, IO2 | 39, 38 | `SPARE1/2` | 4-pin expansion header with 3V3/GND |

Specify module: **ESP32-S3-WROOM-1-N8** (8 MB quad flash, no PSRAM) or N16R2 — **avoid R8/R16V** variants (IO35–37 lost; temperature rating 65 °C) — Espressif datasheet Table 1-1 ✅.

### B.3 Circuit blocks

**Power**
| Ref | Part | Value/Package | Notes |
|---|---|---|---|
| J1 | USB-C receptacle (GCT USB4105-GF-A or equivalent 16-pin) | — | CC1/CC2: R3, R4 5.1 kΩ to GND (as V1) |
| F1 | PTC resettable fuse | 6 V, ≥ 0.75 A hold, 1206 | ESP32 supply needs ≥ 0.5 A per Espressif ✅ Table 6-2 |
| U6 | USBLC6-2SC6 (ST) | SOT-23-6 | on D+/D−/VBUS |
| U3 | AMS1117-3.3 | SOT-223 | keep from V1 |
| C2 | 10 µF tantalum or X5R/X7R | input, near U3 | |
| C1 | **22 µF tantalum** | output, near U3 | ESR for stability [Likely; check AMS1117 datasheet] |
| C3 | 22 µF X5R/X7R 10 V | near U1 3V3 pin | Espressif ref uses 22 µF + 0.1 µF at 3V3 ✅ Fig. 9-1 |
| C4 | 100 nF X7R | near U1 | |
| D1 + R | Green LED + 1 kΩ | power indicator | |

Current budget at 3.3 V (worst case): ESP32 Wi-Fi TX peak 355 mA ✅ Table 6-4 + SD ≤ ~150 mA + 3 × MPU 3.9 mA ≈ 0.52 A < 1 A LDO limit. LDO dissipation ≈ (5 − 3.3) × 0.35 A ≈ 0.6 W worst case [Likely]; give U3 a generous copper pour (V1 already has the tab pad; add area).

**MCU (U1)**: EN network R1 10 kΩ + C5 1 µF only (drop the redundant 100 nF, optional). BOOT button S2 with R2 100 Ω (as V1). RESET button S1 (EN to GND).

**IMU block (repeat ×3: U2, U4, U5 = IMU1, IMU2, IMU3)** — MPU-6050, QFN-24 4×4 mm.

| MPU pin | Name | Connection (Rev 2) | Source |
|---|---|---|---|
| 1 | CLKIN | GND | datasheet §7.1 ✅ |
| 2–5, 14–17 | NC | NC | |
| 6 | AUX_DA | NC | unused |
| 7 | AUX_CL | NC | unused |
| 8 | VLOGIC | +3V3 + **C 10 nF X7R** to GND | §7.3 C4 ✅ |
| 9 | AD0 | **IMU1: GND (0x68); IMU2: +3V3 (0x69); IMU3: GND (0x68)** | §9.2 ✅ |
| 10 | REGOUT | **0.1 µF X7R** to GND | §7.3 C1 ✅ |
| 11 | FSYNC | GND | §7.1 ✅ |
| 12 | INT | `IMUn_INT` | §7.18 ✅ |
| 13 | VDD | +3V3 + **0.1 µF X7R** to GND (≤ 2 mm) | §7.3 C2 ✅ |
| 18 | GND | GND | |
| 19, 21, 22 | RESV | NC | |
| 20 | CPOUT | **2.2 nF X7R, 50 V** to GND | §7.3 C3 ✅ |
| 23 | SCL | bus A (IMU1, IMU2) / bus B (IMU3) | |
| 24 | SDA | same | |

Address map: bus A: 0x68 (IMU1), 0x69 (IMU2); bus B: 0x68 (IMU3). VDD range 2.375–3.46 V ✅ (3.3 V OK). VLOGIC ≤ VDD at all times ✅ (both +3V3).
Pull-ups: **R7/R8 = 2.2 kΩ** on SDA0/SCL0; **R11/R12 = 2.2 kΩ** on SCL1/SDA1. Check: min pull-up for 3 mA sink at 0.4 V = 2.9 V / 3 mA ≈ 970 Ω ✅; 2.2 kΩ with ≈ 60 pF → rise ≈ 0.85·R·C ≈ 0.11 µs < 0.3 µs Fast-mode limit ✅ (datasheet Table 6.7).

**microSD (J2)**: push-push micro-SD socket with card-detect (e.g., Hirose DM3AT-SF-PEJM5 🔗 or JLC-stocked equivalent). SPI mode: CS/MOSI/SCK/MISO/CD per pin map; 10 kΩ pull-ups on CS and MISO; 10 µF + 100 nF at socket VDD. Entire block DNP-able.

**UX/test**: LED_REC (LED + 1 kΩ on IO38). Test pads: +5V, +3V3, GND ×2, SDA0, SCL0, SDA1, SCL1, IMU1–3_INT, TXD0, RXD0. 4-pin expansion header (3V3, GND, IO1, IO2).

### B.4 Net list changes V1 → V2

| V1 net | V2 net |
|---|---|
| `IMU-SDA` (IO36) | `SDA0` (IO8) + new `SDA1` (IO15) |
| `IMU-SCL` (IO35) | `SCL0` (IO9) + new `SCL1` (IO16) |
| `IMU-AD0X1/Y1/Z1` (IO4/5/6 → pin 9) | removed; pin 9 strapped; IO4/5/6 now `IMU1/2/3_INT` → pin 12 |
| INT NC | `IMUn_INT` |
| C9, C12, C15 = 220 pF | 2.2 nF X7R 50 V |
| R9, R10, R13, R14, R17, R18 (AUX pull-ups) | deleted |
| R11, R12, R15, R16 | R11, R12 become bus-B pull-ups; R15, R16 deleted |
| — | F1, U6, J2 + SD parts, LED, test pads, header |

---

## C. Rev 2 PCB specification

| Item | Requirement | Basis |
|---|---|---|
| Stack-up | 2-layer FR4, 1.6 mm, 1 oz Cu (as V1) | V1 |
| Outline | Keep V1 3-arm shape (IMUs at arm ends, ESP32 top, USB-C left edge) unless enclosure forces change; ~75 × 79 mm | V1 PCB |
| **Mounting holes** | **4 × M3 NPTH (3.2 mm)**, ≥ 1 within 10 mm of **each IMU**, plus 1 near the ESP32/LDO; 6.5 mm keep-out ring; GND ring optional | PCB-01; thesis §3.6 |
| IMU placement | Same orientation (rotation 0° as V1); symmetric pad connections; ≥ 6 mm from connectors/buttons/shields; **no signal traces or vias under or directly above the package**; a ground pour under the package is recommended; **no exposed-pad land** | MPU spec §11.4.1–11.4.4 ✅ |
| Decoupling | REGOUT/VDD/VLOGIC/CPOUT caps within 2 mm of their pins, short return to GND | spec §7.3 |
| Thermal | Keep IMUs ≥ 25 mm from U3 and ESP32 (V1: 25.7 / 30.8 mm) | V1 PCB |
| Antenna | Keep the keep-out rule area at the module antenna end; no copper/traces/components; module antenna overhangs or sits at board edge | Espressif ✅ Fig 3-1, §11.2 |
| Ground | Pour on both layers, stitch vias ≈ every 5–10 mm, avoid plane splits under IMUs; route I2C mainly on one layer | PCB-03 |
| Track widths | +5V/+3V3 ≥ 0.5 mm (V1 used 0.3 mm everywhere); signals 0.25–0.3 mm | PCB-02 |
| Silkscreen | `IMU1/2/3` labels; **+X +Y +Z arrows at each IMU**; an arrow "BRIDGE LONGITUDINAL →"; polarity of C1/C2/LED; board name/rev/date; test-point names | PCB-06 |
| Orientation convention | Mount so X = along bridge span, Y = transverse, Z = vertical; record in `meta.json` | thesis §3.6 |
| Fab | DRC clean with fab rules; fiducials for assembly; export Gerber + drill + pos + BOM | — |

Mechanical (for `hardware/mechanical/`):
- Rigid base plate (aluminium or thick PETG) → standoffs (M3, 5–6 mm) at all four holes → board. A tap test (T-09) must show one coherent frequency across the three IMUs; separate peaks mean the arms are flexing independently.
- Attachment to the bridge: per DPWH approval — non-invasive options first (strong pot magnets on a steel member, clamp, or epoxy plate). [Likely] magnets are acceptable only on clean flat steel; verify coupling with the tap test.
- Enclosure: IP-rated box with cable gland for USB power; power bank inside or beside; do not obstruct the antenna end; shade from direct sun (temperature affects both sensor and clock).
- Power bank: choose one with a low-current / always-on mode; the node draws ≈ 0.1–0.25 A at 5 V, which many banks tolerate, but verify no auto-shutoff (T-10).

---

## D. Verification checklist (hardware agent must complete)

1. KiCad ERC clean; DRC clean (use `kicad-cli sch erc` and `kicad-cli pcb drc` if available).
2. Cross-check every IMU pin against the table in B.3 using the **datasheet**, not memory: https://www.mikrocontroller.net/attachment/236856/MPU-6050.pdf ✅
3. Cross-check ESP32 pins against Espressif datasheet Table 3-1 ✅ and avoid IO35–37 and the strapping pins.
4. Provide a netlist diff V1 → V2 (script or manual) and a BOM with MPN, package, voltage rating, and datasheet link; mark DNP parts.
5. Confirm KiCad footprints: MPU-6050 QFN-24 4×4×0.9 mm 0.5 mm pitch (spec §11.2–11.3 ✅), ESP32-S3-WROOM-1 land pattern (datasheet Fig 11-1 ✅), SOT-223, SOT-23-6, USB-C 16-pin.
6. 3-D check: IMU clearance to mounting hardware, USB-C reach through the enclosure, antenna end free.
7. Export `hardware/rev2/` with gerbers, `README`, and a one-page assembly note.

## E. Component and datasheet links (status)

| Component | Link | Status |
|---|---|---|
| ESP32-S3-WROOM-1 / -1U datasheet v1.8 | https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf | ✅ |
| ESP32-S3 Hardware Design Guidelines | https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/index.html | 🔗 |
| MPU-6000/6050 Product Specification Rev 3.4 (mirror) | https://www.mikrocontroller.net/attachment/236856/MPU-6050.pdf | ✅ |
| MPU-6000/6050 Register Map (InvenSense/TDK) | https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Register-Map1.pdf | 🔗 |
| MPU-6050 product page (TDK InvenSense) | https://invensense.tdk.com/products/motion-tracking/6-axis/mpu-6050/ | 🔗 |
| AMS1117 datasheet | http://www.advanced-monolithic.com/pdf/ds1117.pdf | 🔗 |
| USBLC6-2 (ST) | https://www.st.com/resource/en/datasheet/usblc6-2.pdf | 🔗 |
| GCT USB4105 | search "GCT USB4105-GF-A datasheet" at https://gct.co | 🔗 |
| Hirose DM3AT microSD socket | search "Hirose DM3AT-SF-PEJM5" at https://www.hirose.com | 🔗 |
| KiCad documentation | https://docs.kicad.org | 🔗 |
