# V6 manuscript fact-check plan and correction gate

Prepared 2026-10-29 in response to the user's request to check the paper again for incorrect information and make supported corrections.

## Target and preservation

- Audit target: `Documents/The Real Research Paper/GPT Paper/SHM_Research_Aligned_Revision_Draft_v6.docx` and its matching PDF.
- Starting DOCX SHA-256: `967330865C6980EF4F6C7BB6885EF8FEE13B0FD74268D615AF744C198A48C9FD`.
- Starting PDF SHA-256: `407F8CA20F24B4B8EA54705A4C6666F72C0103853E473A90B505BE8EDD8BE2B5`.
- Preserve V2 as the approved research source and preserve all V2–V6 files. Any paper corrections will be made in a separate V7 review candidate; this does not imply approval or replace V2.
- Keep the scope bounded to the manuscript's factual, methodological, technical, statistical, causal, current-status, ethics/privacy, and traceability claims. Do not invent data, measurements, permissions, tests, sources, or institutional determinations.

## Audit sequence

1. Freeze and hash the V6 source pair; map its chapter, paragraph, table, figure, citation, and bibliography locations.
2. Reuse the prior P01–P50 claim ledger only when the exact V6 sentence, scope, and citation are unchanged. Recheck all material V6 claims; identify changed/added claims and source lineage from V2 through V6.
3. Compare manuscript claims with the current firmware, configuration/build artifacts, active KiCad design/spec, available test/DRC records, and actual data/permission records. Treat implementation, simulation, literature precedent, CAD output, and field evidence as separate forms of evidence.
4. For external claims, inspect primary papers, official government/standards/manufacturer sources, and the exact passage or technical table where available. Check corroborating or contradictory evidence. Record source version/date, access scope, exact claim fit, and source locator/URL/DOI.
5. Record each material claim with manuscript paragraph/page/section, claim text or faithful paraphrase, claimed evidence, evidence found, support boundary, status (`verified`, `partially verified`, `unverified`, `contradicted`, `not applicable`), confidence/scope, and closure evidence. Missing evidence is not proof of falsity or universal absence.
6. Before changing V6, log each proposed V7 correction and acceptance criterion. Apply only corrections supported by direct source evidence or an explicit current-code/design observation. For unresolved adviser/owner/ethics/site/data decisions, qualify the statement or leave it visibly open rather than guess.
7. Recheck all changed sentences against their cited source, recheck nearby citations and any affected references, compare paragraph text against V6, generate a new PDF with Word, and verify layout, citations and hashes. Preserve both the before/after claim ledger and failed-check history.
8. Update the project map, verification ledger, research/reference audit, feedback/mistake log, README, and file inventory after the audit/candidate is complete.

## Acceptance criteria

- Every material claim in Chapters I–V and front matter is mapped to an identified source, implementation, data record, owner/institution document, or explicitly listed unresolved question. All bibliography entries are mapped to in-text use and source-access status; an entry count alone does not pass.
- Citation existence/metadata is not treated as proof of claim support. A fact is not promoted to a requirement/conclusion without evidence in the relevant scope.
- Contradictions among the approved manuscript, V6 candidate, firmware, PCB, source literature, and governance records remain explicit until the appropriate owner/source resolves them.
- Only supported, bounded factual corrections are applied in a separate V7. Research design choices that require owner/adviser/institution decisions are not silently changed.
- V7's text diff is explainable; bibliography and citations have source-level records; exact source/output hashes and render checks are retained; open limits are stated.

## Initial source map

- Approved method: `Documents/The Real Research Paper/GPT Paper/SHM_Research_Aligned_Revision_Draft_v2.docx` (owner approval recorded in project handoff; preserve).
- Current review candidate: V6 DOCX/PDF above. V6's previous changes were layout-only.
- Firmware: `Code Files/GPT Build/firmware/SHM_Capstone/`; especially `config.h`, `hardware_profile.h`, `imu_mpu6050.*`, `acquisition.*`, `dsp.*`, `session.*`, `baseline.*`, `storage.*`, and `web_server.*`.
- Current hardware design: `PCB Files/GPT Build - PCB/design/SHM_Node_R2.kicad_sch`, `SHM_Node_R2.kicad_pcb`, `circuit_spec.json`, with the separately identified reference-corrected candidate and actual verification reports kept distinct.
- Prior source/claim work: `10_RESEARCH_REFERENCE_AUDIT.md`, `15_PAPER_REVIEW_AND_INTEGRITY_GATES.md`, `16_PAPER_CLAIM_AND_DECISION_LEDGER.md`, `18_RRL_SUPPORT_AND_GAP_SEARCH.md`, `20_V3_REVIEW_CANDIDATE_AND_RRL_BATCH.md`, `21_V4_VISUAL_RRL_AND_OBJECTIVE_REVIEW.md`, and `09_VERIFICATION_LEDGER.md`.
- Primary external evidence sources will be discovered and checked per claim; source-specific support limits and access failures will be retained.

## Status at plan creation

No V6 paper text has been changed for this audit. The current V6 factual/source audit is incomplete. The prior P01–P50 register and 101-entry bibliography provide useful starting points, not a certification. V6 layout verification does not verify the paper's facts, citations, ethics, Turnitin, or research validity.
