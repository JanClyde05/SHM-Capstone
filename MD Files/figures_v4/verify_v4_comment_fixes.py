from io import BytesIO
from pathlib import Path
import hashlib
import posixpath
from zipfile import ZipFile

from lxml import etree
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
DOCX = ROOT / "Documents/The Real Research Paper/GPT Paper/SHM_Research_Aligned_Revision_Draft_v4.docx"
NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}
W = f"{{{NS['w']}}}"


def para_text(p):
    return "".join(p.xpath(".//w:t/text()", namespaces=NS)).strip()


with ZipFile(DOCX) as z:
    assert z.testzip() is None
    document = etree.fromstring(z.read("word/document.xml"))
    rels = etree.fromstring(z.read("word/_rels/document.xml.rels"))
    rel_map = {r.get("Id"): r.get("Target") for r in rels if r.get("Id") and r.get("Target")}
    body = document.find(".//" + W + "body")
    paragraphs = [p for p in body if p.tag == W + "p"]
    heading_index = next(i for i, p in enumerate(paragraphs) if para_text(p).startswith("1.7 Definition of Terms"))

    glossary = []
    for p in paragraphs[heading_index + 1:]:
        if para_text(p).startswith("CHAPTER II"):
            break
        if not para_text(p):
            continue
        runs = p.findall(W + "r")
        label = runs[0]
        term = "".join(label.xpath("./w:t/text()", namespaces=NS))
        assert term.endswith(":"), repr(term)
        bold = label.find(W + "rPr/" + W + "b")
        assert bold is not None and bold.get(W + "val", "1") not in ("0", "false", "off"), (term, "term not bold")
        for run in runs[1:]:
            bold = run.find(W + "rPr/" + W + "b")
            assert bold is not None and bold.get(W + "val", "1") in ("0", "false", "off"), (term, "definition run bold")
        glossary.append(term)
    assert len(glossary) == 14, len(glossary)
    mems = next(p for p in paragraphs[heading_index + 1:] if para_text(p).startswith("MEMS IMU"))
    assert mems.find(W + "pPr/" + W + "pageBreakBefore") is not None

    figure_records = {}
    for i, p in enumerate(paragraphs):
        if not p.xpath(".//a:blip", namespaces=NS):
            continue
        caption = next((para_text(q) for q in paragraphs[i + 1:] if para_text(q)), "")
        if not caption.startswith(("Figure 1.2.", "Figure 3.4.", "Figure 3.5.")):
            continue
        blip = p.xpath(".//a:blip", namespaces=NS)[0]
        target = posixpath.normpath(posixpath.join("word", rel_map[blip.get("{" + NS["r"] + "}embed")]))
        data = z.read(target)
        image = Image.open(BytesIO(data)).convert("RGB")
        colors = image.getcolors(maxcolors=1_000_000)
        assert colors is not None
        has_color = any(red != green or green != blue for count, (red, green, blue) in colors)
        image_align = p.find(W + "pPr/" + W + "jc")
        caption_p = next(q for q in paragraphs[i + 1:] if para_text(q))
        caption_align = caption_p.find(W + "pPr/" + W + "jc")
        assert image_align is not None and image_align.get(W + "val") == "center", (caption, "image alignment")
        assert caption_align is not None and caption_align.get(W + "val") == "center", (caption, "caption alignment")
        figure_records[caption] = (target, image.size, has_color, hashlib.sha256(data).hexdigest().upper())

    field = next(value for caption, value in figure_records.items() if caption.startswith("Figure 3.5."))
    code = next(value for caption, value in figure_records.items() if caption.startswith("Figure 3.4."))
    map_image = next(value for caption, value in figure_records.items() if caption.startswith("Figure 1.2."))
    assert field[2] is False, "field workflow is not monochrome"
    assert code[2] is False, "code flowchart is not monochrome"
    assert map_image[2] is True, "map has no chromatic pixels"

print("Glossary: 14 labels bold; definitions regular; MEMS IMU starts a new page.")
print("Figure images and captions centered; Figures 3.4 and 3.5 monochrome; Figure 1.2 remains colored.")
for caption, record in figure_records.items():
    print(caption, record)
print("DOCX ZIP CRC: pass")
