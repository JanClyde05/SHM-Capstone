from __future__ import annotations

from hashlib import sha256
import os
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree


ROOT = Path(__file__).resolve().parents[2]
DOCX = ROOT / "Documents/The Real Research Paper/GPT Paper/SHM_Research_Aligned_Revision_Draft_v9.docx"
EXPECTED_BEFORE = "118C19F7FC4B344D9812B0A4C385C36E46C4BFBC508C2445EA1F576BCF1E6409"
PARAGRAPH_255 = (
    "Before collection, record each configuration field in Table 1 from the final board inspection, "
    "bench record, survey and site-approval record, frozen pilot protocol, or source-controlled "
    "software configuration. Mark unavailable values as pending; do not infer them from the "
    "schematic. The 3D view is a CAD preview with approximate MPU-6050 package models; it does "
    "not establish physical assembly or fit."
)
CELLS = {
    (1, 1): "One rigid board carrying the ESP32-S3 and three co-located MPU-6050 triaxial IMU ICs; record board revision, component markings, and channel identifiers.",
    (2, 1): "Poll and timestamp the three onboard channels sequentially; divide each fixed 600-second session into ten consecutive 60-second windows. Record the frozen analysis band, estimator/window settings, Arduino IDE and library versions, and measured per-channel sampling rate.",
    (6, 1): "Record session ID, date/time, total count and rate for the fixed 10-minute session, pilot-defined traffic group, weather, board station/orientation, raw-data fields, session-summary fields, and unusual events.",
}


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest().upper()


def text_in(element: etree._Element, ns: dict[str, str]) -> str:
    return "".join(element.xpath(".//w:t/text()", namespaces=ns))


def set_single_text(element: etree._Element, value: str, ns: dict[str, str]) -> None:
    nodes = element.xpath(".//w:t", namespaces=ns)
    if len(nodes) != 1:
        raise SystemExit(f"Expected one text node in target, found {len(nodes)}")
    nodes[0].text = value
    nodes[0].set("{http://www.w3.org/XML/1998/namespace}space", "preserve")


def main() -> None:
    actual = digest(DOCX)
    if actual != EXPECTED_BEFORE:
        raise SystemExit(f"Unexpected V9 input SHA-256: {actual}")

    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    temp = DOCX.with_suffix(".completeness.tmp.docx")
    with ZipFile(DOCX, "r") as src:
        bad = src.testzip()
        if bad:
            raise SystemExit(f"Input DOCX CRC failure at {bad}")
        parts = [(info, src.read(info.filename)) for info in src.infolist()]

    found_document = False
    for i, (info, data) in enumerate(parts):
        if info.filename != "word/document.xml":
            continue
        root = etree.fromstring(data)
        paras = root.xpath("//w:body/w:p", namespaces=ns)
        old_para = text_in(paras[255], ns)
        if "document each Table 1 value" not in old_para or "approximate MPU-6050 package models" not in old_para:
            raise SystemExit("Target configuration paragraph did not match the expected V9 text")
        set_single_text(paras[255], PARAGRAPH_255, ns)

        tables = root.xpath("//w:body/w:tbl", namespaces=ns)
        if not tables:
            raise SystemExit("Configuration table was not found")
        rows = tables[0].xpath("./w:tr", namespaces=ns)
        for (row_i, cell_i), replacement in CELLS.items():
            cell = rows[row_i].xpath("./w:tc", namespaces=ns)[cell_i]
            old_cell = text_in(cell, ns)
            if row_i == 1 and "record board revision and channel identifiers" not in old_cell:
                raise SystemExit("Table 1 PCB row did not match the expected text")
            if row_i == 2 and "Arduino IDE version, measured per-channel sampling rate, and FFT settings" not in old_cell:
                raise SystemExit("Table 1 ESP32-S3 row did not match the expected text")
            if row_i == 6 and "board station/orientation, and unusual events" not in old_cell:
                raise SystemExit("Table 1 Field log row did not match the expected text")
            set_single_text(cell, replacement, ns)

        parts[i] = (info, etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True))
        found_document = True
    if not found_document:
        raise SystemExit("word/document.xml was not found")

    with ZipFile(temp, "w", compression=ZIP_DEFLATED) as dst:
        for info, data in parts:
            dst.writestr(info, data)
    with ZipFile(temp, "r") as check:
        bad = check.testzip()
        if bad:
            temp.unlink(missing_ok=True)
            raise SystemExit(f"Output DOCX CRC failure at {bad}")
        root = etree.fromstring(check.read("word/document.xml"))
        paras = root.xpath("//w:body/w:p", namespaces=ns)
        assert text_in(paras[255], ns) == PARAGRAPH_255
        rows = root.xpath("//w:body/w:tbl", namespaces=ns)[0].xpath("./w:tr", namespaces=ns)
        for (row_i, cell_i), expected in CELLS.items():
            assert text_in(rows[row_i].xpath("./w:tc", namespaces=ns)[cell_i], ns) == expected
    os.replace(temp, DOCX)
    print("Updated configuration note and Table 1 cells at rows 1, 2, and 6, second column.")
    print(f"V9 DOCX SHA-256: {digest(DOCX)}")


if __name__ == "__main__":
    main()
