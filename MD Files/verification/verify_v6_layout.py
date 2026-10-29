"""Task-specific structural and rendered-page checks for the V6 layout candidate."""

from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import posixpath
import re
from zipfile import ZipFile

from lxml import etree
from PIL import Image, ImageChops
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "Documents/The Real Research Paper/GPT Paper"
V5_DOCX = PAPER / "SHM_Research_Aligned_Revision_Draft_v5.docx"
V5_PDF = PAPER / "SHM_Research_Aligned_Revision_Draft_v5.pdf"
V6_DOCX = PAPER / "SHM_Research_Aligned_Revision_Draft_v6.docx"
V6_PDF = PAPER / "SHM_Research_Aligned_Revision_Draft_v6.pdf"
FIG_DIR = ROOT / "MD Files/figures_v6"
REPORT = ROOT / "MD Files/verification/v6_layout_verification_20261029.json"

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}
W = f"{{{NS['w']}}}"
R = f"{{{NS['r']}}}"
EXPECTED = [
    "Figure 1.1.", "Figure 1.2.", "Figure 3.1.", "Figure 3.2.",
    "Figure 3.3.", "Figure 3.4.", "Figure 3.5.",
]


def digest(data: bytes) -> str:
    return sha256(data).hexdigest().upper()


def text_of(p) -> str:
    return "".join(p.xpath(".//w:t/text()", namespaces=NS)).strip()


def centered(p) -> bool:
    jc = p.find(f"{W}pPr/{W}jc")
    return jc is not None and jc.get(f"{W}val") == "center"


def explicitly_bold(run) -> bool:
    node = run.find(f"{W}rPr/{W}b")
    if node is None:
        return False
    return node.get(f"{W}val", "1").lower() not in {"0", "false", "off"}


def image_paragraph_map(doc_xml, rel_xml, package: ZipFile):
    rels = {
        node.get("Id"): node.get("Target")
        for node in rel_xml
        if node.get("Id") and node.get("Target")
    }
    paragraphs = doc_xml.xpath(".//w:p", namespaces=NS)
    records = []
    for i, p in enumerate(paragraphs):
        blips = p.xpath(".//a:blip", namespaces=NS)
        if not blips:
            continue
        caption_p = next((q for q in paragraphs[i + 1:] if text_of(q)), None)
        caption = text_of(caption_p) if caption_p is not None else ""
        if not caption.startswith("Figure "):
            continue
        rel_id = blips[0].get(R + "embed")
        target = rels[rel_id]
        media = posixpath.normpath(posixpath.join("word", target))
        records.append((caption, p, caption_p, media, package.read(media)))
    return records


def grayscale(data: bytes) -> bool:
    im = Image.open(BytesIO(data)).convert("RGB")
    red, green, blue = im.split()
    return (ImageChops.difference(red, green).getbbox() is None
            and ImageChops.difference(green, blue).getbbox() is None)


def has_color(data: bytes) -> bool:
    return not grayscale(data)


def placeholder_frame(data: bytes) -> bool:
    im = Image.open(BytesIO(data)).convert("RGB")
    w, h = im.size
    bounds = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
    if bounds is None:
        return False
    left, top, right, bottom = bounds
    return (im.getpixel((w // 2, h // 2)) == (255, 255, 255)
            and im.getpixel((w // 2, top)) == (0, 0, 0)
            and im.getpixel((left, h // 2)) == (0, 0, 0))


with ZipFile(V5_DOCX) as v5, ZipFile(V6_DOCX) as v6:
    assert v5.testzip() is None, "V5 source DOCX CRC check failed"
    assert v6.testzip() is None, "V6 DOCX CRC check failed"
    v5_doc = etree.fromstring(v5.read("word/document.xml"))
    v6_doc = etree.fromstring(v6.read("word/document.xml"))
    v5_rels = etree.fromstring(v5.read("word/_rels/document.xml.rels"))
    v6_rels = etree.fromstring(v6.read("word/_rels/document.xml.rels"))
    v5_images = image_paragraph_map(v5_doc, v5_rels, v5)
    v6_images = image_paragraph_map(v6_doc, v6_rels, v6)
    assert len(v6_images) == 7, f"Expected seven captioned inline figures, got {len(v6_images)}"
    captions = [record[0] for record in v6_images]
    assert [next((prefix for prefix in EXPECTED if caption.startswith(prefix)), None)
            for caption in captions] == EXPECTED, "Figure caption order or numbering changed"
    assert all(centered(record[1]) and centered(record[2]) for record in v6_images), \
        "An image or its caption is not centered"

    by_prefix = {next(prefix for prefix in EXPECTED if caption.startswith(prefix)): record
                 for record in v6_images for caption in [record[0]]}
    for caption in captions:
        assert re.fullmatch(r"Figure \d+\.\d+\. .+", caption), \
            f"Figure caption contains text outside the Figure number and description: {caption}"
    for prefix in ("Figure 1.1.", "Figure 3.1.", "Figure 3.4.", "Figure 3.5."):
        assert grayscale(by_prefix[prefix][4]), f"{prefix} is not grayscale"
    assert has_color(by_prefix["Figure 1.2."][4]), "The Buntun Bridge map lost its color"
    assert placeholder_frame(by_prefix["Figure 3.2."][4]), "Figure 3.2 is not a blank bordered frame"
    assert placeholder_frame(by_prefix["Figure 3.3."][4]), "Figure 3.3 is not a blank bordered frame"

    # The map and blank schematic/PCB placeholders remain byte-identical to V5.
    v5_by_prefix = {next(prefix for prefix in EXPECTED if caption.startswith(prefix)): record
                    for record in v5_images for caption in [record[0]]}
    preserved = {}
    for prefix in ("Figure 1.2.", "Figure 3.2.", "Figure 3.3."):
        assert digest(by_prefix[prefix][4]) == digest(v5_by_prefix[prefix][4]), \
            f"{prefix} media changed unexpectedly"
        preserved[prefix] = digest(by_prefix[prefix][4])

    paragraphs = v6_doc.xpath(".//w:p", namespaces=NS)
    heading = next(p for p in paragraphs if text_of(p) == "1.7 Definition of Terms")
    chapter_two = next(p for p in paragraphs if text_of(p) == "CHAPTER II")
    glossary = paragraphs[paragraphs.index(heading) + 1:paragraphs.index(chapter_two)]
    terms = [p for p in glossary if ":" in text_of(p) and text_of(p)]
    assert len(terms) == 14, f"Expected 14 glossary entries, got {len(terms)}"
    for p in terms:
        full = text_of(p)
        colon = full.index(":") + 1
        before = 0
        saw_bold_label = False
        saw_regular_meaning = False
        for run in p.xpath("./w:r", namespaces=NS):
            run_text = "".join(run.xpath(".//w:t/text()", namespaces=NS))
            after = before + len(run_text)
            if run_text.strip() and before < colon:
                saw_bold_label = saw_bold_label or explicitly_bold(run)
            if run_text.strip() and after > colon and before >= colon:
                saw_regular_meaning = saw_regular_meaning or not explicitly_bold(run)
            before = after
        assert saw_bold_label, f"Term label lost bold formatting: {full[:80]}"
        assert saw_regular_meaning, f"Definition meaning is not regular weight: {full[:80]}"
        ppr = p.find(f"{W}pPr")
        spacing = ppr.find(f"{W}spacing") if ppr is not None else None
        assert spacing is not None and spacing.get(f"{W}line") == "480" \
            and spacing.get(f"{W}after") == "0" and spacing.get(f"{W}before") == "0", \
            f"Glossary entry does not use 2.0 spacing with no paragraph gaps: {full[:80]}"
        assert ppr is not None and ppr.find(f"{W}keepLines") is not None, \
            f"Glossary entry can split across pages: {full[:80]}"
    mems = next(p for p in terms if text_of(p).startswith("MEMS IMU ("))
    mems_ppr = mems.find(f"{W}pPr")
    assert mems_ppr is None or mems_ppr.find(f"{W}pageBreakBefore") is None, \
        "A forced page break remains before MEMS IMU"

    figure_list_row = next(p for p in paragraphs if text_of(p).startswith("3.4. Current firmware"))
    list_row_expected = {
        "1.1.": 6, "1.2.": 10, "3.1.": 37, "3.2.": 38,
        "3.3.": 38, "3.4.": 40, "3.5.": 53,
    }
    for number, page in list_row_expected.items():
        row = next(p for p in paragraphs if text_of(p).startswith(number + " "))
        assert text_of(row).endswith(str(page)), f"Static figure-list page is stale for {number}"
    assert b"Figure 3.4" in (FIG_DIR / "figure_3_5_field_workflow_bw.svg").read_bytes(), \
        "Figure 3.5 does not refer to Figure 3.4"

with ZipFile(V5_DOCX) as source_package, ZipFile(V6_DOCX) as package:
    v5_docx_crc = source_package.testzip()
    v6_docx_crc = package.testzip()
    assert v5_docx_crc is None and v6_docx_crc is None
    source_parts = set(source_package.namelist())
    output_parts = set(package.namelist())
    assert source_parts == output_parts, "DOCX package part set changed"
    changed_parts = [name for name in sorted(source_parts)
                     if source_package.read(name) != package.read(name)]
    expected_changed = ["word/document.xml", "word/media/image2.png",
                        "word/media/image7.png", "word/media/image8.png"]
    assert changed_parts == expected_changed, f"Unexpected V5-to-V6 package changes: {changed_parts}"
    assert V5_DOCX.exists()
    v5_doc_xml = etree.fromstring(source_package.read("word/document.xml"))
    v6_doc_xml = etree.fromstring(package.read("word/document.xml"))
    v5_paragraphs = v5_doc_xml.xpath(".//w:p", namespaces=NS)
    v6_paragraphs = v6_doc_xml.xpath(".//w:p", namespaces=NS)
    assert len(v5_paragraphs) == len(v6_paragraphs), "Paragraph count changed between V5 and V6"
    title_index = next(i for i, p in enumerate(v5_paragraphs) if text_of(p).startswith("TITLE"))
    page_value_changes = []
    for i, (old_p, new_p) in enumerate(zip(v5_paragraphs, v6_paragraphs)):
        old_text, new_text = text_of(old_p), text_of(new_p)
        if old_text == new_text:
            continue
        old_base = re.sub(r"\d+$", "", old_text)
        new_base = re.sub(r"\d+$", "", new_text)
        assert i < title_index and old_base == new_base, \
            f"Non-pagination paragraph text changed at paragraph {i}: {old_text!r} -> {new_text!r}"
        page_value_changes.append(i)
    # The abstract/keywords paragraphs remain text- and spacing-identical.
    def find_text(xml, prefix):
        return next(p for p in xml.xpath(".//w:p", namespaces=NS) if text_of(p).startswith(prefix))
    abstract_prefix = "This developmental study aims to develop and field-evaluate a localized system"
    keywords_prefix = "Keywords:"
    for prefix in (abstract_prefix, keywords_prefix):
        old_p, new_p = find_text(v5_doc_xml, prefix), find_text(v6_doc_xml, prefix)
        assert text_of(old_p) == text_of(new_p), f"Abstract content changed: {prefix}"
        old_spacing = old_p.find(f"{W}pPr/{W}spacing")
        new_spacing = new_p.find(f"{W}pPr/{W}spacing")
        old_value = None if old_spacing is None else tuple(old_spacing.get(W + key) for key in ("line", "lineRule", "before", "after"))
        new_value = None if new_spacing is None else tuple(new_spacing.get(W + key) for key in ("line", "lineRule", "before", "after"))
        assert old_value == new_value, f"Abstract spacing changed: {prefix}"

pdf = PdfReader(V6_PDF)
assert len(pdf.pages) == 80, f"Expected 80 physical pages, got {len(pdf.pages)}"
assert all(round(float(page.mediabox.width)) == 612 and round(float(page.mediabox.height)) == 792
           for page in pdf.pages), "A PDF page is not US Letter"
pdf_text = [" ".join((page.extract_text() or "").split()) for page in pdf.pages]


def printed_page(physical_page: int) -> int:
    match = re.search(r"AND ARCHITECTURE\s+(\d+)\s+BACHELOR", pdf_text[physical_page - 1])
    assert match, f"Could not read printed page number on PDF page {physical_page}"
    return int(match.group(1))


figure_pages = {
    "Figure 1.1.": (15, 6), "Figure 1.2.": (19, 10), "Figure 3.1.": (46, 37),
    "Figure 3.2.": (47, 38), "Figure 3.3.": (47, 38), "Figure 3.4.": (49, 40),
    "Figure 3.5.": (62, 53),
}
for caption, (physical, printed) in figure_pages.items():
    assert caption in pdf_text[physical - 1], f"{caption} missing from expected PDF page {physical}"
    assert printed_page(physical) == printed, f"{caption} printed page number mismatch"

chapter_pages = {
    "CHAPTER I": (10, 1), "CHAPTER II": (23, 14), "CHAPTER III": (41, 32),
    "CHAPTER IV": (69, 60), "CHAPTER V": (70, 61), "REFERENCES": (71, 62),
}
for heading_text, (physical, printed) in chapter_pages.items():
    assert heading_text in pdf_text[physical - 1], f"{heading_text} missing from expected page"
    assert printed_page(physical) == printed, f"{heading_text} page number mismatch"

assert "Keywords:" in pdf_text[8], "Abstract Keywords not on physical PDF page 9"
assert "Keywords:" not in pdf_text[9], "Abstract Keywords spilled onto a second page"
assert "Traffic-count group:" in pdf_text[21], "Last glossary entry is not on printed page 13"
assert "CHAPTER II" in pdf_text[22], "Chapter II did not start on its separate printed page 14"

fig_list_text = pdf_text[7]
for entry in ("1.1.", "1.2.", "3.1.", "3.2.", "3.3.", "3.4.", "3.5."):
    assert entry in fig_list_text, f"List of Figures is missing {entry}"
assert "window-processing flowchart" in fig_list_text and "40" in fig_list_text, \
    "List of Figures does not reflect Figure 3.4's caption/page"

table_checks = {
    "Required documentation of the final monitoring-system configuration": (45, 36),
    "Minimum field information recorded for each measurement session": (52, 43),
    "Vibration-acquisition protocol summary": (55, 46),
    "Pilot-derived traffic-group rules": (57, 48),
}
for title, (physical, printed) in table_checks.items():
    assert title in pdf_text[physical - 1], f"{title} not on the recorded page"
    assert printed_page(physical) == printed, f"{title} printed page mismatch"

report = {
    "date": "2026-10-29",
    "status": "verified for the recorded structural, pagination, and layout checks; not an approval or research-validity determination",
    "source_v5": {
        "docx_sha256": digest(V5_DOCX.read_bytes()),
        "pdf_sha256": digest(V5_PDF.read_bytes()),
    },
    "candidate_v6": {
        "docx_sha256": digest(V6_DOCX.read_bytes()),
        "docx_bytes": V6_DOCX.stat().st_size,
        "pdf_sha256": digest(V6_PDF.read_bytes()),
        "pdf_bytes": V6_PDF.stat().st_size,
        "physical_pages": len(pdf.pages),
        "paper_size": "US Letter",
    },
    "figure_pages_physical_and_printed": {
        k: {"pdf_page": v[0], "printed_page": v[1]} for k, v in figure_pages.items()
    },
    "chapter_pages_physical_and_printed": {
        k: {"pdf_page": v[0], "printed_page": v[1]} for k, v in chapter_pages.items()
    },
    "checks": {
        "docx_zip_crc": "pass",
        "seven_centered_figure_image_caption_pairs": "pass",
        "caption_number_sequence_and_list_of_figures": "pass",
        "monochrome_figures_1_1_3_1_3_4_3_5": "pass",
        "colored_map_and_v5_map_placeholder_preservation": "pass",
        "blank_white_black_border_figures_3_2_3_3": "pass",
        "fourteen_bold_term_labels_regular_meanings_and_2_0_spacing": "pass",
        "glossary_no_forced_break_before_mems_imu": "pass",
        "abstract_and_keywords_single_page": "pass",
        "chapter_ii_separate_page_and_continuous_numbering": "pass",
        "static_table_list_page_locations": "pass",
        "figure_3_5_to_figure_3_4_reference": "pass",
        "paragraph_text_preserved_except_front_matter_page_values": "pass",
    },
    "preserved_media_sha256": preserved,
    "front_matter_page_value_paragraphs_changed": page_value_changes,
    "rendered_pages_reviewed_at_160dpi": [5, 6, 7, 8, 9, 15, 19, 20, 21, 22, 23, 46, 47, 49, 52, 55, 57, 62, 69, 70, 71],
    "rendered_all_physical_pages_at_dpi": 75,
    "contact_sheets_reviewed_at_dpi": 75,
    "contact_sheets_reviewed": ["contact_01.png", "contact_02.png", "contact_03.png", "contact_04.png"],
    "word_com_export": "Microsoft Word 16.0; DOCX opened read-only; Repaginate then ExportAsFixedFormat PDF",
    "documents_skill_renderer": "unavailable: LibreOffice soffice.exe not found; Word COM plus Poppler used as fallback",
    "limitations": [
        "This layout pass does not re-audit the bibliography or verify each citation against full text.",
        "No ethics, privacy, Turnitin, AI-writing, site-permission, safety, or adviser approval is established.",
        "No firmware build, hardware test, CAD check, or field-data validation was performed.",
        "The manuscript and firmware's window-selection/valid-window conflicts remain open as recorded in earlier ledgers.",
    ],
}
REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
print("Report:", REPORT)
