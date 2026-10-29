# PCB primary-source research ledger

Checked 2026-10-25 (Asia/Manila). This is the evidence map for the new PCB, not a certification or proof of physical performance. The user selected ESP32-S3-WROOM-1-N16R8, three bare MPU-6050 ICs and external USB-C power/programming. Other component and geometry choices are engineering proposals documented in [ELECTRICAL_DECISIONS.md](ELECTRICAL_DECISIONS.md).

## Verified sources and exact reading locations

| ID | Primary source and verified URL | Relevant location / use |
| --- | --- | --- |
| SRC-01 | [TDK/InvenSense MPU-6000/MPU-6050 product specification, PS-MPU-6000A-00 rev3.4](https://d17t6iyxenbwp1.cloudfront.net/s3fs-public/2026-04/ps-mpu-6000a-00-mpu-6000-and-mpu-6050-datasheet.pdf?VersionId=eMVDQ08Qz7kahOvvE6xCs8WtRhxekFIH) | 52-page PDF; printed pp14–15 electrical limits, p21 pin table, p22 typical circuit/component table, p23 power sequencing, pp40–43 orientation/package/land pattern/assembly. Retrieved and circuit page rendered locally. |
| SRC-02 | [Espressif ESP32-S3-WROOM-1/1U datasheet v1.8](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf) | 53-page PDF; Table1-1 N16R8 variant; Table3-1 module pads; §4 straps; §9 peripheral schematic; §10 package/land pattern. Retrieved/read online. |
| SRC-03 | [Espressif S3 schematic checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html) | Power supply, reset timing, strapping pins and USB sections. Current manufacturer guidance, read online. Bare-SoC circuit details are not additional external parts for an already assembled module. |
| SRC-04 | [Espressif S3 PCB layout guide](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html) | General layer principles, module placement, antenna clearance and USB routing. Read online. |
| SRC-05 | [Espressif ESP32-S3-DevKitC-1 schematic V1.1, 2022-11-30](https://dl.espressif.com/dl/schematics/SCH_ESP32-S3-DevKitC-1_V1.1_20221130.pdf) | Real manufacturer schematic, two sheets. Sheet2 read and rendered: native USB path, EN RC, BOOT/RESET, supply decoupling and optional UART path. Its micro-USB connector, regulator and RGB LED are not copied wholesale. |
| SRC-06 | [Diodes AP7361C datasheet DS37274 rev5-2](https://www.diodes.com/datasheet/download/AP7361C.pdf) | pp1–2 fixed-output circuit/pins; p6 thermal conditions; pp11–12 capacitor/thermal equations; p13 order code; package/land drawing later pages. Verified 22-page PDF. Alternate verified URL: [assets copy](https://www.diodes.com/assets/Datasheets/AP7361C.pdf). |
| SRC-07 | [ST USBLC6-2 datasheet DS4260 rev7](https://www.st.com/resource/en/datasheet/usblc6-2.pdf) | p1 functional diagram; pp4–6 routing/parasitic-inductance examples; package drawings. Verified 20-page PDF. |
| SRC-08 | [ST AN5225, Introduction to USB Type-C Power Delivery, rev7](https://www.st.com/content/ccc/resource/technical/document/application_note/group1/38/94/1d/41/0e/ba/49/21/DM00536349/files/DM00536349.pdf/jcr:content/translations/en.DM00536349.pdf) | pp7–10 connector/power/CC tables; §10 USB2 conversion. Verified 76-page PDF. Passive Rd indicates sink attachment; it does not itself measure the source's available current. |
| SRC-09 | [TI SLVA689A, I2C Bus Pullup Resistor Calculation](https://www.ti.com/lit/an/slva689/slva689.pdf) | §2 equations1/5/6 and timing table. Verified six-page PDF. Basis of pull-up/rise-time estimates, not a substitute for measured board capacitance. |
| SRC-10 | [GCT USB4105 product page](https://gct.co/connector/usb4105) and [manufacturer drawing](https://gct.co/files/drawings/usb4105.pdf) | Product page read online. Drawing direct HTTP download succeeded (164547 bytes), then page1 rendered and visually read: revB4, 18Dec2023; exact ordering grid, 16-pin map, recommended land pattern and stakes. |
| SRC-11 | [KiCad official USB4105 footprint source](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/Connector_USB.pretty/USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal.kicad_mod) | Read online; footprint family names USB4105-GF-A among compatible variants. Installed library version must still be checked against SRC-10. A library entry alone is not manufacturer verification. |

## Local evidence used

- `../../Reference PCB (OLD Version)/Thesis/SHM_PCB_Top.png`: visually inspected. The old design has rounded left/right lobes and a lower lobe, with the wireless module near the upper center and the USB connector at a side edge. This supplies the requested aesthetic reference, not an electrical endorsement.
- `../../../Code Files/GPT Build/docs/HARDWARE_INTERFACE.md` and `../../../Code Files/GPT Build/firmware/SHM_Capstone/hardware_profile.h`: current firmware bus/address/interrupt contract. Source files remain the authority for firmware assignments.
- Old schematic and PCB must remain unchanged. Any discrepancy with manufacturer data is resolved in the new project and logged, not silently propagated.

## Research errors and resolution

| Observation | Resolution / consequence |
| --- | --- |
| Manufacturer GCT drawing could not be opened by the web reader. | Direct `Invoke-WebRequest` of the same manufacturer URL succeeded; rendered locally with Poppler and read page1. No third-party replacement was relied on for the pin/land data. |
| TDK PDF web screenshot requests timed out although text extraction worked. | Downloaded the same official-host PDF directly and rendered printed p22. The actual circuit confirms CPOUT and REGOUT capacitor connections. |
| One AP7361C assets-URL fetch timed out. | Manufacturer `/datasheet/download/AP7361C.pdf` returned the full document and relevant pages. |
| Bundled Python had no `fitz` module. | Used installed Poppler `pdftoppm`; no dependency installation needed. Poppler reported missing display-font warnings; relevant electrical text and drawings remained visible. |
| A conventional QFN exposed-pad footprint would imply soldering the MPU center. | SRC-01 §11.4.2 specifically prohibits soldering this exposed die pad. New MPU footprint must omit center copper/paste and keep active routing/vias out beneath the die. |
| AP7361C E and ER packages have different pin ordering. | Locked AP7361C-33E-13 to IN=1, GND/tab=2, OUT=3. Never substitute an AMS1117 pinout or AP7361C-33ER footprint mapping. |

## Claims this evidence does not establish

### USB routing source recheck — 2026-10-29

Opened SRC-04's current USB section and SRC-07 DS4260 rev7 again while correcting the compact board. Espressif calls for parallel equal-length differential routing, 90 ohm differential impedance within 10%, few layer transitions, nearby ground return vias and a continuous reference layer. ST's first-page functional diagram confirms paired I/O1 pins 1/6, I/O2 pins 3/4, GND pin 2 and VBUS pin 5. These source statements are verified within that scope. The provisional 0.20 mm copper width and routing gap are design geometry only: a selected supplier stackup and field-solver/controlled-impedance review are still required. A clean clearance report does not establish these electrical characteristics. USB route-length and return-path review remains separate from DRC.

Datasheets do not prove that the eventual board meets USB compliance, impedance, ESD immunity, thermal, assembly, mechanical coupling or frequency-accuracy targets. Preserve those as physical validation tasks. Do not label a routed board production-ready merely because ERC/DRC is clear. Do not treat the vintage MPU product specification as proof of current stock, authentic parts or future availability.

Record each later datasheet revision, component substitution, source failure and layout correction in this ledger or the project validation/error log. Link the final schematic/PCB verification results rather than replacing this evidence with an unexplained assurance.

## 2026-10-26 source accessibility recheck and fuse correction

All14 cited source URLs, including alternate regulator and connector URLs plus the added fuse source, were rechecked. Direct HTTP requests returned200 for the TDK PDF, Espressif module PDF, schematic/layout guides, reference schematic, both Diodes PDF URLs, TI pull-up PDF, GCT drawing and KiCad footprint page. PDF responses were also checked for the `%PDF` signature. The module URL redirects to `documentation.espressif.com`; the TI URL redirects to its revisionA file. These redirects are legitimate manufacturer destinations.

Direct requests to the two ST documents timed out; GCT's product page and the Littelfuse PDF returned403 to that client. The web reader then successfully opened the same four URLs and returned the actual documents (ST20pages/76pages, GCT product page, Littelfuse5pages). A failed client request is logged as a client/access limitation, not evidence that the source does not exist.

**SRC-12:** [Littelfuse1206L series datasheet, revised2024-02-26](https://www.littelfuse.com/assetdocs/littelfuse-ptc-1206l-datasheet?assetguid=2b6a1515-d4ee-4c83-8bd4-152b4901b8f5). Printedp4 gives exact order code `1206L075/16WR`; p1 electrical ratings; p2 ambient derating. The initial schematic's `YR` suffix was incorrect and has been corrected by the schematic owner. See [AUDIT_ELECTRICAL.md](AUDIT_ELECTRICAL.md).

## Engineering audit follow-up — 2026-10-29

Source register E1–E9 and exact application limits are in hardware `docs/ENGINEERING_AUDIT_20261029.md`. Reopened official Espressif layout/module v1.8/reset guidance; ST USBLC6-2 rev7 §2.3/Fig17 and AN5225 rev7 §4 Tables6–7; TDK MPU rev3.4 pp14/16/18/42–43; TI SLVA689A (October2026); Littelfuse1206L (February2024). These support component guidance and conditional calculations, not this board's field performance.

The official Diodes AP7361C PDF timed out in the web reader and returned403 in the direct client. Read manufacturer-authored DS37274 rev5-2 (October2020) from a separately identified mirror; saved source/hash in `reports/engineering_audit/sources/source_files.json`. Rendered p6 confirmed110°C/W is for a minimum-pad reference condition. Official-current revision freshness is partially verified; do not treat mirror availability as proof of revision currency. ST local PDF fetch timed out twice although its official web reader worked. Source access failures are retained, not reported as successful downloads.

The 100nF ESD bypass and ≥6mm insertion-component guidance lead to proposed corrections, not empirical failure claims. Equation outputs are verified only under declared inputs. The approved paper and firmware were untouched.

