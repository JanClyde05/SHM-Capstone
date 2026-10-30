from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import hashlib
import os

from lxml import etree


ROOT = Path(__file__).resolve().parents[2]
DOCX = ROOT / "Documents/The Real Research Paper/GPT Paper/SHM_Research_Aligned_Revision_Draft_v9.docx"
EXPECTED_BEFORE = "E5DF5DA7DF0659B70DE7FED82662A3E7CBE035F6F40EC97599701CF9FAD54C72"
REPLACEMENT = (
    "Before collection, document each Table 1 value from the final board inspection, bench record, "
    "survey and site-approval record, frozen pilot protocol, or source-controlled software "
    "configuration. Mark unavailable values as pending; do not infer them from the schematic. The "
    "3D view is a CAD preview with approximate MPU-6050 package models; it does not establish "
    "physical assembly or fit."
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    before = sha256(DOCX)
    if before != EXPECTED_BEFORE:
        raise SystemExit(f"Unexpected V9 input SHA-256: {before}")

    temp = DOCX.with_suffix(".reflow.tmp.docx")
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with ZipFile(DOCX, "r") as src:
        bad = src.testzip()
        if bad:
            raise SystemExit(f"Input DOCX CRC failure at {bad}")
        parts = [(info, src.read(info.filename)) for info in src.infolist()]

    updated = False
    out_parts: list[tuple[object, bytes]] = []
    for info, data in parts:
        if info.filename != "word/document.xml":
            out_parts.append((info, data))
            continue
        root = etree.fromstring(data)
        paras = root.xpath("//w:body/w:p", namespaces=ns)
        p = paras[255]
        old = "".join(p.xpath(".//w:t/text()", namespaces=ns))
        if not ("The 3D rendering is a CAD preview" in old or "The 3D view is a CAD preview" in old):
            raise SystemExit("Expected configuration/caveat paragraph not found at index 255")
        runs = p.xpath(".//w:r[w:t]", namespaces=ns)
        if len(runs) != 1:
            raise SystemExit(f"Expected one text run in target paragraph, found {len(runs)}")
        text_nodes = runs[0].xpath("./w:t", namespaces=ns)
        if len(text_nodes) != 1:
            raise SystemExit(f"Expected one text node in target run, found {len(text_nodes)}")
        text_nodes[0].text = REPLACEMENT
        text_nodes[0].set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        out_parts.append((info, etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)))
        updated = True

    if not updated:
        raise SystemExit("word/document.xml was not located")
    with ZipFile(temp, "w", compression=ZIP_DEFLATED) as dst:
        for info, data in out_parts:
            dst.writestr(info, data)
    with ZipFile(temp, "r") as check:
        bad = check.testzip()
        if bad:
            temp.unlink(missing_ok=True)
            raise SystemExit(f"Output DOCX CRC failure at {bad}")
        out_root = etree.fromstring(check.read("word/document.xml"))
        paras = out_root.xpath("//w:body/w:p", namespaces=ns)
        actual = "".join(paras[255].xpath(".//w:t/text()", namespaces=ns))
        if actual != REPLACEMENT:
            temp.unlink(missing_ok=True)
            raise SystemExit("Output paragraph text verification failed")
    os.replace(temp, DOCX)
    print(f"Updated paragraph 255; chars {len(old)} -> {len(REPLACEMENT)}")
    print(f"V9 DOCX SHA-256: {sha256(DOCX)}")


if __name__ == "__main__":
    main()
