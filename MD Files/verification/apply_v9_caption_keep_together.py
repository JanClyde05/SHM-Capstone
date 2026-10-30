from __future__ import annotations

from hashlib import sha256
import os
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree


ROOT = Path(__file__).resolve().parents[2]
DOCX = ROOT / "Documents/The Real Research Paper/GPT Paper/SHM_Research_Aligned_Revision_Draft_v9.docx"
EXPECTED_BEFORE = "060BCA6C5B277E7E58C4FCB8AAF920EB3A5D6AB71A88A70C4BC4F0433196780C"
TARGET_CAPTION = "Table 1. Required documentation of the final monitoring-system configuration"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    before = digest(DOCX)
    if before != EXPECTED_BEFORE:
        raise SystemExit(f"Unexpected V9 input SHA-256: {before}")
    temp = DOCX.with_suffix(".caption.tmp.docx")
    with ZipFile(DOCX, "r") as src:
        bad = src.testzip()
        if bad:
            raise SystemExit(f"Input CRC error: {bad}")
        parts = [(info, src.read(info.filename)) for info in src.infolist()]

    updated = False
    for idx, (info, data) in enumerate(parts):
        if info.filename != "word/document.xml":
            continue
        root = etree.fromstring(data)
        paras = root.xpath("//w:body/w:p", namespaces=NS)
        caption = paras[256]
        text = "".join(caption.xpath(".//w:t/text()", namespaces=NS))
        if text != TARGET_CAPTION:
            raise SystemExit(f"Unexpected Table 1 caption at paragraph 256: {text!r}")
        spacer = paras[257]
        if "".join(spacer.xpath(".//w:t/text()", namespaces=NS)).strip():
            raise SystemExit("Expected the immediately following paragraph to be the blank table spacer")
        ppr = caption.find("w:pPr", NS)
        if ppr is None:
            ppr = etree.Element(f"{{{W}}}pPr")
            caption.insert(0, ppr)
        if not ppr.xpath("./w:keepNext", namespaces=NS):
            ppr.insert(0, etree.Element(f"{{{W}}}keepNext"))
        if not spacer.xpath("./w:pPr/w:keepNext", namespaces=NS):
            raise SystemExit("Expected the blank spacer already to keep with the following table")
        parts[idx] = (info, etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True))
        updated = True
    if not updated:
        raise SystemExit("word/document.xml was not found")

    with ZipFile(temp, "w", compression=ZIP_DEFLATED) as dst:
        for info, data in parts:
            dst.writestr(info, data)
    with ZipFile(temp, "r") as check:
        bad = check.testzip()
        if bad:
            temp.unlink(missing_ok=True)
            raise SystemExit(f"Output CRC error: {bad}")
        root = etree.fromstring(check.read("word/document.xml"))
        paras = root.xpath("//w:body/w:p", namespaces=NS)
        assert paras[256].xpath("./w:pPr/w:keepNext", namespaces=NS)
        assert "".join(paras[256].xpath(".//w:t/text()", namespaces=NS)) == TARGET_CAPTION
    os.replace(temp, DOCX)
    print(f"Added keep-with-next to Table 1 caption paragraph 256; V9 SHA-256 {digest(DOCX)}")


if __name__ == "__main__":
    main()
