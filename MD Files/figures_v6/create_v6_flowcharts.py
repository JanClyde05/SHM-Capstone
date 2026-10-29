from html import escape
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parent
INKSCAPE = Path(r"D:\Inkscape\bin\inkscape.com")
EXPORT_WIDTH = 2400


def text(x, y, lines, size=30, weight=400, color="#000", leading=None, cls="label"):
    lines = [escape(str(line)) for line in lines]
    leading = leading or size * 1.18
    first_y = y - (len(lines) - 1) * leading / 2
    tspans = "".join(
        f'<tspan x="{x}" y="{first_y + i * leading:.1f}">{line}</tspan>'
        for i, line in enumerate(lines)
    )
    return (f'<text class="{cls}" x="{x}" y="{y}" font-size="{size}px" '
            f'font-weight="{weight}" fill="{color}">{tspans}</text>')


def rect_box(x, y, w, h, lines, size=30, radius=8, weight=500):
    return (f'<rect class="box" x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}"/>'
            + text(x + w / 2, y + h / 2, lines, size=size, weight=weight))


def terminal(x, y, w, h, lines, size=30):
    return (f'<rect class="terminal" x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}"/>'
            + text(x + w / 2, y + h / 2, lines, size=size, weight=500))


def diamond(cx, cy, w, h, lines, size=29):
    points = f"{cx},{cy-h/2} {cx+w/2},{cy} {cx},{cy+h/2} {cx-w/2},{cy}"
    return f'<polygon class="diamond" points="{points}"/>' + text(cx, cy, lines, size=size, weight=500)


def circle(cx, cy, label, r=26):
    return (f'<circle class="connector" cx="{cx}" cy="{cy}" r="{r}"/>'
            + text(cx, cy, [label], size=28, weight=700, cls="connectorText"))


def arrow(path, width=4.5):
    return f'<path class="arrow" stroke-width="{width}px" d="{path}"/>'


def branch(x, y, label):
    width = 46 if label == "YES" else 38
    return (f'<rect class="branchMask" x="{x-width/2}" y="{y-19}" width="{width}" height="38" rx="5"/>'
            + text(x, y, [label], size=24, weight=700, cls="branch"))


def panel(x, y, w, h, title):
    head_h = 72
    return (
        f'<rect class="panel" x="{x}" y="{y}" width="{w}" height="{h}" rx="5"/>'
        f'<rect class="bar" x="{x}" y="{y}" width="{w}" height="{head_h}" rx="5"/>'
        + text(x + w / 2, y + head_h / 2, [title], size=32, weight=700, color="#fff", cls="barText")
    )


def svg_start(width, height, title):
    return [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<defs>
  <marker id="arrow" viewBox="0 0 16 14" refX="15" refY="7" markerWidth="16" markerHeight="14" markerUnits="userSpaceOnUse" orient="auto">
    <path d="M0 0 L16 7 L0 14 Z" fill="#000"/>
  </marker>
</defs>
<style>
  text {{ font-family: Arial, Helvetica, sans-serif; text-anchor: middle; dominant-baseline: middle; }}
  .panel {{ fill:#fff; stroke:#000; stroke-width:3.5; }}
  .bar {{ fill:#000; stroke:#000; stroke-width:3; }}
  .barText {{ letter-spacing:.2px; }}
  .box,.diamond,.terminal {{ fill:#fff; stroke:#000; stroke-width:3.5; }}
  .arrow {{ fill:none; stroke:#000; stroke-linecap:round; stroke-linejoin:round; marker-end:url(#arrow); }}
  .connector {{ fill:#fff; stroke:#000; stroke-width:3.5; }}
  .branchMask {{ fill:#fff; stroke:none; }}
</style>
<rect width="{width}" height="{height}" fill="#fff"/>
<text x="{width/2}" y="32" font-size="34px" font-weight="700">{escape(title)}</text>
''']


def export_svg(name, width, height, parts):
    svg_path = ROOT / f"{name}.svg"
    png_path = ROOT / f"{name}.png"
    svg_path.write_text("".join(parts) + "</svg>\n", encoding="utf-8")
    if not INKSCAPE.exists():
        raise FileNotFoundError(f"Inkscape renderer not found: {INKSCAPE}")
    subprocess.run([
        str(INKSCAPE), str(svg_path), "--export-type=png",
        f"--export-filename={png_path}", f"--export-width={EXPORT_WIDTH}"
    ], check=True)
    return svg_path, png_path


def firmware_flow():
    W, H = 1800, 1970
    p = svg_start(W, H, "CURRENT FIRMWARE FLOW")
    p += [panel(24, 60, 866, 1870, "SESSION CONTROL AND ACQUISITION")]
    p += [panel(910, 60, 866, 1870, "WINDOW ANALYSIS AND FINALIZATION")]

    # Process and decision shapes: session-control panel.
    p += [terminal(207, 160, 500, 70, ["Session request"], 31)]
    p += [rect_box(110, 255, 694, 100,
                   ["Precheck sensors, PSRAM/storage, mode, station,",
                    "orientation, and settings frozen for formal mode"], 29)]
    p += [diamond(457, 445, 360, 132, ["Do all start", "checks pass?"], 29)]
    p += [rect_box(32, 404, 200, 82, ["Reject start;", "report reason"], 27)]
    p += [terminal(97, 514, 100, 52, ["End"], 27)]
    p += [rect_box(160, 590, 594, 76, ["Arm session with a 5-second countdown"], 29)]
    p += [rect_box(130, 705, 650, 88, ["Read sequential X/Y/Z samples", "from the three sensors"], 28)]
    p += [rect_box(130, 815, 650, 78, ["Timestamp and buffer each sensor reading"], 29)]
    p += [diamond(457, 985, 400, 150, ["Are sensors ready", "and the buffer", "available?"], 25)]
    p += [rect_box(32, 944, 200, 82, ["Stop capture;", "mark incomplete"], 27)]
    p += [terminal(97, 1055, 100, 52, ["End"], 27)]
    p += [diamond(457, 1164, 400, 156, ["Has the next", "60-second boundary", "arrived?"], 23)]
    p += [rect_box(122, 1295, 670, 82, ["Seal and queue the completed 60-second window"], 28)]
    p += [diamond(457, 1468, 400, 156, ["Are all 10 windows", "within 600 seconds", "complete?"], 24)]
    p += [rect_box(140, 1575, 634, 78, ["Stop capture and wait for queued window jobs"], 27)]
    p += [circle(457, 1690, "B", 27)]
    p += [text(457, 1734, ["A: continue the capture cycle"], size=25)]
    p += [text(457, 1772, ["B: continue to window analysis"], size=25)]
    p += [circle(850, 748, "A", 26)]
    p += [circle(850, 1164, "A", 26)]
    p += [circle(850, 1468, "A", 26)]

    # Process and decision shapes: queued-window analysis panel.
    p += [circle(950, 190, "B", 26)]
    p += [rect_box(1010, 153, 652, 74, ["Select the next queued window, sensor, and axis"], 28)]
    p += [diamond(1340, 330, 400, 170,
                  ["Do timing, coverage,", "and signal-quality", "checks pass?"], 23)]
    p += [rect_box(920, 285, 190, 90, ["Mark peak", "invalid; retain", "QC status"], 22)]
    p += [rect_box(1060, 465, 560, 68, ["Remove the window mean"], 27)]
    p += [rect_box(1060, 547, 560, 68, ["Apply the symmetric Hann window"], 27)]
    p += [rect_box(1060, 629, 560, 68, ["Compute the N-point DFT using Bluestein"], 25)]
    p += [rect_box(1060, 711, 560, 68, ["Select the largest positive in-band bin"], 25)]
    p += [rect_box(1060, 793, 560, 68, ["Store the window result and QC flags"], 26)]
    p += [diamond(1340, 950, 380, 130, ["Are more queued", "records available?"], 27)]
    p += [rect_box(1160, 1055, 360, 72, ["Count valid peaks for each", "channel-axis"], 24)]
    p += [diamond(1340, 1225, 300, 170,
                  ["At least 10", "valid peaks for", "this channel-axis?"], 18)]
    p += [rect_box(930, 1184, 190, 82, ["Retain QC;", "no median"], 24)]
    p += [rect_box(1570, 1184, 190, 82, ["Calculate", "the median"], 24)]
    p += [rect_box(1080, 1340, 520, 76, ["Save raw records and windows CSV", "plus the session summary"], 24)]
    p += [rect_box(1160, 1435, 360, 70, ["Await the concurrent", "vehicle tally"], 23)]
    p += [diamond(1340, 1600, 300, 170,
                  ["Are local count", "cutoffs", "frozen?"], 22)]
    p += [rect_box(930, 1559, 190, 82, ["Assign", "UNCLASSIFIED"], 22)]
    p += [rect_box(1570, 1559, 190, 82, ["Assign frozen", "local group"], 22)]
    p += [rect_box(1080, 1700, 520, 70, ["Save the finalized session summary"], 26)]
    p += [terminal(1200, 1850, 280, 60, ["End"], 28)]

    # Connectors are drawn after shapes with their endpoints at the shape edges.
    p += [arrow("M457 230 V255"), arrow("M457 355 V379")]
    p += [arrow("M277 445 H232"), arrow("M457 511 V590")]
    p += [arrow("M147 486 V514")]
    p += [arrow("M457 666 V705"), arrow("M455 793 V815"), arrow("M455 893 V910")]
    p += [arrow("M257 985 H232"), arrow("M132 1026 V1055")]
    p += [arrow("M457 1060 V1086"), arrow("M457 1242 V1295")]
    p += [arrow("M457 1377 V1390")]
    p += [arrow("M457 1546 V1575"), arrow("M457 1653 V1663")]
    p += [arrow("M824 748 H780"), arrow("M657 1164 H824"), arrow("M657 1468 H824")]
    p += [arrow("M976 190 H1010")]
    p += [arrow("M1340 227 V245"), arrow("M1140 330 H1110")]
    p += [arrow("M1340 415 V465"), arrow("M1015 375 V827 H1060")]
    p += [arrow("M1340 533 V547"), arrow("M1340 615 V629"), arrow("M1340 697 V711")]
    p += [arrow("M1340 779 V793"), arrow("M1340 861 V885")]
    p += [arrow("M1530 950 H1730 V190 H1662")]
    p += [arrow("M1340 1015 V1055")]
    p += [arrow("M1340 1127 V1140")]
    p += [arrow("M1190 1225 H1120"), arrow("M1490 1225 H1570")]
    p += [arrow("M1025 1266 V1378 H1080"), arrow("M1665 1266 V1378 H1600")]
    p += [arrow("M1340 1416 V1435"), arrow("M1340 1505 V1525")]
    p += [arrow("M1190 1600 H1120"), arrow("M1490 1600 H1570")]
    p += [arrow("M1025 1641 V1735 H1080"), arrow("M1665 1641 V1735 H1600")]
    p += [arrow("M1340 1770 V1850")]

    # Branch labels are white-backed and offset from every connector.
    p += [branch(250, 415, "NO"), branch(510, 548, "YES")]
    p += [branch(250, 955, "NO"), branch(510, 1074, "YES")]
    p += [branch(735, 1132, "NO"), branch(510, 1267, "YES")]
    p += [branch(735, 1436, "NO"), branch(510, 1550, "YES")]
    p += [branch(1130, 290, "NO"), branch(1400, 435, "YES")]
    p += [branch(1605, 920, "YES"), branch(1388, 1035, "NO")]
    p += [branch(1155, 1225, "NO"), branch(1530, 1225, "YES")]
    p += [branch(1155, 1600, "NO"), branch(1530, 1600, "YES")]
    return export_svg("figure_3_4_firmware_flow_bw", W, H, p)


def field_flow():
    W, H = 1800, 1800
    p = svg_start(W, H, "FIELD DATA COLLECTION AND EVALUATION")
    p += [panel(24, 62, 866, 1710, "PREPARE AND ACQUIRE")]
    p += [panel(910, 62, 866, 1710, "ACCEPT, CLASSIFY, AND ANALYZE")]

    preparation = [
        "Obtain written site permission",
        "Obtain ethics and privacy determination",
        "Obtain site-safety clearance",
        "Freeze the analysis settings",
        "Freeze pilot traffic-count cutoffs",
        "Bench-check the single PCB",
        "Verify the approved station and orientation",
        "Install the board at the fixed station",
        "Run the stationary precheck",
    ]
    for i, label in enumerate(preparation):
        p.append(rect_box(86, 155 + i * 58, 742, 52, [label], 26, radius=6))

    p += [rect_box(145, 710, 624, 72, ["Start one fixed 600-second session"], 29)]
    p += [circle(850, 745, "A", 26)]
    p += [rect_box(90, 860, 350, 86, ["Record sequential IMU", "samples"], 27)]
    p += [rect_box(474, 860, 350, 86, ["Tally vehicles", "concurrently"], 27)]
    p += [rect_box(145, 990, 624, 76, ["Stop both activities at 600 seconds"], 28)]
    p += [rect_box(145, 1090, 624, 76, ["Save raw records and session metadata"], 28)]
    p += [circle(457, 1230, "B", 27)]
    p += [text(457, 1300, ["A: repeat the fixed session"], size=26)]
    p += [text(457, 1344, ["B: continue to session checks"], size=26)]

    p += [circle(950, 190, "B", 26)]
    p += [rect_box(1010, 154, 650, 72,
                   ["Check predeclared timing, coverage,", "sensor, and signal criteria"], 25)]
    p += [diamond(1340, 320, 400, 150,
                  ["Does the session meet", "technical criteria?"], 23)]
    p += [rect_box(920, 279, 190, 82, ["Log exclusion", "reason"], 23)]
    p += [rect_box(920, 390, 190, 82, ["Exclude from", "valid-session", "set"], 22)]
    p += [circle(950, 520, "A", 26)]
    p += [rect_box(1160, 430, 360, 80, ["Calculate rate:", "r = C/10 vehicles/min"], 23)]
    p += [diamond(1340, 600, 300, 170,
                  ["Are local count", "cutoffs", "frozen?"], 22)]
    p += [rect_box(900, 560, 220, 80, ["Assign", "UNCLASSIFIED"], 23)]
    p += [rect_box(1560, 560, 210, 80, ["Assign the", "pilot-defined group"], 22)]
    p += [rect_box(1120, 705, 440, 86, ["Create ten consecutive", "60-second windows"], 25)]
    p += [rect_box(1120, 815, 440, 104,
                   ["Process each", "channel-axis window", "using Figure 3.4"], 23)]
    p += [rect_box(1120, 945, 440, 88, ["Summarize valid estimates by", "channel and axis"], 25)]
    p += [rect_box(1120, 1053, 440, 88, ["Compare with the matching", "descriptive baseline"], 25)]
    p += [rect_box(1120, 1161, 440, 88, ["Serve the session summary", "on the local dashboard"], 25)]
    p += [diamond(1340, 1340, 400, 150,
                  ["Are five valid sessions", "available in every group?"], 24)]
    p += [circle(950, 1340, "A", 26)]
    p += [rect_box(1120, 1480, 440, 82, ["Report actual valid-session", "counts"], 24)]
    p += [terminal(1200, 1595, 280, 65, ["End"], 28)]

    # Parallel acquisition branches, session-review branches, and processing path.
    p += [arrow("M457 782 V820 H265 V860"), arrow("M457 820 H649 V860")]
    p += [arrow("M265 946 V970 H345 V990"), arrow("M649 946 V970 H569 V990")]
    p += [arrow("M457 1066 V1090"), arrow("M457 1166 V1203")]
    p += [arrow("M824 745 H769")]
    p += [arrow("M976 190 H1010"), arrow("M1340 226 V245")]
    p += [arrow("M1140 320 H1110"), arrow("M1015 361 V390")]
    p += [arrow("M1015 472 V520 H976")]
    p += [arrow("M1340 395 V430"), arrow("M1340 510 V525")]
    p += [arrow("M1190 600 H1120"), arrow("M1490 600 H1560")]
    p += [arrow("M1010 640 V685 H1260 V705"), arrow("M1665 640 V685 H1420 V705")]
    p += [arrow("M1340 791 V815"), arrow("M1340 919 V945"), arrow("M1340 1033 V1053")]
    p += [arrow("M1340 1141 V1161"), arrow("M1340 1249 V1265")]
    p += [arrow("M1140 1340 H976"), arrow("M1340 1415 V1480"), arrow("M1340 1562 V1595")]

    p += [branch(1135, 280, "NO"), branch(1390, 410, "YES")]
    p += [branch(1155, 600, "NO"), branch(1530, 600, "YES")]
    p += [branch(1065, 1308, "NO"), branch(1390, 1445, "YES")]
    return export_svg("figure_3_5_field_workflow_bw", W, H, p)


if __name__ == "__main__":
    print("Created:", firmware_flow())
    print("Created:", field_flow())
