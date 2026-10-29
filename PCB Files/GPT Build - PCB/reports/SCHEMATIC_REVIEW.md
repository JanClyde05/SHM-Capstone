# Schematic review, 26 October 2026

## Files and reproduction

The editable design is `design/SHM_Node_R2.kicad_sch`. Its source is `tools/build_schematic.py`; run that with the Python bundled with KiCad 10.0.6. It writes the schematic, `design/circuit_spec.json`, and the local ESP32 overhang footprint. It does not edit the PCB.

The generator uses installed KiCad symbol definitions and flattens inherited symbol geometry into the schematic cache. The current design has 49 physical components. Local footprint registration is in `design/fp-lib-table`.

The schematic uses an A3 landscape sheet to preserve the reference design's framed functional blocks and short labeled connections while providing space for three full XYZ sensor circuits, protection, independent bus pullups and testpoints. Graphical rectangles form the frames; they are not electrical buses. A4 would require either several sheets or reduced legibility at this component count.

## Corrections recorded

1. Initial automatic ERC found missing local footprint registration and off-grid power flag positions. The local library table and grid positions were corrected. The initial report is retained in `erc_initial.json`.
2. Component reference/value fields near the ESP32 and MPU power stems were separated. U5 and U6 fields were moved above their bodies. Passive fields were changed to left justification to prevent the long CC resistance values from touching their resistor symbols.
3. The testpoint strip was lifted off the sheet border. Testpoint values are hidden because each stub already has its connected net label; this removes duplicated text on TP1. J2 explicitly reads `UART DEBUG (3V3 LOGIC)` and has only GND, MCU TX and MCU RX pins.
4. U5's explanatory note was moved below its ground symbol. Power flag labels were moved clear of their diamond symbols.
5. F1's procurement metadata was corrected from the unverified `1206L075/16YR` to manufacturer-listed `1206L075/16WR`. Capacitance tolerance is recorded as 10% or better; C9/C13/C17 are explicitly 2.2 nF, 50 V, X7R.
6. The ESP32 footprint was cloned as `SHM_Local:ESP32-S3-WROOM-1_Overhang`. Three front silkscreen antenna graphics whose local bounding box starts above y = -7.8 mm were moved to front fabrication. Pads, pad numbering, pad positions/sizes/shapes, courtyard and antenna rule area retain their source geometry. The generator asserts identical pad geometry after saving and reloading the clone.
7. The first footprint generation attempt used `SetDescription`, unavailable on KiCad's FOOTPRINT API. The correct `SetLibDescription` API was used and generation completed successfully. No failed output was accepted as final.

## Checks completed

- KiCad 10.0.6 parses the generated schematic and exports its XML netlist, SVG and PDF.
- `reports/erc_current.json` contains zero errors and zero warnings. KiCad's default ignored checks are listed in that report; no individual ERC violations were excluded to obtain this result.
- All 148 intentionally connected package pin endpoints in the exported netlist were compared with the declared component/net mapping. Local-label leading slashes were normalized solely for this comparison.
- Native U1 package pins match the firmware's two I2C buses, three interrupt inputs and native USB pins. U2/U3/U4 use fixed AD0 low/high/low respectively, with both VDD and VLOGIC at 3.3 V.
- The local ESP32 footprint generation assertion confirms the pad geometry remained identical after the artwork change.
- The PDF was rendered with Poppler and inspected as a full sheet and with the USB/power section enlarged. The final PNG is `previews/SHM_Node_R2_schematic.png`; the vector document is `previews/SHM_Node_R2_schematic.pdf`.

ERC and netlist agreement establish schematic consistency. They do not establish regulator temperature, USB compliance, assembly yield, RF performance, mechanical coupling or measured acquisition accuracy. Those remain prototype checks documented elsewhere in this project.
