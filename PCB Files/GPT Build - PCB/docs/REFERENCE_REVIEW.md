# Old design review and aesthetic map

Reviewed2026-10-25; corrected and re-inspected2026-10-28. **The user's latest instruction selects only `PCB Files/Reference PCB (OLD Version)/Thesis/SHM_PCB_New/` as the intended old reference.** Use its root `SHM_PCB_New.kicad_sch` and `.kicad_pcb`. The parent Thesis project and nested `SHM_Proto_PCB` below are historical comparisons only. This read-only inspection does not endorse old electrical correctness; current firmware and the confirmed ESP32-S3-WROOM-1-N16R8 / three bare MPU-6050 requirements govern the new electrical interface.

## October28 correction: prior geometry acceptance is superseded

The old selected reference PCB hash is `372996943A9C3EB3C9087C315B7C810DF9C0B70A4E0D1B47A99E9EC81B52C23F`; its schematic hash is `FDEC6C2144BB29514277FDE18DD1DFC94389EF3B5C5ED57F76D1D258EDDD6D97`. Direct KiCad10 pcbnew inspection verifies12 outline primitives,79.50 x50.45mm centerline extent, two copper layers and the component positions tabulated below.

The saved R2 board at this checkpoint, hash `DA80B01E83B4625F8C970DF54883DBA27B5402EBCA027CB8A6274129E32A0E54`, uses the parent's larger16-primitive outline and83.608663 x83.118463mm stroke-inclusive bounds. Its conformity to the clarified reference is **contradicted**. Prior clean CAD checks remain narrow evidence for their recorded old hashes; they neither validate the wrong reference selection nor transfer to a revised layout. See `reports/reference/reference_correction_20261028.json` for exact compared geometry and placements.

## Source selection

All paths below are relative to `PCB Files/Reference PCB (OLD Version)/Thesis/`.

| Source | Measured outline | Contents | Use in the new design |
| --- | --- | --- | --- |
| `Thesis.kicad_pcb` | 83.608663 x 83.118463 mm including stroke | 36 footprints, 480 track/via objects; 2 copper layers, 1.6 mm board | Historical comparison only; **not the user's intended reference**; original IO35/36 routes conflict with N16R8 |
| `SHM_PCB_New/SHM_PCB_New.kicad_pcb` | **79.50 x 50.45 mm centerline extent**; 79.60 x 50.55 mm including 0.10 mm outline stroke | 37 footprints, 480 track/via objects; 2 copper layers, 1.6 mm board | **User-selected reference**: compact three-lobe/T form; module above center, USB-C on lower left edge, one IMU per rounded end |
| `SHM_PCB_New/SHM_Proto_PCB/SHM_Proto_PCB.kicad_pcb` | 65 x 70 mm rectangle centerline; 65.05 x 70.05 mm including stroke | 21 footprint objects, including unnamed custom objects; dev board and external MPU breakout footprints | Breadboard/prototype history; unsuitable as the bare-IC board geometry source |

The existing `SHM_PCB_Top.png` was opened and visually inspected. Its broad horizontal upper bar, semicircular sensor ends, center module antenna protrusion, and downward rounded sensor arm match the **SHM_PCB_New** geometry rather than the larger top-level Thesis board. File naming alone would therefore select the wrong shape.

Neither bare-IC board contains a dedicated mounting-hole footprint. Preserve the three rounded sensor regions and overall symmetry as an aesthetic, while allowing the new layout to enlarge or reshape them for mounting, connector access, antenna clearance, and routing. Old dimensions are observed history, not an imposed enclosure constraint.

## Exact preferred outline geometry

Coordinates are millimetres in the original KiCad coordinate system. Centerline limits: X = 99.15 to 178.65, Y = 53.55 to 104.00. Three semicircles have 10 mm radius. The polygon can be traversed continuously as follows; ARC specifies a point on the arc between its endpoints.

| Primitive | Start X,Y | Midpoint X,Y if arc | End X,Y |
| --- | --- | --- | --- |
| Line | 122.05,53.55 | - | 155.75,53.55 |
| Line | 155.75,53.55 | - | 168.65,54.20 |
| ARC (right sensor end) | 168.65,54.20 | 178.65,64.20 | 168.65,74.20 |
| Line | 168.65,74.20 | - | 155.75,74.85 |
| Line | 155.75,74.85 | - | 155.75,85.55 |
| Line | 155.75,85.55 | - | 148.75,94.00 |
| ARC (bottom sensor end) | 148.75,94.00 | 138.75,104.00 | 128.75,94.00 |
| Line | 128.75,94.00 | - | 122.05,85.55 |
| Line | 122.05,85.55 | - | 122.05,74.85 |
| Line | 122.05,74.85 | - | 109.15,74.20 |
| ARC (left sensor end) | 109.15,74.20 | 99.15,64.20 | 109.15,54.20 |
| Line | 109.15,54.20 | - | 122.05,53.55 |

Original placements: MCU U1 at (138.90,60.55), rotation 0 degrees; left MPU U5 at (109.15,64.20), right MPU U4 at (168.65,64.20), bottom MPU U2 at (138.726098,93.999244), all rotation 0 degrees. USB J1 at (124.635,80.36), rotation -90 degrees. These are reference positions only; new sensor identity is defined by the firmware bus/address/INT table, not the old X/Y/Z label names.

## Schematic visual language

The old `SHM_PCB_New/SHM_Schematics.pdf` was rendered and inspected, and the current `.kicad_sch` was exported separately to SVG. The reference uses A4 landscape with:

- Three similarly sized and aligned MPU circuits across the upper half, in one visually grouped sensor block.
- USB and regulator at lower left; MCU in the lower center; supply decoupling, EN/reset and boot at lower right.
- Thin blue L-shaped separator lines with short blue block headings, ample whitespace between blocks, named global signal labels instead of long interblock wires.
- Short orthogonal wires, visible connection dots, supply arrows above circuits and ground symbols below.

Keep those grouping principles, repeated sensor alignment and clear headings. A larger sheet or separate power/control/sensor sheets is appropriate if the added protection and test points no longer fit without collisions. Correct the old heading `AX-AY-AX`: each MPU supplies X, Y and Z; the devices are IMU1, IMU2 and IMU3, not one sensor per axis.

## Footprints and reusable assets

Observed library identities in both old bare-IC designs:

| Item | Old library footprint | Reuse boundary |
| --- | --- | --- |
| ESP32-S3-WROOM-1 | `RF_Module:ESP32-S3-WROOM-1` | Recheck current manufacturer land pattern, module ordering code, antenna exclusion and exposed ground pads |
| MPU-6050, three | `Sensor_Motion:InvenSense_QFN-24_4x4mm_P0.5mm` | Recheck all 24 pad numbers and manufacturer handling/layout guidance; no generic exposed-pad QFN substitution |
| USB-C J1 | `Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal` | Useful style and mechanical starting point; verify exact purchased connector drawing |
| Resistors | `Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder` | Larger hand-solder pads; electrical values require fresh design |
| Ceramic capacitors | `Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder` | Package option, not proof of value/rating suitability |
| Tantalum capacitors | `Capacitor_Tantalum_SMD:CP_EIA-2012-15_AVX-P_HandSolder` | Do not inherit regulator stability/ESR assumptions |
| AMS1117 regulator | `Package_TO_SOT_SMD:SOT-223-3_TabPin2` | Historical component, new power design requires datasheet and dissipation analysis |
| Buttons | `TS-1088 (Push Button):SW_TS-1088-AR02016` | Custom external library name; embedded geometry is available in old PCB, but verify exact switch MPN before reuse |
| Logos | Embedded footprints with library identifier `LOGO` | Decorative assets; separate from electrical footprint count and keep away from pads/assembly markings |

No old traces, zones or net names should be transferred as validated electrical design. An embedded footprint makes a board viewable without the original library, but does not establish datasheet accuracy.

## Historical electrical conflicts

Direct pad/net inspection establishes these differences:

| Old item | Observed old implementation | Current design requirement |
| --- | --- | --- |
| Main I2C bus | Top-level Thesis uses module pads28/29 = IO35/36; later SHM_PCB_New already moved to pads12/17 = IO8/9 | IO8/9 bus0 plus **IO10/11 bus1**, consistent with `hardware_profile.h` |
| MPU AD0 | GPIO4/5/6 go to three AD0 pins | Fixed AD0 low/high/low; GPIO4/5/6 connect to individual INT pins |
| MPU INT | All three unconnected | Individual data-ready interrupt inputs are required by the implemented timestamp/FIFO method |
| CPOUT capacitors | C9/C12/C15 = 220 pF in old schematic | Recheck and implement manufacturer typical circuit; historical engineering review identifies 2.2 nF, not the old value |
| Pull-ups | Main bus plus AUX pull-ups remain | One correctly sized pair per main I2C bus; unused AUX pins handled per manufacturer instructions |
| Mounting | No dedicated mounting-hole footprints | Deliberate rigid mechanical attachment and local support must be designed |

The historical `MD Files/05_SCHEMATIC_PCB_V2_SPEC.md` is an engineering proposal, not current authorization to override user choices. In particular it proposes IO15/16 for bus1 and IO10/11 for SD, recommends avoiding R8 modules, suggests FIFO without mandatory INT, and gives an approximate 75 x 79 mm outline. All conflict with current firmware, the confirmed N16R8 choice, or the measured files. Its proposed microSD block is absent from current firmware. Its current, thermal, mechanical-distance and pull-up estimates must be re-derived for the selected design, not quoted as measured facts. The active method retains raw data in PSRAM and later persists to onboard flash.

## Evidence and reproduction

Artifacts under `../reports/reference/`:

- `reference_inventory.json`: exact old source paths and SHA-256 hashes, edge primitives, footprint identities/positions/rotations and pad/net assignments for all three boards, extracted with installed KiCad10 `pcbnew`.
- `SHM_PCB_New-top.svg`: KiCad CLI export of front copper/silkscreen/outline, current source board.
- `SHM_PCB_New.svg`: KiCad CLI export of current source schematic.
- `old-schematic-pdf.png`: visual inspection raster of existing old schematic PDF (a historical PDF may not contain the latest editor changes).

Read-only tooling observations: first inventory command used an obsolete `LIB_ID.GetUniString()` API; corrected to `GetUniStringLibId()` and successfully reran. Initial Inkscape raster conversion reported a `Gio::DBus::Error`; a subsequent invocation completed asynchronously and produced `SHM_PCB_New-schematic.png` and `SHM_PCB_New-top.png`, both opened and visually inspected. Existing PDF rasterization with Poppler also succeeded. KiCad printed duplicate image-handler warnings when loading several boards in one process; all three board inventories were produced. No old source file was saved or modified.

Historical integration decision, **superseded2026-10-28**: the larger top-level Thesis outline was initially selected to provide room for mounting and revised circuitry. The user's clarified reference rejects that choice as the active basis. Preserve this entry as provenance; use the root SHM_PCB_New geometry and repeat affected design checks. See `DECISION_MAP.md` and `HANDOFF.md` for current implementation status.

## Placement guidance for the corrected reference

Observed reference anchors: U1=(138.90,60.55), left IMU=(109.15,64.20), right IMU=(168.65,64.20), bottom IMU approximately(138.75,94.00), all rotation0degrees; USB-C=(124.635,80.36), rotation-90degrees. The center spine spansX122.05..155.75 andY53.55..85.55 before its tapered lower arm. This is a compact layout, so carrying over positions from the larger board would place some parts beyond its outline.

**Proposed, unverified placement candidates:** retain the module/side-sensor anchors where the actual courtyard and antenna checks permit. Side mounting-hole centers near(114.65,69.70) and(163.15,69.70) are each7.78mm from their reference sensor center. A bottom sensor near(138.75,92.00) and hole near(138.75,99.00) would have7mm separation. These numbers are geometric suggestions only, not mechanical acceptance or final CAD instructions. Review the complete screw/washer keepout, hole-edge margin, nearby passives, stress, package distances and enclosure before adopting them. No fixed thermal-separation distance is claimed from these coordinates.

Preserve device identity by nets, not historic references: old U2/U4/U5 are three sensor locations; current R2 U2/U3/U4 are IMU1/2/3. The lower sensor's reference center should not force channel relabeling. Keep all physical axes consistent and document any chosen relocation.

The separate `.obsidian-vault/05-hardware/SCHEMATIC_AESTHETIC_STANDARD.md` cites the parent Thesis source and includes old220pF CPOUT, dynamic-AD0 labels, optional INT and one-device-per-axis wording. Only its visual grouping/stub/spacing ideas are reusable after comparison to the now-specified root SHM_PCB_New schematic; those electrical details and parent-source selection are historical, not requirements.
