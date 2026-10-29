# Engineering audit of the active compact board

Checked 2026-10-29. **Overall status: partially verified; engineering review/prototype design, not fabrication release.** The previously clean configured ERC/DRC result remains valid for the unchanged CAD. This deeper review found additional concerns that those checks do not cover.

## Identity, method and navigation

- Active board: `design/SHM_Node_R2.kicad_pcb`, SHA-256 `0ea352e982e6ccb87134d1d3dcef7bd3adb747efab5ba28b136cd1090f99540e`.
- Plan: [ENGINEERING_AUDIT_PLAN.md](ENGINEERING_AUDIT_PLAN.md).
- Read-only measurement script: [audit_engineering_geometry.py](../tools/audit_engineering_geometry.py); evidence: [geometry.json](../reports/engineering_audit/20261029/geometry.json).
- Labeled calculation script: [audit_engineering_math.py](../tools/audit_engineering_math.py); evidence: [math.json](../reports/engineering_audit/20261029/math.json).
- Run identity, source/report hashes and access/tool limits: [audit manifest](../reports/engineering_audit/20261029/manifest.json).
- [USB reference-plane screen](../reports/engineering_audit/20261029/usb_reference_screen.png) shows actual trace geometry and sampled clearance holes. It is an engineering illustration, not a manufacturing plot or electromagnetic simulation.
- Existing CAD acceptance: `reports/reference_corrected/validation_20261029T145905461959Z/manifest.json`. KiCad 10.0.6; zero findings among configured checks and independent endpoint/geometry checks. Four ERC and five DRC categories remain ignored as listed there. No fresh ERC/DRC rerun was needed because this pass did not edit CAD.
- Source hashes before/after match for PCB, project, schematic and specification. Paper, firmware and old-reference CAD were not changed. Parallel reviewer sessions stopped at the usage limit; this is a primary-agent audit with one partial USB observation, not three completed independent reviews.

## Findings and closure criteria

Priorities express review order, not demonstrated field failure. Evidence status describes the claim in the second column; the final column records what remains open.

| ID / priority | Claim and evidence | Status | Next action / closure evidence |
|---|---|---|---|
| ENG-01 / high | USB paths are not exactly equal. The old <0.08 mm comparison excludes via depth. A-contact D+ traverses four vias; D− two. | Verified geometry; electrical matching unverified | Review connector fanout and reduce/balance transitions; compare actual complete paths on the selected stackup, preserving connector and ESD topology. Test both plug orientations. |
| ENG-02 / high | No explicit dielectric stackup is stored in the active board. The 0.20 mm USB width and changing gaps do not establish 90 Ω. Default netclass suggests 0.25 mm differential width, unlike actual routing. | Verified file facts; impedance unverified | Choose fabricator/layer construction, copper thickness and dielectric data; solve width/gap including nearby ground; record controlled-impedance requirements and align project settings with the accepted geometry. |
| ENG-03 / medium | U6 pin 5 is on VBUS_USB; no capacitor is directly on that net. C1 is 4.7 µF on the other side of F1. ST Figure 17 includes a local 100 nF VBUS bypass. | Verified topology/reference difference; ESD performance unverified | Add/review a local 100 nF VBUS-to-GND capacitor with short connections, update schematic/spec/BOM/PCB, and check inrush and ESD layout. This is a recommended correction, not proof the present board fails an ESD test. |
| ENG-04 / medium | Antenna-region rectangle has no baseboard intersection or pad/track/via/fill intrusion; nominal boundary margin is only 0.10 mm. | Verified nominal geometry; toleranced fit/RF unverified | Calculate placement/module/outline tolerance allowance. Review final enclosure, cable, screws and roadway mounting; perform end-product RF tests. |
| ENG-05 / medium | J2 header body outline is about 5.18 mm from U3; including F.Fab stroke gives a conservative 5.13 mm. | Verified CAD distance; placement suitability partially verified | TDK §11.4.4 advises ≥6 mm from insertion components. Use conservative body-edge distance as an explicit engineering interpretation; select the actual header and reposition/review to meet that separation with tolerances. Do not call an unselected connector physically compliant. |
| ENG-06 / high | LDO loss is 0.85 W at an assumed 5 V input/3.3 V output/0.5 A. Actual board thermal resistance and load envelope are unknown. | Verified conditional arithmetic; thermal margin unverified | Bound input, sustained/peak current, ambient and enclosure; qualify copper/thermal paths and measure rail and device temperatures under the real duty cycle. The 1 A part rating does not release a 1 A board. |
| ENG-07 / medium | Eleven 1 mm back test pads have 3 mm nearest-neighbor pitch, mask openings and no paste. Only TP2 is a named GND pad. | Verified CAD; practical access unverified | Plan probe/fixture and access after mounting. Add/review accessible VBUS, fused 5 V and EN test locations and nearby grounds where useful. Avoid adding USB stubs merely for test coverage. |
| ENG-08 / high | No complete maximum load/startup/source-current budget, effective capacitor selection or measured voltage/transient record exists in this audit. | Unverified operating envelope | Specify source/cable and load cases; verify CC/source-current behavior, fuse derating, voltage drop, inrush and cold/warm startup. |
| ENG-09 / medium | Nominal 2.2 kΩ I2C pullups give a 300 ns rise-time capacitance budget of about 161 pF. | Verified conditional arithmetic; bus waveform unverified | Measure 30–70% rise time, VOL and waveform on both 400 kHz buses, including probe loading. Final resistor MPN/tolerance and total capacitance remain open. |
| ENG-10 / medium | EN uses 10 kΩ/1 µF, nominal RC=10 ms. | Verified values/arithmetic; startup timing unverified | Scope 3V3 and EN with actual source ramp, repeated unplug/replug and reset; RC alone is not an enable delay guarantee. |
| ENG-11 / high | N16R8 temperature specification differs from non-R8 variants. No enclosure temperature evidence or confirmed ECC operating configuration was supplied. | Verified variant distinction; application suitability unverified | Use the actual module variant/firmware limits in the operating envelope. Do not assume every WROOM version is rated to 85 °C. |
| ENG-12 / medium | Footprint/package, pad assignment and die-keepout checks pass their existing geometric checks; assembly supplier/remaining MPNs are not fixed. | Partially verified | Complete selected-part drawing, paste/stencil, soldermask, drill/slot, finish and assembler DFM review. Smallest observed drill is 0.20 mm; minimum track is 0.15 mm. They are dimensions, not supplier approval. |
| ENG-13 / high | PCB/enclosure/mount response and sensor frequency accuracy have not been physically characterized. | Unverified | Compare the assembled rigidly mounted node with an appropriate reference excitation/instrument. Preserve separate XYZ channels and characterize timing, noise, mechanical transfer and repeatability. Clean CAD cannot establish bridge-frequency accuracy. |

## USB geometry and return-path screen

**EQ-G01 — planar Euclidean path:** \(L_{xy}=\sum_i\sqrt{(x_{i+1}-x_i)^2+(y_{i+1}-y_i)^2}\).

**EQ-G02 — nominal geometric depth sensitivity:** \(L_{nom}=L_{xy}+N_v h\), using the saved board thickness \(h=1.6\) mm. All six USB vias are F.Cu–B.Cu through vias. This excludes connector/resistor/ESD internal conductors, pad traversal and actual finished layer spacing. It is not electrical delay; dielectric and coupling effects are unresolved.

| Plug contact path | D− planar total to module, mm | D+ planar total to module, mm | Via transitions D− / D+ | D−−D+ planar, mm | D−−D+ with nominal barrels, mm |
|---|---:|---:|---:|---:|---:|
| A7 / A6 | 26.522850 | 26.448011 | 2 / 4 | +0.074839 | −3.125161 |
| B7 / B6 | 25.193560 | 25.272275 | 2 / 2 | −0.078715 | −0.078715 |

Totals add connector-to-resistor and resistor-to-module tracks; resistor body is excluded. The four A-D+ transitions include two before U6. The nominal barrel correction demonstrates why the planar number is insufficient; it does not predict a USB failure. This is the module's full-speed interface, not a claim of 480 Mb/s operation because the ESD part supports that rate. [E2]

Actual trace width is 0.20 mm. Selected long parallel segments have gaps 0.153553 mm (diagonal), 0.199999 mm (vertical), 0.507106 mm (fanout), and 1.70 mm across the ESD pins. These are segment observations, not a single uniform controlled pair. Espressif calls for parallel matched routing, 90 Ω ±10%, few transitions, local ground returns and a continuous reference layer. [E1]

Sampled 3,588 points along USB trace centers and edges at ≤0.05 mm spacing on adjacent In1.Cu/In2.Cu fills. There were 437 misses, all within 0.6 mm of a USB signal via; the visual screen places them around transition clearance holes. There were **no sampled misses farther away**. This is favorable geometric evidence but does not prove the full electromagnetic return path, especially around antipads, transitions and broad fanouts. Ground-via center distances: nearest 0.75–1.40 mm; second nearest 1.13–2.53 mm. These numbers have no invented pass threshold. Improve symmetric return-via placement during any reroute. [E1]

Connector-to-ESD planar paths are 3.165–4.495 mm; A-D+ has two extra transitions there. U6 ground-pad center to nearest ground via is 0.7875 mm; this is not loop inductance. ST emphasizes short I/O, VBUS and ground connections and proximity to the connector; its Figure 17 shows 100 nF at VBUS. Physical ESD immunity remains untested. [E3]

## RF and mechanical geometry

U1 is at (138.90, 60.20) mm, 0°. Actual F.Fab antenna-region bounds are X129.90–147.90, Y47.45–53.45; the top board edge is Y53.55. Polygon collision and copper-shape checks found no overlap with that rectangle. The 0.10 mm nominal margin is **not** the antenna feedpoint coordinate or a tolerance allowance. A conservative tolerance budget is \(m_{min}=0.10-T_{outline}-T_{placement}-T_{module}\); those tolerances have not been selected.

The WROOM module already contains its RF circuit. Bare-chip RF matching instructions are not a request to reproduce that circuit on this carrier. Espressif recommends antenna overhang, housing clearance and final-product RF testing. The enclosure recommendation is at least 15 mm around the antenna; the roadway surface, cables and metal hardware still need evaluation. [E1]

For each 4×4 mm nominal MPU body, the closest screened insertion/body item is U2→J1 at 10.694 mm, U3→J2 at 5.130 mm, U4→SW1 at 8.600 mm, using conservative F.Fab bounding boxes including stroke. Actual header/switch part selection and user-applied connector/button loads remain unresolved. TDK identifies mounting stress and insertion-component proximity as concerns; its prohibition on soldering the exposed die pad and routing under it remains respected by the existing geometric audit. [E4]

## Test-point access

| Pads | Signals | Face / spacing | Distance from named GND TP2 |
|---|---|---|---|
| TP1 / TP2 | 3V3 / GND | Back; 1 mm circular exposed copper; 3 mm pitch | 3 / 0 mm |
| TP3–TP6 | I2C0 SDA/SCL, I2C1 SDA/SCL | Same | 3 / 6 / 9 / 12 mm |
| TP7–TP9 | IMU1/2/3 INT | Same | 4.243 / 3 / 4.243 mm |
| TP10–TP11 | UART TX/RX | Same | 6.708 / 9.487 mm |

All have B.Mask openings and no paste. There is no dedicated TP for VBUS_USB, +5V_FUSED, EN or BOOT. That is incomplete bring-up convenience, not an automatic electrical error. Component pads may be usable, but their assembled access was not established. A flush back mounting plate could obstruct the entire test field; no plate/enclosure/probe dimensions are fixed. Test accessibility and measurement-ground quality therefore remain open.

## Hardware equation registry and bounds

These are hardware calculations, not a new audit of firmware FFT/statistical algorithms. Numeric outputs and their assumptions are in `math.json`.

**EQ-P01 — linear-regulator power balance**

\[P_D=(V_{IN}-V_{OUT})I_{OUT}+V_{IN}I_{GND}.\]

The simplified datasheet expression omits the small ground-current term; its loaded value is not measured here. **EQ-P02 — steady-state lumped thermal model:** \(T_J=T_A+\theta_{JA}P_D\). The manufacturer's SOT223 reference-board value is 110 °C/W, with minimum recommended pads; it is not this board's thermal resistance. [E5]

| Assumed current at 5→3.3 V | Loss ignoring ground current | Rise if θJA=110 °C/W |
|---|---:|---:|
| 0.30 A | 0.51 W | 56.1 °C |
| 0.50 A | 0.85 W | 93.5 °C |
| 1.00 A | 1.70 W | 187.0 °C |

The last row is an unsustainable extrapolation on that reference thermal model, not a predicted measured temperature. Existing ground spreading/vias do not establish actual θJA. Supplier thermal evidence or measurement is still required.

**EQ-P03 — load-budget sum:** \(I_{supply}=I_{module}+\sum I_{IMU}+I_{pullups}+I_{other}\). One illustrative subtotal is 355 + 3×(3.8+0.1) + 6 = **372.7 mA**, combining one documented module TX condition, typical sensor/logic currents and four ideal low I2C lines. These are mixed conditions; this is neither a maximum nor a guaranteed average. Actual PSRAM/flash activity, startup and other loads/margins are unresolved. [E2, E4]

**EQ-P04 — rail headroom screen:** \(3.46-3.3(1.01)=0.127\) V. The 1% LDO accuracy applies only at its stated conditions. This leaves no verified allowance for line/load/temperature/ripple/overshoot; do not treat it as a full worst-case rail proof. Nominal C1=4.7 µF and C2=10 µF exceed the regulator's 1 µF input/2.2 µF output guidance, but effective capacitance at bias and temperature awaits exact MPNs. [E4, E5]

**EQ-I01 — first-order RC rise, 30–70%:**

\[t_r=t_{70}-t_{30}=R_pC_b\ln(0.7/0.3)\approx0.8473R_pC_b.\]

**EQ-I02 — maximum capacitance:** \(C_{b,max}=t_{r,max}/(0.8473R_p)\). At 2.2 kΩ and Fast-mode 300 ns this gives **160.94 pF**; with a proposed +1% resistor, **159.35 pF**. At 100 pF the nominal rise is 186.406 ns. ICs, tracks and connected probes all consume that budget. [E6]

**EQ-I03 — sink constraint:** \(R_{p,min}=(V_{DD}-V_{OL})/I_{OL}\). With 3.3 V, 0.4 V and 3 mA it is 966.67 Ω; 2.2 kΩ implies 1.318 mA at VOL=0.4 V. MPU primary-I2C parameters support this nominal screen; that table is labeled Typical, so it is not a new guaranteed all-temperature specification. ESP sink capability and real waveforms remain part of closure. [E4, E6]

**EQ-R01/R02 — enable RC:** \(\tau=RC=10\,ms\); for an ideal supply step, \(t(V_T)=-RC\ln(1-V_T/V_S)\). The illustrative 75% point is 13.863 ms, not the asserted actual EN trip voltage/time. Espressif recommends the current nominal component values but requires adjustment for real power-up behavior. [E7]

F1 is correctly identified as 1206L075/16WR. Its 0.75 A hold label applies at 20 °C; published hold currents are 0.59 A at 50 °C and 0.54 A at 60 °C. These are not transient/source-current authorization. [E8] Independent 5.1 kΩ CC terminations do not themselves implement source-current advertisement sensing. Source/cable choice and USB current behavior remain a separate review gate. [E9]

## Primary-source register

Checked 2026-10-29. A source supports only the stated component rule/test condition, never this assembled board's performance. The equation sections are the support map; pending evidence appears in the findings table.

| ID | Source / version / locator | Access and limits |
|---|---|---|
| E1 | [Espressif ESP32-S3 PCB layout guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html), sections “USB” and module positioning | Official live page opened. Requirements/recommendations, not a stackup or RF test for this carrier. |
| E2 | [WROOM-1/1U datasheet v1.8](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf), Table 1-1, §6.4.1/Table 6-4 | Opened. N16R8 −40…65 °C ambient; stated ECC condition can extend the upper limit to 85 °C with reduced usable PSRAM. Actual ECC setup and temperature not verified. |
| E3 | [ST USBLC6-2 DS4260 rev 7](https://www.st.com/resource/en/datasheet/usblc6-2.pdf), §2.3 p.6 and Fig.17 p.11 | Official PDF opened through web reader. Local PDF fetch timed out twice; no local successful-download claim. Text/figure labels support the local bypass recommendation; physical ESD tests absent. |
| E4 | [TDK/InvenSense PS-MPU-6000A-00 rev 3.4](https://d17t6iyxenbwp1.cloudfront.net/s3fs-public/2026-04/ps-mpu-6000a-00-mpu-6000-and-mpu-6050-datasheet.pdf?VersionId=eMVDQ08Qz7kahOvvE6xCs8WtRhxekFIH), pp.14,16,18,42–43 | Manufacturer-distributed PDF opened. Pin/voltage/timing, placement and assembly guidance. Does not establish current availability, authenticity, mechanical response or calibrated accuracy. |
| E5 | [Diodes AP7361C official locator](https://www.diodes.com/datasheet/download/AP7361C.pdf); [manufacturer-authored rev 5-2 mirror](https://cdn.promelec.ru/upload/grab/4donline.ihs.com/images/VipMasterIC/IC/DIOD/DIOD-S-A0011117498/DIOD-S-A0011265249-1.pdf), pp.1–2,5–6,10,12 | Official download timed out/returned 403; retrieved and hashed the manufacturer-authored October 2020 PDF from a mirror. p.6 rendered/visually checked. Current official revision freshness remains partially verified; no assertion of mirror custody equivalence or newer-revision absence. |
| E6 | [TI SLVA689A](https://www.ti.com/lit/an/slva689/slva689.pdf), revised October 2026, §2/Table 2-1 | Official PDF opened. RC/pullup relations; use physical t70−t30 for positive rise time. Actual total capacitance not provided. |
| E7 | [Espressif schematic checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html), power-up/reset | Official live page opened. RC guidance is conditional on actual supply behavior. |
| E8 | [Littelfuse 1206L datasheet](https://www.littelfuse.com/assetdocs/littelfuse-ptc-1206l-datasheet?assetguid=2b6a1515-d4ee-4c83-8bd4-152b4901b8f5), revised 2024-02-26, pp.1–2/4 | Official PDF opened; exact suffix and temperature table checked. No actual voltage-drop or trip test. |
| E9 | [ST AN5225 USB Type-C/Power Delivery guide](https://www.st.com/content/ccc/resource/technical/document/application_note/group1/38/94/1d/41/0e/ba/49/21/DM00536349/files/DM00536349.pdf/jcr:content/translations/en.DM00536349.pdf), rev 7 June 2023, §4/Table 6–7 p.10 | Official PDF reopened; source capability is detected by measuring CC voltage, not by Rd alone. Current board CC nets have no such measurement path. Distinguish this from negotiated PD. |

## Ordered continuation

1. Correct the bounded schematic/layout issues: local ESD VBUS bypass and J2-to-U3 separation; preserve exact old-reference outline. Plan and save a separate candidate first, then synchronize specification/netlist/BOM/CAD.
2. Select a fabrication stackup and actual remaining parts. Resolve USB routing and project settings together; do not add arbitrary meanders to hide the nominal via-depth mismatch.
3. Establish the load/source/ambient and mounting/access envelope. Decide regulator suitability using those inputs; finish thermal, DFM and probe-access review.
4. After changes, rerun ERC/DRC/parity/independent net and geometry checks, regenerate previews and compare hashes. Keep this report as history rather than overwriting its findings.
5. Prototype checks: unpowered shorts/assembly, current-limited power and rail/EN waveform, USB both orientations/transfer, I2C rise/VOL, three WHO_AM_I/address/INT/FIFO channels, thermal/duty-cycle behavior, mounted RF and reference-frequency tests. Define numeric operating acceptance limits before using measurements to claim qualification.

No physical measurement, field result, impedance solution, thermal simulation, EMC/ESD certification or fabrication approval was performed in this audit.
