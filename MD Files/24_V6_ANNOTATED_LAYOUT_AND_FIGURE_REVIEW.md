# V6 annotated layout and figure review

Reviewed 2026-10-29. This is a layout and document-structure record for the separate V6 review candidate. It does not verify the research claims, citations, code, PCB, ethics, or field performance.

## Source, scope, and preservation

V6 was derived from V5, with V2 remaining the approved source of research intent. V2–V5 were preserved. The applied scope was limited to the user's four annotated V5 comments:

1. Remove the explanatory note beneath the IPO illustration and use only `Figure n.n. Description` captions throughout.
2. Set the complete Definition of Terms section to uniform 2.0 line spacing while retaining bold terms and regular-weight definitions. Leave the Abstract/Keywords formatting unchanged.
3. Enlarge and reflow Figure 3.4 process/decision blocks and route labels/connectors so text fits and branch direction is clear.
4. Enlarge/reflow Figure 3.5 in the same manner and remove the boxed note beneath its workflow.

No research prose, references, claims, methods, field results, firmware, PCB/CAD, or source data were intentionally changed. The static contents and table/figure lists were updated only to match Word's new pagination.

## Changes and acceptance results

| Item | Result | Evidence/status |
|---|---|---|
| Figure captions | All seven captions follow `Figure n.n. Description`; image/caption pairs are centered and ordered. | Verified structurally and against PDF text. No extra standalone caption material remains. |
| Figure 1.1 IPO | Removed the small explanatory note beneath the IPO blocks. | Cropped monochrome replacement is embedded. |
| Definition of Terms | All 14 entries use 2.0 line spacing, zero before/after spacing, keep-lines, bold labels, and regular meanings. | Verified in DOCX XML and at page scale. |
| Figure 3.4 firmware flow | Reworked box sizes, text wrapping, branch paths, and YES/NO placement. | Monochrome page inspected at 160 dpi (physical p. 49). No text extends outside blocks. |
| Figure 3.5 field workflow | Reworked block sizing/spacing and branch paths; removed the bottom note panel. | Monochrome page inspected at 160 dpi (physical p. 62). No text extends outside blocks. |
| Other figure treatments | Buntun Bridge map remains byte-identical and colored; schematic and PCB placeholder images remain blank white with black borders. IPO, Figure 3.1, and Figures 3.4–3.5 remain monochrome. | Image checks passed; original map and placeholders match V5 hashes. |
| Abstract and Keywords | Text and paragraph spacing remain identical to V5 and fit on one page. | Verified structurally and visually (physical p. 9). |
| Chapter/page layout | Chapter II starts on a separate page; Arabic pagination continues. | Chapter II is printed p. 14 / PDF p. 23; page number does not reset. |
| Lists and page references | Static contents, table list, and figure list locations match the final PDF. | Verified by extracted PDF text/page headers and visual inspection of front matter. |

## Pagination and glossary tradeoff

The 2.0 spacing requested for all glossary entries moves the final **Traffic-count group** definition to printed p. 13 by itself. Its text remains intact; Chapter II starts separately on printed p. 14. This extra glossary page was retained to meet the explicit uniform-spacing request without changing definition content, font size, margins, or chapter numbering. If the owner later prefers a more compact glossary, that requires a separate formatting/content decision.

## Final page map

Printed page / physical PDF page:

- Chapter I 1 / 10; Chapter II 14 / 23; Chapter III 32 / 41; Chapter IV 60 / 69; Chapter V 61 / 70; References 62 / 71.
- Figures 1.1 6 / 15; 1.2 10 / 19; 3.1 37 / 46; 3.2 and 3.3 38 / 47; 3.4 40 / 49; 3.5 53 / 62.
- Tables 1–4: printed pp. 36, 43, 46, and 48; physical PDF pp. 45, 52, 55, and 57.
- Abstract and Keywords remain on physical PDF p. 9.

## Verification evidence

- Microsoft Word 16.0.20326.20232 opened the V6 DOCX read-only, repaginated it, and exported the 80-page US Letter PDF. LibreOffice `soffice.exe` was unavailable, so the documents skill's normal renderer could not run; Word COM was the fallback.
- Poppler `pdftoppm` 26.07.0 rendered all 80 physical pages at 75 dpi. Four contact sheets covering the whole PDF were inspected. The following 21 pages were also rendered and inspected at 160 dpi: 5–9, 15, 19–23, 46–47, 49, 52, 55, 57, 62, and 69–71. Inkscape 1.4.2 generated the revised flowchart assets.
- The bundled Python 3.12.14 runtime, pypdf 6.10.0, lxml 6.1.1, and Pillow 12.3.0 ran `verification/verify_v6_layout.py`; it passed DOCX CRC, figure/caption sequence and centering, image color/placeholder checks, all 14 glossary formatting checks, abstract preservation, page maps, chapter starts, and static-list locations. The machine-readable record is `verification/v6_layout_verification_20261029.json`.
- A V5/V6 paragraph-text comparison found 56 changed paragraphs, all in the front-matter contents/table/figure lists and each differing only in its trailing page number; all other paragraph text matched. The verifier now enforces this limit.
- V5-to-V6 DOCX package comparison found exactly four changed package parts: `word/document.xml`, `word/media/image2.png`, `word/media/image7.png`, and `word/media/image8.png`.
- V6 DOCX SHA-256: `967330865C6980EF4F6C7BB6885EF8FEE13B0FD74268D615AF744C198A48C9FD` (1,929,249 bytes). V6 PDF SHA-256: `407F8CA20F24B4B8EA54705A4C6666F72C0103853E473A90B505BE8EDD8BE2B5` (1,478,744 bytes; 80 US Letter pages).

## Failed attempts retained

- `render_docx.py` could not start because `soffice.exe` was not installed. Word COM export and Poppler inspection succeeded as the fallback; the missing renderer is a tool limitation, not a document pass.
- The first V6 glossary assertion treated `<w:b w:val="0">` as bold and failed. The checker was corrected to interpret the explicit false value; the corrected verifier passed all 14 entries.
- An early flowchart PNG still had crowded branch labels/connectors. Page-scale inspection caught it before embedding; the SVG geometry was revised, regenerated, and re-inspected in the exported PDF.
- The first local Python invocations could not run the verifier (`py -3.12` was unavailable, and system Python 3.14.4 lacked `lxml`). The bundled workspace Python runtime had the required packages and ran the final verifier successfully.
- The initial V6 JSON inherited inaccurate 150/180 dpi labels from an earlier record. This was caught before handoff, corrected to the actual 75/160 dpi evidence, and the verifier reran successfully. The corrected JSON is the current record.
- Several patch attempts used stale context and made no file changes; the edits were reapplied against the current file contents. No deliverable content was lost.

## Limits and open status

This is a layout candidate, not an adviser-approved or submission-ready manuscript. No bibliography re-audit, claim-to-source verification, ethics/privacy determination, Turnitin or AI-writing review, site permission/safety approval, firmware build, CAD check, hardware test, or field-data validation was performed. The manuscript/firmware window-selection and valid-window conflicts remain open in the prior ledgers. The 75 dpi all-page review and 160 dpi targeted review support only the layout scope described above.
