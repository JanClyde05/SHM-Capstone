from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
SVG = ROOT / "figure_3_5_field_workflow_bw.svg"
PNG = ROOT / "figure_3_5_field_workflow_bw.png"
INKSCAPE = Path(r"D:\Inkscape\bin\inkscape.com")
W, H = 1800, 1490


def box(x, y, w, h, lines, size=22, radius=5):
    gap = 27
    first = y + h / 2 - (len(lines) - 1) * gap / 2
    text = "".join(
        f'<tspan x="{x+w/2}" dy="{0 if i == 0 else gap}">{line}</tspan>'
        for i, line in enumerate(lines)
    )
    return (f'<rect class="box" x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}"/>'
            f'<text class="label" x="{x+w/2}" y="{first}" style="font-size:{size}px">{text}</text>')


def diamond(cx, cy, w, h, lines, size=21):
    pts = f"{cx},{cy-h/2} {cx+w/2},{cy} {cx},{cy+h/2} {cx-w/2},{cy}"
    gap = 25
    first = cy - (len(lines) - 1) * gap / 2
    text = "".join(
        f'<tspan x="{cx}" dy="{0 if i == 0 else gap}">{line}</tspan>'
        for i, line in enumerate(lines)
    )
    return (f'<polygon class="diamond" points="{pts}"/>'
            f'<text class="label" x="{cx}" y="{first}" style="font-size:{size}px">{text}</text>')


def connector(cx, cy, label):
    return (f'<circle class="connector" cx="{cx}" cy="{cy}" r="22"/>'
            f'<text class="connectorText" x="{cx}" y="{cy}">{label}</text>')


def arrow(path):
    return f'<path class="arrow" d="{path}"/>'


parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><marker id="arrow" viewBox="0 0 12 12" refX="10" refY="6" markerWidth="13" markerHeight="13" orient="auto">
<path d="M1 1 L11 6 L1 11 Z" fill="#000"/></marker></defs>
<style>
text {{ font-family: Arial, Helvetica, sans-serif; fill:#000; }}
.panel {{ fill:#fff; stroke:#000; stroke-width:3; }}
.bar {{ fill:#000; stroke:#000; stroke-width:2; }}
.barText {{ fill:#fff; font-size:27px; font-weight:700; letter-spacing:.4px; }}
.box,.diamond {{ fill:#fff; stroke:#000; stroke-width:2.5; }}
.label {{ text-anchor:middle; dominant-baseline:middle; font-size:21px; }}
.branch {{ text-anchor:middle; dominant-baseline:middle; font-size:19px; font-weight:700; }}
.arrow {{ fill:none; stroke:#000; stroke-width:3; stroke-linecap:square; stroke-linejoin:round; marker-end:url(#arrow); }}
.connector {{ fill:#fff; stroke:#000; stroke-width:2.5; }}
.connectorText {{ text-anchor:middle; dominant-baseline:middle; font-size:22px; font-weight:700; }}
.note {{ text-anchor:middle; dominant-baseline:middle; font-size:22px; }}
</style>
<rect width="{W}" height="{H}" fill="#fff"/>
<text x="900" y="42" text-anchor="middle" font-size="32px" font-weight="700">FIELD DATA COLLECTION AND EVALUATION</text>
<rect class="panel" x="35" y="80" width="850" height="1240" rx="8"/>
<rect class="bar" x="35" y="80" width="850" height="64" rx="7"/>
<text class="barText" x="460" y="112" text-anchor="middle" dominant-baseline="middle">PREPARE AND ACQUIRE</text>
<rect class="panel" x="915" y="80" width="850" height="1240" rx="8"/>
<rect class="bar" x="915" y="80" width="850" height="64" rx="7"/>
<text class="barText" x="1340" y="112" text-anchor="middle" dominant-baseline="middle">ACCEPT, CLASSIFY, AND ANALYZE</text>
''']

# Arrows are drawn before boxes so their lines never cross text or shapes.
for i in range(8):
    top_next = 212 + i * 50
    bottom_current = 202 + i * 50
    parts.append(arrow(f"M460 {bottom_current} V{top_next}"))
parts += [
    arrow("M460 602 V632"),
    arrow("M460 694 V730 H270 V754"),
    arrow("M460 694 V730 H650 V754"),
    arrow("M270 816 V840 H460 V860"),
    arrow("M650 816 V840 H460"),
    arrow("M460 920 V960"),
    arrow("M460 1020 V1080"),
    arrow("M818 663 H772"),
    arrow("M1340 190 V215"),
    arrow("M1190 270 H1125"),
    arrow("M1030 300 V340"),
    arrow("M1030 400 V425 H984"),
    arrow("M1340 325 V350"),
    arrow("M1340 410 V425"),
    arrow("M1190 480 H1125"),
    arrow("M1490 480 H1555"),
    arrow("M1030 510 V540 H1340 V570"),
    arrow("M1650 510 V540 H1340"),
    arrow("M1340 630 V655"),
    arrow("M1340 725 V750"),
    arrow("M1340 810 V835"),
    arrow("M1340 895 V920"),
    arrow("M1340 980 V1010"),
    arrow("M1190 1065 H984"),
    arrow("M1340 1120 V1170"),
]

prep = [
    "Obtain written site permission",
    "Obtain ethics and privacy determination",
    "Obtain site-safety clearance",
    "Freeze analysis settings",
    "Freeze pilot traffic-count cutoffs",
    "Bench-check the single PCB",
    "Verify approved station and orientation",
    "Install the board at the fixed station",
    "Run the stationary precheck",
]
for i, label in enumerate(prep):
    parts.append(box(110, 160 + i*50, 700, 42, [label], 20, 4))

parts += [
    box(150, 632, 620, 62, ["Start the fixed 600-second session"]),
    connector(840, 663, "A"),
    box(110, 754, 320, 62, ["Record sequential IMU", "samples"], 20),
    box(490, 754, 320, 62, ["Tally vehicles", "concurrently"], 20),
    box(150, 860, 620, 60, ["Stop both activities at 600 seconds"]),
    box(150, 960, 620, 60, ["Save raw records and session metadata"]),
    connector(460, 1080, "B"),
    '<text class="note" x="460" y="1142">A: repeat the fixed session</text>',
    '<text class="note" x="460" y="1180">B: continue to session checks</text>',
    connector(1340, 168, "B"),
    diamond(1340, 270, 300, 110, ["Meets technical", "acceptance criteria?"], 20),
    box(935, 240, 190, 60, ["Log exclusion reason"], 19),
    box(935, 340, 190, 60, ["Exclude from valid-", "session set"], 19),
    connector(960, 425, "A"),
    box(1160, 350, 360, 60, ["Calculate rate: r = C/10 vehicles/min"], 19),
    diamond(1340, 480, 300, 110, ["Are count cutoffs", "frozen?"], 20),
    box(935, 450, 190, 60, ["Assign", "UNCLASSIFIED"], 19),
    box(1555, 450, 190, 60, ["Assign pilot-defined", "local group"], 19),
    box(1160, 570, 360, 60, ["Create ten consecutive", "60-second windows"], 19),
    box(1160, 655, 360, 70, ["Process channel-axis windows using", "the firmware flowchart (Figure 3.4)"], 19),
    box(1160, 750, 360, 60, ["Summarize valid estimates by", "channel and axis"], 19),
    box(1160, 835, 360, 60, ["Compare with the matching", "descriptive baseline"], 19),
    box(1160, 920, 360, 60, ["Serve the session summary on", "the local dashboard"], 19),
    diamond(1340, 1065, 300, 110, ["Five valid sessions", "in every group?"], 19),
    connector(960, 1065, "A"),
    box(1160, 1170, 360, 60, ["Report actual valid-session counts"], 20),
    '<text class="branch" x="1155" y="252">NO</text>',
    '<text class="branch" x="1380" y="336">YES</text>',
    '<text class="branch" x="1155" y="462">NO</text>',
    '<text class="branch" x="1525" y="462">YES</text>',
    '<text class="branch" x="1100" y="1042">NO</text>',
    '<text class="branch" x="1380" y="1145">YES</text>',
    '<rect class="box" x="35" y="1340" width="1730" height="105" rx="5"/>',
    '<text class="note" x="900" y="1378"><tspan x="900">Five sessions per group is a practical target, not a power calculation.</tspan>',
    '<tspan x="900" dy="34">Align manuscript and firmware window-validity rules before formal collection.</tspan></text>',
    '</svg>',
]

SVG.write_text("".join(parts), encoding="utf-8")
subprocess.run([str(INKSCAPE), str(SVG), "--export-type=png", f"--export-filename={PNG}", "--export-width=1800"], check=True)
print(f"Created {SVG.name} and {PNG.name}")
