from pathlib import Path
from PIL import Image

# Legacy combined renderer retained for provenance. Its field-workflow outputs
# are intentionally suffixed `_legacy`; use generate_field_workflow_bw.py for
# the active Figure 3.5 SVG/PNG pair.
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "figure_3_3_field_workflow_color_restored.png"
BW = ROOT / "figure_3_3_field_workflow_bw_legacy.png"
FLOW_SVG = ROOT / "figure_3_4_firmware_flow_bw.svg"
FIELD_SVG = ROOT / "figure_3_5_field_workflow_bw_legacy.svg"

# Preserve the field-workflow content/layout while converting it to high-contrast
# black and white. Original colored source stays available for provenance.
im = Image.open(SRC).convert("RGB")
pixels = im.load()
for y in range(im.height):
    for x in range(im.width):
        r, g, b = pixels[x, y]
        luminance = (299 * r + 587 * g + 114 * b) // 1000
        value = 0 if luminance < 218 else 255
        pixels[x, y] = (value, value, value)
im.save(BW, optimize=True)

W, H = 1800, 2100
parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <marker id="arrow" viewBox="0 0 12 12" refX="10" refY="6" markerWidth="15" markerHeight="15" orient="auto">
    <path d="M 1 1 L 11 6 L 1 11 z" fill="#000"/>
  </marker>
  <style>
    text {{ font-family: Arial, Helvetica, sans-serif; fill: #000; }}
    .panel {{ fill: #fff; stroke: #000; stroke-width: 3; }}
    .bar {{ fill: #000; stroke: #000; stroke-width: 2; }}
    .barText {{ fill: #fff; font-size: 30px; font-weight: 700; letter-spacing: .5px; }}
    .box, .diamond, .term {{ fill: #fff; stroke: #000; stroke-width: 3; }}
    .label {{ font-size: 25px; text-anchor: middle; dominant-baseline: middle; }}
    .labelSmall {{ font-size: 22px; text-anchor: middle; dominant-baseline: middle; }}
    .branch {{ font-size: 22px; font-weight: 700; text-anchor: middle; dominant-baseline: middle; }}
    .arrow {{ fill: none; stroke: #000; stroke-width: 3.5; stroke-linecap: square; stroke-linejoin: round; marker-end: url(#arrow); }}
    .connector {{ fill: #fff; stroke: #000; stroke-width: 3; }}
    .connectorText {{ font-size: 25px; font-weight: 700; text-anchor: middle; dominant-baseline: middle; }}
    .note {{ font-size: 21px; text-anchor: middle; dominant-baseline: middle; }}
  </style>
</defs>
<rect width="1800" height="2100" fill="#fff"/>
<text x="900" y="48" text-anchor="middle" font-size="34px" font-weight="700">CURRENT FIRMWARE FLOW</text>
''']

def text_lines(cx, cy, lines, cls="label", gap=30):
    first = cy - (len(lines) - 1) * gap / 2
    out = [f'<text class="{cls}" x="{cx}" y="{first}">']
    for i, line in enumerate(lines):
        out.append(f'<tspan x="{cx}" dy="{0 if i == 0 else gap}">{line}</tspan>')
    out.append("</text>")
    return "".join(out)

def box(x, y, w, h, lines, cls="box", font="label", gap=30, radius=4):
    return (f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}"/>'
            + text_lines(x + w / 2, y + h / 2, lines, font, gap))

def diamond(cx, cy, w, h, lines, gap=29):
    pts = f"{cx},{cy-h/2} {cx+w/2},{cy} {cx},{cy+h/2} {cx-w/2},{cy}"
    return f'<polygon class="diamond" points="{pts}"/>' + text_lines(cx, cy, lines, "labelSmall", gap)

def terminator(x, y, w, h, lines):
    return box(x, y, w, h, lines, "term", "label", 30, h / 2)

def arrow(d):
    return f'<path class="arrow" d="{d}"/>'

def connector(cx, cy, letter, r=24):
    return (f'<circle class="connector" cx="{cx}" cy="{cy}" r="{r}"/>'
            f'<text class="connectorText" x="{cx}" y="{cy}">{letter}</text>')

parts += [
 '<rect class="panel" x="35" y="90" width="850" height="1970" rx="10"/>',
 '<rect class="bar" x="35" y="90" width="850" height="68" rx="8"/>',
 '<text class="barText" x="460" y="124" text-anchor="middle" dominant-baseline="middle">SESSION CONTROL &amp; ACQUISITION</text>',
 '<rect class="panel" x="915" y="90" width="850" height="1970" rx="10"/>',
 '<rect class="bar" x="915" y="90" width="850" height="68" rx="8"/>',
 '<text class="barText" x="1340" y="124" text-anchor="middle" dominant-baseline="middle">WINDOW ANALYSIS &amp; FINALIZATION</text>',
]

# Arrows are drawn first so arrowheads are visible and do not cover node text.
parts += [
 # Session start and acquisition
 arrow("M 460 260 V 285"), arrow("M 460 375 V 402"),
 arrow("M 320 450 H 275"), arrow("M 460 515 V 585"),
 arrow("M 460 670 V 695"), arrow("M 460 795 V 820"),
 arrow("M 320 890 H 280"), arrow("M 460 960 V 1015"),
 arrow("M 600 1085 H 824"), arrow("M 460 1155 V 1190"),
 arrow("M 460 1285 V 1315"), arrow("M 600 1385 H 824"),
 arrow("M 460 1455 V 1505"),
 # A means return to the next capture cycle.
 arrow("M 826 745 H 782"),
 # Incomplete path to queued-window analysis.
 arrow("M 165 940 V 1015 H 93 V 1050"),
 # Normal completion handoff.
 arrow("M 460 1595 V 1626"),
 # B continues in the right panel; C loops to the next window-axis record.
 arrow("M 985 250 H 1035"), arrow("M 1695 250 H 1660"),
 arrow("M 1340 290 V 330"), arrow("M 1200 400 H 1145"),
 arrow("M 1340 470 V 510"), arrow("M 1340 580 V 605"),
 arrow("M 1340 675 V 700"), arrow("M 1340 770 V 795"),
 arrow("M 1340 865 V 900"), arrow("M 1340 975 V 1015"),
 arrow("M 1035 455 V 937 H 1080"),
 arrow("M 1480 1085 H 1696"), arrow("M 1340 1155 V 1190"),
 arrow("M 1340 1265 V 1295"), arrow("M 1200 1365 H 1105"),
 arrow("M 1480 1365 H 1560"),
 # Both median outcomes feed the same persistence step.
 arrow("M 1015 1410 V 1460 H 1215 V 1490"),
 arrow("M 1650 1410 V 1460 H 1465 V 1490"),
 arrow("M 1340 1565 V 1590"), arrow("M 1340 1665 V 1690"),
 arrow("M 1200 1755 H 1105"), arrow("M 1480 1755 H 1560"),
 arrow("M 1015 1800 V 1845 H 1215 V 1875"),
 arrow("M 1650 1800 V 1845 H 1465 V 1875"),
 arrow("M 1340 1950 V 1975"),
]

# Left panel: session control and data capture.
parts += [
 terminator(270,190,380,70,["Session request"]),
 box(115,285,690,90,["Check precheck, sensors, PSRAM/storage, mode, station,",
                      "orientation, and frozen formal settings"],"box","labelSmall",29),
 diamond(460,450,280,130,["All start checks","pass?"]),
 box(50,420,225,100,["Reject start;","report reason"],"box","labelSmall",28),
 box(195,585,530,85,["Arm session with a 5-second countdown"],"box","labelSmall",28),
 box(140,695,640,100,["Capture the fixed 600-second session:",
                       "read and timestamp sequential channel X/Y/Z samples"],"box","labelSmall",29),
 diamond(460,890,280,140,["Sensors ready and","buffer capacity available?"]),
 box(50,840,230,100,["Stop capture;","mark record incomplete"],"box","labelSmall",28),
 diamond(460,1085,280,140,["Has the next","60-second boundary passed?"]),
 box(95,1190,730,95,["Seal and queue the completed window after",
                      "all three sensors reach its boundary"],"box","labelSmall",29),
 diamond(460,1385,280,140,["Are 10 windows","(600 seconds) complete?"]),
 box(175,1505,570,90,["Stop capture and wait for queued window jobs"],"box","labelSmall",28),
 connector(850,745,"A",24), connector(850,1085,"A",24), connector(850,1385,"A",24),
 connector(93,1074,"B",24), connector(460,1650,"B",24),
 text_lines(460,1715,["A: continue the capture cycle","B: proceed to queued-window analysis"],"note",30),
]

# Right panel: one process box per firmware action.
parts += [
 connector(960,250,"B",24), connector(1720,250,"C",24), connector(1720,1070,"C",24),
 box(1035,210,625,80,["Select the next queued window, sensor, and axis"],"box","labelSmall",28),
 diamond(1340,400,280,140,["Do timing, coverage,","and signal-quality checks pass?"]),
 box(925,350,220,105,["Skip spectral steps;","mark peak invalid"],"box","labelSmall",25),
 box(1080,510,520,70,["Remove the window mean"],"box","labelSmall",27),
 box(1080,605,520,70,["Apply the symmetric Hann window"],"box","labelSmall",27),
 box(1080,700,520,70,["Compute the N-point DFT using Bluestein"],"box","labelSmall",27),
 box(1080,795,520,70,["Select the largest positive in-band bin"],"box","labelSmall",27),
 box(1080,900,520,75,["Store window result and QC flags"],"box","labelSmall",27),
 diamond(1340,1085,280,140,["More queued","records?"]),
 box(1080,1190,520,75,["Count valid peaks for each channel-axis"],"box","labelSmall",27),
 diamond(1340,1365,280,140,["At least 10 valid peaks","for this channel-axis?"]),
 box(925,1320,180,90,["Retain QC;","no median"],"box","labelSmall",25),
 box(1560,1320,180,90,["Calculate","per-axis median"],"box","labelSmall",25),
 box(1040,1490,600,75,["Save raw records, windows CSV, and session summary"],"box","labelSmall",27),
 box(1040,1590,600,75,["Await the operator’s concurrent vehicle tally"],"box","labelSmall",27),
 diamond(1340,1755,280,130,["Are local count cutoffs","frozen?"]),
 box(925,1710,180,90,["Assign","UNCLASSIFIED"],"box","labelSmall",26),
 box(1560,1710,180,90,["Assign frozen","local group"],"box","labelSmall",26),
 box(1040,1875,600,75,["Save the finalized session summary"],"box","labelSmall",27),
 terminator(1240,1975,200,50,["End"]),
]

# Branch labels are placed outside diamonds and connector routes.
parts += [
 '<text class="branch" x="298" y="430">NO</text>',
 '<text class="branch" x="500" y="555">YES</text>',
 '<text class="branch" x="298" y="875">NO</text>',
 '<text class="branch" x="500" y="978">YES</text>',
 '<text class="branch" x="710" y="1062">NO</text>',
 '<text class="branch" x="500" y="1176">YES</text>',
 '<text class="branch" x="710" y="1362">NO</text>',
 '<text class="branch" x="500" y="1477">YES</text>',
 '<text class="branch" x="1172" y="372">NO</text>',
 '<text class="branch" x="1395" y="492">YES</text>',
 '<text class="branch" x="1585" y="1062">YES</text>',
 '<text class="branch" x="1395" y="1172">NO</text>',
 '<text class="branch" x="1150" y="1340">NO</text>',
 '<text class="branch" x="1520" y="1340">YES</text>',
 '<text class="branch" x="1150" y="1730">NO</text>',
 '<text class="branch" x="1520" y="1730">YES</text>',
]
parts.append("</svg>")
FLOW_SVG.write_text("".join(parts), encoding="utf-8")

# A separate monochrome field workflow uses one process per rectangle and
# conventional decision/connector shapes. It preserves the source workflow's
# approval, acquisition, acceptance, classification, and reporting steps.
FW, FH = 1800, 1710
field = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{FW}" height="{FH}" viewBox="0 0 {FW} {FH}">
<defs><marker id="fArrow" viewBox="0 0 12 12" refX="10" refY="6" markerWidth="15" markerHeight="15" orient="auto">
<path d="M 1 1 L 11 6 L 1 11 z" fill="#000"/></marker></defs>
<style>
text {{ font-family: Arial, Helvetica, sans-serif; fill:#000; }}
.panel {{ fill:#fff; stroke:#000; stroke-width:3; }}
.bar {{ fill:#000; stroke:#000; stroke-width:2; }}
.barText {{ fill:#fff; font-size:29px; font-weight:700; letter-spacing:.4px; }}
.box,.diamond,.term {{ fill:#fff; stroke:#000; stroke-width:3; }}
.labelSmall {{ font-size:25px; text-anchor:middle; dominant-baseline:middle; }}
.branch {{ font-size:22px; font-weight:700; text-anchor:middle; dominant-baseline:middle; }}
.note {{ font-size:24px; text-anchor:middle; dominant-baseline:middle; }}
.arrow {{ fill:none; stroke:#000; stroke-width:3.5; stroke-linecap:square; stroke-linejoin:round; marker-end:url(#fArrow); }}
.line {{ fill:none; stroke:#000; stroke-width:3.5; stroke-linecap:square; stroke-linejoin:round; }}
.connector {{ fill:#fff; stroke:#000; stroke-width:3; }}
.connectorText {{ font-size:25px; font-weight:700; text-anchor:middle; dominant-baseline:middle; }}
</style>
<rect width="1800" height="1710" fill="#fff"/>
<text x="900" y="46" text-anchor="middle" font-size="34px" font-weight="700">FIELD DATA COLLECTION &amp; EVALUATION</text>
''']

field += [
 '<rect class="panel" x="35" y="90" width="850" height="1430" rx="10"/>',
 '<rect class="bar" x="35" y="90" width="850" height="68" rx="8"/>',
 '<text class="barText" x="460" y="124" text-anchor="middle" dominant-baseline="middle">PREPARE &amp; ACQUIRE</text>',
 '<rect class="panel" x="915" y="90" width="850" height="1430" rx="10"/>',
 '<rect class="bar" x="915" y="90" width="850" height="68" rx="8"/>',
 '<text class="barText" x="1340" y="124" text-anchor="middle" dominant-baseline="middle">ACCEPT, CLASSIFY &amp; ANALYZE</text>',
]

# Prepare and acquire: explicit sequential steps, then concurrent sampling/counting.
for i in range(9):
    y = 180 + i * 65
    if i:
        field.append(f'<path class="arrow" d="M 460 {y-20} V {y}"/>')
field += [
 '<path class="arrow" d="M 460 746 V 800"/>',
 '<path class="arrow" d="M 460 870 V 915 H 270 V 945"/>',
 '<path class="arrow" d="M 460 870 V 915 H 650 V 945"/>',
 '<path class="line" d="M 270 1030 V 1072 H 460"/>',
 '<path class="arrow" d="M 650 1030 V 1072 H 460 V 1110"/>',
 '<path class="arrow" d="M 460 1180 V 1230"/>',
 '<path class="arrow" d="M 460 1300 V 1326"/>',
 '<path class="arrow" d="M 816 835 H 790"/>',
 # B continues to the acceptance check in the right panel.
 '<path class="arrow" d="M 1340 209 V 225"/>',
 # Technical rejection and the next-session connector.
 '<path class="arrow" d="M 1195 290 H 1120"/>',
 '<path class="arrow" d="M 1025 330 V 375"/>',
 '<path class="arrow" d="M 1025 455 V 476"/>',
 # Accepted session path.
 '<path class="arrow" d="M 1340 355 V 390"/>',
 '<path class="arrow" d="M 1340 460 V 545"/>',
 '<path class="arrow" d="M 1195 605 H 1120"/>',
 '<path class="arrow" d="M 1485 605 H 1550"/>',
 '<path class="arrow" d="M 1025 645 V 690 H 1245 V 725"/>',
 '<path class="arrow" d="M 1645 645 V 690 H 1425 V 725"/>',
 '<path class="arrow" d="M 1340 800 V 830"/>',
 '<path class="arrow" d="M 1340 905 V 940"/>',
 '<path class="arrow" d="M 1340 1015 V 1050"/>',
 '<path class="arrow" d="M 1340 1125 V 1160"/>',
 '<path class="arrow" d="M 1340 1235 V 1260"/>',
 '<path class="arrow" d="M 1195 1320 H 984"/>',
 '<path class="arrow" d="M 1340 1380 V 1420"/>',
]

prep = [
 "Obtain written site permission",
 "Obtain ethics and privacy determination",
 "Obtain site-safety clearance",
 "Freeze analysis settings",
 "Freeze pilot traffic-count cutoffs",
 "Bench-check the single PCB",
 "Verify the approved station and orientation",
 "Install the board at the fixed station",
 "Run the stationary precheck",
]
for i, label in enumerate(prep):
    field.append(box(110,180+i*65,700,46,[label],"box","labelSmall",28))

field += [
 box(150,800,620,70,["Start the fixed 600-second session"],"box","labelSmall",28),
 connector(840,835,"A",24),
 box(110,945,320,85,["Record sequential IMU","samples"],"box","labelSmall",28),
 box(490,945,320,85,["Tally vehicles","concurrently"],"box","labelSmall",28),
 box(150,1110,620,70,["Stop both activities at 600 seconds"],"box","labelSmall",28),
 box(150,1230,620,70,["Save raw records and session metadata"],"box","labelSmall",28),
 connector(460,1350,"B",24),
 connector(960,220,"B",24),
 diamond(1340,270,290,130,["Does the session meet","technical criteria?"]),
 box(930,230,190,80,["Log exclusion","reason"],"box","labelSmall",27),
 box(930,350,190,80,["Exclude from the","valid-session set"],"box","labelSmall",27),
 connector(960,500,"A",24),
 box(1160,375,360,70,["Calculate rate: r = C/10 vehicles/min"],"box","labelSmall",27),
 diamond(1340,550,290,120,["Are local count cutoffs","frozen?"]),
 box(930,510,190,80,["Assign","UNCLASSIFIED"],"box","labelSmall",27),
 box(1550,510,190,80,["Assign pilot-defined","local group"],"box","labelSmall",27),
 box(1160,675,360,75,["Create ten consecutive 60-second windows"],"box","labelSmall",27),
 box(1160,785,360,75,["Process channel-axis windows using","the firmware flowchart (Figure 3.4)"],"box","labelSmall",27),
 box(1160,895,360,75,["Summarize valid estimates by","channel and axis"],"box","labelSmall",27),
 box(1160,1005,360,75,["Compare with the matching","descriptive baseline"],"box","labelSmall",27),
 box(1160,1115,360,75,["Serve the session summary on","the local dashboard"],"box","labelSmall",27),
 diamond(1340,1280,290,120,["Five valid sessions reached","in each group?"]),
 box(1160,1375,360,70,["Report actual valid-session counts"],"box","labelSmall",27),
 connector(960,1280,"A",24),
 '<text class="branch" x="1158" y="248">NO</text>',
 '<text class="branch" x="1378" y="358">YES</text>',
 '<text class="branch" x="1155" y="530">NO</text>',
 '<text class="branch" x="1508" y="530">YES</text>',
 '<text class="branch" x="1088" y="1256">NO</text>',
 '<text class="branch" x="1378" y="1357">YES</text>',
 '<rect class="box" x="35" y="1490" width="1730" height="90" rx="5"/>',
 '<text class="note" x="900" y="1522"><tspan x="900" dy="0">Five sessions per group is a practical target, not a power calculation.</tspan>',
 '<tspan x="900" dy="31">Align the manuscript and firmware window-validity rules before formal collection.</tspan></text>',
 '</svg>',
]
FIELD_SVG.write_text("".join(field), encoding="utf-8")
print(f"Created {BW.name} ({Image.open(BW).size}), {FLOW_SVG.name}, and {FIELD_SVG.name}; use generate_field_workflow_bw.py for active Figure 3.5")
