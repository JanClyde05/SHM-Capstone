# AI feedback, preferences, and mistake/fix log

This file preserves project-relevant user preferences and lessons from AI work so future sessions can retrieve them. It is a project memory aid; it does not retrain a model or guarantee error-free work. The current user request always takes precedence.

## How future sessions should use this log

- Read this file before work that changes a project artifact. Confirm that a preference still fits the current request; a newer direct user instruction overrides an older one.
- Keep **direct user instructions** separate from **inferences**. The preferences below are direct, project-specific instructions. Do not promote an inference or one-off choice into a permanent user preference without evidence.
- After each task, log every known substantive mistake or failed verification attempt that affected an artifact, path, claim, calculation, decision, or evidence record. Include mistakes caught before delivery if they informed a correction. Do not hide a failed check just because the rerun passed.
- For each event, record what was wrong, how it was detected, impact, correction, rerun evidence, whether the root cause is known, and the next-time rule. Mark unresolved causes honestly. Preserve earlier entries; add a correction/superseding entry instead of rewriting history.
- Record only project-relevant preferences and lessons. Avoid storing unrelated personal details or duplicating sensitive source material. Keep identities and claims tied to the project evidence records.
- Append new entries with a date and an ID. Update `00_README.md` and the project inventory when files or current guidance change.

## User preferences — direct instructions

| ID | Preference | Application |
|---|---|---|
| P-01 | The user wants an evidence-first workflow: map the project, identify the problem and affected parts, research and verify material claims, log the plan and evidence, make authorized changes, then remap and verify. | Trace paper statements to sources, code, PCB, and data where relevant. Label unknowns; do not turn unsupported claims into requirements. “100% verified” is not a defensible promise; make provenance and limits auditable. |
| P-02 | The user wants careful, clean revisions that do not damage the research or lose historical material. | Preserve approved V2 and prior candidates unless explicitly asked otherwise. Prefer narrow edits, retain provenance, and visually check document layout after edits. |
| P-03 | The user wants a large Chapter II literature base (at least 100 references) and prioritizes unanswered questions, weak sources, and claims without evidence. | Add no citation by count alone. Verify metadata and claim support, state access limits, and keep citations attached to the specific supported claim. |
| P-04 | For document visuals, the user prefers simple black-and-white, e-ink-like styling without decorative color, and centered figures. | Keep the IPO, block diagrams, firmware flowchart, and, after the later annotated comment, the field workflow monochrome. Preserve the Buntun Bridge map's original color. Preserve original colors in actual schematic/PCB design visuals; when only placeholders exist, use blank white frames with black borders. Center figures and captions. Do not apply monochrome indiscriminately to unrelated visuals. |
| P-05 | In Definition of Terms, the user wants the term labels bold while the definitions remain regular-weight, with consistent spacing. Chapters should start on separate pages while main page numbering remains continuous. | Check the entire glossary, not just the marked paragraph. Verify the rendered pages and confirm a new chapter page does not reset numbering. |
| P-06 | For block diagrams and flowcharts, the user wants one process per block, clear arrow direction, visible arrowheads, correct branch/loop placement, and no overlapping lines or blocks. | Render at page scale and inspect the affected regions; do not rely only on the source SVG or DOCX structure. |
| P-07 | The user expects authorized work to proceed through a reviewable result with logging, without repeated unnecessary confirmation requests. | Resolve routine implementation choices independently. Ask only when a genuine owner, institutional, safety, or data decision blocks the dependent action. |
| P-08 | The user explicitly wants future sessions to log mistakes, fixes, and their project preferences so the next AI can use that history. | Maintain this file as persistent project context and update the reusable instructions. Explain that the log improves retrieval/continuity but does not literally train the model. |
| P-11 | For marked layout corrections, spacing should use the page well without stranding Keywords or a glossary item on an almost empty page. Keep definition labels bold and meanings regular; place YES/NO labels clear of arrows and blocks, with visible arrow direction. | Tune spacing after Word pagination, allow complete glossary entries to flow naturally, and inspect diagrams at both source and final page scale. |
| P-12 | Figure captions should contain only the figure number and description; explanatory callout boxes should not be added as caption-like material. Keep all Definition of Terms entries at uniform 2.0 line spacing when requested, with term labels bold and meanings regular. Flowchart blocks should contain their text without spillover, and branch arrows/YES/NO labels should be clear and separated. | Apply to all figures and glossary entries in future revisions. If 2.0 spacing forces a glossary item onto an additional page, preserve the wording and record the pagination tradeoff rather than silently changing spacing. |

## Mistakes and fixes

### M-2026-10-29-01 — First field-flow draft had crowded routing

- **What happened:** The initial Figure 3.5 SVG draft placed some decision labels too close to branch arrows and the rejection-loop connector. The first render showed labels and paths crowding the diamonds and a continuation connector too close to adjacent process boxes.
- **Detection/impact:** Visual inspection of the generated PNG caught the layout issue before it was embedded in the final V4. No user deliverable was finalized from that draft.
- **Correction:** Reworked the decision labels and diamond widths, moved the A connector, routed branch paths outside process boxes, and regenerated the monochrome SVG/PNG. Rendered final physical PDF page 61 at 160 dpi and checked the image/caption fit.
- **Status/root cause:** Corrected and visually rechecked. Root cause was layout geometry, not research content.
- **Next-time rule:** Inspect a diagram at both full asset resolution and final page scale; validate branches and arrow endpoints before embedding.

### M-2026-10-29-02 — Field-workflow asset used an obsolete figure number

- **What happened:** The first generated black-and-white Figure 3.5 PNG was named `figure_3_3_field_workflow_bw.png`, reflecting an earlier figure sequence, although the current manuscript labels it Figure 3.5.
- **Detection/impact:** A filename/reference search found the mismatch before final handoff. The manuscript caption itself was correctly numbered.
- **Correction:** Renamed the active PNG and SVG to `figure_3_5_field_workflow_bw.*`, updated the generation and DOCX-application scripts, and verified the embedded Figure 3.5 media hash against the active PNG.
- **Status/root cause:** Corrected. The mismatch came from a stale pre-placeholder filename.
- **Next-time rule:** Check figure asset names against current captions and static lists after renumbering.

### M-2026-10-29-03 — Legacy generator could overwrite the active field asset

- **What happened:** The older combined `generate_review_figures.py` still contained a thresholded field-workflow export and an earlier field SVG layout. Running it could overwrite active Figure 3.5 assets with stale output.
- **Detection/impact:** Inspection of generator outputs during the final asset rename exposed the collision. It was corrected before a future rerun could replace the active figure.
- **Correction:** Marked the combined script as legacy and changed its old field PNG/SVG outputs to `_legacy` filenames. The active Figure 3.5 is generated by `generate_field_workflow_bw.py`.
- **Status/root cause:** Corrected; documented in `figures_v4/README.md`.
- **Next-time rule:** When replacing an asset-generation path, search for all scripts that write the same output path and remove or isolate stale writers.

### M-2026-10-29-04 — First verifier mishandled Pillow color-count tuples

- **What happened:** A one-off structural verification script unpacked `PIL.Image.getcolors()` results as `(color, count)`, but Pillow returns `(count, color)`. The check stopped with a `TypeError` before producing a result.
- **Detection/impact:** The exception occurred during QA; it was a checker defect, not evidence of a document defect.
- **Correction:** Fixed the tuple order in the persistent `verify_v4_comment_fixes.py` checker and reran it successfully. It confirmed the field/code-flow images contain no chromatic pixels and the map retains color.
- **Status/root cause:** Corrected; rerun passed.
- **Next-time rule:** Confirm third-party return shapes in the installed library/version before building assertions around them.

### M-2026-10-29-05 — Temporary figure-alignment assertion gave an inconclusive failure

- **What happened:** An early temporary verifier stopped on a Figure 1.2 caption assertion. A focused XML probe then showed the map image and caption both had centered alignment; the final dedicated verifier passed for the map, code-flow, and field-flow figures.
- **Detection/impact:** This was a verification-script failure, not a confirmed document defect. The exact cause in the temporary script was not isolated, so it must not be described as a confirmed false positive with a known root cause.
- **Correction:** Replaced the temporary probe with the persistent `verify_v4_comment_fixes.py` and reran all relevant checks successfully.
- **Status/root cause:** Artifact check passed; temporary checker root cause remains unisolated.
- **Next-time rule:** When an assertion conflicts with a focused inspection, preserve the failed output, isolate the predicate, and report the checker and artifact statuses separately.

### M-2026-10-29-06 — Inventory snapshot was stale

- **What happened:** The prior inventory stated 426 files. A fresh recursive scan after recent project additions found 433 files and the same 82 directories.
- **Detection/impact:** The old count no longer described the current repository. No project files were lost or altered by the scan.
- **Correction:** Regenerated `13_PROJECT_FILE_INVENTORY.md` from the project root; the latest record lists 433 files.
- **Status/root cause:** Corrected; older snapshots remain historical records.
- **Next-time rule:** Recompute the inventory after adding or renaming project files instead of carrying forward a previous count.

### M-2026-10-29-07 — Two documentation paths were guessed incorrectly

- **What happened:** During inspection, two assumed Markdown paths did not exist. The actual project files were `15_PAPER_REVIEW_AND_INTEGRITY_GATES.md` and `21_V4_VISUAL_RRL_AND_OBJECTIVE_REVIEW.md`.
- **Detection/impact:** File reads failed; no project content was modified by the failed lookup.
- **Correction:** Listed actual Markdown paths with `rg --files` and read the existing records.
- **Status/root cause:** Corrected; navigation-only issue.
- **Next-time rule:** Resolve filenames through the project index or `rg --files` before relying on remembered or guessed names.

## Current task reference

The 2026-10-29 V4 annotated-comment correction is recorded in `09_VERIFICATION_LEDGER.md` and `21_V4_VISUAL_RRL_AND_OBJECTIVE_REVIEW.md`. Final V4 hashes and render/structural evidence are in those files. The V4 visual corrections did not re-verify research citations, ethics, Turnitin, or institutional approval.

## V5 annotated-layout task reference

The latest V5 layout comments, final candidate hashes, page map, and check limits are in `09_VERIFICATION_LEDGER.md` and `23_V5_ANNOTATED_LAYOUT_AND_FIGURE_REVIEW.md`. Machine-readable checks are in `verification/v5_layout_verification_20261029.json`; scripts/assets are in `figures_v5/`. V2 remains the approved source. V5 did not re-audit literature, ethics/privacy, or institutional review.


## PCB continuation: direct preferences and mistakes (2026-10-29)

**P-09 (direct):** The intended old PCB is the root `Thesis/SHM_PCB_New/SHM_PCB_New.kicad_pcb` and matching schematic, as the owner corrected on October 28. Parent `Thesis` and nested `SHM_Proto_PCB` are not substitutes. **P-10 (direct):** Before continuing implementation, leave a comprehensive plan, instructions, references and exact continuation status for other AI sessions. The hardware plan is `PCB Files/GPT Build - PCB/docs/CONTINUATION_PLAN.md`.

### M-2026-10-29-PCB-01 — Wrong old board selected

The assistant selected the larger parent Thesis outline (approximately 83.6 x 83.1 mm), despite the intended old reference being the compact SHM_PCB_New project (79.50 x 50.45 mm centerline). The user identified the error. Impact: placement/routing and the old clean CAD checks do not satisfy the corrected shape request. Cause: choosing a different historical board for available space without resolving reference identity. Correction: preserve the old work in `archive/20261028_before_reference_correction.zip`, record the owner's exact path/hashes, and rebuild a separate compact candidate. Exact 12-edge copying is implemented; final geometry/net/DRC acceptance remains pending. Next time: bind reference path and hash before geometry selection; do not silently replace a user reference because another one is easier.

### M-2026-10-29-PCB-02 — KiCad footprint Flip crashed generation

The compact generator called Flip on an unattached footprint using a boolean argument. Python exited with access violation before saving a board; `reports/build_corrected_trace.log` localizes the failure. Correction: add the footprint to the board first and pass `FLIP_DIRECTION_LEFT_RIGHT`. Rerun saved the compact placement. Both changes were made together, so their individual causal contribution was not isolated. Next time: use the installed API enum and valid board ownership before geometry operations.

### M-2026-10-29-PCB-03 — Compact placement failed rule checks

First compact placement reported 4 courtyard overlaps and 2 copper-edge errors, plus silk warnings. Moving connector/support parts removed the edge errors and two overlaps. The next actual report still has J2/SW2 and H1/SW1 courtyard overlaps; preroute has 2 errors, 21 warnings and 113 unconnected items. This is incomplete routing, not a final pass. Failed snapshots are retained under `reports/reference_corrected/failed_before_20261029_plan_*`. Next time: clear component/fastener placement errors before spending time on autorouting, and retain each report before overwrite.

### M-2026-10-29-PCB-04 — Silent optional USB preparation

Inspection found prepare_corrected_routing.py conditionally skipped route_corrected_usb.py when absent. The missing script means USB preparation has not been completed. No complete-USB claim is justified. Cause: an optional import was used while a separately assigned script was unfinished. The continuation plan explicitly blocks routing acceptance until that step exists or a reviewed alternative is supplied. Next time: fail explicitly for required generated inputs rather than silently skip them.

### M-2026-10-29-PCB-03 follow-up — Placement conflicts cleared

Moved J2 and H1 as logged in MD09. `preroute_placement_fixed.json` reports zero active errors, 22 silkscreen warnings and 113 unconnected items. The previous two courtyard errors are corrected; remaining silk/routing work is not waived.

### M-2026-10-29-PCB-05 — Bypass orientation contradicted generator comment

Inspection showed pad1 on the VLOGIC/REGOUT/CPOUT bypass capacitors faced away from the MPU pins, despite the generator comment claiming inward-facing pads. Net assignments were correct; this caused unnecessarily long local connections. The compact generator rotations were corrected (-90 degrees for VLOGIC/REGOUT, +90 for CPOUT). Regeneration and post-change checks are pending at this checkpoint. Next-time rule: derive actual transformed pad coordinates instead of assuming a rotation's meaning from visual placement or comments.

## V5 annotated-layout mistakes and fixes (2026-10-29)

### M-2026-10-29-08 — SVG arrowheads and first branch layout were too crowded

- **What happened:** The initial SVG render used the default marker scaling, which produced oversized arrowheads. After that fix, first flowchart renders still placed some YES/NO labels too close to decision edges, and outcome text was wider than its block.
- **Detection/impact:** Source PNG review and final PDF page/crop review caught these issues before V5 handoff; no source research or firmware was changed.
- **Correction:** Set `markerUnits="userSpaceOnUse"`, adjusted diamond/outcome widths and connector endpoints, moved labels clear of the branch lines, and regenerated both figures. Final Word pages 48 and 61 were reviewed at 150/180 dpi.
- **Status/root cause:** Corrected. The first issue came from SVG default marker units; remaining crowding came from tight geometry at the target page width.
- **Next-time rule:** Render at the intended document width before treating an SVG as final; inspect arrowheads, decision labels, block text, and arrow tails in both the source PNG and Word-exported page.

### M-2026-10-29-09 — Initial spacing choice stranded content

- **What happened:** The first layout used 1.5 spacing for the abstract and double spacing for definitions. Word moved Keywords onto a nearly empty second abstract page and moved the last glossary entry to a third page.
- **Detection/impact:** The 81-page Word export and pages 9–10 and 21–23 made the pagination problem visible; this did not alter research text.
- **Correction:** Set the abstract/Keywords to 1.35 spacing with 4 pt after the abstract, and the 14 glossary entries to 1.5 spacing with 5 pt after. The final Word export returned to 79 pages; abstract and Keywords share PDF p. 9; the glossary flows across printed pp. 11–12; Chapter II starts on printed p. 13.
- **Status/root cause:** Corrected. The initial spacing values were chosen before checking how the actual Word template paginated.
- **Next-time rule:** Measure spacing decisions in Word's rendered output; do not infer page fit from paragraph XML or estimated line counts.

### M-2026-10-29-10 — V5 verifier used the wrong caption and cross-reference scope

- **What happened:** The first caption check treated every paragraph starting with “Figure” as a caption, including the List of Figures header and a Figure 3.4 implementation note. A separate cross-reference check expected “using Figure 3.4” in narrative prose although the reference appears inside the Figure 3.5 image.
- **Detection/impact:** The candidate build stopped on false structural assertions. Investigation showed seven actual captions and the cross-reference in the SVG; these failures were verifier defects, not missing paper captions.
- **Correction:** Restrict caption matching to the seven exact expected number prefixes; check Figure 3.4 in the Figure 3.5 SVG source. The candidate rebuilt, passed DOCX ZIP CRC, and the final verifier passed.
- **Status/root cause:** Corrected; the failed checks and their rerun are retained here and in `23`.
- **Next-time rule:** Validate what each assertion targets against the actual document structure (caption, list row, explanatory note, or embedded diagram) before using it as a hard gate.

### M-2026-10-29-11 — Placeholder verifier assumed the border touched the image edge

- **What happened:** The first placeholder-frame assertion sampled the outermost raster pixel, but the black border is inset four pixels around a white canvas.
- **Detection/impact:** The verifier failed even though visual inspection showed a blank white rectangle with a black border. No document edit was needed for the placeholders.
- **Correction:** Measure the non-white bounding box first, then sample its top/left border and the white center. Rerun confirmed Figures 3.2 and 3.3 pass the structural image check.
- **Status/root cause:** Corrected; the failure was an inaccurate test assumption.
- **Next-time rule:** Use measured visual bounds rather than assuming borders touch the raster edge.

### M-2026-10-29-12 — Figure 3.5 process label exceeded its block

- **What happened:** At final document scale, “Process each channel-axis window” protruded beyond the Figure 3.5 process rectangle.
- **Detection/impact:** An enlarged crop from PDF p. 61 showed the text was wider than the block, violating the user's no-overlap requirement.
- **Correction:** Split it into “Process each / channel-axis window / using Figure 3.4,” regenerated the PNG, rebuilt the DOCX, re-exported Word's PDF, and re-inspected p. 61.
- **Status/root cause:** Corrected; long line length was not assessed at the embedded 5.95-inch display width on the first draft.
- **Next-time rule:** Check every long diagram label at the target print width and wrap it before finalizing.

### M-2026-10-29-13 — Figure 3.4 List of Figures title was stale

- **What happened:** The V4 List of Figures shortened Figure 3.4's caption to “Current Firmware Session-Control Flowchart,” while the actual caption also named window processing.
- **Detection/impact:** Comparison of the rendered caption with the static list found a title mismatch; the page number itself was correct.
- **Correction:** Updated only the V5 List of Figures title to match the full caption and re-rendered Roman p. viii. It remained on one page and still lists printed p. 39.
- **Status/root cause:** Corrected; the list text had not been synced after the diagram caption changed.
- **Next-time rule:** Compare each static list title and page against its final rendered caption after figure edits.

### M-2026-10-29-14 — V5 list-page visual review was initially incomplete

- **What happened:** The first final verification record said both lists had been visually reviewed, but only the List of Figures page had a retained 180-dpi render; the List of Tables had only been checked by extracted text and page-map comparison.
- **Detection/impact:** A final evidence audit found the mismatch between the stated visual-review scope and the retained renders. The List of Tables page was not shown to have a layout defect, but the record overstated what had been visually inspected.
- **Correction:** Rendered PDF p. 7 (printed Roman p. vii) at 180 dpi and visually inspected its heading, column headers, four table rows, leaders, page numbers, margins, and footer. The page is legible and its listed pages match the table captions. Updated the verification ledger and V5 review report to name the render.
- **Status/root cause:** Closed. The process treated textual page-map verification as equivalent to visual list-page review.
- **Next-time rule:** For every claimed visual review, retain and inspect a render of each cited page; distinguish extracted-text checks from visual checks in the evidence log.

## V6 annotated-layout mistakes and fixes (2026-10-29)

### M-2026-10-29-15 — First V6 flowchart geometry remained crowded

- **What happened:** The first V6 redraw enlarged several blocks, but some branch labels and connector paths remained crowded at page scale.
- **Detection/impact:** Inspection of the generated PNGs caught the issue before those images were embedded in V6. No manuscript source content or firmware was changed by the failed draft.
- **Correction:** Reworked the SVG decision widths, label positions, connector endpoints, and block geometry, regenerated the flowcharts, then inspected final PDF pages 49 and 62 at 160 dpi.
- **Status/root cause:** Corrected and rechecked. The issue came from checking an earlier geometry pass before the final embedded page scale.
- **Next-time rule:** Treat the PDF page render as the acceptance view; rerender after every geometry adjustment.

### M-2026-10-29-16 — Glossary bold-check misread an explicit false value

- **What happened:** The first V6 structural check treated a `<w:b w:val="0">` run as bold because it checked only for the presence of `<w:b>`.
- **Detection/impact:** The checker failed even though DOCX uses that explicit false value to turn bold off for meanings. This was a verifier error, not a formatting defect.
- **Correction:** Parse the `w:val` value (`0`, `false`, or `off` means not bold), then rerun the structural check. All 14 labels are bold, meanings regular, and spacing checks pass.
- **Status/root cause:** Corrected; rerun evidence is in `verification/v6_layout_verification_20261029.json`.
- **Next-time rule:** Interpret WordprocessingML toggle values instead of equating element presence with enabled formatting.

### M-2026-10-29-17 — Preferred DOCX renderer unavailable; local Python lacked verifier packages

- **What happened:** `render_docx.py` could not run because LibreOffice `soffice.exe` was unavailable. Initial Python calls also failed: the Python 3.12 launcher target was missing and system Python 3.14.4 did not include `lxml`.
- **Detection/impact:** The normal document render path and two attempted verifier launches did not complete. These attempts produced no document edits or validation result.
- **Correction:** Opened the V6 DOCX read-only in Microsoft Word 16.0, repaginated and exported PDF through Word COM, rendered the PDF using Poppler, and ran the structural verifier with the bundled workspace Python runtime.
- **Status/root cause:** The final fallback checks passed. The missing `soffice.exe` remains an environment limitation; system-Python package availability is separate from the project artifact.
- **Next-time rule:** Resolve the documented workspace runtime paths before using system Python; record renderer substitutions and do not describe a fallback as the unavailable renderer's success.

### M-2026-10-29-18 — Initial V6 render-resolution record was inaccurate

- **What happened:** The first V6 JSON copied 150/180 dpi field labels from V5 even though V6's targeted renders were 160 dpi.
- **Detection/impact:** A final evidence audit compared the recorded labels with the actual rendered page files and found the mismatch. The PDF and images were unchanged, but the audit trail incorrectly described the review resolution.
- **Correction:** Updated the verifier to record 75 dpi for all pages, four 75 dpi contact sheets, and the 21 targeted pages at 160 dpi; reran the verifier and replaced the JSON.
- **Status/root cause:** Corrected before handoff; current machine-readable evidence matches the visual review.
- **Next-time rule:** Populate QA reports from the actual render command and reviewed file list; do not inherit resolution claims from prior versions.

### M-2026-10-29-19 — Patch context did not match current memory files

- **What happened:** A few initial documentation patches targeted stale end-of-file context and did not apply.
- **Detection/impact:** The patch tool reported no matching context; no file contents were changed by those attempts.
- **Correction:** Read the current file tails and reapplied the intended changes against the actual headings/contents.
- **Status/root cause:** Corrected; no content loss or partial edit occurred.
- **Next-time rule:** Re-read the target section before applying a large append when the working file has since grown.

### M-2026-10-29-20 — Double-spacing glossary adds one lightly populated page

- **What happened:** Applying uniform 2.0 spacing to all 14 definitions moves the Traffic-count group entry to printed p. 13 by itself.
- **Detection/impact:** Final pagination and rendered pages 21–23 showed the entry remains complete, with Chapter II starting separately on p. 14. This meets the direct spacing request but leaves page 13 sparsely used.
- **Correction:** Kept all requested spacing and content; updated the static contents and document page map to reflect Word's actual pagination. The tradeoff is recorded in the V6 review report.
- **Status/root cause:** Known layout tradeoff, not a silent failure. No research meaning was changed to force a fit.
- **Next-time rule:** Surface pagination consequences of explicit uniform spacing and obtain a separate content/layout decision before condensing definitions or altering page geometry.

## V6 annotated-layout task reference

V6's caption, glossary, flowchart, page-map, and verification details are in `09_VERIFICATION_LEDGER.md` and `24_V6_ANNOTATED_LAYOUT_AND_FIGURE_REVIEW.md`. The machine-readable record and repeatable verifier are `verification/v6_layout_verification_20261029.json` and `verification/verify_v6_layout.py`; V6 source assets are in `figures_v6/`. V6 is a separate layout review candidate; V2 remains the approved source. The one-page glossary pagination tradeoff and renderer/checker corrections are retained above.

### M-PCB-2026-10-29-USB — Connector escape clearance failed twice

Observed six copper clearance errors in the first two USB drafts (`usb_drc_v1.json`, `usb_drc_v2.json`). Bends were too close to neighboring USB-C pads. The third route moved bends outward; actual `usb_drc_v3.json` and the regenerated combined `preroute_usb_v3_drc.json` show zero copper errors under the same 0.15 mm rule. The latter still has 21 silk warnings and 102 unconnected items, so it is not a finished board. No physical USB performance was established. Next time: inspect pad extents before choosing escape bends, retain failed reports, and keep length/return/impedance review distinct from DRC. Domain details remain in hardware `docs/ERROR_LOG.md`.

### M-PCB-2026-10-29-USB-v5 — Return via clearance and stale reroute report

A new USB return via had 0.145 mm clearance against the unchanged 0.150 mm rule. Moved it 0.05 mm; `preroute_usb_v5_support_drc.json` records zero errors, 21 silk warnings and 90 unconnected items. The failed v4 support report remains. Separately, removing existing USB tracks via KiCad SWIG caused an invalid pad-container exception before saving; a subsequently launched check used stale input (`usb_v4_drc.json`) and is not acceptance evidence. Fresh generation from placement succeeded. The USB helper now rejects already routed input before mutation. Next-time rule: use fresh intermediate sources, check tool success before dependent commands, and bind each report to its input hash. See hardware ERROR_LOG and usb_v5_geometry.json for bounded route metrics.

### M-PCB-2026-10-29-IMPORT — Exact placement guard detected one-nanometre interchange rounding

The first actual compact SES import failed its exact-placement assertion before any final board save. Read-only comparison showed only R1, R2 and H3 X coordinates rounded by one KiCad internal unit (1 nm), with orientation and side unchanged; all 105 locked copper items were preserved. The finisher now records/restores only this bounded one-IU translation and still rejects larger movement or any side/rotation change. Original failed import_integrity.json remains. Next-time rule: characterize interchange quantization explicitly, restore original positions, and never weaken movement checks without retaining measured differences. Final rerun results are recorded in the hardware handoff/manifests.

### M-PCB-2026-10-29-FINISHER — Loaded-track removal and audit coverage gaps

Source review found the finisher used the same Python Remove ownership wrapper that failed in the USB reroute. A read-only historical fixture confirmed RemoveNative with retained wrappers could detach 69 unlocked GND objects, rebuild connectivity and still read U6 pads. The bounded finishing process now uses that path. Review also found missing checks for SES preservation, same-net drill spacing, actual MPU center copper/paste, forbidden/reserved pins, rule-area flags/layers, unexpected references and newly suppressed checks. These gates were added with scope/acceptance recorded before edits; syntax/help/API readiness is not final design acceptance. Next-time rule: check transformations and effective geometry, not only pad names or a successful tool exit. See reports/reference_corrected/validation_gate_plan.md and finisher review records.

### M-PCB-2026-10-29-PROJECT — Alternate board input lost its intended rules

Copied a routed .kicad_pcb to a new input basename without its matching .kicad_pro. KiCad loaded default settings and propagated them when saving the final output: the next DRC reported 223 violations under 0.20 mm clearance/0.30 mm minimum drill and other default rules. The run did achieve zero unconnected items and eight tab vias, but was not accepted. Preserved the wrong project and reports; restored the exact earlier documented preroute .kicad_pro and supplied the missing input sidecar. The finisher now refuses an input without its sidecar, and the final runner explicitly verifies baseline rule values plus ignored-check/exclusion settings. This restores prior rules, not a new relaxation to hide violations. Next-time rule: copy the board and project together, hash both, and verify effective rules on each alternate-input run. Final rerun evidence belongs in the dated validation manifest.

The earlier attempted process stop found no such process because the bridge search had already finished. A progress note initially described it as interrupted; ERROR_LOG explicitly corrects that statement. Next time poll the actual tool session before asserting a process was stopped.

## Direct preference added after this pass

| ID | Preference | Application |
|---|---|---|
| P-13 | Apply the user's exact reviewer-supplied name spellings: `CRISTOPHER R. CAPILI` and `ENGR. EULOGIO NEIL A. MALLILLIN`. | Search the editable DOCX text and inspect the final rendered front matter; do not infer a spelling from OCR or a low-resolution image. |

## V7 fact-check and final-export mistakes — 2026-10-29

### M-2026-10-29-21 — Initial firmware path assumption was wrong

- **What happened:** Initial read commands assumed a `src/` subdirectory for firmware sources; this repository stores `config.h`, `dsp.cpp`, `session.cpp`, and web-server files at the firmware project root.
- **Detection/impact:** The expected paths returned no files; no project file was changed and no source finding was based on the failed reads.
- **Correction/rerun:** Located the active project through the map and inspected the actual `Code Files/GPT Build/firmware/SHM_Capstone/` paths.
- **Status/root cause:** Closed; path layout was assumed instead of resolved from the project tree.
- **Next-time rule:** Use `rg --files` or the active project map before constructing source paths.

### M-2026-10-29-22 — Crossref request/parser attempt was incomplete

- **What happened:** A fresh eight-way metadata probe parsed 75 rather than 77 DOI-bearing references because its URL parser did not handle two Wiley DOI locators; multiple requests returned HTTP 429.
- **Detection/impact:** Coverage did not include all identifiers, so the attempt could not verify the bibliography and was not used as an acceptance result.
- **Correction/rerun:** Reconciled the reference paragraphs against V4/V5/V6, which carry the same 101 entries, retained only the previous serial 77/77 metadata screen as bounded prior evidence, and checked the corrected Hidalgo-Fort author list directly at the publisher.
- **Status/root cause:** The attempted fresh metadata screen remains rejected; full-text audit remains open.
- **Next-time rule:** Decode and validate every DOI locator before requests; use a serial or rate-limited queue with retry/backoff and report coverage explicitly.

### M-2026-10-29-23 — Long-running command session ID was not retained

- **What happened:** A page-map/render command continued after the caller did not retain its returned session identifier.
- **Detection/impact:** The command was not lost but its first output was not available in the initial response.
- **Correction/rerun:** Retrieved its session output with the returned terminal session and checked its artifacts before using results.
- **Status/root cause:** Closed; the execution wrapper did not surface/persist the session ID for follow-up.
- **Next-time rule:** Capture and poll any returned session ID; do not report a background command's outcome until collected.

### M-2026-10-29-24 — Two ripgrep regular expressions were malformed

- **What happened:** Escaping in combined `rg` patterns failed to parse, so those searches returned errors.
- **Detection/impact:** No source file or paper was changed; the failed searches were not treated as negative findings.
- **Correction/rerun:** Re-ran targeted searches with simple fixed strings and literal matching, then inspected the actual firmware files.
- **Status/root cause:** Closed; shell/string escaping was overcomplicated.
- **Next-time rule:** Prefer `rg -F` for literal source names and split distinct patterns rather than nesting escaping.

### M-2026-10-29-25 — Literal PDF text finder missed line-wrapped/hyphenated text

- **What happened:** A first PDF text search did not find some expected strings because extraction inserted line breaks and hyphenation; `pdftotext` was also unavailable.
- **Detection/impact:** The search result was a false negative and was not used to claim missing content.
- **Correction/rerun:** Used pypdf 6.10.0, inspected the relevant page text/render, and later compared normalized alphanumeric text for the final checks.
- **Status/root cause:** Closed; text extraction layout differs from visible page layout.
- **Next-time rule:** Normalize line breaks/hyphenation and visually inspect a render before treating a text-extraction miss as document loss.

### M-2026-10-29-26 — First Hidalgo-Fort paragraph patch had variable-name collision

- **What happened:** The patch script reused a path variable for an XML paragraph, causing an `AttributeError` before the temporary DOCX was written.
- **Detection/impact:** The patch stopped before writing V7; no partial document change occurred.
- **Correction/rerun:** Used distinct `docx_path` and `para` variables, rebuilt the targeted paragraph, and passed ZIP CRC before Word export.
- **Status/root cause:** Closed; a generic variable name shadowed the document path.
- **Next-time rule:** Use distinct typed names for paths, XML nodes, and serialized text; validate the temporary archive before replacement.

### M-2026-10-29-27 — First Hidalgo-Fort wording duplicated a performance limitation

- **What happened:** The first rewrite added a repeated sentence about latency/reliability.
- **Detection/impact:** Self-review found the duplication before the final export.
- **Correction/rerun:** Removed the redundant sentence; final V7 text comparisons and rendered page 34 show the concise wording.
- **Status/root cause:** Closed; overlapping sentence scope was not checked in the first draft.
- **Next-time rule:** Read the full edited paragraph before accepting a local sentence replacement.

### M-2026-10-29-28 — Word save downsampled the full-color Buntun map

- **What happened:** A writable Microsoft Word COM save changed the embedded map from 1800×860 to 1307×624 pixels without a requested visual edit.
- **Detection/impact:** A package-level pixel/dimension comparison found the reduction even though the map still looked colored in the first PDF. This was an unintended image-quality change in V7.
- **Correction/rerun:** Restored the exact original V6 `image2.png` bytes in V7; verified all eight media assets match V6; opened the corrected DOCX read-only and exported a fresh PDF. Final p. 19 is color and legible. The pre-restore PDF is retained at `verification/v7_render/SHM_Research_Aligned_Revision_Draft_v7_pre_map_restore.pdf`.
- **Status/root cause:** Closed; Word's document-save operation applied image compression/downsampling.
- **Next-time rule:** Compare embedded-media bytes/dimensions against source after any Word save; use read-only Word export when only regenerating a PDF.

### M-2026-10-29-29 — First map-restoration replacement held the source ZIP open

- **What happened:** Windows rejected the first atomic replacement because the source V7 ZIP context was still open.
- **Detection/impact:** `os.replace` returned `PermissionError`; the original V7 DOCX was unchanged and the temporary file was removed.
- **Correction/rerun:** Closed the source ZIP before the atomic replacement, then passed CRC and exact map-image hash/pixel comparison.
- **Status/root cause:** Closed; replacement was attempted inside the open source archive context.
- **Next-time rule:** Close every archive/file handle before replacing its path, then verify CRC/hash after the swap.

### M-2026-10-29-30 — Reference-count regex undercounted entries

- **What happened:** A narrow author/year regex counted 93 reference entries, while the bibliography has 101 paragraphs because corporate authors and several styles do not match that pattern.
- **Detection/impact:** It conflicted with the known 101-entry list, so the result was rejected and no references were edited from it.
- **Correction/rerun:** Located the References heading and counted the 101 non-empty alphabetized paragraphs to end of document; checked the corrected entry in the rendered reference pages.
- **Status/root cause:** Closed for entry count; this is not a claim-support check.
- **Next-time rule:** Use paragraph boundaries/styles and reconcile with the source list rather than assuming one author-format regex covers every reference type.

### M-2026-10-29-31 — Quick DOI URL count omitted Wiley-path DOI links

- **What happened:** A URL-only counter found 75 `doi.org` strings; it missed two DOI-bearing references whose locators use Wiley's direct DOI path. A separate regex that stopped at `)` also truncated ASCE DOI suffixes.
- **Detection/impact:** Both quick counts were incomplete and rejected as refreshed metadata evidence; they did not prompt reference deletion or alteration.
- **Correction/rerun:** Reconciled against the previous 77/77 DOI metadata screen and recorded that this turn did not rerun Crossref. The two affected Wiley references remain present.
- **Status/root cause:** Parser defect; no current comprehensive DOI audit was performed.
- **Next-time rule:** Parse DOI tokens independently from URL hostnames and preserve balanced parentheses/percent escapes; compare extracted identifiers against every bibliography paragraph.

### M-2026-10-29-32 — Initial PDF literal assertions were too strict

- **What happened:** Exact substring assertions failed because pypdf inserts whitespace, line breaks, and hyphens in extracted text.
- **Detection/impact:** The assertions were false negatives, not missing manuscript changes.
- **Correction/rerun:** Normalized extracted page text to alphanumeric form and confirmed F01/F02/F08/F09 and R01 in the final PDF.
- **Status/root cause:** Closed.
- **Next-time rule:** Test normalized page text and retain visual verification for layout-dependent content.

### M-2026-10-29-33 — Word export command and optional Python COM route were unavailable as first attempted

- **What happened:** A command combining deletion of the old generated PDF and Word COM export was rejected before execution; a Python `win32com` fallback import also failed because that package is absent. `pdftotext` was not installed.
- **Detection/impact:** No existing PDF was deleted and no export result was produced by the rejected attempt.
- **Correction/rerun:** Used PowerShell Word COM to export to a new unique PDF path, with the corrected DOCX opened read-only; used pypdf for text extraction.
- **Status/root cause:** Closed; command policy and runtime package availability limited the first routes.
- **Next-time rule:** Export to a fresh output path, avoid bundling destructive cleanup with COM, and check available renderer/runtime dependencies before choosing a fallback.

### M-2026-10-29-34 — PowerShell existence-probe loop had invalid pipeline syntax

- **What happened:** A `foreach` statement was piped without grouping, causing a parser error.
- **Detection/impact:** The probe produced no path result and changed no file.
- **Correction/rerun:** Piped the path strings into `ForEach-Object`; it confirmed the final V7 PDF destination and backup path were unused before copy.
- **Status/root cause:** Closed; PowerShell statement/pipeline syntax was incorrect.
- **Next-time rule:** Use `ForEach-Object` for pipeline transformations or wrap a `foreach` statement before piping.

### M-2026-10-29-35 — Final verification command used a nonexistent pdftotext executable

- **What happened:** `Get-Command pdftotext` returned no executable; invoking the null result caused a command error.
- **Detection/impact:** No PDF extraction was performed by that command and no artifact changed.
- **Correction/rerun:** Confirmed Poppler `pdftoppm` is available and used pypdf for text checks.
- **Status/root cause:** Closed; `pdftotext` is not installed in this runtime.
- **Next-time rule:** Test tool presence before invoking optional binaries and record the actual extraction tool used.


### M-2026-10-29-36 - python-docx resave changed unrelated package serialization

- **What happened:** A python-docx-based F11 patch rewrote/serialized many XML package parts, producing unrelated package differences.
- **Detection/impact:** Package diff showed widespread changes beyond the one intended traffic paragraph. That output was rejected; no such broad serialization was delivered as final.
- **Correction/rerun:** Preserved the rejected DOCX as `verification/v7_render/SHM_Research_Aligned_Revision_Draft_v7_python_docx_resave_rejected.docx`; the F11 attempt used a document-XML-only path, and the final candidate was restored byte-for-byte from the verified pre-F11 snapshot.
- **Status/root cause:** Closed; a convenience document library serialized more of the package than the narrow correction required.
- **Next-time rule:** For surgical edits to established Word files, compare package parts before acceptance; reject broad rewrites and restore from a known-good source when an edit is withdrawn.

### M-2026-10-29-37 - First ASCII search script had a quoting syntax error

- **What happened:** A Python check embedded an apostrophe in a single-quoted literal and failed to parse.
- **Detection/impact:** The check did not run and no artifact changed.
- **Correction/rerun:** Replaced the brittle literal with a safe predicate and reran the search.
- **Status/root cause:** Closed; shell heredoc source quoting was not validated before execution.
- **Next-time rule:** Prefer escaped, double-quoted, or normalized predicates for mixed apostrophe/quote text and confirm the script exits successfully before interpreting results.

### M-2026-10-29-38 - Partial Poppler render was mistaken for the final page count

- **What happened:** A directory count returned 66 image pages while Poppler was still rendering the 80-page PDF.
- **Detection/impact:** The incomplete count was temporarily interpreted as missing pages; it was not entered as final verification evidence.
- **Correction/rerun:** Waited for rendering to finish, counted all 80 pages, and confirmed no page numbers were missing.
- **Status/root cause:** Closed; the count ran before the asynchronous renderer completed.
- **Next-time rule:** Check process completion before inventorying render outputs; compare expected physical page numbers, not just an early file count.

### M-2026-10-29-39 - FHWA exact-text search produced a false negative and a false proposed correction

- **What happened:** A `find` search for the exact phrase `10 minute` returned no match because FHWA 2022 section 3.8.3 uses the wording `10 minutes`. I incorrectly treated the no-match result as evidence that the guide did not list that interval and drafted an F11 replacement.
- **Detection/impact:** Opening the exact official section showed that Step 1 explicitly lists hourly, 10-minute, 5-minute, and 1-minute intervals for the continuous-count-station AADT method. The F11 inference and proposed rewrite were wrong. The user was told the rewrite was being applied before this direct check resolved the source.
- **Correction/rerun:** Withdrew F11 and restored the pre-F11 V7 DOCX/PDF byte-for-byte. The original wording accurately confines the 10-minute option to a specific traffic-count procedure and says that it does not validate the project's vibration/count pairing. FHWA 2013's typical 24-hour, 48-hour, or one-week short-duration count description remains cited.
- **Status/root cause:** Closed; exact phrase matching failed on a plural/formatting variant and was treated as a complete source search.
- **Next-time rule:** A no-match search is not evidence of absence. Open the relevant section, inspect surrounding context, and search spelling, plural, and hyphen variants before changing a claim.

### M-2026-10-29-40 - PDF text display was mistaken for a replacement character in the DOCX

- **What happened:** pypdf/terminal output displayed the curly apostrophe in `FHWA's` as a replacement glyph, prompting an incorrect alert that the DOCX contained U+FFFD.
- **Detection/impact:** Before making a character edit, raw DOCX XML was inspected; it contains U+2019, and the rendered PDF page visibly shows the proper apostrophe. No manuscript edit was made. Two byte-identical audit snapshots were retained and renamed to describe a Unicode-display check/false alarm.
- **Correction/rerun:** Checked the source code point and rendered restored PDF p. 56 at 160 dpi; confirmed the punctuation is intact.
- **Status/root cause:** Closed; text-extraction/console encoding was mistaken for source content. The initial user-facing warning was premature and was corrected in the same turn.
- **Next-time rule:** Verify suspected character corruption in the source package and rendered page before reporting or editing; do not rely on terminal glyph rendering alone.

### M-2026-10-29-41 - System Python lacked pypdf

- **What happened:** The default `C:\Python314\python.exe` runtime could not import pypdf.
- **Detection/impact:** The initial validation command stopped before checking the files and changed nothing.
- **Correction/rerun:** Loaded the bundled workspace runtime and reran the package/PDF checks using its Python dependencies.
- **Status/root cause:** Closed; the system interpreter is not the document-analysis runtime.
- **Next-time rule:** Load the workspace dependency paths before running PDF/document verification.

### M-2026-10-29-42 - Reference-heading check assumed title case

- **What happened:** A DOCX validation script looked for a paragraph exactly equal to `References`, while the manuscript heading is `REFERENCES`; the script raised before finishing.
- **Detection/impact:** CRC, paragraph and media comparisons had already passed, but the reference count and later checks in that run did not complete. No artifact changed.
- **Correction/rerun:** Reran with a case-insensitive heading match and confirmed 101 bibliography paragraphs, 80 Letter PDF pages, and final hashes.
- **Status/root cause:** Closed; the assertion was case-sensitive against a styled all-caps heading.
- **Next-time rule:** Normalize heading case and whitespace when locating document sections; report only checks that completed in a successful run.


### M-2026-10-29-43 - Final PDF exact-sentence assertion ignored extraction line breaks

- **What happened:** A final assertion searched for `No field results are reported in this draft.` as one literal substring in extracted PDF text. The extractor inserted a line break between `are` and `reported`, so the assertion failed.
- **Detection/impact:** No manuscript issue was established and no file changed. The output was a text-layout false negative.
- **Correction/rerun:** Normalized extracted whitespace and checked physical PDF p. 9 visually; the sentence is present and correctly rendered. Other FHWA page text was confirmed visually on p. 56.
- **Status/root cause:** Closed; raw PDF extraction was treated as continuous prose.
- **Next-time rule:** Normalize whitespace and line-breaks before exact PDF text assertions, then use the rendered page for layout-dependent confirmation.

### M-2026-10-29-44 - Console could not print an extracted mathematical glyph

- **What happened:** A diagnostic attempted to print a PDF page excerpt containing a mathematical italic glyph; the Windows console encoding raised `UnicodeEncodeError`.
- **Detection/impact:** That diagnostic output was incomplete; no manuscript or verification artifact was changed by the failed command.
- **Correction/rerun:** Limited subsequent diagnostics to ASCII-safe summaries/normalized predicates and used the visual page render for glyph and layout review.
- **Status/root cause:** Closed; cp1252 console output cannot encode every mathematical Unicode glyph.
- **Next-time rule:** Use `ascii()` or code-point summaries for extracted Unicode text before sending it through a legacy console encoding.

### M-2026-10-29-45 - Active directory retained stale footprint copy during board promotion

- **What happened:** When promoting the corrected 79.5mm board from `design/reference_corrected/` to `design/`, the initial script copied board and project files but did not overwrite `design/SHM_Local.pretty/ESP32-S3-WROOM-1_Overhang.kicad_mod` because the local folder already existed. The first KiCad DRC on the promoted board reported a `lib_footprint_mismatch` warning.
- **Detection/impact:** KiCad CLI DRC caught the mismatch immediately in `reports/drc_active_promoted.json`.
- **Correction/rerun:** Copied the updated footprint library from `reference_corrected/SHM_Local.pretty` into `design/SHM_Local.pretty/` and reran DRC. KiCad 10.0.6 DRC completed with 0 errors, 0 warnings, 0 unconnected items, and 0 schematic parity issues.
- **Status/root cause:** Closed; local footprint library was not synchronized simultaneously with the board promotion.
- **Next-time rule:** Synchronize project-local footprint libraries (`SHM_Local.pretty`) and project files (`.kicad_pro`) whenever promoting a board file to active status.


### M-PCB-2026-10-29-AUDIT — Independent checker constructor and UTF8 comparison defects

The first full independent audit falsely reported 312 copper/paste-in-core findings and 49 footprint mismatches. The two-vector SHAPE_RECT constructor interprets opposite corners, not origin/size; the intended 3.08 mm core became a very large rectangle. The SWIG UTF8 object's inequality comparison also did not match Python string behavior. Corrected to explicit X/Y/width/height with a dimension assertion and converted full library IDs to Python strings. No copper was changed to satisfy these false failures. Rerun validation_20261029T102930156196Z passed with zero independent failures, zero ERC/DRC/connectivity/parity findings and unchanged sources. Next-time rule: verify geometry bounding boxes and convert binding wrapper values before comparison; preserve failed reports.

### M-PCB-2026-10-29-LABEL — DRC-clean labels were hidden under component bodies

Visual 3D review found R1/R8 references under the ESP module and U1/J1 references under their own bodies, despite a clean DRC. Moved four labels only. The first R1 position clipped its pad mask; the second approached U1's silk/pad. Both failed reports are retained in timestamped validation folders. Moved R1 beside the part and reran; final accepted report is named in the hardware handoff. Next-time rule: include assembled-body visibility in label review; mask clearance alone does not establish readable assembled markings.

### M-PCB-2026-10-29-CLOSE — Final rerun and handoff reconciliation

The accepted active check is `reports/reference_corrected/validation_20261029T145905461959Z/manifest.json`: zero findings, expected rules, unchanged sources and zero independent failures. Four body-hidden labels were corrected and the final R1 placement passed. Prior failures remain retained. Hardware HANDOFF/AGENTS/README/map still described a not-yet-promoted board after another saved checkpoint had promoted it; compared hashes before edits, confirmed the active/candidate identity, and reconciled those stale instructions. Preserved prior documentation ZIP. Next-time rule: re-read actual files after interruption, reconcile promotion status, and report current evidence separately from historical checkpoints. No physical gates were closed by these CAD checks.

## Engineering audit follow-up — 2026-10-29

**Direct user preference:** Continue substantive engineering verification, including mathematics, differential routing, RF, test points and wider checks. Explain what was actually verified; keep retrievable equations, sources and closure criteria. This is a direct request, not an inferred approval of fabrication or physical performance.

**M-PCB-ENG-SCOPE:** The prior planar mismatch metric was explicitly limited but insufficient to answer electrical length matching. New read-only graph reproduces it and adds nominal through-via depth: A contacts change from +0.074839mm planar D−−D+ to −3.125161mm under the1.6mm depth assumption. No CAD was altered to conceal the mismatch. Next-time rule: report layer transitions, path exclusions and stackup together with every differential-length claim.

**M-PCB-ENG-PLACEMENT:** A clean configured DRC did not check the manufacturer's insertion-component spacing. A new body-envelope screen found J2 about5.18mm fromU3 (5.13mm including artwork stroke). The chosen conservative body-edge interpretation and exact-part uncertainty are explicit. Correction remains pending; do not mark this physically closed. Next-time rule: translate applicable component-specific assembly/placement guidance into a separate acceptance review.

**M-PCB-ENG-TOOLS:** Read-only probes initially filtered USB names without removing a leading slash, so no tracks were printed; corrected normalization and asserted a nonempty set in the saved checker. Two exploratory KiCad API calls failed: GetStart on PCB_TEXT and GetName on ZONE. Filtered PCB_SHAPE and used GetZoneName; subsequent geometry run completed. Optional fitz import was unavailable, so used installed Poppler26.07.0. Poppler warned about Symbol/ArialUnicode fonts; inspected the generated regulator p6 and confirmed the table/footnote legible. No failed tool result was used as design evidence; no CAD was mutated by these attempts.

**M-PCB-ENG-REVIEW:** Parallel reviewers stopped at the usage limit, so no three-reviewer signoff is claimed. The primary agent completed the bounded checks. Source-fetch timeouts/403 and the explicitly identified regulator-PDF mirror are logged in the engineering report. Next-time rule: preserve access/tool limitations and verify narrow facts with available primary content without inventing unavailable results.

Evidence: `PCB Files/GPT Build - PCB/docs/ENGINEERING_AUDIT_20261029.md` and `reports/engineering_audit/20261029/`. Active CAD hashes remained unchanged. Open electrical, mechanical, thermal, impedance and physical gates remain listed in ENG-01–ENG-13.

