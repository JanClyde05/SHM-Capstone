# Project map and artifact traceability

## Current hardware-reference correction (2026-10-28/29)

The user clarified that **only `PCB Files/Reference PCB (OLD Version)/Thesis/SHM_PCB_New/` is the intended old reference**, specifically its root `SHM_PCB_New.kicad_sch` and `SHM_PCB_New.kicad_pcb`. The parent `Thesis.kicad_pcb` and nested `SHM_Proto_PCB` are historical comparisons, not defaults. This correction authorizes targeted hardware geometry/layout work; the paper-only statements later in this map describe their earlier task scope.

Read-onlyKiCad10 inspection verified the intended outline's79.50 x50.45mm centerline extent and12 edge primitives. The R2 board at the correction checkpoint had16 edge primitives and83.608663 x83.118463mm stroke-inclusive bounds from the wrong parent reference. Reference hash:`372996943A9C3EB3C9087C315B7C810DF9C0B70A4E0D1B47A99E9EC81B52C23F`; wrong-R2 snapshot hash:`DA80B01E83B4625F8C970DF54883DBA27B5402EBCA027CB8A6274129E32A0E54`. Comparison evidence is `PCB Files/GPT Build - PCB/reports/reference/reference_correction_20261028.json`.

**Conformity of that earlier R2 shape to the clarified reference: contradicted.** On 2026-10-29, the user directed the complete separation of the superseded and corrected files. The superseded 83.6 mm board and its intermediate placement/preroute files were moved to `PCB Files/GPT Build - PCB/design/superseded_wrong_83mm_outline/` with an explicit audit notice. The corrected 79.50 × 50.45 mm 12-edge compact board (`SHM_Node_R2.kicad_pcb`, SHA-256 `804D5B67AF300BFD1435103EC163E99917812B64A9055980DF44E0CCA97D3EE5`) was promoted to the active root `PCB Files/GPT Build - PCB/design/`. Fresh KiCad 10.0.6 checks confirm **0 ERC violations, 0 DRC violations, 0 unconnected items, 0 schematic parity issues**, and exact 12-edge outline agreement with `SHM_PCB_New.kicad_pcb`. Active visual previews and machine-readable manifests (`00_README_ACTIVE_DESIGN.md`, `DESIGN_MANIFEST.json`) document this layout. Controlled-impedance USB stackup, regulator thermal dissipation under load, and physical fabrication qualification remain open.

Snapshot refreshed 2026-10-29 after V7 fact-check and final document QA. See `13_PROJECT_FILE_INVENTORY.md` for the current file-level inventory. Paths below are relative to the repository root.

## Repository map

| Area | Observed contents | Role / cautions |
|---|---|---|
| `.obsidian-vault/` | Obsidian project notes and hardware context | Notes may contain old design assumptions. `05-hardware/CONTEXT.md` was already modified and `SCHEMATIC_AESTHETIC_STANDARD.md` was already untracked at inspection; preserve. |
| `3D Files/` | Empty at snapshot | No 3D enclosure or mounting model found. |
| `Code Files/` | 137 files at initial scan; active `GPT Build/` firmware, docs, reports and tests | Current implementation evidence. Check all technical statements against source and configuration. |
| `Documents/` | Thesis, handoff, source forms and adapted working copies; current aligned draft is under `The Real Research Paper/GPT Paper/` | Manuscript scope is authoritative for proposed method, subject to owner approval. Never infer results from proposal language. |
| `MD Files/` | `01`–`07` legacy notes; current map/audit/plan docs `08`–`26`; `verification/`, and `figures_v4/`–`figures_v6/` assets | `01`–`07` contain conflicting earlier plans (e.g. Welch, other pin mapping, microSD). Historical only unless revalidated. The reviewer correction log preserves transcription/provenance; V3–V7 candidate edits and verification are recorded in `20`–`26`; `26` is the latest targeted fact-check record. |
| `PCB Files/` | 164 files at initial scan; active `GPT Build - PCB/` KiCad project and older board folders/backups | Current design files are under `GPT Build - PCB/design/`. Preserve the 47 zip backups from old PCB areas. Prior README/HANDOFF/audit reports can be stale. |
| `Pictures/` | 5 files at initial scan | Visual project context; not measurement or validation evidence unless provenance/method is documented. |
| `Presentations/` | 2 files at initial scan | Presentation context; verify every claim against current sources. |

The directory and file inventory was refreshed after V6 figures, render evidence, logs, and verification records were added; see `13_PROJECT_FILE_INVENTORY.md` for the current path and size snapshot. Inventory records presence and byte size, not content validity.

## Active artifact paths

| Concern | Current artifact | What it establishes | What it does not establish |
|---|---|---|---|
| Research method | Approved source: `Documents/The Real Research Paper/GPT Paper/SHM_Research_Aligned_Revision_Draft_v2.docx`; V3–V7 are separate candidates beside it | V2 records owner approval on 2026-10-24; V3 has correction dispositions and a 100-reference RRL; V4 adds a 101-entry RRL; V5/V6 address later annotated layout comments; V7 applies a targeted fact-check and bounded corrections | V3–V7 are not approved/adopted; none establishes collected data, field access, validated thresholds, ethics/privacy clearance, or final conclusions. V5/V6 did not re-audit the research claims or bibliography |
| Reviewer corrections and dispositions | Marked-up v2 PDF; transcription in `19_ENGR_MAY_ANNE_VALENCIA_CORRECTION_LOG.md`; candidate dispositions and QA in `20_V3_REVIEW_CANDIDATE_AND_RRL_BATCH.md` | Notes mapped to pages, then clear/bounded items applied to a separately authorized candidate; user attributes the review to Engr. May Anne Valencia | PDF metadata does not authenticate the reviewer; ambiguous notes remain open; v3 is not adviser/institution approval and does not prove ethics, Turnitin, or field readiness |
| Personalized administrative forms | `Documents/Forms/Forms Edited - GPT/Personalized Copies/` (six COE-SR01–SR06 DOCX copies) | User-directed editable copies with supplied proponent/contact, subject adviser, department chair, candidate order, consultation entry, and seven SR06 sheets; the user-supplied corrected format was retained, and SR06 has retrospective page/section-paragraph cross-references to the approved v2 draft with an explicit N/A for the timeline question | Working copies only; reported consultation/comments are user-provided and uncorroborated, and the SR06 locators are topical cross-references rather than original panel citations. They do not establish institutional acceptance, adviser commitment/selection, other attendance, defense stage, signatures, or approval. SR04 asks for at least 10 consultations per semester but provides nine writable log rows; confirm the approved format before use. Earlier placeholder copies remain in the parent folder. Current six-file hashes and sizes plus the SR06 locator audit are recorded in `verification/forms_sr06_page_reference_audit_20261026.json`. |
| Firmware | `Code Files/GPT Build/firmware/SHM_Capstone/` | Current source behavior and defaults; manifest/build artifacts support reproducibility | Correct physical sensor response or field performance |
| Firmware docs and reports | `Code Files/GPT Build/docs/`, `reports/`, tests | Existing algorithm, interface, build/test evidence, and intended choices | A substitute for reading current code or conducting hardware tests |
| CAD | `PCB Files/GPT Build - PCB/design/SHM_Node_R2.kicad_sch`, `.kicad_pcb`, `circuit_spec.json` | Current KiCad schematic, PCB and circuit spec; CLI ERC/DRC snapshots in `MD Files/verification/` | Fabrication readiness, assembled operation, sensor calibration, or proof that the mounted sensor is suitable |
| CAD generator | `PCB Files/GPT Build - PCB/` scripts and docs | Inputs and generation workflow; inspect generator + output when changing design | CAD reports alone do not validate generator correctness or physical implementation |
| Old documents | `MD Files/01_RESEARCH_CONTEXT.md` through `07_REFERENCES.md`; legacy KiCad notes/reports | Provenance, prior reasoning, questions and discarded proposals | Current requirements. Several statements conflict with current approved draft, firmware or CAD. |

## Research ↔ firmware ↔ PCB traceability

| Research/method element | Manuscript | Firmware / CAD evidence | Status and gap |
|---|---|---|---|
| Site and placement | One fixed roadway-deck station at Buntun Bridge | Current board is a single node; no multi-node time sync is present | Proposed setup only. Exact member/span/mount, access approval, mounting transfer function and field layout remain unresolved. |
| Sensors | Three co-located MPU-6050 ICs, each triaxial | Hardware profile: bus 0 GPIO8/9 carries IMU1+IMU2; bus 1 GPIO10/11 carries IMU3; INT GPIO4/5/6; addresses 0x68/0x69/0x68 | Firmware and board configuration agree on topology. Co-location means three redundant local tri-axis units, not a spatial array and not an X/Y/Z allocation. Board assembly and sensor identity are not verified. |
| Controller / pin safety | ESP32-S3-WROOM-1-N16R8 | Firmware reserves GPIO35/36/37 for R8 PSRAM and GPIO19/20 for USB | Consistent with the selected module variant as configured. Verify actual purchased module and physical assembly before powering hardware. |
| Sampling | Sequential device reads; nominal 100 Hz | Firmware defaults nominal `fs=100 Hz`; scheduler/timing tolerance configured in source. No simultaneous multi-IMU sample capture. | Nominal rate is not measured rate. Sequential sampling introduces inter-device phase/time offset; avoid coherent fusion claims. Bench/field timing characterization remains. |
| Analysis | Frequency characterization; fixed pilot-selected settings; ten 60-s windows within 600-s session; manuscript says median of valid windows | `dsp.cpp`: mean removal, symmetric Hann, N-point Bluestein FFT; selects strongest positive in-band bin. `session.cpp`: accepts session only when all 10 windows valid (`SHM_MIN_VALID_WINDOWS=10`) | Material mismatch: median of valid windows permits fewer than 10; firmware requires all 10. Resolve protocol or code before collection. Manuscript's pilot-fixed window-function language must align with hardcoded Hann. |
| Frequency band / QC | Left to local pilot and method finalization | Firmware defaults include 0.5–20 Hz and timing/QC limits; these are prototype defaults, not pilot-validated thresholds | Do not present as final scientific settings. Freeze after pilot with version/hash stored in each session. |
| Storage | Session capture/output described by current implementation notes | Firmware captures raw data in PSRAM, then writes to LittleFS after capture | Not microSD. Validate actual capacity, power-loss behavior, throughput, file integrity and retention on hardware before field sessions. |
| Frequency claim | Dominant frequency characterization only | Current estimator is largest in-band FFT magnitude bin, not vector magnitude, Welch PSD, peak interpolation or identified structural modal frequency | Call it the estimator's dominant in-band spectral bin unless the protocol validates a stronger interpretation. Avoid “modal frequency” as a demonstrated property. |
| Live output / title wording | Paper title/glossary use “real-time”; methods say fixed 60-second windows in 600-second sessions | `/api/live` exposes status/latest raw readings and latest completed window; final result requires ten valid windows and finalizes after session/count submission | Keep “real-time” bounded to the dashboard's measured update behavior; measure latency and distinguish live preview from finalized session summaries. See `15` and `16`. |
| Privacy / operator | Paper says driver/pedestrian identifying data are not needed and limits imagery | UI requires an operator name; `session.cpp` stores it as `operator`; repository has no complete retention/access/deletion/backup policy | The road-user statement is narrow, but the system also processes operator identity. Minimize or document it and obtain CSU privacy advice; review incidental images. |
| Traffic groups | Locally pilot-defined vehicle count groups | No evidence that firmware determines traffic groups; count collection is a field protocol | Define operational classification/count procedure and independent observers/data before analysis. Do not use near-zero/medium/heavy thresholds from legacy docs without approval. |
| Results / validation | Chapters IV–V are proposal-stage, with no reported bridge results in reviewed draft | Firmware has host/compile evidence; CAD has ERC/DRC evidence | No Buntun field dataset or physical validation found in reviewed artifacts. State “not located in reviewed project sources,” not that none exists anywhere. |

## Superseded or stale project assumptions

The old `MD Files/01`–`07` set proposes different hardware pins, Welch analysis, microSD, sensor fusion/averaging, thresholds, and milestones. These conflict with one or more current files and were not adopted by this audit. Old PCB `README`, `HANDOFF`, and `AUDIT_ELECTRICAL` notes describe earlier routing/audit states; the current CAD snapshot is documented in `14`. Do not silently copy an old choice into current code or design.

## Paper integrity follow-up

The v2 manuscript remains unchanged and approved. A separate v3 candidate is stored beside it; reviewer-note dispositions, 40 added RRL references and QA are recorded in `MD Files/20_V3_REVIEW_CANDIDATE_AND_RRL_BATCH.md`. Ambiguous notes and scientific/institutional gates remain open. Its current paper claim and decision register is `MD Files/16_PAPER_CLAIM_AND_DECISION_LEDGER.md`; ethics/privacy, Turnitin, front matter, layout and collection readiness are in `MD Files/15_PAPER_REVIEW_AND_INTEGRITY_GATES.md`. These are partial review artifacts, not ethics or Turnitin clearance. The previous v2 handoff's “further revisions deferred” language is historical and does not override the current audit request.

## Open traceability questions

1. Confirm manuscript version/approval and whether its “median of valid windows” rule is binding.
2. Confirm exact installed module/sensor part markings, board assembly status, and sensor mounting point.
3. Set the pilot protocol and define valid-window criteria, analysis band, frequency estimator terminology, and sample/replicate plan before collecting thesis data.
4. Obtain/document bridge access and safety approvals through the responsible authorities before field deployment.
5. Perform bench timing/noise/storage and frequency-reference tests; none are implied by software build or CAD checks.
6. Reconcile the pilot-selected window wording with hardcoded symmetric Hann and the valid-window median wording with the firmware's ten-valid-window requirement.
7. Obtain a written institutional ethics/privacy classification, site authorization and field safety approval; none was located in the reviewed project artifacts.
8. Decide whether to keep the unqualified “localized” and “real-time” claims, replace generic Dedication/Acknowledgement filler, and correct the approval-sheet stage/placeholders.
9. Review v3 with the adviser/owner and decide whether to adopt it; resolve or explicitly retain its deferred notes, method/code conflicts, and institutional gates before data collection or submission.

## 2026-10-27 final V3 map refresh

The separate V3 review candidate has 100 bibliography entries (40 additions) and is 75 physical pages in the final Word export. Chapter I–V start on separate pages; main page numbering starts at Chapter I and remains continuous. V2 remains the approved source of truth and is hash-preserved. Current candidate hash, page map, corrected source links, and verification limits are recorded in `09_VERIFICATION_LEDGER.md`, `10_RESEARCH_REFERENCE_AUDIT.md`, `20_V3_REVIEW_CANDIDATE_AND_RRL_BATCH.md`, and `verification/v3_final_verification_20261027.json`. V3 is not approved; no code or PCB implementation changed. The project claim, code, PCB, field, ethics/privacy, and source-support open items remain in force.


## 2026-10-28 final V3 map refresh

The promoted V3 review candidate is 76 physical US Letter pages, hash `EC2EF0C01090CF57D9AEA343E1F981ED151784C9858E4CD6D8CC86E4D01ADA4F`. Printed-to-physical page map: Chapter I 1/10; Chapter II 13/22; Chapter III 32/41; Chapter IV 56/65; Chapter V 57/66; References 58/67. Front matter uses Roman numbering; Arabic numbering is continuous through the chapters. The glossary now fits on printed p. 12, before Chapter II's separate p. 13 start. Table list/caption pages are 36, 39, 42, and 44; figure pages are 6, 10, 37, and 49. All 76 pages were rendered and visually reviewed; details and hash-pinned QA export are in `09`, `20`, and `verification/v3_final_verification_20261027.json` (updated 2026-10-28).

V2 remains unchanged and approved; V3 remains a review candidate. The full-text audit of all 100 references, firmware/window-rule reconciliation, statistical/pilot decisions, owner placeholders on the approval sheet, and site/safety/ethics/privacy/physical/Turnitin gates remain unresolved. A valid `.repacked.docx` intermediate remains beside V3; it is superseded and must not be treated as the current candidate. Its cleanup removal was blocked by the tool policy, so it is retained and listed in the inventory.

## 2026-10-28 V4 map refresh

V4 is a separate 77-page review candidate, SHA-256 `532D130E2A2FDD3889B824C6B7E1DDAC4FFCEFB153CC6FA22AA598D178FF5456`. V2 remains the approved source and V3 remains unchanged. V4 has 101 reference entries (77 DOI-bearing, all unique), monochrome figure/table assets under `MD Files/figures_v4/`, and a firmware flowchart mapped to current source behavior. Word 16.0 and Poppler 26.07.0 visual review confirmed continuous Arabic numbering and the page map in `09`/`21`: Chapter I–V start at printed pages 1, 13, 30, 57, and 58; References start at 59. Figures 1.1, 1.2, 3.1, 3.2, and 3.3 are on printed pages 6, 10, 35, 37, and 50; tables 1–4 are on 34, 40, 43, and 45.

V4 does not resolve the firmware/method window-validity mismatch or the pilot-selected/Hann conflict. Full-text verification of every reference, owner/adviser adoption, and site, safety, ethics/privacy, physical/field, Turnitin, and AI-writing gates remain open. No code or PCB artifact changed.

## 2026-10-29 V4 annotated-comment fixes — latest artifact map

The user-directed V4 formatting pass revised the complete Definition of Terms layout, kept the 14 term labels bold and meanings regular, balanced the glossary across printed pp. 11–12, and preserved Chapter II's separate p. 13 start. Figure 3.4's firmware flowchart was redrawn with clearer branch arrows/connectors; Figure 3.5's field workflow is now a separate, two-panel monochrome flowchart. Figure 1.2 retains the colored Buntun Bridge map. Figures 3.2–3.3 remain placeholder frames; their CAD sources were not changed.

Latest V4 DOCX: 79 physical US Letter pages, 1,370,946 bytes, SHA-256 `6CA3559D426DBC5B66F375402EAD771E166EC26E19096F74BE36BBAA02AF4190`. Matching Word 16.0 PDF: 1,357,961 bytes, SHA-256 `B600026A2678F236CD11821A2A42C4DECA176A44A4B2BD145CDB2074459F3E0F`. V2 and V3 were not changed. See `09_VERIFICATION_LEDGER.md`, `21_V4_VISUAL_RRL_AND_OBJECTIVE_REVIEW.md`, and `MD Files/figures_v4/README.md` for render evidence and open limits. The candidate is not institutional approval or validation of the thesis claims.
## Final V4 map correction (2026-10-28) — supersedes the preliminary V4 map block above

Final V4 DOCX SHA-256 is `B5D61F760D43E201D3F37382852E9B1B1CC75D39758BFC8006D5E5927C060CCD` (736,229 bytes), exported by Word 16.0 to a 77-page US Letter QA PDF. Final chapter starts: I 1/physical 10; II 13/22; III 31/40; IV 57/66; V 58/67; References 59/68. Final figure pages: 1.1 p. 6, 1.2 p. 10, 3.1 p. 36, 3.2 p. 37, 3.3 p. 50. Final table pages: 1 p. 35, 2 p. 40, 3 p. 43, 4 p. 45–46. Static lists on Roman pages vii–viii were corrected and visually checked against the caption pages. V2 and V3 hashes remain unchanged; V2 remains approved and V4 remains a candidate. Structural count: 101 references, 77 unique DOI-bearing entries; full-text claim support remains incomplete. See `09_VERIFICATION_LEDGER.md` and `21_V4_VISUAL_RRL_AND_OBJECTIVE_REVIEW.md` for exact evidence limits and unresolved gates.
The reviewable PDF export is provided beside the DOCX at `Documents/The Real Research Paper/GPT Paper/SHM_Research_Aligned_Revision_Draft_v4.pdf` (1,254,568 bytes; SHA-256 `455F65A3DEC89C71C3FD44F7F40013603D14DC55441DC8B93D37679DA56A22E6`). It is the Word 16.0 77-page US Letter export verified with Poppler 26.07.0.

## Final V4 source-link correction (2026-10-28) — latest candidate identity

The Patinio (2025) PNA locator in V4 returned 404 and was replaced by the indexed Inquirer republication; direct browser opening returned 403, so the link is only partially verified. The final DOCX is 736,259 bytes, SHA-256 `D2CD42918960792AD91B55F0C1BD721EA0110291E89360E8B123633C4D0CED83`. Its 77-page PDF preview is 1,254,697 bytes, SHA-256 `843EC606F074C1C03CA7F6F1FED368D9609D0444812BB27D9CE2E879F7579D32`. Chapter starts and figure/table pages remain those recorded in the preceding final map. V2 remains the approved source; V4 remains a review candidate.

## 2026-10-29 V4 figure-layout map refresh — latest candidate state

V4 is now a 79-page US Letter review candidate, DOCX 959,972 bytes (SHA-256 `28508C88652FAE1A1302694CB4D99B852F4A6F84C4388015BE94DF7440D921D7`) and PDF 1,341,944 bytes (SHA-256 `FD7A372BEB76BC3D36B4BA42E6260BFD00EEF9EAB1BDF2C453EEB6F97E0C07B8`). This entry supersedes earlier V4 hashes and pagination above. Chapter I–V start on printed pages 1, 13, 31, 59, and 60; References starts p. 61. Figures are 1.1 p. 6, 1.2 p. 10, 3.1 p. 36, 3.2–3.3 p. 37, 3.4 p. 39, and 3.5 p. 52. The two static figure/table lists match the rendered captions. IPO, system block diagram, and code flowchart use monochrome; the original colored bridge map and field workflow are restored. Schematic/PCB placeholders are embedded; a separate code-flow placeholder asset is retained alongside the actual code flowchart. V2/V3 remain unchanged. No code/CAD change or validation is implied. The inventory at `13_PROJECT_FILE_INVENTORY.md` was regenerated on 2026-10-29: 82 directories and 426 listed files. See `09`, `13`, and `21` for details.



## 2026-10-29 V5 annotated layout map — prior candidate snapshot

At that snapshot, V5 was the current separate layout review candidate, not the approved research source. It preserves the V4 text and bibliography while adjusting the abstract/glossary spacing, redrawing Figures 3.4–3.5 in monochrome, and aligning the Figure 3.4 List of Figures label. The abstract plus Keywords fit on Roman p. ix; the glossary flows across printed pp. 11–12; Chapter II begins separately on p. 13. V2–V4 hashes remain unchanged.

V5 is 79 physical US Letter pages. Printed/physical starts are Chapter I 1/10, II 13/22, III 31/40, IV 59/68, V 60/69, References 61/70. Figures 1.1, 1.2, 3.1, 3.2–3.3, 3.4, and 3.5 are on printed pages 6, 10, 36, 37, 39, and 52. Tables 1–4 are on printed pages 35, 42, 45, and 47. DOCX SHA-256 is `43D260EC5C1156BE2CC44C1D984651E77CF8676F92E47F814F7B081C01915759`; matching PDF SHA-256 is `26F744DAA298C87567B3D54E2CBDC3210FF8A76CE1BCE37CFD213E946CE6F273`. Refer to `23_V5_ANNOTATED_LAYOUT_AND_FIGURE_REVIEW.md` and `verification/v5_layout_verification_20261029.json` for checks and limits. The inventory currently records 84 directories and 468 files. No research/reference audit or institutional, field, code, or CAD verification was performed in this layout pass.

## Latest paper candidate: V6 annotated layout (2026-10-29)

V6 is the latest separate layout-review candidate, built from V5. V2 remains the approved source of research intent, and V2–V5 were preserved. V6 is an 80-page US Letter DOCX/PDF pair; it applies the latest figure-caption, glossary-spacing, and flowchart-layout comments without revising research claims, citations, methodology, firmware, PCB/CAD, or data. Figure captions use the number-plus-description form; the IPO callout note and Figure 3.5 bottom note are removed; all 14 definitions use 2.0 spacing with bold labels and regular meanings. The last glossary definition consequently occupies printed p. 13 by itself; Chapter II begins separately on printed p. 14 with continuous Arabic numbering.

V6 DOCX SHA-256: `967330865C6980EF4F6C7BB6885EF8FEE13B0FD74268D615AF744C198A48C9FD`. PDF SHA-256: `407F8CA20F24B4B8EA54705A4C6666F72C0103853E473A90B505BE8EDD8BE2B5`. The map, placeholders, static lists, monochrome figures, captions, glossary, and page map have recorded layout checks. The V6 report is `24_V6_ANNOTATED_LAYOUT_AND_FIGURE_REVIEW.md`; machine-readable evidence is `verification/v6_layout_verification_20261029.json`. The regenerated project inventory contains 88 directories and 593 listed files. V5 remains a preserved earlier candidate. This pass did not audit literature/citation support, ethics, privacy, Turnitin, adviser acceptance, code, CAD, hardware, permissions, or field data. Read `22_AI_FEEDBACK_AND_MISTAKE_LOG.md` for the updated direct preference and V6 correction history.


## Current paper candidate — V7 fact-check (2026-10-29)

The active approved research source remains `Documents/The Real Research Paper/GPT Paper/SHM_Research_Aligned_Revision_Draft_v2.docx`. V7 is a separate candidate at `Documents/The Real Research Paper/GPT Paper/SHM_Research_Aligned_Revision_Draft_v7.docx` with a matching 80-page PDF preview beside it. It derives from V6 and changes only nine bounded factual/claim paragraphs plus the Hidalgo-Fort reference author list. V7's map asset was restored byte-for-byte from V6 after a Word save downsampled it; all eight media parts then matched V6. The final render, hashes, exact claim dispositions, primary source links, page map, rejected/incomplete parser attempts, and open decisions are in `26_V6_FACT_CHECK_AND_V7_CORRECTIONS.md`, `09_VERIFICATION_LEDGER.md`, `10_RESEARCH_REFERENCE_AUDIT.md`, and the V7 addendum to `16_PAPER_CLAIM_AND_DECISION_LEDGER.md`.

This is targeted review evidence, not exhaustive full-text verification of 101 references. Firmware-method alignment, privacy/ethics/site/safety approvals, external bridge-baseline search, calibration/timing, physical/field validation, institutional stage, and Turnitin/AI-writing review remain open. Code and PCB were not changed.


## V7 follow-up source-check disposition (2026-10-29)

A second FHWA 2022 check initially misread an exact-search no-match. Section 3.8.3 explicitly lists 10-minute increments for the specified continuous-count-station AADT procedure. The proposed F11 rewrite was withdrawn; V7 was restored to the pre-F11 verified DOCX/PDF byte-for-byte. The original claim is supported only as a traffic-count interval precedent, not as validation of the study's vibration/count pairing. See `09`, `10`, `16`, `22`, `26`, and the machine-readable verification JSON.

## Final corrected PCB CAD delivery — 2026-10-29

Active artifact: `PCB Files/GPT Build - PCB/design/SHM_Node_R2.kicad_pcb`, SHA-256 `0ea352e982e6ccb87134d1d3dcef7bd3adb747efab5ba28b136cd1090f99540e`. The four final reference-label moves change the earlier promoted hash `804D5B67...`; components, pad nets, copper and outline are unchanged by those moves. Old source/report hashes are historical.

Exact evidence: `PCB Files/GPT Build - PCB/reports/reference_corrected/validation_20261029T145905461959Z/manifest.json`. KiCad 10.0.6 ERC/DRC/connectivity/parity and independent audit: zero findings; 233 numbered pads, 148 spec endpoints, firmware mappings, native USB/reserved pins, actual MPU center copper/paste and rule areas checked. Exact SHM_PCB_New 12-edge 79.50 × 50.45 mm outline. Baseline four ERC/five DRC ignored categories remain explicitly listed; no explicit exclusions/new suppressions. Report commands, timestamps and source/report hashes are retained.

Current recovery/navigation: hardware `docs/HANDOFF.md`, `CONTINUATION_PLAN.md`, `PROJECT_MAP.md`, `LAYOUT_REVIEW.md`, `RESEARCH_LEDGER.md`, `ERROR_LOG.md`, `BOM.md` and `PROTOTYPE_BRINGUP.md`. Active native files are in `design/`; staging in `design/reference_corrected/`; wrong 83 mm history in `design/superseded_wrong_83mm_outline/`. Run `tools/run_corrected_checks.py --active` for active files. Do not run legacy writers or regenerate over later manual work.

Remaining gates: fabricator stackup/USB impedance, exact remaining parts and DFM/stencil, enclosure/cable/mounting, thermal/current/USB/I2C/DRDY/FIFO, reference-frequency and field tests. No physical validation or fabrication release is claimed. Paper and firmware were not edited during this continuation. Top/bottom native renders and copper plots were visually inspected, and the existing schematic layout remains unchanged.

## Engineering audit follow-up — 2026-10-29

Hardware review: [engineering audit](../PCB%20Files/GPT%20Build%20-%20PCB/docs/ENGINEERING_AUDIT_20261029.md), [scope/plan](../PCB%20Files/GPT%20Build%20-%20PCB/docs/ENGINEERING_AUDIT_PLAN.md). The deeper read-only audit found issues beyond configured ERC/DRC: USB A-contact transition imbalance (4 D+ versus 2 D−), missing explicit impedance stackup, no local capacitor directly on the ESD VBUS net, J2-to-U3 nominal body separation about 5.18 mm (5.13 mm conservative F.Fab box) against the TDK 6 mm insertion-component guidance, and unresolved thermal/probe-access qualification. Nominal antenna overhang is 0.10 mm with no recorded tolerance budget. These are engineering concerns, not observed prototype failures. Active PCB remains unchanged at SHA-256 `0ea352e982e6ccb87134d1d3dcef7bd3adb747efab5ba28b136cd1090f99540e`; the earlier configured CAD pass remains bounded evidence.

The report maps ENG-01–ENG-13 to file evidence, source IDs E1–E9, equation IDs and closure steps. `tools/audit_engineering_geometry.py` measures paths, reference-fill samples, antenna geometry, test pads and insertion-component proximity; `tools/audit_engineering_math.py` records conditional power/thermal/I2C/RC arithmetic. Data is in `PCB Files/GPT Build - PCB/reports/engineering_audit/20261029/`. No physical tests or new CAD edits were performed.

