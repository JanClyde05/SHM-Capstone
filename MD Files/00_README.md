# SHM Capstone: current AI and research index

Updated 2026-10-30. Project: localized vibration/frequency monitoring research for Buntun Bridge using MEMS IMUs and an ESP32-S3. The project is still at proposal/prototype stage: do not imply bridge results or physical validation that are not recorded.

## Start here

| Order | File | Use |
|---|---|---|
| 1 | `AGENTS.md` and repository-root `AGENTS.md` | Evidence rules and workflow; user request remains authoritative |
| 2 | `08_PROJECT_MAP_AND_SOURCE_OF_TRUTH.md` | Folder map, active artifacts, code ↔ method ↔ PCB traceability |
| 3 | `09_VERIFICATION_LEDGER.md` | Reproducible checks, status, hashes, evidence gaps |
| 4 | `10_RESEARCH_REFERENCE_AUDIT.md` | Claims, citations, external support, and limits |
| 5 | `12_EXECUTION_PLAN.md` | Problem statement, revision candidates, gates, and order of work |
| 6 | `13_PROJECT_FILE_INVENTORY.md` | Dated file path/size inventory snapshot |
| 7 | `14_CAD_VALIDATION_SNAPSHOT.md` | KiCad DRC/ERC evidence and limitations |
| 8 | `15_PAPER_REVIEW_AND_INTEGRITY_GATES.md` | Paper review, ethics/privacy/Turnitin status, and collection/submission gates |
| 9 | `16_PAPER_CLAIM_AND_DECISION_LEDGER.md` | Claim-level paper-to-source/code evidence and unresolved owner decisions |
| 10 | `19_ENGR_MAY_ANNE_VALENCIA_CORRECTION_LOG.md` | Correction-note transcription and provenance; original “not applied” statuses are superseded by the later v3 candidate authorization |
| 11 | `18_RRL_SUPPORT_AND_GAP_SEARCH.md` | Prioritized literature search, exact support limits, and unanswered research/measurement gaps |
| 12 | `20_V3_REVIEW_CANDIDATE_AND_RRL_BATCH.md` | C01–C26 dispositions, adviser-name clarification, 40 added sources, candidate hashes, QA and remaining gates |
| 13 | `21_V4_VISUAL_RRL_AND_OBJECTIVE_REVIEW.md` | V4 source map, design/citation edits, visual QA, hashes, and limits |
| 14 | `22_AI_FEEDBACK_AND_MISTAKE_LOG.md` | Direct user preferences and dated AI mistake/fix history; update after substantive corrections |
| 15 | `11_AI_WORK_PROMPT.md` | Reusable evidence-first prompt for a future AI session |
| 16 | `17_RESEARCH_PAPER_AUDIT_PROMPT.md` | Reusable manuscript claim/source, ethics/privacy, Turnitin, and project-traceability review prompt |
| 17 | `verification/v3_final_verification_20261027.json` | Machine-readable V3 hashes, page map, link repairs, verification scope, and open limits |
| 18 | `23_V5_ANNOTATED_LAYOUT_AND_FIGURE_REVIEW.md` | Current V5 comment-by-comment layout scope, page map, checks, mistakes, and limits |
| 19 | `verification/v5_layout_verification_20261029.json` and `verification/verify_v5_layout.py` | Machine-readable V5 QA result and repeatable structure/page-map checker |
| 20 | `24_V6_ANNOTATED_LAYOUT_AND_FIGURE_REVIEW.md` | Latest V6 annotated-comment response, rendered page map, QA limits, and glossary pagination tradeoff |
| 21 | `verification/v6_layout_verification_20261029.json` and `verification/verify_v6_layout.py` | Machine-readable V6 QA result and repeatable layout/page-map checker |
| 22 | `26_V6_FACT_CHECK_AND_V7_CORRECTIONS.md` | V6 claim audit, V7 corrections, FHWA recheck adjudication, exact sources, final hashes, QA and open limits |
| 23 | `SHM_Research_Aligned_Revision_Draft_v7.docx` and `.pdf` in `Documents/The Real Research Paper/GPT Paper/` | Separate fact-check review candidate and its Word-export preview; V2 remains approved |
| 24 | verification/v7_fact_check_verification_20261029.json | Historical V7 hashes, FHWA adjudication, page count, render scope, and limits |
| 25 | SHM_Research_Aligned_Revision_Draft_v8.docx and .pdf in Documents/The Real Research Paper/GPT Paper/ | Separate local-precedent fact-check candidate and Word-export preview; V2 remains approved |
| 26 | verification/v8_local_precedent_factcheck_20261030.json | Machine-readable V8 hashes, scoped text/media/reference checks, render review, sources, failures, and limits |
| 27 | `Documents/The Real Research Paper/GPT Paper/SHM_Research_Aligned_Revision_Draft_v9.docx` and `.pdf` | V9 review candidate with active schematic, PCB top view, and 3D CAD view; V2 remains approved |
| 28 | `verification/v9_figure_insertion_verification_20261030.json` and `verify_v9_figure_insertion.py` | Machine-readable V9 source hashes, package diff, page map, render checks, limits, and repeatable verifier |
| 29 | `verification/v9_figures_20261030/v9_figure_assets_manifest.json` | Source and derived figure hashes, preserved V9 snapshots, caption/table reflow, and final outputs |
| 30 | `verification/v9_render_20261030_caption_kept_final/` | Final hash-matched 80-page render, four contact sheets, and targeted 160-dpi pages |
| 31 | `verification/apply_v9_caption_keep_together.py` and `create_v9_caption_kept_contact_sheets.py` | Hash-guarded table-caption formatting change and repeatable final render contact sheets |
| 32 | `../PCB Files/GPT Build - PCB/docs/DOST_EPDC_MANUFACTURING_COMPATIBILITY_20261030.md` | Supplied EPDC evidence, current-board limits comparison, inquiry-form privacy/process notes; no order or Gerber submission |

Then read the approved manuscript at `Documents/The Real Research Paper/GPT Paper/SHM_Research_Aligned_Revision_Draft_v2.docx`, its marked-up review copy under `Documents/The Real Research Paper/GPT Paper/Corrections for the Paper/`, current firmware under `Code Files/GPT Build/firmware/SHM_Capstone/`, and current CAD under `PCB Files/GPT Build - PCB/design/`. The correction log preserves the review marks and history. The user authorized separate V3, V4, V5, and V6 review candidates; V2 remains unchanged as approved source, and none of V3–V6 is institutionally approved. The files in this folder numbered `01`–`07` are legacy proposals from 2026-10-23. Preserve them for provenance; do not use them as current requirements without checking against the active method, source, and owner decisions.

## Current research scope, in brief

The approved proposal describes one fixed roadway-deck monitoring station, three co-located triaxial MPU-6050 devices, an ESP32-S3-WROOM-1-N16R8, sequentially sampled channels, ten consecutive 60-second analysis windows per 600-second session, locally pilot-defined vehicle-count groups, and frequency characterization. It does not yet report collected Buntun vibration results, validated structural frequencies, damage diagnosis, or proven warning thresholds. See the manuscript and the conflict list in `08` before relying on any summary.

## Evidence statuses

- **Verified:** direct evidence supports the narrow statement as written.
- **Partially verified:** evidence supports only a narrower scope or leaves meaningful caveats.
- **Unverified:** adequate evidence was not found or the check has not been done.
- **Contradicted:** available evidence conflicts with the statement.
- **Not applicable:** the proposed check does not apply.

These labels are claims about recorded evidence, not guarantees of truth. No workflow can promise zero hallucinations or absolute certainty. The rule is to expose provenance, confidence, and remaining gaps, and to stop implementation when a material unresolved item would force guesswork.

Current paper review: 15_PAPER_REVIEW_AND_INTEGRITY_GATES.md, 16_PAPER_CLAIM_AND_DECISION_LEDGER.md, and 26_V6_FACT_CHECK_AND_V7_CORRECTIONS.md record scope, claim review, corrections, hashes, evidence, and remaining gaps. V2 remains unchanged and approved; V3–V9 are separate review candidates. V8 is a targeted local-precedent and citation-scope fact-check candidate; V9 adds source-linked schematic/PCB/3D figures and layout reflow. Neither is a full-text audit of all 101 references and neither certifies ethics, Turnitin, AI-writing status, site permission, field readiness, or institutional approval.

## Scope and decision rule

Current paper candidate is V9, a separate figure-insertion and layout candidate derived from V8. It replaces the schematic and PCB placeholders with the active schematic and a paired PCB-top/3D CAD view, retains the 101-entry reference list, and exports to an 80-page Word PDF. V2 remains the approved source. The V9 pass did not recheck the 101 references or change code/CAD. Method/firmware mismatches, ethics/privacy, site/safety, physical/field validation, and Turnitin/AI review remain open. See records 08, 09, 16, 22, 26, and `verification/v9_figure_insertion_verification_20261030.json` for source lineage, hashes, render scope, limitations, and retained failures.

If an old plan disagrees with current code/design or the approved manuscript, record the mismatch. Do not silently resolve by treating the newest file as scientifically correct. Use `12_EXECUTION_PLAN.md` to gate future work.

## External reference starting points

See `10_RESEARCH_REFERENCE_AUDIT.md` for claim-by-claim use and limits. Key starting sources include [NIST sample-size guidance](https://www.itl.nist.gov/div898/handbook/prc/section2/prc222.htm), [Oth & Picozzi (2012)](https://doi.org/10.1155/2012/876174), [FHWA Traffic Monitoring Guide formats](https://www.fhwa.dot.gov/policyinformation/tmguide/tmg_2022/traffic-data-formats.cfm), and [Espressif ESP32-S3-WROOM-1 datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf). Source links and exact boundaries are recorded in the audit.

## 2026-10-28 V4 final pagination and file identity

Final V4 is 77 US Letter pages, 736,229 bytes, SHA-256 `B5D61F760D43E201D3F37382852E9B1B1CC75D39758BFC8006D5E5927C060CCD`. The corrected final map is Chapter I–V printed pages 1, 13, 31, 57, and 58; References p. 59. Tables 1–4 are on pp. 35, 40, 43, and 45–46; Figures 1.1, 1.2, 3.1, 3.2, and 3.3 are on pp. 6, 10, 36, 37, and 50. The static lists were updated and re-rendered. See `09`, `08`, and `21` for verification details. V2 remains the approved source; V4 remains a review candidate. Reference passage verification and institutional, method, site, ethics/privacy, physical/field, Turnitin, and AI-writing gates remain open.

A 77-page PDF preview matching the final V4 Word export is also delivered beside the DOCX: `SHM_Research_Aligned_Revision_Draft_v4.pdf` (SHA-256 `455F65A3DEC89C71C3FD44F7F40013603D14DC55441DC8B93D37679DA56A22E6`).

Latest V4 identity after the Patinio link repair: DOCX SHA-256 `D2CD42918960792AD91B55F0C1BD721EA0110291E89360E8B123633C4D0CED83`; matching 77-page PDF SHA-256 `843EC606F074C1C03CA7F6F1FED368D9609D0444812BB27D9CE2E879F7579D32`. The repaired Inquirer locator is partially verified because direct browser opening returned 403. See `09`, `10`, and `21` for source and verification limits.

## Latest V4 visual-layout state (2026-10-29)

The separate V4 review candidate at that snapshot was 79 pages. Figures 1.1 (IPO), 3.1 (system block diagram), 3.4 (firmware flowchart), and 3.5 (field workflow) use simple monochrome styling; Figure 1.2 keeps the original colored Buntun Bridge map. Figures 3.2–3.3 are blank white/black schematic and PCB placeholders; the active KiCad files were not changed. The firmware code flowchart remains in the paper, and a separate blank code-flow placeholder is available for later use. The glossary labels are bold with regular-weight meanings, split across printed pages 11–12; Chapter II starts separately on page 13. V4 hashes, page map, QA evidence, and limits are in `09_VERIFICATION_LEDGER.md`, `08_PROJECT_MAP_AND_SOURCE_OF_TRUTH.md`, and `21_V4_VISUAL_RRL_AND_OBJECTIVE_REVIEW.md`. V2 remains the approved source; V4 remains a review candidate. No research claims, code, PCB CAD, or data were changed in that comment-fix pass. The persistent preference and AI mistake/fix record is `22_AI_FEEDBACK_AND_MISTAKE_LOG.md`. The inventory count in this historical snapshot was 82 directories and 434 files; see the current inventory for updated counts.

## Prior V5 annotated layout snapshot (2026-10-29)

At the time of this historical snapshot, V5 was a separate 79-page US Letter layout candidate with updated abstract/glossary spacing, the corrected Figure 3.4 List of Figures label, and regenerated monochrome flowcharts. Abstract and Keywords share PDF p. 9; the glossary occupies printed pp. 11–12; Chapter II begins on printed p. 13 without a page-number reset. All seven figure/caption pairs and both static lists were checked; the List of Tables page was visually inspected at 180 dpi, and figure page numbers are 6, 10, 36, 37, 37, 39, and 52. V5 DOCX SHA-256 `43D260EC5C1156BE2CC44C1D984651E77CF8676F92E47F814F7B081C01915759`; matching PDF SHA-256 `26F744DAA298C87567B3D54E2CBDC3210FF8A76CE1BCE37CFD213E946CE6F273`. V2–V4 remain unchanged. This is a layout QA result, not a full research/source audit or institutional approval. See `23_V5_ANNOTATED_LAYOUT_AND_FIGURE_REVIEW.md`, `09_VERIFICATION_LEDGER.md`, and `22_AI_FEEDBACK_AND_MISTAKE_LOG.md`; the refreshed file inventory records 84 directories and 468 files in this snapshot.



## Current PCB continuation plan (2026-10-29)

Read [`CONTINUATION_PLAN.md`](../PCB%20Files/GPT%20Build%20-%20PCB/docs/CONTINUATION_PLAN.md) before CAD generation. It binds the corrected SHM_PCB_New reference, lists actual incomplete candidate files, sources, next steps and acceptance gates. MD22 contains the reference-selection mistake and CAD failed-check history. This hardware continuation does not alter the manuscript or firmware.


### V7 follow-up source check (2026-10-29)

The attempted F11 rewrite was withdrawn after opening the exact FHWA 2022 section: the guide does list 10-minute increments for a specified AADT procedure. The original V7 traffic wording remains, with the project-specific vibration/count limitation explicit. V7 is byte-identical to its pre-F11 verified snapshot. The failed exact search and correction are logged in `22_AI_FEEDBACK_AND_MISTAKE_LOG.md`, `26_V6_FACT_CHECK_AND_V7_CORRECTIONS.md`, and `verification/v7_fact_check_verification_20261029.json`.

## Final corrected PCB CAD delivery — 2026-10-29

Active artifact: `PCB Files/GPT Build - PCB/design/SHM_Node_R2.kicad_pcb`, SHA-256 `0ea352e982e6ccb87134d1d3dcef7bd3adb747efab5ba28b136cd1090f99540e`. The four final reference-label moves change the earlier promoted hash `804D5B67...`; components, pad nets, copper and outline are unchanged by those moves. Old source/report hashes are historical.

Exact evidence: `PCB Files/GPT Build - PCB/reports/reference_corrected/validation_20261029T145905461959Z/manifest.json`. KiCad 10.0.6 ERC/DRC/connectivity/parity and independent audit: zero findings; 233 numbered pads, 148 spec endpoints, firmware mappings, native USB/reserved pins, actual MPU center copper/paste and rule areas checked. Exact SHM_PCB_New 12-edge 79.50 × 50.45 mm outline. Baseline four ERC/five DRC ignored categories remain explicitly listed; no explicit exclusions/new suppressions. Report commands, timestamps and source/report hashes are retained.

Current recovery/navigation: hardware `docs/HANDOFF.md`, `CONTINUATION_PLAN.md`, `PROJECT_MAP.md`, `LAYOUT_REVIEW.md`, `RESEARCH_LEDGER.md`, `ERROR_LOG.md`, `BOM.md` and `PROTOTYPE_BRINGUP.md`. Active native files are in `design/`; staging in `design/reference_corrected/`; wrong 83 mm history in `design/superseded_wrong_83mm_outline/`. Run `tools/run_corrected_checks.py --active` for active files. Do not run legacy writers or regenerate over later manual work.

Remaining gates: fabricator stackup/USB impedance, exact remaining parts and DFM/stencil, enclosure/cable/mounting, thermal/current/USB/I2C/DRDY/FIFO, reference-frequency and field tests. No physical validation or fabrication release is claimed. Paper and firmware were not edited during this continuation. Top/bottom native renders and copper plots were visually inspected, and the existing schematic layout remains unchanged.

## Engineering audit follow-up — 2026-10-29

Hardware review: [engineering audit](../PCB%20Files/GPT%20Build%20-%20PCB/docs/ENGINEERING_AUDIT_20261029.md), [scope/plan](../PCB%20Files/GPT%20Build%20-%20PCB/docs/ENGINEERING_AUDIT_PLAN.md). The deeper read-only audit found issues beyond configured ERC/DRC: USB A-contact transition imbalance (4 D+ versus 2 D−), missing explicit impedance stackup, no local capacitor directly on the ESD VBUS net, J2-to-U3 nominal body separation about 5.18 mm (5.13 mm conservative F.Fab box) against the TDK 6 mm insertion-component guidance, and unresolved thermal/probe-access qualification. Nominal antenna overhang is 0.10 mm with no recorded tolerance budget. These are engineering concerns, not observed prototype failures. Active PCB remains unchanged at SHA-256 `0ea352e982e6ccb87134d1d3dcef7bd3adb747efab5ba28b136cd1090f99540e`; the earlier configured CAD pass remains bounded evidence.

The report maps ENG-01–ENG-13 to file evidence, source IDs E1–E9, equation IDs and closure steps. `tools/audit_engineering_geometry.py` measures paths, reference-fill samples, antenna geometry, test pads and insertion-component proximity; `tools/audit_engineering_math.py` records conditional power/thermal/I2C/RC arithmetic. Data is in `PCB Files/GPT Build - PCB/reports/engineering_audit/20261029/`. No physical tests or new CAD edits were performed.

## V8 local-precedent fact-check (2026-10-30)

V8 is a separate candidate with four scoped edits to citation placement, the Gaviña et al. (2017) bridge count, the PCIEERD USHER description, and its bibliography locator. The 80-page Word-export PDF, four paragraph diffs, 101-reference count, unchanged media, render review, source-access limits, failure history, and hashes are recorded in 26_V6_FACT_CHECK_AND_V7_CORRECTIONS.md, 09_VERIFICATION_LEDGER.md, 10_RESEARCH_REFERENCE_AUDIT.md, 16_PAPER_CLAIM_AND_DECISION_LEDGER.md, and verification/v8_local_precedent_factcheck_20261030.json. V2 remains approved; V8 is not an exhaustive full-text citation audit or ethics, Turnitin, field-validation, or institutional clearance.

## V9 schematic, PCB, and 3D figure insertion (2026-10-30)

V9 replaces Figure 3.2 and Figure 3.3 placeholders with the active SHM_Node_R2 schematic and a two-panel active PCB top layout/3D CAD rendering. Figure 3.2 and 3.3 appear on printed p. 38; Figures 3.4 and 3.5 remain on pp. 40 and 53. The full CAD-only caveat is on printed p. 35. Table 1 and its caption now stay together on printed p. 36; the List of Tables points there. It explicitly lists board/component IDs, the 600-second and ten-by-60-second schedule, frozen analysis settings, IDE/library versions, measured per-channel rate, and raw/summary fields. Final V9 DOCX SHA-256 is `BCD8B916EE54AAA4414DC7A3D4AAC5FD7B79A193110E2ADE21625A17A6CD1B80`; matching 80-page Word-export PDF SHA-256 is `ED6DAE71277C2A7C2D69095E260E453E213A0859C576CEF28926A6D0814D712D`. Front matter is numbered i–ix followed by Arabic pp. 1–71 continuously; the 101 references are unchanged. V2 remains approved and V9 is a review candidate, not an adviser/institution-approved or physically validated paper. The detailed source hashes, page map, structural checks, rendered evidence, caveat, limitations, and failure history are in `verification/v9_figure_insertion_verification_20261030.json`, `verification/v9_figures_20261030/v9_figure_assets_manifest.json`, `verification/v9_render_20261030_caption_kept_final/`, `09_VERIFICATION_LEDGER.md`, `16_PAPER_CLAIM_AND_DECISION_LEDGER.md`, `26_V6_FACT_CHECK_AND_V7_CORRECTIONS.md`, and `22_AI_FEEDBACK_AND_MISTAKE_LOG.md`.

## Portable PCB design skill — 2026-10-30

`AI Skills/pcb-design-astra/SKILL.md` is a project-root, model-neutral workflow for schematic and PCB planning, implementation, review, and handoff. Its decision-ledger and validation-matrix references capture source identity, primary evidence, explicit assumptions, layered CAD/independent checks, preserved failures, and physical/manufacturing limits. Root `AGENTS.md` directs future AI sessions to it. The method is distilled from public GPT-6 Astra capability descriptions and observable project records; it does not claim access to hidden model reasoning or guarantee equivalent performance. Creating the skill changed no schematic, PCB, firmware, manuscript, or research data.

## DOST-ASTI EPDC manufacturing pre-screen — 2026-10-30

The user supplied a DOST-ASTI EPDC sales reply and four PDFs in `Documents/For PCB Ordering - DOST/`. The source-hash-linked read-only compatibility assessment is `PCB Files/GPT Build - PCB/docs/DOST_EPDC_MANUFACTURING_COMPATIBILITY_20261030.md`. The supplied Rev 02 specification limits fabrication to 1-2 layers; the active 4-layer R2 board also has current track-width, clearance, via-hole, and annular-ring conflicts. Its 79.50 x 50.45 mm outline and configured 1.6 mm thickness are within/match the stated maxima/nominal limit, while material/copper stackup and USB controlled-impedance support remain unverified. The supplied inquiry form is a prefilled sample containing another client's information/signature and should not be returned as-is. No Gerbers were generated or sent, no form was edited, and no order was placed. Read the DOST report before any supplier-package work.
