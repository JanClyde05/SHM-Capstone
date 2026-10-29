# Problem statement, revision candidates, and gated plan

Prepared 2026-10-26 from the approved draft, firmware, current KiCad design, existing reports, legacy notes, and external-source review; updated 2026-10-27 for reviewer notes and a separately authorized v3 paper/RRL candidate. V2 remains approved and unchanged; firmware and PCB remain unchanged.

## Problem statement

The project has a current proposal, firmware prototype, and KiCad node, but the documentation set mixes earlier and current designs. The central immediate risk is traceability: a reader/AI can confuse proposed scientific methods with implemented defaults, or mistake build/CAD checks and literature precedent for physical/field validation. The key method mismatch is manuscript median aggregation over valid windows versus firmware rejection unless all ten windows are valid; the paper also says the window function is pilot-selected while current code fixes symmetric Hann. The paper audit additionally found unresolved front-matter placeholders, overbroad “localized”/“real-time” definitions, operator-name collection without a project privacy/retention plan, and no located ethics/site determination or Turnitin report. Sampling, pilot settings, field permissions/mounting, and hardware validation remain open. Therefore, future data collection, paper-submission claims, or implementation should be gated on the relevant method, institutional and field decisions.

## Revision candidates

| ID | Candidate issue | Evidence | Priority | Decision / acceptance criterion |
|---|---|---|---|---|
| R1 | Resolve valid-window aggregation conflict | Manuscript says median of valid windows; `session.cpp` requires all 10 | P0 before collecting research data | Owner approves a single protocol; manuscript, firmware and session metadata agree; malformed/incomplete-session behavior is explicitly defined. |
| R2 | Freeze frequency estimator naming and analysis settings | Code selects maximum positive in-band FFT bin with hardcoded symmetric Hann; band/QC defaults remain prototype settings | P0 before collection | Pilot protocol records validated band, window, sampling-rate source, QC rules and estimator name. Do not use “modal frequency” as validated output without appropriate reference evidence. |
| R3 | Establish sampling characterization | Three devices are sequentially read; nominal 100 Hz and scheduler tolerance do not prove measured rate, jitter, gaps, or device-to-device alignment | P0 before data interpretation | Bench evidence documents timestamps, actual per-device rate, jitter, gaps, and inter-device offset with acceptance thresholds justified for this method. |
| R4 | Confirm deployment conditions | Reviewed draft has one fixed roadway-deck station; exact member/span/mount and access approval unresolved | P0 before field deployment | Record written access/installation permissions, location/mount plan, sensor orientation, safety plan, and environmental/traffic metadata. |
| R5 | Define traffic classification and sample plan | Counts/groups locally pilot-defined; NIST guidance makes sample size depend on variance/effect/power; up to nine related channel-axis tests are contemplated | P0 before inferential claims | Predeclare group operational rules, observer/count procedure, pairing window, exclusions, replication unit, pilot variance, primary outcome/test family, sample-size rationale, and multiplicity handling. |
| R6 | Verify assembled hardware and storage | Pin map and topology are source-level; no physical bring-up evidence located; raw data buffered in PSRAM then stored in LittleFS | P1 before sustained capture | Confirm actual part markings and board assembly; bench-test I2C identity, sensor configuration, power, timing, filesystem capacity/integrity and recovery on reset. |
| R7 | Clean citation list and claim attribution | V3 has 100 entries (40 additions), 76 unique DOI strings and no duplicate DOI; known broken/old links were repaired or replaced in V3; Sohn (2004) access remains limited; source-level claim audit and style review remain incomplete (`10`, `18`, `20`) | P1 before thesis submission | Audit each material in-text claim against the exact source passage; resolve source-access limits and metadata; apply required reference style; distinguish precedent from project validation. |
| R8 | Sync stale project documentation | Old `MD Files/01`–`07` and prior PCB handoffs disagree with current method/design | P1 | Preserve historical files; mark/update current pointers or create dated supersession notes only after owner review. Do not silently overwrite provenance. |
| R9 | Assess PCB design beyond ERC/DRC | Current CLI outputs show no active rule violations; ignored categories remain; no fab/assembly checks or physical test | P1 before fabrication | Review every exclusion and footprints/net/component choices; complete manufacturer/BOM/package review, design-for-fabrication checks and assembly/bring-up plan. User's fabrication decision and supplier constraints required. |
| R10 | Resolve proposal front matter and generic template filler | V2 has a “final defense” approval sheet with blank grade, generic panel-name placeholders and dated dean acceptance; Dedication/Acknowledgement are template instructions; proposal-stage handoff conflicts in appearance | P1 before institutional submission | Adviser/department confirms correct proposal/final-defense format and names/date. Do not fabricate approval or personal dedication/thanks. |
| R11 | Define precise “localized” and “real-time” claims | Glossary claims local/low-cost/non-proprietary feasibility without cost/sourcing evidence; firmware provides live readings/latest completed window but final session result is after capture | P1 before title/abstract finalization | Supply a documented operational definition, cost/supplier basis and measured latency, or qualify the terminology. Do not infer feasibility from component selection. |
| R12 | Decide whether/how operator identity and incidental images are collected | UI requires an operator name and firmware saves it; paper only discusses road-user identifiers and limited photos/video; no full retention/access/deletion plan located | P0 before data collection | Prefer a coded operator identifier when adequate; get CSU DPO/privacy advice and document data categories, purpose, access, safeguards, backup, retention, deletion and image minimization. |
| R13 | Obtain ethics-office classification; do not self-declare exemption | No written REC/ethics determination found; protocol has observer/operator, traffic observation and potential identifiable imagery; current CSU process not verified | P0 before data collection | Ask current CSU research/ethics office or adviser for written review/exemption/not-in-scope determination as applicable. This is separate from site authorization and safety clearance. |
| R14 | Complete actual Turnitin/similarity review if required by institution | No Similarity Report/AI report found; Turnitin states similarity is not plagiarism and settings include storage options | P1 before submission if required | Use authorized institutional workflow; record assignment/account, comparison and repository settings, exclusions and report; manually inspect matches. No universal score or AI authorship pass is claimed. |
| R15 | Disposition the reviewer correction register | The user authorized a separate v3 candidate; item-by-item dispositions are in `19`/`20`; C20–C22 received bounded evidence/caveat edits, while their arrow intent remains ambiguous; v2 remains unchanged | P0 before adopting v3 as the approved manuscript | Obtain owner/adviser review of v3; resolve or explicitly retain ambiguous C02/C07/C08/C14 and the C20–C22 arrow intent, plus method/code/institutional questions; preserve v2 and record the accepted version/hash. |

## Execution gates

**Gate A — Map and evidence (complete for this documentation pass).** Maintain file inventory, identify active files, compare method/code/CAD, record source and hashes. Re-map after any change.

**Gate B — Resolve scientific method before collection.** Resolve R1–R5 and the method-related correction items in R15; update methods, figures, firmware requirements, data schema and collection protocol consistently. No inferential claim or collection plan should rely on unresolved placeholders.

**Gate C — Bench validation before bridge use.** Resolve R6 and establish measurable acceptance criteria for actual sampling, sensor response, storage and estimator behavior. Bench/reference tests are distinct from literature citations and CAD checks.

**Gate D — Deployment and ethics/safety readiness.** Resolve bridge access, mounting, safety, permissions, and data collection responsibilities. Do not infer permission from the existence of a proposal.

**Gate D2 — Institutional integrity and privacy.** Obtain the current institutional ethics determination, data-privacy guidance and data-stewardship plan; resolve the operator-name field and incidental imagery. A Turnitin report, if required, is a separate authorized task and must be human-reviewed. No clearance is claimed without the record.

**Gate E — Targeted implementation.** Once every relevant correction has a recorded disposition, a concrete change is requested, and relevant evidence/owner gates are met, modify only the mapped files. Preserve old sources, update a change log, and verify against acceptance criteria. If the evidence supports more than one choice, document options and obtain the owner decision rather than hardcoding a preference.

**Gate F — Re-map and handoff.** Regenerate inventory and traceability; repeat relevant static/automated/bench checks as authorized; distinguish results from unperformed checks; publish exact evidence and remaining limitations.

## Recommended next decisions

1. Confirm whether the approved method's “median of valid windows” is intended to permit fewer than ten valid windows or whether all ten are required.
2. Confirm the target deployed module and board assembly status; identify mount location and permission status.
3. Approve a pilot protocol and accept/reject criteria before freezing settings or generating research data.
4. Decide whether the existing R2 board is a prototype for bench work or a fabrication candidate; current clean DRC/ERC alone does not answer that.
5. Ask the adviser/department to confirm the approval-sheet format and the CSU ethics/privacy route before any bridge collection.
6. Resolve the valid-window and Hann-window decisions and revise the method/code mapping consistently before freezing a campaign.
7. Review the separate v3 candidate and `20_V3_REVIEW_CANDIDATE_AND_RRL_BATCH.md`; resolve or retain the remaining ambiguous notes and C20–C22 arrow intent, then record adviser/owner acceptance before replacing v2 as the approved source of truth.

## Work authorized by this audit

The 2026-10-27 user instruction separately authorized a v3 paper candidate with bounded correction-note edits and 40 relevant RRL additions. V2 remains unchanged as the approved source of truth. Documentation/maps/logs were updated; no firmware or CAD source was changed. The candidate does not close the method, site, ethics/privacy, bench, reference full-text, or Turnitin gates. Code/PCB implementation and field collection remain separately gated.


## 2026-10-28 V3 candidate handoff status

The V3 review candidate has been layout- and package-checked at 76 pages; see `09_VERIFICATION_LEDGER.md` and `20_V3_REVIEW_CANDIDATE_AND_RRL_BATCH.md`. V2 remains the approved source. The candidate still must not be treated as an approved or submission-ready thesis: complete the reference claim-support review, obtain owner/adviser review, resolve method/firmware conflicts and pilot/statistical decisions, and close the site, safety, ethics/privacy, physical-validation and institutional integrity gates before dependent execution. No code or PCB changed in this continuation.

## 2026-10-28 V4 visual/RRL candidate status

The user's later figure/RRL/objective request produced a separate V4 review candidate; details and acceptance results are in `09_VERIFICATION_LEDGER.md` and `21_V4_VISUAL_RRL_AND_OBJECTIVE_REVIEW.md`. V4 is 77 pages with 101 references, 77 unique DOI-bearing entries, monochrome figures/tables, a current-firmware flowchart, and updated claim-adjacent citations. V2 remains the approved source; V3 and V4 are review candidates only. This paper/layout work does not close the research-method, source-passage, site/safety, ethics/privacy, hardware/field, Turnitin, or AI-writing gates. Before data collection, resolve the all-ten-valid versus median-valid-window and hardcoded-Hann versus pilot-selected-window conflicts against the owner-approved method. No code or PCB modification was included in V4.

## 2026-10-28 final V4 closeout

The final V4 reflow is 77 pages with corrected static figure/table lists. Printed chapter starts: I 1, II 13, III 31, IV 57, V 58; References 59. Final DOCX SHA-256: `B5D61F760D43E201D3F37382852E9B1B1CC75D39758BFC8006D5E5927C060CCD`. V2 remains approved and unchanged; V4 remains a review candidate. The remaining source-passage, firmware/method, pilot/statistical, owner/adviser, frontmatter, site/safety, ethics/privacy, physical-validation, Turnitin, and AI-writing gates remain open. See `09`, `08`, and `21`.

A matching 77-page PDF preview is available beside the V4 DOCX for stable visual review; see `09_VERIFICATION_LEDGER.md` for its hash.

Latest V4 DOCX/PDF hashes after the logged reference-locator repair are in `09_VERIFICATION_LEDGER.md`. The DOI metadata screen matched all 77 DOI records; exact passage support remains open. Do not start dependent field execution until the method/firmware, pilot/statistical, site/safety, ethics/privacy, and owner approval gates are closed.


## Authorized PCB reference correction — 2026-10-28

The owner explicitly identifies `PCB Files/Reference PCB (OLD Version)/Thesis/SHM_PCB_New/` as the intended old design. Earlier use of the parent `Thesis/Thesis.kicad_pcb` outline is contradicted as a reference selection. This direct correction authorizes the dependent reference/geometry/layout changes; unrelated research, firmware, and paper gates remain unchanged.

Proposed bounded change: preserve the previous R2 design and reports, use the direct `SHM_PCB_New.kicad_pcb` and `.kicad_sch` as visual/geometric reference, and construct a separate corrected-outline candidate before replacing active routing. Preserve the current electrical topology and firmware pin contract. Acceptance: exact copied 12-edge geometry (79.50 x 50.45 mm centerline), unchanged reference hashes, revised placements within the smaller shape, documented antenna/MEMS/mounting exclusions, net correlation, fresh ERC/DRC and visual review. Previous 83.6 x 83.1 mm board checks do not validate this geometry. Controlled impedance, thermal and bench/field evidence remain separate open gates.

## V4 figure-layout pass closed (2026-10-29)

The user-authorized centering, selective-color restoration, and placeholder work is complete in V4 and logged in `09_VERIFICATION_LEDGER.md`/`21_V4_VISUAL_RRL_AND_OBJECTIVE_REVIEW.md`. The final page map and file hashes are in `08_PROJECT_MAP_AND_SOURCE_OF_TRUTH.md`. No code or CAD edit was required. Treat V4 as a review candidate; do not promote it over V2 without owner/adviser adoption. Literature, claims, methods, ethics/privacy, site/safety, and physical validation remain independently gated.

## Final corrected PCB CAD delivery — 2026-10-29

Active artifact: `PCB Files/GPT Build - PCB/design/SHM_Node_R2.kicad_pcb`, SHA-256 `0ea352e982e6ccb87134d1d3dcef7bd3adb747efab5ba28b136cd1090f99540e`. The four final reference-label moves change the earlier promoted hash `804D5B67...`; components, pad nets, copper and outline are unchanged by those moves. Old source/report hashes are historical.

Exact evidence: `PCB Files/GPT Build - PCB/reports/reference_corrected/validation_20261029T145905461959Z/manifest.json`. KiCad 10.0.6 ERC/DRC/connectivity/parity and independent audit: zero findings; 233 numbered pads, 148 spec endpoints, firmware mappings, native USB/reserved pins, actual MPU center copper/paste and rule areas checked. Exact SHM_PCB_New 12-edge 79.50 × 50.45 mm outline. Baseline four ERC/five DRC ignored categories remain explicitly listed; no explicit exclusions/new suppressions. Report commands, timestamps and source/report hashes are retained.

Current recovery/navigation: hardware `docs/HANDOFF.md`, `CONTINUATION_PLAN.md`, `PROJECT_MAP.md`, `LAYOUT_REVIEW.md`, `RESEARCH_LEDGER.md`, `ERROR_LOG.md`, `BOM.md` and `PROTOTYPE_BRINGUP.md`. Active native files are in `design/`; staging in `design/reference_corrected/`; wrong 83 mm history in `design/superseded_wrong_83mm_outline/`. Run `tools/run_corrected_checks.py --active` for active files. Do not run legacy writers or regenerate over later manual work.

Remaining gates: fabricator stackup/USB impedance, exact remaining parts and DFM/stencil, enclosure/cable/mounting, thermal/current/USB/I2C/DRDY/FIFO, reference-frequency and field tests. No physical validation or fabrication release is claimed. Paper and firmware were not edited during this continuation. Top/bottom native renders and copper plots were visually inspected, and the existing schematic layout remains unchanged.

## Engineering audit follow-up — 2026-10-29

Hardware review: [engineering audit](../PCB%20Files/GPT%20Build%20-%20PCB/docs/ENGINEERING_AUDIT_20261029.md), [scope/plan](../PCB%20Files/GPT%20Build%20-%20PCB/docs/ENGINEERING_AUDIT_PLAN.md). The deeper read-only audit found issues beyond configured ERC/DRC: USB A-contact transition imbalance (4 D+ versus 2 D−), missing explicit impedance stackup, no local capacitor directly on the ESD VBUS net, J2-to-U3 nominal body separation about 5.18 mm (5.13 mm conservative F.Fab box) against the TDK 6 mm insertion-component guidance, and unresolved thermal/probe-access qualification. Nominal antenna overhang is 0.10 mm with no recorded tolerance budget. These are engineering concerns, not observed prototype failures. Active PCB remains unchanged at SHA-256 `0ea352e982e6ccb87134d1d3dcef7bd3adb747efab5ba28b136cd1090f99540e`; the earlier configured CAD pass remains bounded evidence.

The report maps ENG-01–ENG-13 to file evidence, source IDs E1–E9, equation IDs and closure steps. `tools/audit_engineering_geometry.py` measures paths, reference-fill samples, antenna geometry, test pads and insertion-component proximity; `tools/audit_engineering_math.py` records conditional power/thermal/I2C/RC arithmetic. Data is in `PCB Files/GPT Build - PCB/reports/engineering_audit/20261029/`. No physical tests or new CAD edits were performed.

Next hardware work is bounded by the audit: plan a separate candidate for ESD bypass and header clearance; select real stackup/remaining parts; revise USB with balanced transitions and verified geometry; resolve power/source/ambient and mounting/access limits. Synchronize schematic/spec/netlist/BOM, then rerun ERC/DRC/parity and independent checks. A nominal barrel-length correction is not permission to add arbitrary meanders. Physical qualification remains a separate gate.

