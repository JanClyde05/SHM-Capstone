# V4 figure assets and color policy

Updated 2026-10-29 for the V4 layout pass. The active figure set is embedded in `Documents/The Real Research Paper/GPT Paper/SHM_Research_Aligned_Revision_Draft_v4.docx` and was checked in its Word-rendered PDF.

## Active appearance

- Figure 1.1 IPO: simplified black and white.
- Figure 1.2 Buntun Bridge location map: original color restored from approved V2's `word/media/image3.png` (1280 × 679; 258,994 bytes). The red location marker is preserved.
- Figure 3.1 system block diagram: simplified black and white.
- Figure 3.2 device schematic: blank white image with a black border; placeholder only.
- Figure 3.3 PCB layout: blank white image with a black border; placeholder only.
- Figure 3.4 firmware code flowchart: simplified black and white and retained as an actual flowchart.
- Figure 3.5 field-data workflow: simplified black and white, redrawn as a two-panel process flow with separate process steps and labeled A/B continuation connectors. The active asset is `figure_3_5_field_workflow_bw.png`. The prior colored V3 source is retained as `figure_3_3_field_workflow_color_restored.png` for provenance, not embedded in the current V4.

The image paragraphs and corresponding figure captions are centered in V4. The separate `placeholders/placeholder_code_flowchart.png` is a reusable blank frame for later replacement; it is not embedded over the actual code flowchart. The device-schematic and PCB-layout placeholders are embedded in V4. `generate_field_workflow_bw.py` creates the active Figure 3.5 SVG and PNG. `generate_review_figures.py` is retained for provenance; its old field assets are suffixed `_legacy` and must not be used in V4. The KiCad schematic, board, and project files were not changed; the placeholders do not represent verified designs or layouts.

`verify_v4_comment_fixes.py` checks glossary label/definition weights, page-break marker, figure alignment, figure color mode, and DOCX ZIP integrity. See `MD Files/09_VERIFICATION_LEDGER.md` and `MD Files/21_V4_VISUAL_RRL_AND_OBJECTIVE_REVIEW.md` for final page map, hashes, rendered checks, and open limitations.
