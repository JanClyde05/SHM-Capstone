from copy import deepcopy
from pathlib import Path, PurePosixPath
import hashlib
import os
import posixpath
import re
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED

from lxml import etree
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
DOCX = ROOT / "Documents/The Real Research Paper/GPT Paper/SHM_Research_Aligned_Revision_Draft_v4.docx"
FLOW = ROOT / "MD Files/figures_v4/figure_3_4_firmware_flow_bw.png"
FIELD = ROOT / "MD Files/figures_v4/figure_3_5_field_workflow_bw.png"
OUTPUT = Path(tempfile.gettempdir()) / "SHM_Research_Aligned_Revision_Draft_v4_commentfix.docx"

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
}
W = f"{{{NS['w']}}}"
R = f"{{{NS['r']}}}"
WP = f"{{{NS['wp']}}}"
A = f"{{{NS['a']}}}"
XML = "{http://www.w3.org/XML/1998/namespace}"


def para_text(p):
    return "".join(p.xpath(".//w:t/text()", namespaces=NS)).strip()


def set_boolean(run_properties, name, value):
    node = run_properties.find(W + name)
    if node is None:
        node = etree.SubElement(run_properties, W + name)
    node.set(W + "val", "1" if value else "0")


def set_term_run(run, term):
    props = run.find(W + "rPr")
    if props is None:
        props = etree.Element(W + "rPr")
        run.insert(0, props)
    set_boolean(props, "b", True)
    set_boolean(props, "bCs", True)
    for child in list(run):
        if child is not props:
            run.remove(child)
    t = etree.SubElement(run, W + "t")
    t.text = term


def split_term_run(run):
    text_nodes = run.xpath("./w:t", namespaces=NS)
    text = "".join(n.text or "" for n in text_nodes)
    colon = text.find(":")
    if colon < 0:
        return None, None
    term, remainder = text[:colon + 1], text[colon + 1:]
    term_run = deepcopy(run)
    def_run = deepcopy(run) if remainder else None
    set_term_run(term_run, term)
    if def_run is not None:
        props = def_run.find(W + "rPr")
        if props is None:
            props = etree.Element(W + "rPr")
            def_run.insert(0, props)
        set_boolean(props, "b", False)
        set_boolean(props, "bCs", False)
        for child in list(def_run):
            if child is not props:
                def_run.remove(child)
        t = etree.SubElement(def_run, W + "t")
        t.text = remainder
        if remainder[:1].isspace():
            t.set(XML + "space", "preserve")
    return term_run, def_run


def format_term_paragraph(p):
    ppr = p.find(W + "pPr")
    if ppr is None:
        ppr = etree.Element(W + "pPr")
        p.insert(0, ppr)
    for name in ("keepLines", "widowControl", "spacing", "ind", "jc"):
        for node in ppr.findall(W + name):
            ppr.remove(node)
    keep = etree.Element(W + "keepLines")
    widow = etree.Element(W + "widowControl")
    spacing = etree.Element(W + "spacing")
    spacing.set(W + "before", "0")
    spacing.set(W + "after", "100")
    spacing.set(W + "line", "264")
    spacing.set(W + "lineRule", "auto")
    ind = etree.Element(W + "ind")
    ind.set(W + "left", "0")
    ind.set(W + "firstLine", "0")
    jc = etree.Element(W + "jc")
    jc.set(W + "val", "left")
    ppr.extend((keep, widow, spacing, ind, jc))

    direct_runs = p.findall(W + "r")
    label_run = None
    term_name = None
    for run in direct_runs:
        run_text = "".join(run.xpath("./w:t/text()", namespaces=NS))
        if ":" in run_text:
            term_run, def_run = split_term_run(run)
            if term_run is not None:
                index = p.index(run)
                p.remove(run)
                p.insert(index, term_run)
                if def_run is not None:
                    p.insert(index + 1, def_run)
                label_run = term_run
                term_name = term_run.xpath("string(w:t)", namespaces=NS)
                break
    if label_run is None:
        return None

    if term_name == "Baseline Frequency Range:":
        math_node = p.find("{http://schemas.openxmlformats.org/officeDocument/2006/math}oMath")
        if math_node is not None:
            space_run = etree.Element(W + "r")
            space_text = etree.SubElement(space_run, W + "t")
            space_text.set(XML + "space", "preserve")
            space_text.text = " "
            p.insert(p.index(math_node), space_run)

    after_label = False
    for child in p:
        if child is label_run:
            after_label = True
            continue
        if not after_label or child.tag != W + "r":
            continue
        props = child.find(W + "rPr")
        if props is None:
            props = etree.Element(W + "rPr")
            child.insert(0, props)
        set_boolean(props, "b", False)
        set_boolean(props, "bCs", False)
        for t in child.findall(W + "t"):
            if t.text:
                t.text = re.sub(r" {2,}", " ", t.text)
    return term_name


def set_page_break_before(p):
    ppr = p.find(W + "pPr")
    if ppr is None:
        ppr = etree.Element(W + "pPr")
        p.insert(0, ppr)
    if ppr.find(W + "pageBreakBefore") is None:
        page_break = etree.Element(W + "pageBreakBefore")
        keep_lines = ppr.find(W + "keepLines")
        if keep_lines is not None:
            ppr.insert(ppr.index(keep_lines) + 1, page_break)
        else:
            ppr.insert(0, page_break)


with ZipFile(DOCX, "r") as source:
    document = etree.fromstring(source.read("word/document.xml"))
    relationships = etree.fromstring(source.read("word/_rels/document.xml.rels"))
    rel_targets = {
        rel.get("Id"): rel.get("Target")
        for rel in relationships
        if rel.get("Id") and rel.get("Target")
    }
    body = document.find(".//" + W + "body")
    paragraphs = [p for p in body if p.tag == W + "p"]

    heading = next(i for i, p in enumerate(paragraphs)
                   if para_text(p).startswith("1.7 Definition of Terms"))
    glossary = []
    for p in paragraphs[heading + 1:]:
        text = para_text(p)
        if text.startswith("CHAPTER II"):
            break
        if ":" in text and not p.xpath(".//w:drawing", namespaces=NS):
            term = format_term_paragraph(p)
            if term:
                glossary.append(term)
                if term.startswith("MEMS IMU "):
                    set_page_break_before(p)

    heading_ppr = paragraphs[heading].find(W + "pPr")
    if heading_ppr is None:
        heading_ppr = etree.Element(W + "pPr")
        paragraphs[heading].insert(0, heading_ppr)
    if heading_ppr.find(W + "keepNext") is None:
        style = heading_ppr.find(W + "pStyle")
        index = heading_ppr.index(style) + 1 if style is not None else 0
        heading_ppr.insert(index, etree.Element(W + "keepNext"))

    media_replacements = {}
    image_shapes = []
    for i, p in enumerate(paragraphs):
        blips = p.xpath(".//a:blip", namespaces=NS)
        if not blips:
            continue
        caption = ""
        for candidate in paragraphs[i + 1:]:
            caption = para_text(candidate)
            if caption:
                break
        if caption.startswith("Figure 3.4."):
            asset = FLOW
            target_png = Image.open(FLOW)
            ratio = target_png.height / target_png.width
            for extent in p.xpath(".//wp:extent", namespaces=NS):
                cx = int(extent.get("cx"))
                extent.set("cy", str(round(cx * ratio)))
            for ext in p.xpath(".//a:xfrm/a:ext", namespaces=NS):
                cx = int(ext.get("cx"))
                ext.set("cy", str(round(cx * ratio)))
            image_shapes.append((caption, "resized to asset aspect ratio"))
        elif caption.startswith("Figure 3.5."):
            asset = FIELD
            target_png = Image.open(FIELD)
            ratio = target_png.height / target_png.width
            for extent in p.xpath(".//wp:extent", namespaces=NS):
                cx = int(extent.get("cx"))
                extent.set("cy", str(round(cx * ratio)))
            for ext in p.xpath(".//a:xfrm/a:ext", namespaces=NS):
                cx = int(ext.get("cx"))
                ext.set("cy", str(round(cx * ratio)))
            image_shapes.append((caption, "resized to monochrome asset aspect ratio"))
        else:
            continue
        rel_id = blips[0].get(R + "embed")
        target = rel_targets[rel_id]
        zip_name = posixpath.normpath(posixpath.join("word", target))
        media_replacements[zip_name] = asset.read_bytes()

    if len(glossary) != 14:
        raise RuntimeError(f"Expected 14 glossary terms; found {len(glossary)}: {glossary}")
    if len(media_replacements) != 2:
        raise RuntimeError(f"Expected two figure media replacements; got {media_replacements.keys()}")

    updated_xml = etree.tostring(
        document, xml_declaration=True, encoding="UTF-8", standalone=True
    )
    with ZipFile(OUTPUT, "w", compression=ZIP_DEFLATED) as result:
        for item in source.infolist():
            data = updated_xml if item.filename == "word/document.xml" else source.read(item.filename)
            if item.filename in media_replacements:
                data = media_replacements[item.filename]
            result.writestr(item, data)

with ZipFile(OUTPUT) as check:
    bad = check.testzip()
    if bad:
        raise RuntimeError(f"ZIP CRC error: {bad}")
    print("Glossary terms:", len(glossary))
    print("Labels:", "; ".join(glossary))
    print("Replaced image parts:", ", ".join(media_replacements))
    print("Figure handling:", image_shapes)
    print("DOCX output:", OUTPUT)
    print("Bytes:", OUTPUT.stat().st_size)
    print("SHA-256:", hashlib.sha256(OUTPUT.read_bytes()).hexdigest().upper())
