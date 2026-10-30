from __future__ import annotations

from datetime import datetime, timezone, timedelta
from hashlib import sha256
import json
from pathlib import Path
import re
from zipfile import ZipFile

from lxml import etree
from PIL import Image
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "Documents/The Real Research Paper/GPT Paper/SHM_Research_Aligned_Revision_Draft_v2.docx"
V8 = ROOT / "Documents/The Real Research Paper/GPT Paper/SHM_Research_Aligned_Revision_Draft_v8.docx"
V9 = ROOT / "Documents/The Real Research Paper/GPT Paper/SHM_Research_Aligned_Revision_Draft_v9.docx"
PDF = ROOT / "Documents/The Real Research Paper/GPT Paper/SHM_Research_Aligned_Revision_Draft_v9.pdf"
INITIAL_V9 = ROOT / "MD Files/verification/v9_render_20261030/SHM_Research_Aligned_Revision_Draft_v9_initial.docx"
INITIAL_PDF = ROOT / "MD Files/verification/v9_render_20261030/SHM_Research_Aligned_Revision_Draft_v9_initial.pdf"
REFLOW1_V9 = ROOT / "MD Files/verification/v9_render_20261030/SHM_Research_Aligned_Revision_Draft_v9_reflow1.docx"
REFLOW2_V9 = ROOT / "MD Files/verification/v9_render_20261030/SHM_Research_Aligned_Revision_Draft_v9_reflow2.docx"
CAPTION_KEEP_V9 = ROOT / "MD Files/verification/v9_render_20261030/SHM_Research_Aligned_Revision_Draft_v9_caption_kept.docx"
CAPTION_KEEP_PDF = ROOT / "MD Files/verification/v9_render_20261030/SHM_Research_Aligned_Revision_Draft_v9_caption_kept.pdf"
ASSETS = ROOT / "MD Files/verification/v9_figures_20261030"
FINAL_RENDER = ROOT / "MD Files/verification/v9_render_20261030_caption_kept_final"
REPORT = ROOT / "MD Files/verification/v9_figure_insertion_verification_20261030.json"

EXPECTED = {
    "v2": "B09C741309444DAB16ACA6957250217CB776E310C20459820547AA747264CB42",
    "v8": "7B5CD7F9D341D47ED7DB82C1351CDF9EFADE1D275D36A01927BAD673966DED1C",
    "initial_v9": "56457ECB5B0B859634A00F8F9205169E1A7C5693CE9EE3542A9F0FB7C7243DE4",
    "reflow1_v9": "E5DF5DA7DF0659B70DE7FED82662A3E7CBE035F6F40EC97599701CF9FAD54C72",
    "reflow2_v9": "118C19F7FC4B344D9812B0A4C385C36E46C4BFBC508C2445EA1F576BCF1E6409",
    "caption_keep_v9": "BCD8B916EE54AAA4414DC7A3D4AAC5FD7B79A193110E2ADE21625A17A6CD1B80",
    "caption_keep_pdf": "ED6DAE71277C2A7C2D69095E260E453E213A0859C576CEF28926A6D0814D712D",
    "final_v9": "BCD8B916EE54AAA4414DC7A3D4AAC5FD7B79A193110E2ADE21625A17A6CD1B80",
    "final_pdf": "ED6DAE71277C2A7C2D69095E260E453E213A0859C576CEF28926A6D0814D712D",
}

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
WP = {"wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"}


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest().upper()


def body_paragraphs(docx: Path) -> tuple[list[etree._Element], list[str], dict[str, bytes]]:
    with ZipFile(docx) as zf:
        bad = zf.testzip()
        assert bad is None, f"DOCX ZIP CRC error: {bad}"
        parts = {info.filename: zf.read(info.filename) for info in zf.infolist()}
    root = etree.fromstring(parts["word/document.xml"])
    paras = root.xpath("//w:body/w:p", namespaces=NS)
    texts = ["".join(p.xpath(".//w:t/text()", namespaces=NS)) for p in paras]
    return paras, texts, parts


def first_table_cells(docx: Path) -> list[list[str]]:
    with ZipFile(docx) as zf:
        root = etree.fromstring(zf.read("word/document.xml"))
    tables = root.xpath("//w:body/w:tbl", namespaces=NS)
    assert tables, f"No table found in {docx.name}"
    return [
        ["".join(cell.xpath(".//w:t/text()", namespaces=NS)) for cell in row.xpath("./w:tc", namespaces=NS)]
        for row in tables[0].xpath("./w:tr", namespaces=NS)
    ]


def image_hash(data: bytes) -> str:
    return sha256(data).hexdigest().upper()


def require_hash(path: Path, value: str, label: str) -> str:
    actual = digest(path)
    assert actual == value, f"{label} SHA-256 mismatch: {actual}"
    return actual


def main() -> None:
    v2_hash = require_hash(V2, EXPECTED["v2"], "V2 approved source")
    v8_hash = require_hash(V8, EXPECTED["v8"], "V8 base")
    initial_hash = require_hash(INITIAL_V9, EXPECTED["initial_v9"], "Initial V9 snapshot")
    reflow1_hash = require_hash(REFLOW1_V9, EXPECTED["reflow1_v9"], "Intermediate reflow snapshot")
    reflow2_hash = require_hash(REFLOW2_V9, EXPECTED["reflow2_v9"], "Intermediate reflow2 snapshot")
    caption_keep_hash = require_hash(CAPTION_KEEP_V9, EXPECTED["caption_keep_v9"], "Caption-keep V9 snapshot")
    caption_keep_pdf_hash = require_hash(CAPTION_KEEP_PDF, EXPECTED["caption_keep_pdf"], "Caption-keep PDF snapshot")
    final_hash = require_hash(V9, EXPECTED["final_v9"], "Final V9 DOCX")
    pdf_hash = require_hash(PDF, EXPECTED["final_pdf"], "Final V9 PDF")
    initial_pdf_hash = digest(INITIAL_PDF)

    initial_paras, initial_text, initial_parts = body_paragraphs(INITIAL_V9)
    final_paras, final_text, final_parts = body_paragraphs(V9)
    base_paras, base_text, base_parts = body_paragraphs(V8)
    assert len(initial_paras) == len(final_paras) == 458
    caption_keep_paras, caption_keep_text, _ = body_paragraphs(CAPTION_KEEP_V9)
    assert caption_keep_text == final_text
    assert caption_keep_hash == final_hash
    assert caption_keep_pdf_hash == pdf_hash
    changed_since_initial = [i for i, (a, b) in enumerate(zip(initial_text, final_text)) if a != b]
    assert changed_since_initial == [255], changed_since_initial
    changed_from_v8 = [i for i, (a, b) in enumerate(zip(base_text, final_text)) if a != b]
    assert changed_from_v8 == [93, 94, 255, 260, 262], changed_from_v8
    package_parts_changed_from_v8 = sorted(
        name for name in set(base_parts) | set(final_parts)
        if base_parts.get(name) != final_parts.get(name)
    )
    expected_changed = ["word/document.xml", "word/media/image5.png", "word/media/image6.png"]
    assert package_parts_changed_from_v8 == expected_changed, package_parts_changed_from_v8
    initial_table = first_table_cells(INITIAL_V9)
    reflow2_table = first_table_cells(REFLOW2_V9)
    base_table = first_table_cells(V8)
    final_table = first_table_cells(V9)
    changed_table_cells_from_v8 = [
        [r, c] for r in range(len(final_table)) for c in range(len(final_table[r]))
        if base_table[r][c] != final_table[r][c]
    ]
    changed_table_cells_from_reflow2 = [
        [r, c] for r in range(len(final_table)) for c in range(len(final_table[r]))
        if reflow2_table[r][c] != final_table[r][c]
    ]
    assert changed_table_cells_from_v8 == [[1, 1], [2, 1], [6, 1]], changed_table_cells_from_v8
    assert changed_table_cells_from_reflow2 == [[1, 1], [2, 1], [6, 1]], changed_table_cells_from_reflow2
    assert initial_table[1][1] == base_table[1][1]
    assert final_table[1][1].endswith("record board revision, component markings, and channel identifiers.")
    assert "600-second session" in final_table[2][1]
    assert "ten consecutive 60-second windows" in final_table[2][1]
    assert "analysis band, estimator/window settings" in final_table[2][1]
    assert "Arduino IDE and library versions" in final_table[2][1]
    assert "measured per-channel sampling rate" in final_table[2][1]
    assert "raw-data fields, session-summary fields" in final_table[6][1]
    assert final_text[256] == "Table 1. Required documentation of the final monitoring-system configuration"
    assert final_paras[256].xpath("./w:pPr/w:keepNext", namespaces=NS)
    assert final_paras[257].xpath("./w:pPr/w:keepNext", namespaces=NS)

    expected_captions = {
        260: "Figure 3.2. Device schematic diagram",
        262: "Figure 3.3. PCB layout and 3D CAD view",
    }
    for i, expected in expected_captions.items():
        assert final_text[i] == expected, (i, final_text[i])
        jc = final_paras[i].xpath("./w:pPr/w:jc/@w:val", namespaces=NS)
        assert jc == ["center"], (i, jc)
    for i in (259, 261):
        jc = final_paras[i].xpath("./w:pPr/w:jc/@w:val", namespaces=NS)
        assert jc == ["center"], (i, jc)
    assert "placeholder" not in final_text[93].lower()
    assert "placeholder" not in final_text[94].lower()
    assert "placeholder" not in final_text[260].lower()
    assert "placeholder" not in final_text[262].lower()
    assert sum(bool(s.strip()) for s in final_text[356:]) == 101
    with ZipFile(V9) as zf:
        document_root = etree.fromstring(zf.read("word/document.xml"))
    inline_picture_count = len(document_root.xpath("//wp:inline", namespaces=WP))
    assert inline_picture_count == 7

    design_manifest_path = ROOT / "PCB Files/GPT Build - PCB/design/DESIGN_MANIFEST.json"
    design_manifest = json.loads(design_manifest_path.read_text(encoding="utf-8"))
    pcb_path = ROOT / "PCB Files/GPT Build - PCB/design/SHM_Node_R2.kicad_pcb"
    schematic_path = ROOT / "PCB Files/GPT Build - PCB/design/SHM_Node_R2.kicad_sch"
    pcb_hash = digest(pcb_path)
    schematic_hash = digest(schematic_path)
    assert pcb_hash == design_manifest["file_hashes_sha256"]["SHM_Node_R2.kicad_pcb"].upper()
    assert schematic_hash == design_manifest["file_hashes_sha256"]["SHM_Node_R2.kicad_sch"].upper()

    preview_readme = ROOT / "PCB Files/GPT Build - PCB/previews/00_README_ACTIVE_PREVIEWS.md"
    preview_text = preview_readme.read_text(encoding="utf-8")
    assert "active_pcb_3d_top.png" in preview_text
    assert "Generic MPU 3D models are approximate" in preview_text
    assert "active_pcb_top.svg" in preview_text
    schematic_asset = ROOT / "PCB Files/GPT Build - PCB/previews/active_schematic.png"
    pcb_top_asset = ROOT / "PCB Files/GPT Build - PCB/previews/active_pcb_top.svg"
    pcb_3d_asset = ROOT / "PCB Files/GPT Build - PCB/previews/active_pcb_3d_top.png"
    composite_asset = ASSETS / "figure_3_3_pcb_layout_and_3d.png"
    with Image.open(schematic_asset) as im:
        schematic_dimensions = list(im.size)
    with Image.open(composite_asset) as im:
        composite_dimensions = list(im.size)
        composite_mode = im.mode
        palette = im.convert("RGB").getcolors(maxcolors=1_000_000)
        color_count = len(palette) if palette else None
    with ZipFile(V9) as zf:
        embedded_schematic_hash = image_hash(zf.read("word/media/image5.png"))
        embedded_composite_hash = image_hash(zf.read("word/media/image6.png"))
    assert embedded_schematic_hash == digest(schematic_asset)
    assert embedded_composite_hash == digest(composite_asset)

    reader = PdfReader(str(PDF))
    assert len(reader.pages) == 80
    assert all(abs(float(page.mediabox.width) - 612) < 0.01 and abs(float(page.mediabox.height) - 792) < 0.01 for page in reader.pages)
    pdf_text = [page.extract_text() or "" for page in reader.pages]
    printed_page_numbers = []
    for i, text in enumerate(pdf_text):
        m = re.search(r"AND ARCHITECTURE\s+([ivxlcdm]+|\d+)\b", text, re.I)
        assert m, f"Printed page number not found on physical PDF page {i + 1}"
        printed_page_numbers.append(m.group(1).lower())
    expected_page_numbers = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix"] + [str(i) for i in range(1, 72)]
    assert printed_page_numbers == expected_page_numbers, printed_page_numbers
    list_figures = re.sub(r"\s+", " ", pdf_text[7])
    list_tables = re.sub(r"\s+", " ", pdf_text[6])
    assert "Required documentation of the final monitoring-system configuration" in list_tables
    assert re.search(r"configuration\s+\.*36\b", list_tables)
    for label, phrase in (
        ("3.2", "Device schematic diagram"),
        ("3.3", "PCB layout and 3D CAD view"),
        ("3.4", "Current firmware session-control and window-processing flowchart"),
        ("3.5", "Field Data Collection and Evaluation Flowchart"),
    ):
        assert f"{label}. {phrase}" in list_figures, (label, list_figures)
    assert "38" in list_figures and "40" in list_figures and "53" in list_figures
    p44 = pdf_text[43]
    p45 = pdf_text[44]
    p47 = pdf_text[46]
    p49 = pdf_text[48]
    p62 = pdf_text[61]
    assert "The 3D view is a CAD preview" in p44
    assert "physical assembly or fit" in p44
    assert "Table 1. Required documentation" not in p44
    assert "Table 1. Required documentation of the final monitoring-system configuration" in p45
    assert "Component" in p45 and "Board mounting" in p45
    assert "Figure 3.2. Device schematic diagram" in p47
    assert "Figure 3.3. PCB layout and 3D CAD view" in p47
    assert "Figure 3.4. Current firmware" in p49
    assert "Figure 3.5. Field Data Collection" in p62
    assert len(list(FINAL_RENDER.glob("page-*.png"))) == 80
    for page_num in (8, 44, 45, 46, 47, 49, 62):
        assert (FINAL_RENDER / f"hi-{page_num:02d}.png").exists()
    assert len(list(FINAL_RENDER.glob("contact_*.png"))) == 4

    now = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
    report = {
        "record": "V9 schematic/PCB/3D figure insertion and final layout verification",
        "created_local": now,
        "status": "passed for scoped figure insertion, document-package integrity, pagination, and rendered layout checks",
        "authority": "User explicitly requested insertion of the existing schematic, PCB layout, and 3D view.",
        "approval_boundary": "V2 remains the approved source; V9 is a separate review candidate and is not adviser/institution approval.",
        "artifacts": {
            "approved_v2": {"path": str(V2.relative_to(ROOT)), "sha256": v2_hash},
            "base_v8": {"path": str(V8.relative_to(ROOT)), "sha256": v8_hash},
            "initial_v9_snapshot": {"path": str(INITIAL_V9.relative_to(ROOT)), "sha256": initial_hash},
            "initial_v9_pdf_snapshot": {"path": str(INITIAL_PDF.relative_to(ROOT)), "sha256": initial_pdf_hash},
            "intermediate_reflow1_snapshot": {"path": str(REFLOW1_V9.relative_to(ROOT)), "sha256": reflow1_hash},
            "intermediate_reflow2_snapshot": {"path": str(REFLOW2_V9.relative_to(ROOT)), "sha256": reflow2_hash},
            "caption_kept_v9_snapshot": {"path": str(CAPTION_KEEP_V9.relative_to(ROOT)), "bytes": CAPTION_KEEP_V9.stat().st_size, "sha256": caption_keep_hash},
            "caption_kept_pdf_snapshot": {"path": str(CAPTION_KEEP_PDF.relative_to(ROOT)), "bytes": CAPTION_KEEP_PDF.stat().st_size, "sha256": caption_keep_pdf_hash},
            "final_v9_docx": {"path": str(V9.relative_to(ROOT)), "bytes": V9.stat().st_size, "sha256": final_hash},
            "final_v9_pdf": {"path": str(PDF.relative_to(ROOT)), "bytes": PDF.stat().st_size, "sha256": pdf_hash},
        },
        "source_provenance": {
            "design_manifest": str(design_manifest_path.relative_to(ROOT)),
            "active_schematic": {"path": str(schematic_path.relative_to(ROOT)), "sha256": schematic_hash},
            "active_pcb": {"path": str(pcb_path.relative_to(ROOT)), "sha256": pcb_hash},
            "schematic_render": {"path": str(schematic_asset.relative_to(ROOT)), "sha256": digest(schematic_asset), "dimensions_px": schematic_dimensions},
            "pcb_top_plot": {"path": str(pcb_top_asset.relative_to(ROOT)), "sha256": digest(pcb_top_asset)},
            "pcb_3d_render": {"path": str(pcb_3d_asset.relative_to(ROOT)), "sha256": digest(pcb_3d_asset)},
            "composite_inserted_figure": {"path": str(composite_asset.relative_to(ROOT)), "sha256": digest(composite_asset), "dimensions_px": composite_dimensions, "mode": composite_mode, "distinct_color_count": color_count},
            "embedded_media_hashes": {"word/media/image5.png": embedded_schematic_hash, "word/media/image6.png": embedded_composite_hash},
            "source_limit": "The preview register identifies generic MPU-6050 3D packages as approximate; a CAD view is not evidence of assembly or physical fit.",
        },
        "document_diff": {
            "final_v9_vs_v8_changed_body_paragraph_indexes": changed_from_v8,
            "final_v9_vs_v8_changed_table_cells_zero_based": changed_table_cells_from_v8,
            "final_v9_vs_v8_changed_package_parts": package_parts_changed_from_v8,
            "final_v9_vs_initial_v9_changed_body_paragraph_indexes": changed_since_initial,
            "final_v9_vs_reflow2_changed_table_cells_zero_based": changed_table_cells_from_reflow2,
            "table_caption_keep_next_paragraph_indexes": [256, 257],
            "table_caption_keep_next_text": final_text[256],
            "reference_entry_count": 101,
            "inline_picture_count": inline_picture_count,
        },
        "figure_page_map": {
            "list_of_figures": {"physical_pdf_page": 8, "printed_page": "viii", "verified_entries": ["3.2 p. 38", "3.3 p. 38", "3.4 p. 40", "3.5 p. 53"]},
            "configuration_caveat": {"physical_pdf_page": 44, "printed_page": 35},
            "table_1_caption_and_table": {"physical_pdf_page": 45, "printed_page": 36},
            "figure_3_1": {"physical_pdf_page": 46, "printed_page": 37},
            "figures_3_2_and_3_3": {"physical_pdf_page": 47, "printed_page": 38},
            "figure_3_4": {"physical_pdf_page": 49, "printed_page": 40},
            "figure_3_5": {"physical_pdf_page": 62, "printed_page": 53},
        },
        "printed_page_number_sequence": "Roman i–ix front matter followed by Arabic 1–71 continuously; verified from each page header.",
        "checks": [
            {"check": "V2/V8 preservation and fixed artifact identities", "status": "passed", "evidence": "Expected SHA-256 values match; V2 and V8 were not written."},
            {"check": "OOXML package integrity and bounded differences", "status": "passed", "evidence": "DOCX ZIP CRC passed; V9 differs from V8 only in document.xml and replacement media image5/image6; body-text reflow changes paragraph 255, the final table-completeness edit changes three Table 1 cells, and caption keepNext formatting applies to paragraphs 256–257."},
            {"check": "Active design/source lineage", "status": "passed", "evidence": "Active schematic and PCB hashes match design/DESIGN_MANIFEST.json; preview index marks these renders active and warns that generic MPU 3D models are approximate."},
            {"check": "Figure contents, colors, alignment, captions, and static list", "status": "passed", "evidence": "Embedded schematic and composite hashes match source/derived files; picture and caption paragraphs are centered; captions contain figure number and description; List of Figures entries match PDF pagination."},
            {"check": "Table 1 configuration-field completeness", "status": "passed", "evidence": "The board revision/component markings, session/window schedule, analysis settings, software/library versions, measured per-channel rate, raw-data fields, and session-summary fields are stated in the corresponding table rows; window selection remains neutral pending resolution."},
            {"check": "Pagination, caveat, and table-caption keep-together", "status": "passed", "evidence": "Word 2019 export is 80 US Letter pages; Roman front matter i–ix is followed by Arabic pages 1–71; the CAD-only/approximate-model caveat is on physical p. 44, and the complete Table 1 caption and table are together on physical p. 45 / printed p. 36. The List of Tables also gives page 36."},
            {"check": "Full-document visual pass", "status": "passed", "evidence": "All 80 pages from the caption-kept PDF were rendered at 75 dpi and reviewed in four contact sheets; physical pp. 8, 44–47, 49, and 62 were inspected at 160 dpi. The schematic, PCB/3D composite, and diagrams are centered; no text overflow or arrow/decision-label overlaps were observed in targeted figures."},
        ],
        "toolchain": {
            "exporter": "Microsoft Word 2019 / Word 16.0, opened read-only",
            "renderer": "Poppler 26.07.0 pdftoppm",
            "python": "Bundled workspace Python runtime",
            "pypdf": "6.10.0",
            "lxml": "6.1.1",
            "pillow": "12.3.0",
            "render_resolution_dpi": {"all_pages": 75, "targeted_pages": 160},
        },
        "limitations": [
            "This verifies insertion, source file identity, document structure and rendered layout only; it is not a full-paper claim/reference audit.",
            "The figures describe the active CAD design; they do not prove fabrication, assembly, fit, electrical behavior, sensor timing, or field performance.",
            "Ethics/privacy, Turnitin/AI-writing review, site permission/safety, and adviser/institution approval are separate unresolved gates.",
            "No code, PCB CAD, measurements, or reference entries were changed in this figure-insertion pass.",
        ],
        "retained_failures": [
            "Initial V9 render split the CAD caveat across physical pp. 44–45; the paragraph was condensed to refer to Table 1 while preserving evidence-source, pending-value, and CAD limitation text. Final render inspected with the complete caveat on p. 44.",
            "A read-only project-document print failed because the Windows console could not encode a Unicode arrow; reran with UTF-8 output and no files were changed by the failed read.",
            "The initial reflow-writer invocation had an indentation syntax error before execution; no files changed. The corrected script ran with hash preconditions.",
            "A second reflow script stopped on an outdated text precondition after the intermediate wording changed; no document write occurred. The guard was corrected and rerun successfully.",
            "The initial structural verifier expected seven w:drawing containers; inspection found seven inline pictures plus anchored diagram containers. No paper file changed; the assertion was corrected to count wp:inline and the verification then passed.",
            "A post-render content audit found Table 1 lacked several configuration fields listed in the pre-reflow note. Three table cells were expanded from already stated method requirements; the final Word export and full render were repeated, and Table 1 remains on printed p. 36.",
            "The table-complete render stranded the Table 1 caption on printed p. 35. The caption/spacer were set to keep with the table; a new Word PDF export and full-page render verified caption and table together on printed p. 36 and the List of Tables entry matches.",
            "An existing directory named v9_render_20261030_final contained an older PDF render. Its page 45 did not contain the final caption/expanded fields; it was retained as historical, and all 80 pages were rerendered from the caption-kept PDF into v9_render_20261030_caption_kept_final/.",
            "A PowerShell PDF snapshot command attempted a self-copy and warned that the source and destination were identical. The source was unchanged; snapshot and output hashes were verified equal.",
            "System Python lacked pypdf and pdftotext was not available on PATH. The configured workspace Python/pypdf runtime was used for read-only page extraction and passed the text/page checks.",
        ],
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "docx_sha256": final_hash, "pdf_sha256": pdf_hash, "report": str(REPORT.relative_to(ROOT))}, indent=2))


if __name__ == "__main__":
    main()
