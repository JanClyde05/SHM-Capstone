from copy import deepcopy
from pathlib import Path
import hashlib
import posixpath
import re
from zipfile import ZipFile, ZIP_DEFLATED

from lxml import etree
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
PAPER_DIR = ROOT / "Documents/The Real Research Paper/GPT Paper"
SOURCE = PAPER_DIR / "SHM_Research_Aligned_Revision_Draft_v5.docx"
OUTPUT = PAPER_DIR / "SHM_Research_Aligned_Revision_Draft_v6.docx"
FIG_DIR = Path(__file__).resolve().parent
FIGURE_ASSETS = {
    "Figure 1.1.": FIG_DIR / "figure_1_1_ipo_bw.png",
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


def set_trailing_page_number(p, page):
    nodes = p.xpath(".//w:t", namespaces=NS)
    node = next((n for n in reversed(nodes) if (n.text or "").strip().isdigit()), None)
    if node is None:
        raise RuntimeError(f"Could not locate a static page number in: {ptext(p)}")
    node.text = str(page)


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

    # The double-spaced glossary adds one printed page. Update the static contents
    # entries from Chapter II onward and reconcile both static caption lists to V6.
    toc = next(p for p in paragraphs if ptext(p) == "TABLE OF CONTENTS")
    list_tables_heading = next(p for p in paragraphs if ptext(p) == "LIST OF TABLES")
    toc_rows = paragraphs[paragraphs.index(toc) + 1:paragraphs.index(list_tables_heading)]
    shifted_toc_rows = 0
    for p in toc_rows:
        trailing = re.search(r"(\d+)$", ptext(p))
        if trailing and int(trailing.group(1)) >= 13:
            set_trailing_page_number(p, int(trailing.group(1)) + 1)
            shifted_toc_rows += 1

    list_figures_heading = next(p for p in paragraphs if ptext(p) == "LIST OF FIGURES")
    tables_end = paragraphs.index(list_figures_heading)
    table_page_map = {"1.": 36, "2.": 43, "3.": 46, "4.": 48}
    table_rows = paragraphs[paragraphs.index(list_tables_heading) + 1:tables_end]
    for number, page in table_page_map.items():
        matches = [p for p in table_rows if ptext(p).startswith(number + " ")]
        if len(matches) != 1:
            raise RuntimeError(f"Expected one static table-list row for {number}; found {len(matches)}")
        set_trailing_page_number(matches[0], page)

    figure_page_map = {"1.1.": 6, "1.2.": 10, "3.1.": 37, "3.2.": 38,
                       "3.3.": 38, "3.4.": 40, "3.5.": 53}
    figure_rows = paragraphs[paragraphs.index(list_figures_heading) + 1:]
    for number, page in figure_page_map.items():
        matches = [p for p in figure_rows if ptext(p).startswith(number + " ")]
        if len(matches) != 1:
            raise RuntimeError(f"Expected one static figure-list row for {number}; found {len(matches)}")
        set_trailing_page_number(matches[0], page)

    # Preserve the abstract exactly as it appears in V5; normalize only glossary entries.
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
        set_spacing(p, line=480, before=0, after=0)
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

    # Center all seven images and captions; replace only the three annotated figure assets.
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
        if not caption.startswith(tuple(FIGURE_ASSETS)):
            continue
        asset = FIGURE_ASSETS[next(prefix for prefix in FIGURE_ASSETS if caption.startswith(prefix))]
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

    if len(figure_records) != 3 or len(replacements) != 3:
        raise RuntimeError(f"Expected three distinct figure replacements: {figure_records}")
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
    field_flow_svg = FIGURE_ASSETS["Figure 3.5."].with_suffix(".svg")
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
    final_glossary = final_paragraphs[final_paragraphs.index(final_heading) + 1:]
    final_chapter_two = next(p for p in final_glossary if ptext(p) == "CHAPTER II")
    final_entries = [p for p in final_glossary[:final_glossary.index(final_chapter_two)]
                     if ptext(p) and ":" in ptext(p) and not p.xpath(".//w:drawing", namespaces=NS)]
    for p in final_entries:
        spacing = ppr(p).find(W + "spacing")
        if spacing is None or spacing.get(W + "line") != "480" or spacing.get(W + "after") != "0":
            raise RuntimeError(f"Glossary entry does not use 2.0/0 pt spacing: {ptext(p)}")
        term_label = ptext(p).split(":", 1)[0] + ":"
        runs = p.xpath(".//w:r", namespaces=NS)
        term_run = next((r for r in runs if term_label in "".join(
            r.xpath(".//w:t/text()", namespaces=NS))), None)
        term_bold = None if term_run is None else term_run.find("w:rPr/w:b", namespaces=NS)
        if term_bold is None or term_bold.get(W + "val", "1").lower() in {"0", "false", "off"}:
            raise RuntimeError(f"Glossary term label is not explicitly bold: {term_label}")
        term_index = runs.index(term_run)
        for meaning_run in runs[term_index + 1:]:
            meaning_bold = meaning_run.find("w:rPr/w:b", namespaces=NS)
            if meaning_bold is not None and meaning_bold.get(W + "val", "1").lower() not in {"0", "false", "off"}:
                raise RuntimeError(f"Glossary meaning is bold: {ptext(p)}")
    if len(final_entries) != 14:
        raise RuntimeError(f"Expected 14 final glossary entries; found {len(final_entries)}")

print("Output:", OUTPUT)
print("Bytes:", OUTPUT.stat().st_size)
print("SHA-256:", hashlib.sha256(OUTPUT.read_bytes()).hexdigest().upper())
print("Abstract and keywords: preserved unchanged from V5.")
print("Glossary: 14 entries at 2.0 spacing with 0 pt before/after; no forced break before MEMS IMU.")
print(f"Static contents page numbers shifted after p. 12: {shifted_toc_rows} entries.")
print("Static table and figure lists reconciled to the V6 Word pagination.")
print("Figure captions:", " | ".join(caption_texts))
for caption, record in figure_records.items():
    print(caption, record)
print("DOCX ZIP CRC: pass")
