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
    W, H = 1800, 1840
    p = svg_start(W, H, "CURRENT FIRMWARE FLOW")
    p += [panel(24, 60, 866, 1740, "SESSION CONTROL AND ACQUISITION")]
    p += [panel(910, 60, 866, 1740, "WINDOW ANALYSIS AND FINALIZATION")]

    # Process and decision shapes: session-control panel.
    p += [terminal(207, 160, 500, 70, ["Session request"], 31)]
    p += [rect_box(110, 255, 694, 100,
                   ["Precheck sensors, PSRAM/storage, mode, station,",
                    "orientation, and settings frozen for formal mode"], 29)]
    p += [diamond(457, 445, 360, 132, ["Do all start", "checks pass?"], 29)]
    p += [rect_box(52, 404, 190, 82, ["Reject start;", "report reason"], 27)]
    p += [terminal(97, 514, 100, 52, ["End"], 27)]
    p += [rect_box(160, 590, 594, 76, ["Arm session with a 5-second countdown"], 29)]
    p += [rect_box(130, 705, 650, 88, ["Read sequential X/Y/Z samples", "from the three sensors"], 28)]
    p += [rect_box(130, 815, 650, 78, ["Timestamp and buffer each sensor reading"], 29)]
    p += [diamond(457, 985, 360, 130, ["Are sensors ready", "and buffer available?"], 28)]
    p += [rect_box(52, 944, 190, 82, ["Stop capture;", "mark incomplete"], 27)]
    p += [terminal(97, 1055, 100, 52, ["End"], 27)]
    p += [diamond(457, 1158, 360, 132, ["Has the next 60-second", "window boundary arrived?"], 26)]
    p += [rect_box(122, 1265, 670, 82, ["Seal and queue the completed 60-second window"], 28)]
    p += [diamond(457, 1435, 360, 126, ["Are all 10 windows", "(600 seconds) complete?"], 28)]
    p += [rect_box(140, 1540, 634, 78, ["Stop capture and wait for queued window jobs"], 27)]
    p += [circle(457, 1664, "B", 27)]
    p += [text(457, 1724, ["A: continue the capture cycle"], size=25)]
    p += [text(457, 1762, ["B: continue to window analysis"], size=25)]
    p += [circle(850, 748, "A", 26)]
    p += [circle(850, 1158, "A", 26)]
    p += [circle(850, 1435, "A", 26)]

    # Process and decision shapes: queued-window analysis panel.
    p += [circle(950, 190, "B", 26)]
    p += [rect_box(1010, 153, 652, 74, ["Select the next queued window, sensor, and axis"], 28)]
    p += [diamond(1340, 315, 360, 130, ["Do timing, coverage, and", "signal-quality checks pass?"], 26)]
    p += [rect_box(940, 274, 180, 82, ["Mark peak", "invalid; retain", "QC status"], 23)]
    p += [rect_box(1080, 420, 520, 62, ["Remove the window mean"], 28)]
    p += [rect_box(1080, 505, 520, 62, ["Apply the symmetric Hann window"], 28)]
    p += [rect_box(1080, 590, 520, 62, ["Compute the N-point DFT using Bluestein"], 27)]
    p += [rect_box(1080, 675, 520, 62, ["Select the largest positive in-band bin"], 27)]
    p += [rect_box(1080, 760, 520, 62, ["Store the window result and QC flags"], 27)]
    p += [diamond(1340, 900, 360, 118, ["Are more queued", "records available?"], 28)]
    p += [rect_box(1160, 1000, 360, 74, ["Count valid peaks for each", "channel-axis"], 25)]
    p += [diamond(1340, 1170, 280, 124, ["At least 10 valid peaks", "for this channel-axis?"], 25)]
    p += [rect_box(930, 1129, 190, 82, ["Retain QC;", "no median"], 25)]
    p += [rect_box(1570, 1129, 190, 82, ["Calculate", "the median"], 25)]
    p += [rect_box(1080, 1255, 520, 72, ["Save raw records and windows CSV", "plus the session summary"], 25)]
    p += [rect_box(1160, 1360, 360, 70, ["Await the concurrent", "vehicle tally"], 24)]
    p += [diamond(1340, 1515, 280, 118, ["Are local count cutoffs", "frozen?"], 26)]
    p += [rect_box(930, 1474, 190, 82, ["Assign", "UNCLASSIFIED"], 23)]
    p += [rect_box(1570, 1474, 190, 82, ["Assign frozen", "local group"], 23)]
    p += [rect_box(1080, 1620, 520, 70, ["Save the finalized session summary"], 27)]
    p += [terminal(1200, 1710, 280, 66, ["End"], 29)]

    # Connectors are drawn after shapes with their endpoints at the shape edges.
    p += [arrow("M457 230 V255"), arrow("M457 355 V379")]
    p += [arrow("M277 445 H242"), arrow("M457 511 V590")]
    p += [arrow("M147 486 V514")]
    p += [arrow("M457 666 V705"), arrow("M455 793 V815"), arrow("M455 893 V920")]
    p += [arrow("M277 985 H242"), arrow("M147 1026 V1055")]
    p += [arrow("M457 1050 V1092"), arrow("M457 1224 V1265")]
    p += [arrow("M457 1347 V1372")]
    p += [arrow("M457 1498 V1540"), arrow("M457 1618 V1637")]
    p += [arrow("M824 748 H780"), arrow("M637 1158 H824"), arrow("M637 1435 H824")]
    p += [arrow("M976 190 H1010")]
    p += [arrow("M1340 227 V250"), arrow("M1160 315 H1120")]
    p += [arrow("M1340 380 V420"), arrow("M1030 356 V791 H1080")]
    p += [arrow("M1340 482 V505"), arrow("M1340 567 V590"), arrow("M1340 652 V675")]
    p += [arrow("M1340 737 V760"), arrow("M1340 822 V841")]
    p += [arrow("M1520 900 H1730 V190 H1662")]
    p += [arrow("M1340 959 V1000")]
    p += [arrow("M1340 1074 V1108")]
    p += [arrow("M1200 1170 H1120"), arrow("M1480 1170 H1570")]
    p += [arrow("M1025 1211 V1306 H1080"), arrow("M1665 1211 V1306 H1600")]
    p += [arrow("M1340 1342 V1360"), arrow("M1340 1428 V1456")]
    p += [arrow("M1200 1515 H1120"), arrow("M1480 1515 H1570")]
    p += [arrow("M1025 1556 V1655 H1080"), arrow("M1665 1556 V1655 H1600")]
    p += [arrow("M1340 1690 V1710")]

    # Branch labels are white-backed and offset from every connector.
    p += [branch(264, 415, "NO"), branch(510, 548, "YES")]
    p += [branch(264, 955, "NO"), branch(510, 1060, "YES")]
    p += [branch(735, 1126, "NO"), branch(510, 1240, "YES")]
    p += [branch(735, 1403, "NO"), branch(510, 1518, "YES")]
    p += [branch(1140, 284, "NO"), branch(1390, 400, "YES")]
    p += [branch(1600, 863, "YES"), branch(1545, 978, "NO")]
    p += [branch(1160, 1130, "NO"), branch(1525, 1130, "YES")]
    p += [branch(1160, 1490, "NO"), branch(1525, 1490, "YES")]
    return export_svg("figure_3_4_firmware_flow_bw", W, H, p)


def field_flow():
    W, H = 1800, 1730
    p = svg_start(W, H, "FIELD DATA COLLECTION AND EVALUATION")
    p += [panel(24, 62, 866, 1480, "PREPARE AND ACQUIRE")]
    p += [panel(910, 62, 866, 1480, "ACCEPT, CLASSIFY, AND ANALYZE")]

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
        p.append(rect_box(86, 155 + i * 58, 742, 48, [label], 27, radius=6))

    p += [rect_box(145, 710, 624, 70, ["Start one fixed 600-second session"], 30)]
    p += [circle(850, 745, "A", 26)]
    p += [rect_box(90, 860, 350, 82, ["Record sequential IMU", "samples"], 29)]
    p += [rect_box(474, 860, 350, 82, ["Tally vehicles", "concurrently"], 29)]
    p += [rect_box(145, 990, 624, 70, ["Stop both activities at 600 seconds"], 29)]
    p += [rect_box(145, 1090, 624, 70, ["Save raw records and session metadata"], 29)]
    p += [circle(457, 1225, "B", 27)]
    p += [text(457, 1310, ["A: repeat the fixed session"], size=27)]
    p += [text(457, 1356, ["B: continue to session checks"], size=27)]

    p += [circle(950, 190, "B", 26)]
    p += [rect_box(1010, 154, 650, 72,
                   ["Check predeclared timing, coverage,", "sensor, and signal criteria"], 25)]
    p += [diamond(1340, 315, 360, 126, ["Does the session meet", "technical criteria?"], 28)]
    p += [rect_box(940, 272, 180, 74, ["Log exclusion", "reason"], 24)]
    p += [rect_box(940, 375, 180, 78, ["Exclude from", "valid-session", "set"], 21)]
    p += [circle(950, 500, "A", 26)]
    p += [rect_box(1160, 398, 360, 80, ["Calculate rate:", "r = C/10 vehicles/min"], 24)]
    p += [diamond(1340, 570, 300, 120, ["Are local count cutoffs", "frozen?"], 26)]
    p += [rect_box(900, 530, 220, 80, ["Assign", "UNCLASSIFIED"], 24)]
    p += [rect_box(1560, 530, 210, 80, ["Assign the", "pilot-defined group"], 23)]
    p += [rect_box(1160, 650, 360, 76, ["Create ten consecutive", "60-second windows"], 25)]
    p += [rect_box(1160, 755, 360, 90,
                   ["Process each", "channel-axis window", "using Figure 3.4"], 22)]
    p += [rect_box(1160, 855, 360, 70, ["Summarize valid estimates by", "channel and axis"], 26)]
    p += [rect_box(1160, 949, 360, 70, ["Compare with the matching", "descriptive baseline"], 26)]
    p += [rect_box(1160, 1043, 360, 70, ["Serve the session summary", "on the local dashboard"], 26)]
    p += [diamond(1340, 1195, 360, 120, ["Are five valid sessions", "available in every group?"], 26)]
    p += [circle(950, 1195, "A", 26)]
    p += [rect_box(1160, 1310, 360, 76, ["Report actual valid-session", "counts"], 25)]
    p += [terminal(1200, 1420, 280, 66, ["End"], 29)]

    # Parallel acquisition branches, session-review branches, and processing path.
    p += [arrow("M457 780 V820 H265 V860"), arrow("M457 820 H649 V860")]
    p += [arrow("M265 942 V970 H345 V990"), arrow("M649 942 V970 H569 V990")]
    p += [arrow("M457 1060 V1090"), arrow("M457 1160 V1198")]
    p += [arrow("M824 745 H769")]
    p += [arrow("M976 190 H1010"), arrow("M1340 226 V252")]
    p += [arrow("M1160 315 H1120"), arrow("M1030 346 V375")]
    p += [arrow("M1030 453 V482 H968")]
    p += [arrow("M1340 378 V405"), arrow("M1340 471 V510")]
    p += [arrow("M1190 570 H1120"), arrow("M1490 570 H1560")]
    p += [arrow("M1010 610 V620 H1260 V650"), arrow("M1665 610 V620 H1420 V650")]
    p += [arrow("M1340 726 V755"), arrow("M1340 845 V855"), arrow("M1340 925 V949")]
    p += [arrow("M1340 1019 V1043"), arrow("M1340 1113 V1135")]
    p += [arrow("M1160 1195 H976"), arrow("M1340 1255 V1310"), arrow("M1340 1386 V1420")]

    p += [branch(1140, 284, "NO"), branch(1550, 390, "YES")]
    p += [branch(1155, 540, "NO"), branch(1520, 540, "YES")]
    p += [branch(1080, 1165, "NO"), branch(1390, 1280, "YES")]
    p += [
        '<rect class="box" x="34" y="1572" width="1732" height="112" rx="8"/>',
        text(900, 1608, ["Five sessions per group is a practical target, not a power calculation."], size=27),
        text(900, 1648, ["Align the manuscript and firmware window-validity rules before formal collection."], size=25),
    ]
    return export_svg("figure_3_5_field_workflow_bw", W, H, p)


if __name__ == "__main__":
    print("Created:", firmware_flow())
    print("Created:", field_flow())
