# Engr. May Anne Valencia correction-note register

> **Current update (2026-10-27):** the initial transcription-only scope and “not applied” statuses below are historical. A later direct user instruction authorized a separate v3 review candidate. Clear or bounded notes were applied to that candidate, uncertain notes remain deferred, and the approved v2 DOCX remains unchanged. See `20_V3_REVIEW_CANDIDATE_AND_RRL_BATCH.md` for C01–C26 dispositions, the new RRL batch, hashes, and QA.

Review log created 2026-10-27 (Asia/Manila) from the marked-up manuscript PDF supplied by the user. This register records the corrections before any manuscript change.

## Authority, provenance, and limits

- Current user request: log and map the correction notes first. This authorizes transcription and project documentation only; it does not authorize applying these marks to the active DOCX, firmware, or PCB.
- Reviewer attribution: the user identifies the handwritten review as checked by Engr. May Anne Valencia. This attribution comes from the user; it is not confirmed by the PDF metadata.
- Marked-up source: Documents/The Real Research Paper/GPT Paper/Corrections for the Paper/SHM_Research_Aligned_Revision_Draft_v2.pdf
- Active draft to which the notes appear to refer: Documents/The Real Research Paper/GPT Paper/SHM_Research_Aligned_Revision_Draft_v2.docx
- The PDF has 65 pages. Its PDF physical page number differs from the manuscript’s printed page number. Each entry below gives both where available.
- PDF metadata: Microsoft Word 2016 producer/creator; creation and modification time 2026-10-26 14:36:54 +08:00; the Author field contains an email address and does not identify who made the handwritten marks. The address is omitted here because it is not needed to interpret the corrections.
- SHA-256 of marked-up PDF: 64BE08E43159969BAD3F6DDDEDC5016092809DFFA6BAF20844FE6E7AFB698AA1.
- SHA-256 of active DOCX at review: B09C741309444DAB16ACA6957250217CB776E310C20459820547AA747264CB42.
- pypdf 6.10.0 found handwritten Ink annotation objects on PDF pages 2, 11, 12, 14, 15, 16, 19, 20, 21, 22, 23, 40, 42, 43, 44, 45, 46, 47, 48, and 51. The annotation objects have no searchable comment text; they were read from page renderings.
- Poppler pdftoppm 26.07.0 rendered the marked pages at 165 dpi. It emitted “Bad block header in flate stream” warnings on embedded streams, although the marked text/pages used for this transcription rendered visibly. Preserve and consult the original PDF for any disputed reading. Ambiguous marks are explicitly identified below.
- This was a transcription and mapping pass, not a fresh literature or primary-source verification. No claim is marked verified solely because the reviewer circled or requested a change. Existing claim and evidence records remain controlling.

### Status key

- **Captured — clear:** the visible note is readable; its eventual disposition still needs to be recorded.
- **Captured — partial/ambiguous:** the target or intended change is not precise enough to apply without clarification.
- **Evidence follow-up:** the mark requests support or concerns a claim/method that must be traced to the active paper, source, code, design, or data before revision.
- **Not applied:** no correction in this register has been applied to the active manuscript.

## Correction register

### C01 — Approval-sheet adviser name

- **Location:** PDF p. 2; printed page ii; Approval Sheet, adviser line.
- **Visible mark:** handwritten name appears to read “R. Christopher Capili” over the printed “ENGR. CHRISTOPHER R. CAPILI.”
- **Correction target:** confirm the adviser’s official name format and correct the line only from an authoritative department/adviser record.
- **Status:** Captured — partial/ambiguous. The handwriting is legible enough to identify a proposed name/order change, but the official name and intended ordering are not independently established. The approval sheet’s proposal/final-defense stage is separately tracked in 15_PAPER_REVIEW_AND_INTEGRITY_GATES.md and decision D06 in 16_PAPER_CLAIM_AND_DECISION_LEDGER.md.
- **Disposition:** Not applied.

### C02 — Approval-sheet department-chair name

- **Location:** PDF p. 2; printed page ii; Approval Sheet, Department Chair line.
- **Visible mark:** handwritten spelling appears to read “MALLILLIN” above the printed name, apparently adding or emphasizing an L.
- **Correction target:** compare with the official Cagayan State University name/role listing and correct spelling only when confirmed.
- **Status:** Captured — partial. The printed and handwritten spellings are difficult to distinguish at the marked resolution; do not infer a preferred spelling from the annotation alone.
- **Disposition:** Not applied.

### C03 — Add support for broad bridge and hazard statements

- **Location:** PDF p. 11; printed p. 1; Chapter I, §1.1 Introduction, opening paragraph.
- **Visible mark:** several broad statements are underlined, with the note “Cite some references as proof.”
- **Correction target:** trace each proposition separately (bridge importance, Philippine hazard exposure, deterioration under environmental/operational stress, and value of monitoring) to sources that actually support it. Existing citations at the paragraph end do not establish that every clause is supported.
- **Verification path:** inspect the cited sources and the claim-by-claim literature records in 10_RESEARCH_REFERENCE_AUDIT.md and 18_RRL_SUPPORT_AND_GAP_SEARCH.md; add or revise citations only after matching source text to each claim. Search for contrary/qualifying evidence as required by the project rules.
- **Status:** Evidence follow-up; no new source was checked in this transcription pass.
- **Disposition:** Not applied.

### C04 — Clarify the Cabagan Bridge cause-assessment sentence

- **Location:** PDF p. 11; printed p. 1; §1.1 paragraph on the February 2025 Cabagan–Sta. Maria Bridge collapse.
- **Visible mark:** “was assessing the cause” is circled; note: “What do you mean? Revise this into specific yet clearer sentence.”
- **Correction target:** state precisely what the cited agency/report said and when, with attribution; do not imply a determined cause or causal finding if the source only reports an ongoing assessment.
- **Verification path:** existing claim P05 in 16_PAPER_CLAIM_AND_DECISION_LEDGER.md bounds the report to event context and says cause is unsupported. Recheck the cited primary/reporting sources before changing wording.
- **Status:** Evidence follow-up; the reviewer’s request is clear, while acceptable replacement wording depends on the source.
- **Disposition:** Not applied.

### C05 — “either” to “the” in the collapse sentence

- **Location:** PDF p. 12; printed p. 2; sentence: “They do not establish that frequency monitoring could have predicted or prevented either collapse.”
- **Visible mark:** “either” is circled, and handwritten “the” appears above it.
- **Correction target:** reviewer appears to request replacing “either” with “the.” The surrounding text refers to two collapse events, so a singular “the collapse” may leave the referent unclear. Confirm intended meaning and retain the limitation that the cited events do not validate this prototype’s prediction/prevention capability.
- **Status:** Captured — partial/ambiguous; literal substitution is visible, but the intended referent is not settled.
- **Disposition:** Not applied.

### C06 — Punctuation around “therefore”

- **Location:** PDF p. 12; printed p. 2; “The present study therefore addresses a narrower task.”
- **Visible mark:** red comma marks appear after “study” and “therefore.”
- **Correction target:** punctuation appears to request “The present study, therefore, addresses …”
- **Status:** Captured — clear editorial note.
- **Disposition:** Not applied.

### C07 — Mark after Objective 1 punctuation

- **Location:** PDF p. 14; printed p. 4; Objective 1 ending “…evaluate record completeness and timing;”
- **Visible mark:** a red curved/tick-like mark appears after the semicolon; no legible wording accompanies it.
- **Correction target:** unknown; the punctuation mark alone does not establish whether to keep, change, or remove the semicolon.
- **Status:** Captured — ambiguous.
- **Disposition:** Not applied; request clarification if this punctuation is to be changed.

### C08 — Possible “and” insertion after “axis”

- **Location:** PDF p. 15; printed p. 5; Objective 2 ending “…each traffic group, onboard channel, and axis.”
- **Visible mark:** handwritten punctuation and “and” appear after “axis.”
- **Correction target:** unclear because the printed list already contains a conjunction before “axis” and the objective ends there. Do not insert a second conjunction or extend the list without knowing what item is intended.
- **Status:** Captured — ambiguous.
- **Disposition:** Not applied.

### C09 — Choose one framework label

- **Location:** PDF p. 15; printed p. 5; §1.4 heading “Conceptual or Theoretical Framework of the Study.”
- **Visible mark:** heading is circled and the note reads “choose one only.”
- **Correction target:** select either “Conceptual Framework” or “Theoretical Framework,” then align the section text, diagram, and references with that choice. The current section calls the IPO diagram a conceptual framework, but the final classification remains an author/adviser decision.
- **Status:** Captured — clear request; substantive framing decision remains open.
- **Disposition:** Not applied.

### C10 — Clarify whether Figure 1 is the study-conduct process

- **Location:** PDF p. 16; printed p. 6; Figure 1, IPO framework and process column.
- **Visible mark:** process column is circled; note asks, “Is this the process on how you will conduct the study?”
- **Correction target:** distinguish the system’s input/processing/output pipeline from the research procedure. Check the figure against Chapter III’s field protocol, including permissions, site/setup, concurrent traffic tally, fixed acquisition, QC/exclusions, processing, and analysis.
- **Code/PCB trace:** compare the depicted sequential three-channel scan, 600-second session, ten 60-second windows, and estimator with current firmware and the active R2 design; see 08_PROJECT_MAP_AND_SOURCE_OF_TRUTH.md and claim decisions P01–P03 and P23–P26 in 16_PAPER_CLAIM_AND_DECISION_LEDGER.md. A figure must not imply a physical validation or behavior absent from the current sources.
- **Status:** Evidence follow-up; reviewer question is clear, but the figure’s intended role needs an explicit decision and traceability check.
- **Disposition:** Not applied.

### C11 — Locate Figure 2 in relation to the text

- **Location:** PDF p. 19; printed p. 9; §1.6 Scope and Delimitation, Figure 2 callout.
- **Visible mark:** “Figure 2” is circled; note reads “Where is this in this chapter?”
- **Correction target:** map the callout to the actual figure and decide whether the map belongs near this Chapter I discussion or whether the text should point clearly to its later location. In this PDF, the map caption appears on printed p. 30 in Chapter III.
- **Status:** Captured — clear question; layout/cross-reference disposition remains open.
- **Disposition:** Not applied.

### C12 — Bold “Baseline Frequency Range”

- **Location:** PDF p. 20; printed p. 10; §1.7 Definition of Terms.
- **Visible mark:** term is underlined; note reads “make it bold.”
- **Correction target:** apply consistent term-label formatting without bolding the definition body unless the approved style requires it.
- **Status:** Captured — clear formatting note.
- **Disposition:** Not applied.

### C13 — Bold selected glossary labels; resolve MEMS IMU styling

- **Location:** PDF p. 21; printed p. 11; §1.7 Definition of Terms.
- **Visible marks:** “BOLD” notes for Frequency Monitoring, Dominant Spectral-Frequency Indicator, and Natural Frequency; the MEMS IMU entry is circled with “ADD BOLD.”
- **Correction target:** make glossary term labels visually consistent. In the rendering, the MEMS IMU entry appears bold italic across both label and definition, unlike adjacent entries; confirm whether the note means bold only the label and return the definition body to the normal style.
- **Status:** Captured — clear for the listed labels; MEMS IMU scope is partially ambiguous because it already renders bold.
- **Disposition:** Not applied.

### C14 — Unlabeled upward arrow in glossary whitespace

- **Location:** PDF p. 22; printed p. 12; large blank area beneath the Vibration Signal definition.
- **Visible mark:** long upward arrow through the blank lower area; no words.
- **Correction target:** likely a pagination/placement cue, but the mark does not identify what content should move. Printed p. 13 begins with the Traffic-count group definition and then Chapter II.
- **Status:** Captured — ambiguous visual mark only.
- **Disposition:** Not applied; confirm intended target before moving content.

### C15 — Bold “Traffic-count group”

- **Location:** PDF p. 23; printed p. 13; definition preceding Chapter II.
- **Visible mark:** term is underlined; handwritten note appears to say “BOLD.”
- **Correction target:** format the term label consistently with the glossary entries if that is the intended note.
- **Status:** Captured — likely clear; handwriting is read as “BOLD” in context of the other explicit bold notes.
- **Disposition:** Not applied.

### C16 — Start Chapter II on the next page

- **Location:** PDF p. 23; printed p. 13; transition from final glossary definition to Chapter II.
- **Visible mark:** note beside the Chapter II heading reads “next page.”
- **Correction target:** insert a page break before the Chapter II heading so the chapter begins on a new page, subject to the institution’s formatting rules.
- **Status:** Captured — clear layout request.
- **Disposition:** Not applied.

### C17 — Add more references in Chapter II

- **Location:** PDF p. 23; printed p. 13; Chapter II opening and “2.1 Introduction.”
- **Visible mark:** note reads “add more references in this chapter.”
- **Correction target:** identify unsupported or under-supported RRL claims and add only relevant sources that support the specific statements. The number of citations by itself is not a verification criterion; include limitations and contradictory findings where relevant.
- **Verification path:** use 10_RESEARCH_REFERENCE_AUDIT.md, 16_PAPER_CLAIM_AND_DECISION_LEDGER.md, and 18_RRL_SUPPORT_AND_GAP_SEARCH.md; the earlier user request specifically prioritizes unsupported, weak, and unanswered claims.
- **Status:** Evidence follow-up; no new literature was searched for this transcription-only pass.
- **Disposition:** Not applied.

### C18 — Figure-number query/revision at the site map

- **Location:** PDF p. 40; printed p. 30; map caption currently begins “Figure 2.”
- **Visible mark:** printed “Figure 2” is circled; red handwriting appears to say “Figure 3.”
- **Correction target:** verify the figure order and every in-text cross-reference across the full draft before renumbering. The following block diagram is captioned Figure 3 and the field workflow is Figure 4, so a change here may require updating downstream captions and references; do not change a single caption in isolation.
- **Related note:** C11 asks where Figure 2 appears relative to Chapter I.
- **Status:** Captured — partial; “Figure 3” is the likely handwritten replacement, but the reason for the numbering change is not stated.
- **Disposition:** Not applied.

### C19 — Clarify “The final manuscript shall report”

- **Location:** PDF p. 42; printed p. 32; paragraph listing the confirmed board revision, part/model, site, sampling, session, software, storage, and library details.
- **Visible mark:** “The final manuscript” is circled; note reads “What do you mean?”
- **Correction target:** explain whether this is a commitment about later reporting, a requirement for the current methods section, or wording intended to direct the author. Do not fill in board/configuration values from assumptions; use confirmed design, bench, site, and pilot records.
- **Status:** Captured — clear question; intended temporal/document meaning is unresolved.
- **Disposition:** Not applied.

### C20 — Arrow at the measurement-session unit

- **Location:** PDF p. 43; printed p. 33; §3.5, sentence defining one valid 10-minute measurement session as the unit of observation.
- **Visible mark:** red arrow points to the sentence; no written comment.
- **Correction target:** no change can be inferred. Check that “valid session,” observation unit, and repeated-session definition agree with the approved analysis plan and firmware acceptance rules.
- **Status:** Captured — ambiguous arrow; evidence follow-up for the underlying method.
- **Disposition:** Not applied.

### C21 — Arrow at five sessions per traffic group

- **Location:** PDF p. 43; printed p. 33; §3.5, practical target of five valid 10-minute sessions in each of three local groups.
- **Visible mark:** red arrow points to the sentence; no written comment.
- **Correction target:** no specific correction is written. Preserve the current caveat that five is a practical completion target, not a power/sample-size justification. See claim P20 and revision candidate R5.
- **Status:** Captured — ambiguous arrow; sample-size interpretation remains bounded by existing audit.
- **Disposition:** Not applied.

### C22 — Arrow at session metadata requirements

- **Location:** PDF p. 44; printed p. 34; §3.5 session metadata paragraph.
- **Visible mark:** red arrow points to the paragraph listing time, session ID, count/rate, traffic group, weather/surface, station/orientation, channel status, sampling intervals, and unusual events; no written comment.
- **Correction target:** no specific change is legible. Trace every field against the actual firmware schema and the proposed field/data form before treating the list as implementable.
- **Code/PCB trace:** current implementation and output schema are mapped in 08_PROJECT_MAP_AND_SOURCE_OF_TRUTH.md. Do not claim that the firmware records a field merely because the paper lists it.
- **Status:** Captured — ambiguous arrow; evidence follow-up.
- **Disposition:** Not applied.

### C23 — Reword the coordination sentence

- **Location:** PDF p. 45; printed p. 35; §3.7 Data Gathering Procedure, opening paragraph.
- **Visible mark:** “The researchers shall coordinate” is struck through; “Coordination” is written above it; “will be conducted” is added at the end of the sentence after the list of emergency procedures.
- **Correction target:** the marks appear to recast the sentence as “Coordination … will be conducted,” but the final syntax and actor/responsibility are not fully specified. Preserve the requirement for written permission/site-safety arrangements and do not imply that permission has already been obtained.
- **Status:** Captured — partial; wording fragments are visible but a clean replacement sentence is not given.
- **Disposition:** Not applied.

### C24 — Show the vibration-acquisition procedure in table form

- **Location:** PDF p. 46; printed p. 36; §3.7, step 6 “Vibration acquisition.”
- **Visible mark:** the step is circled; note reads “show also in the table form.”
- **Correction target:** provide a table representation of the acquisition step if that is the intended request. First confirm which form/table is meant and derive fields/values from the approved protocol and actual code; do not repeat unverified timing, channel, or validity assumptions as facts.
- **Status:** Captured — clear request for a table presentation; target table/form is unspecified.
- **Disposition:** Not applied.

### C25 — Show traffic-group rules in table form

- **Location:** PDF p. 47–48; printed pp. 37–38; §3.8 Traffic-Condition Characterization and the count-cutoff/category rules.
- **Visible mark:** classification text is outlined; note on printed p. 38 reads “Show also in table form.”
- **Correction target:** present the local NEAR_ZERO, MEDIUM, and HEAVY rules in a table if requested, while preserving the fact that integer cutoffs come from pilot counts and are frozen before formal collection. Do not invent cutoffs or present the labels as universal traffic/load classes.
- **Verification path:** align with claim P19, the count procedure, and the pilot/frozen-cutoff gate in 12_EXECUTION_PLAN.md.
- **Status:** Captured — clear presentation request; numerical values remain unavailable until pilot data and owner decisions exist.
- **Disposition:** Not applied.

### C26 — Split the field workflow into distinct blocks

- **Location:** PDF p. 51; printed p. 41; Figure 4, Field Data Collection and Processing Flowchart.
- **Visible mark:** several activity boxes are circled; note reads “Separate the processes into blocks.”
- **Correction target:** reorganize the flowchart so preparation/site checks, acquisition and traffic tally, quality decision/rejection, storage/session closure, repetition/group targets, and baseline/review output are distinguishable. Preserve decision branches and keep the workflow consistent with §3.7, the data schema, and current firmware.
- **Status:** Captured — clear structural request; exact block boundaries need to be checked against the approved protocol and implementation.
- **Disposition:** Not applied.

## Cross-cutting mapping and closeout gates

1. **Introduction/citation edits:** C03, C04, and C17 require source-level verification against 10 and 18; support must attach to exact claims and the cited work’s limits.
2. **Research design and process figures:** C09–C11 and C18–C26 must be checked against the active method, 08 project traceability, 12 gates, firmware, and the current R2 schematic/PCB. The three sensors are co-located and polled sequentially; no figure may imply a spatial sensor array or unimplemented simultaneous capture.
3. **Statistical and traffic rules:** C20–C21 and C25 do not authorize changing the replication unit, five-session target, traffic cutoffs, or statistical claims. Keep descriptive/practical targets separate from sample-size justification.
4. **Field authorization:** C23–C24 concern a proposed procedure. Written bridge/site access, safety, ethics, and privacy determinations remain separate open gates in 15_PAPER_REVIEW_AND_INTEGRITY_GATES.md and 12_EXECUTION_PLAN.md.
5. **Formatting/layout:** C06, C12–C16 are editorial/layout requests, but the unclear items C07–C08 and C14 still need clarification before application.
6. **Reviewer decision record:** Before a future editing pass, add a disposition for every C01–C26 entry: accept, revise with rationale, defer, or reject; cite the evidence/owner decision and define a checkable acceptance criterion. Then edit only the authorized artifact, re-map it, and record the resulting hash/checks.

No external source was checked and no correction was implemented during this pass. “Captured” means the visible comment was transcribed/mapped, not that the underlying claim is true or the reviewer’s proposed solution is accepted.



## Superseding v3 candidate disposition (2026-10-27)

- The user clarified the adviser name as **Engr. Cristopher R. Capili**; v3 uses `ENGR. CRISTOPHER R. CAPILI`. This spelling is user-supplied, not independently confirmed from an official record.
- Reviewer attribution remains the user's statement that Engr. May Anne Valencia checked the notes. The PDF's metadata does not establish reviewer identity.
- Clear and evidence-bounded notes were applied to the separate `SHM_Research_Aligned_Revision_Draft_v3.docx`; ambiguous marks and the department-chair spelling remain open. The initial individual “Disposition: Not applied” labels in the transcription register record the state before the later authorization and must not be read as the current v3 result.
- The v3 candidate is not approved or field-ready. The detailed item-by-item disposition and unchanged v2 hash are in `20_V3_REVIEW_CANDIDATE_AND_RRL_BATCH.md`.

## 2026-10-27 follow-up: bounded treatment of C20–C22 and final pagination

The initial V3 disposition table marked C20–C22 deferred because the arrows alone did not specify the requested edit. After checking the mapped method text and relevant sources, the candidate now makes bounded edits while keeping the arrow intent unresolved: C20 identifies the 10-minute session as a study-defined protocol choice and cites Oth and Picozzi only as a one-minute-window precedent; C21 labels five sessions/group a practical target, not a power/sample-size justification; C22 keeps the metadata list and limits FHWA support to traffic-count fields. No source justifies the project's complete protocol. See `20` and `10` for source boundaries.

Final visual review also found that Chapter IV and V had been flowing after prior-chapter text. V3 now inserts page breaks before those headings. Printed page numbers remain continuous: Chapter I p. 1, II p. 14, III p. 33, IV p. 55, V p. 56. The updated contents and layout check are recorded in `09` and `20`. This is a V3-only correction; v2 remains unchanged.

## 2026-10-27 user-supplied correction batch (attributed to Engr. May Anne Valencia)

The user supplied an expanded, typed correction list and authorized applying the necessary fixes to the separate V3 candidate. These are user-provided notes attributed to Engr. May Anne Valencia; the attribution is not independently authenticated. V2 remains the approved source and must stay unchanged.

### Source review and current disposition before this edit batch

- **Already present in V3:** `ENGR. CRISTOPHER R. CAPILI` appears on the approval page and abstract; `ENGR. EULOGIO NEIL A. MALLILLIN` appears on the approval page; the objective uses the serial comma; §1.4 is titled **Conceptual Framework**; the four requested glossary labels are bold while their definitions are regular; the MEMS IMU term label is bold while its definition is regular; Chapter II starts on a separate page with continuous chapter page numbering; 100 references (including 40 prior additions) are present.
- **To apply to V3:** evidence-linked introduction revisions; clearer Cabagan collapse reporting; replace ambiguous “either collapse” with a plural, explicit referent; bullet-form IPO graphic; chapter-based figure identifiers and in-text/list-of-figures updates; glossary spacing/keep-together refinement; explicit acquisition and traffic count/rate tables; plain-language revision of the results-reporting sentence; first-line indents on the three specified methodology paragraphs; the requested coordination sentence; and diagrams rebuilt with one action per process box.
- **Reference updates:** PIA’s Buntun Bridge feature is already in the 100-entry list. Its visible byline is Oliver T. Baccay and its publication date is November 13, 2025; update the citation/reference author formatting accordingly. Replace Patinio’s secondary Inquirer republication locator with the original Philippine News Agency report (PNA article 1245082). This is a locator/source-quality repair, not a claim that the 100 references have all been full-text audited.

### External evidence checked for the introduction

- Baccay, O. T. (2025, November 13), Philippine Information Agency, “Buntun Bridge: The Steel Giant of Cagayan’s Lifeline,” https://pia.gov.ph/features/buntun-bridge-the-steel-giant-of-cagayans-lifeline/. The report says the bridge links Tuguegarao City and Solana and identifies commuters, emergency responders, and the business sector as relying on it. This supports the bounded connectivity/commuter/emergency/business context; it does not establish measured economic impact or engineering criticality.
- OECD (2024), *Economic Outlook for Southeast Asia, China and India 2024*, Philippines disaster-risk chapter, https://www.oecd.org/en/publications/economic-outlook-for-southeast-asia-china-and-india/volume-2024/issue-1_3bbe7dfe-en/full-report/component-10.html. It describes high exposure and explicitly lists typhoons, floods, earthquakes, volcanic eruptions, landslides, fires, and drought. It does not support the specific soil-erosion example in the prior reviewer wording; replace that example with landslides in the sentence supported by OECD.
- Patinio, F. (2025, February 28), Philippine News Agency, “DPWH: Assessment underway on cause of Isabela bridge collapse,” https://www.pna.gov.ph/articles/1245082. The report states that DPWH Region II said it had requested Bureau of Design and Bureau of Construction experts from the central office for further evaluation/assessment and that analysis to determine the cause was underway. It does not establish a final cause.

Web sources accessed 2026-10-27. Search/page text supports only the described scope above.

### Method/code boundary for the diagrams and tables

Current source mapping confirms three MPU-6050 ICs and one ESP32-S3-WROOM-1-N16R8 in `PCB Files/GPT Build - PCB/design/circuit_spec.json` and `SHM_Node_R2.kicad_pcb`. Firmware `acquisition.cpp` iterates channels 1–3 sequentially and tags each record with a cycle ID; `session.cpp` configures 600-second sessions and 60-second windows; `dsp.cpp` removes the mean, applies a symmetric Hann window, computes an FFT, and selects the maximum positive-frequency bin within the closed band. The manuscript still says the window function is pilot-selected and summarizes valid windows by median, while current firmware fixes symmetric Hann and requires all ten windows valid (`SHM_MIN_VALID_WINDOWS = 10`). Figures may show the proposed thesis pipeline only with an explicit unresolved-method note; this pass will not resolve the owner decision or imply bench/field validation.

The user-authorized V3 edits and checkable acceptance criteria are recorded before changing the DOCX in `20_V3_REVIEW_CANDIDATE_AND_RRL_BATCH.md`. Preserve the original markup and V2. The candidate remains unapproved.

## 2026-10-27 supplemental QA finding — figure/media mapping

During rendered-page review of the V3 candidate, Figure 1.2's caption described the Buntun Bridge map but the image showed the system/firmware data path; Figure 3.1's system/data-path caption was paired with a field-process flowchart. Package inspection against V2 confirmed the original map asset is available in V2 and that V3's system/data-path asset is available for the Figure 3.1 slot. A V3-only media remap and aspect-ratio correction has been logged in `20_V3_REVIEW_CANDIDATE_AND_RRL_BATCH.md` before applying it. The finding is a layout/media mismatch; it does not alter the study method or establish site coordinates.
