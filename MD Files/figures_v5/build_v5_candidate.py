from copy import deepcopy
from pathlib import Path
import hashlib
import posixpath
from zipfile import ZipFile, ZIP_DEFLATED

from lxml import etree
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
PAPER_DIR = ROOT / "Documents/The Real Research Paper/GPT Paper"
SOURCE = PAPER_DIR / "SHM_Research_Aligned_Revision_Draft_v4.docx"
OUTPUT = PAPER_DIR / "SHM_Research_Aligned_Revision_Draft_v5.docx"
FIG_DIR = Path(__file__).resolve().parent
FLOW_ASSETS = {
    "Figure 3.4.": FIG_DIR / "figure_3_4_firmware_flow_bw.png",
    "Figure 3.5.": FIG_DIR / "figure_3_5_field_workflow_bw.png",
}

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
}
W = f"{{{NS['w']}}}"
R = f"{{{NS['r']}}}"
EMU_PER_INCH = 914400
MAX_FIGURE_WIDTH_EMU = round(5.95 * EMU_PER_INCH)


def ptext(p):
    return "".join(p.xpath(".//w:t/text()", namespaces=NS)).strip()


def ppr(p):
    node = p.find(W + "pPr")
    if node is None:
        node = etree.Element(W + "pPr")
        p.insert(0, node)
    return node


def set_spacing(p, line, before=0, after=0):
    props = ppr(p)
    spacing = props.find(W + "spacing")
    if spacing is None:
        spacing = etree.SubElement(props, W + "spacing")
    spacing.set(W + "before", str(before))
    spacing.set(W + "after", str(after))
    spacing.set(W + "line", str(line))
    spacing.set(W + "lineRule", "auto")


def set_alignment(p, value="center"):
    props = ppr(p)
    jc = props.find(W + "jc")
    if jc is None:
        jc = etree.SubElement(props, W + "jc")
    jc.set(W + "val", value)
    ind = props.find(W + "ind")
    if ind is None:
        ind = etree.SubElement(props, W + "ind")
    ind.set(W + "left", "0")
    ind.set(W + "right", "0")
    ind.set(W + "firstLine", "0")


with ZipFile(SOURCE, "r") as source:
    bad = source.testzip()
    if bad:
        raise RuntimeError(f"Source DOCX has a CRC error in {bad}")
    document = etree.fromstring(source.read("word/document.xml"))
    relationships = etree.fromstring(source.read("word/_rels/document.xml.rels"))
    rel_targets = {
        relationship.get("Id"): relationship.get("Target")
        for relationship in relationships
        if relationship.get("Id") and relationship.get("Target")
    }
    paragraphs = document.xpath(".//w:p", namespaces=NS)
    all_text = [ptext(p) for p in paragraphs]

    # Keep the static List of Figures title aligned with the actual Figure 3.4 caption.
    old_figure_list_title = "3.4. Current Firmware Session-Control Flowchart39"
    figure_list_rows = [p for p in paragraphs if ptext(p) == old_figure_list_title]
    if len(figure_list_rows) != 1:
        raise RuntimeError(f"Expected one Figure 3.4 List of Figures row; found {len(figure_list_rows)}")
    list_title_run = next((node for node in figure_list_rows[0].xpath(".//w:t", namespaces=NS)
                           if (node.text or "").startswith("3.4. Current Firmware Session-Control Flowchart")), None)
    if list_title_run is None:
        raise RuntimeError("Could not find the Figure 3.4 title run in the List of Figures")
    list_title_run.text = "3.4. Current firmware session-control and window-processing flowchart"

    # Use 1.35 spacing so the abstract and keywords remain together on one page.
    abstract = next(p for p in paragraphs if ptext(p).startswith(
        "This developmental study aims to develop and field-evaluate a localized system"))
    keywords = next(p for p in paragraphs if ptext(p).startswith("Keywords:"))
    set_spacing(abstract, line=324, before=0, after=80)
    set_spacing(keywords, line=324, before=0, after=0)
    for p in (abstract, keywords):
        props = ppr(p)
        if props.find(W + "keepLines") is None:
            etree.SubElement(props, W + "keepLines")

    # Use 1.5 spacing and let complete glossary entries paginate naturally.
    heading = next(p for p in paragraphs if ptext(p) == "1.7 Definition of Terms")
    after_heading = paragraphs[paragraphs.index(heading) + 1:]
    chapter_two = next(p for p in after_heading if ptext(p) == "CHAPTER II")
    glossary_candidates = paragraphs[paragraphs.index(heading) + 1:paragraphs.index(chapter_two)]
    glossary_terms = []
    for p in glossary_candidates:
        value = ptext(p)
        if not value or ":" not in value or p.xpath(".//w:drawing", namespaces=NS):
            continue
        glossary_terms.append(value.split(":", 1)[0] + ":")
        set_spacing(p, line=360, before=0, after=100)
        props = ppr(p)
        for page_break in props.findall(W + "pageBreakBefore"):
            props.remove(page_break)
        if props.find(W + "keepLines") is None:
            etree.SubElement(props, W + "keepLines")
        if props.find(W + "widowControl") is None:
            etree.SubElement(props, W + "widowControl")
    if len(glossary_terms) != 14:
        raise RuntimeError(f"Expected 14 glossary terms; found {len(glossary_terms)}")
    heading_props = ppr(heading)
    if heading_props.find(W + "keepNext") is None:
        etree.SubElement(heading_props, W + "keepNext")

    # Center all images and captions, replacing only the two annotated flowcharts.
    replacements = {}
    figure_records = {}
    for index, p in enumerate(paragraphs):
        blips = p.xpath(".//a:blip", namespaces=NS)
        if not blips:
            continue
        caption = next((ptext(q) for q in paragraphs[index + 1:] if ptext(q)), "")
        if not caption.startswith("Figure "):
            continue
        set_alignment(p)
        caption_p = next(q for q in paragraphs[index + 1:] if ptext(q))
        set_alignment(caption_p)
        if not caption.startswith(tuple(FLOW_ASSETS)):
            continue
        asset = FLOW_ASSETS[next(prefix for prefix in FLOW_ASSETS if caption.startswith(prefix))]
        image = Image.open(asset)
        aspect = image.height / image.width
        for extent in p.xpath(".//wp:extent | .//a:xfrm/a:ext", namespaces=NS):
            extent.set("cx", str(MAX_FIGURE_WIDTH_EMU))
            extent.set("cy", str(round(MAX_FIGURE_WIDTH_EMU * aspect)))
        relationship_id = blips[0].get(R + "embed")
        target = rel_targets[relationship_id]
        media_name = posixpath.normpath(posixpath.join("word", target))
        if media_name in replacements:
            raise RuntimeError(f"Flowchart media part is shared unexpectedly: {media_name}")
        replacements[media_name] = asset.read_bytes()
        figure_records[caption] = {
            "asset": asset.name,
            "media": media_name,
            "pixels": image.size,
            "sha256": hashlib.sha256(asset.read_bytes()).hexdigest().upper(),
        }

    if len(figure_records) != 2 or len(replacements) != 2:
        raise RuntimeError(f"Expected two distinct figure replacements: {figure_records}")
    expected_figures = [
        "Figure 1.1.", "Figure 1.2.", "Figure 3.1.", "Figure 3.2.",
        "Figure 3.3.", "Figure 3.4.", "Figure 3.5.",
    ]
    caption_texts = [value for value in all_text
                     if any(value.startswith(prefix) for prefix in expected_figures)]
    observed_numbers = [next((prefix for prefix in expected_figures if value.startswith(prefix)), None)
                        for value in caption_texts]
    if observed_numbers != expected_figures:
        raise RuntimeError(f"Figure caption sequence mismatch: {observed_numbers}")
    field_flow_svg = FLOW_ASSETS["Figure 3.5."].with_suffix(".svg")
    if b"Figure 3.4" not in field_flow_svg.read_bytes():
        raise RuntimeError("Figure 3.5's Figure 3.4 cross-reference is missing")

    updated_document = etree.tostring(document, xml_declaration=True, encoding="UTF-8", standalone=True)
    with ZipFile(OUTPUT, "w", compression=ZIP_DEFLATED) as result:
        for item in source.infolist():
            if item.filename == "word/document.xml":
                data = updated_document
            elif item.filename in replacements:
                data = replacements[item.filename]
            else:
                data = source.read(item.filename)
            result.writestr(item, data)

with ZipFile(OUTPUT, "r") as check:
    bad = check.testzip()
    if bad:
        raise RuntimeError(f"Output DOCX has a CRC error in {bad}")
    final_xml = etree.fromstring(check.read("word/document.xml"))
    final_paragraphs = final_xml.xpath(".//w:p", namespaces=NS)
    final_heading = next(p for p in final_paragraphs if ptext(p) == "1.7 Definition of Terms")
    final_mems = next(p for p in final_paragraphs if ptext(p).startswith("MEMS IMU ("))
    if ppr(final_mems).find(W + "pageBreakBefore") is not None:
        raise RuntimeError("MEMS IMU still has pageBreakBefore")

print("Output:", OUTPUT)
print("Bytes:", OUTPUT.stat().st_size)
print("SHA-256:", hashlib.sha256(OUTPUT.read_bytes()).hexdigest().upper())
print("Abstract and keywords: 1.35 spacing; 4 pt after abstract.")
print("Glossary: 14 entries at 1.5 spacing with 5 pt after; no forced break before MEMS IMU.")
print("Figure captions:", " | ".join(caption_texts))
for caption, record in figure_records.items():
    print(caption, record)
print("DOCX ZIP CRC: pass")
