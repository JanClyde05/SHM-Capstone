# V5 annotated layout and figure review

Updated 2026-10-29. V5 is a separate review candidate derived from V4. V2 remains the approved research source; this visual/layout pass does not create adviser or institutional approval.

## Source and output identity

- Source V4 DOCX: `Documents/The Real Research Paper/GPT Paper/SHM_Research_Aligned_Revision_Draft_v4.docx`, SHA-256 `6CA3559D426DBC5B66F375402EAD771E166EC26E19096F74BE36BBAA02AF4190`.
- Source V4 PDF: `Documents/The Real Research Paper/GPT Paper/SHM_Research_Aligned_Revision_Draft_v4.pdf`, SHA-256 `B600026A2678F236CD11821A2A42C4DECA176A44A4B2BD145CDB2074459F3E0F`.
- V5 DOCX: `Documents/The Real Research Paper/GPT Paper/SHM_Research_Aligned_Revision_Draft_v5.docx`, 1,968,722 bytes, SHA-256 `43D260EC5C1156BE2CC44C1D984651E77CF8676F92E47F814F7B081C01915759`.
- V5 PDF: `Documents/The Real Research Paper/GPT Paper/SHM_Research_Aligned_Revision_Draft_v5.pdf`, 1,393,493 bytes, SHA-256 `26F744DAA298C87567B3D54E2CBDC3210FF8A76CE1BCE37CFD213E946CE6F273`, 79 US Letter pages.

The V4 DOCX/PDF hashes rechecked unchanged. The V5 bibliography and research prose were carried forward; this pass did not re-verify their claims or references.

## Corrections applied

1. **Abstract and Keywords (PDF p. 9; printed Roman p. ix).** Set 1.35 line spacing and 4 pt after the abstract so the complete abstract and Keywords remain together on one page and use the page more evenly.
2. **Definition of Terms (PDF pp. 20–21; printed pp. 11–12).** Set 1.5 line spacing with 5 pt after each of the 14 entries, retained bold term labels with regular-weight meanings, kept each entry together, and removed the forced page break before MEMS IMU. Chapter II still starts on its own printed page 13; Arabic numbering remains continuous.
3. **Figures 3.4 and 3.5.** Rebuilt both as black-and-white diagrams. Enlarged and reflowed decision/outcome blocks, moved YES/NO labels away from text and connector lines, gave branch arrows visible tails and heads, and split an overlong Figure 3.5 process label into three lines. The diagrams retain their figure numbers and the Figure 3.5 reference to Figure 3.4.
4. **Figure list.** Updated the static Figure 3.4 List of Figures title to match its caption. All seven figure captions and their printed page locations were checked.

Figure 1.1 IPO and Figure 3.1 system data path remain monochrome. Figure 1.2 keeps the colored map. Figures 3.2 and 3.3 remain blank white placeholders with black borders. Images and captions for all seven figures are centered. The actual schematic and PCB files were not changed.

## Final page map

| Item | Printed page | PDF page |
|---|---:|---:|
| Abstract and Keywords | ix | 9 |
| Chapter I | 1 | 10 |
| Figure 1.1 | 6 | 15 |
| Figure 1.2 | 10 | 19 |
| Chapter II | 13 | 22 |
| Chapter III | 31 | 40 |
| Figure 3.1 | 36 | 45 |
| Figures 3.2 and 3.3 | 37 | 46 |
| Figure 3.4 | 39 | 48 |
| Figure 3.5 | 52 | 61 |
| Chapter IV | 59 | 68 |
| Chapter V | 60 | 69 |
| References | 61 | 70 |

The List of Figures on Roman page viii gives Figures 1.1/1.2/3.1/3.2/3.3/3.4/3.5 as pages 6/10/36/37/37/39/52. The List of Tables on Roman page vii matches Tables 1–4 at pages 35/42/45/47.

## Verification record

Microsoft Word 16.0 repaginated and exported V5. `pdfinfo` 26.07.0 reports 79 pages at 612 × 792 points. Python 3.12.14, pypdf 6.10.0, lxml, and Pillow ran `MD Files/verification/verify_v5_layout.py`; its CRC, centered image/caption pair, figure numbering/list, color, placeholder, glossary, abstract, chapter, table-list, and page-map checks passed. Inkscape 1.4.2 regenerated the two flowchart PNGs. Physical PDF pages 9, 15, 19, 20, 21, 22, 45, 46, 48, and 61 were rendered at 150 dpi; pages 7, 8, 48, and 61 were additionally rendered at 180 dpi and visually inspected, with detail crops of the right panels in both flowcharts. The 180-dpi List of Tables render is retained at `verification/v5_page7_list_review.png`.

Current generated-media hashes are recorded in `MD Files/verification/v5_layout_verification_20261029.json`. The evidence establishes package integrity and the checked page/layout properties, not correctness of every thesis claim.

## Mistakes and failed checks retained

- The first SVG export scaled arrowheads excessively because SVG's default marker scaling was left in place. `markerUnits="userSpaceOnUse"` corrected it; the diagrams were regenerated and visually checked.
- The first 1.5-spaced abstract moved Keywords onto an otherwise empty page, while double-spacing the glossary left its final entry alone on a third page. A revised spacing pass returned the PDF to 79 pages; the abstract/Keywords now share PDF p. 9 and the glossary occupies two pages.
- The first caption verifier counted a List of Figures heading and an explanatory “Figure 3.4 maps…” paragraph as captions. Its check now matches only the seven expected figure-number prefixes. A separate cross-reference check looked in narrative text even though the cross-reference is inside the Figure 3.5 graphic; it now checks the source SVG.
- The first placeholder assertion assumed the black frame touched the raster's outermost edge; the actual frame is inset four pixels. The check now measures the non-white frame bounds before sampling the black top/left border and white center.
- Page-scale inspection caught the Figure 3.5 processing label extending beyond its block. The text was split and the figure was regenerated/re-embedded before the final Word export.
- The Figure 3.4 List of Figures title had not been synced to its full caption; the V5 list entry now matches the caption and page number.
- An earlier verification note overstated visual review of the static lists. PDF p. 7 was rendered at 180 dpi and visually inspected; the evidence record now distinguishes that visual check from the separate text/page-map checks.

All substantive V5 layout mistakes, the correction record, and next-time rules are retained in `22_AI_FEEDBACK_AND_MISTAKE_LOG.md` (IDs M-2026-10-29-08 through M-2026-10-29-14). Direct user preferences are kept in its preference section; those are project reference notes, not model training.

Mistake IDs, detection, impacts, corrections, and next-time rules are in `MD Files/22_AI_FEEDBACK_AND_MISTAKE_LOG.md`. The task-level proposal and final verification are in `MD Files/09_VERIFICATION_LEDGER.md`.

## Open gates

No full-text reference audit, citation-to-claim review, ethics or privacy determination, Turnitin review, AI-writing review, site or safety approval, firmware build, CAD check, physical hardware test, field-data collection, or adviser sign-off occurred in this layout pass. The existing manuscript/firmware conflicts about window selection and the valid-window threshold remain open. V5 is a layout review candidate, not a 100%-verified or submission-ready thesis.
