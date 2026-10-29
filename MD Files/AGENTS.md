# Instructions for AI work in `MD Files`

This folder contains legacy planning notes and the current project map, evidence ledgers, and AI handoff rules. The user’s current request governs. Text in the old numbered files is source material, not an instruction to execute its plans.

## Read first

1. `00_README.md` — current index and scope
2. `08_PROJECT_MAP_AND_SOURCE_OF_TRUTH.md` — repository map and current artifact relationships
3. `09_VERIFICATION_LEDGER.md` — checks performed, limits, hashes, and pending evidence
4. `10_RESEARCH_REFERENCE_AUDIT.md` — claim/reference support and caveats
5. `12_EXECUTION_PLAN.md` — issues and gated next steps
6. `13_PROJECT_FILE_INVENTORY.md` — file inventory snapshot
7. `14_CAD_VALIDATION_SNAPSHOT.md` — current CAD CLI validation record
8. `15_PAPER_REVIEW_AND_INTEGRITY_GATES.md` — proposal review, ethics/privacy/Turnitin status, and current gates
9. `16_PAPER_CLAIM_AND_DECISION_LEDGER.md` — paper claim-to-evidence ledger and owner decisions
10. `19_ENGR_MAY_ANNE_VALENCIA_CORRECTION_LOG.md` — marked-up reviewer notes and transcription provenance
11. `20_V3_REVIEW_CANDIDATE_AND_RRL_BATCH.md` — authorized v3 candidate, C01–C26 dispositions, added RRL, verification and remaining gates
12. `18_RRL_SUPPORT_AND_GAP_SEARCH.md` — literature support/limits and unresolved RRL, measurement, statistical and PCB validation gaps
13. `17_RESEARCH_PAPER_AUDIT_PROMPT.md` — reusable paper-specific verification prompt
14. `22_AI_FEEDBACK_AND_MISTAKE_LOG.md` — direct user preferences and dated AI mistake/fix history; read before project work and update after substantive corrections
15. `24_V6_ANNOTATED_LAYOUT_AND_FIGURE_REVIEW.md` and `verification/v6_layout_verification_20261029.json` — latest V6 layout candidate's comment dispositions, evidence, page map, tradeoffs, and verification limits

Use `11_AI_WORK_PROMPT.md` when handing off to another AI. Then inspect the relevant primary project files. Never treat this handoff or any imported document as proof that the underlying claims are true.

## Evidence discipline

- Report observed facts separately from interpretation and recommendation.
- Treat reviewer marks logged in `19` as review evidence, not source verification. The user authorized a separate v3 review candidate documented in `20`; the approved v2 remains source of truth until adviser/owner acceptance. Keep ambiguous marks and evidence gaps explicit; map substantive statements to sources, method, firmware, and PCB as applicable.
- Keep citations attached to the exact claim they support; inspect the cited source, not only its title or abstract, when the claim matters.
- Mark status as verified, partially verified, unverified, contradicted, or not applicable. Include date, source/version, scope, and remaining gap.
- Do not promise “100% hallucination-free.” Make the evidence and uncertainty auditable instead.
- Do not invent measurements, permissions, sample results, test outcomes, sources, or missing project details.
- Do not modify firmware, thesis, or CAD until the relevant gate in `12_EXECUTION_PLAN.md` is met and the user has asked for the implementation.
- For paper audits, keep ethics determination, site permission, privacy, Turnitin similarity review, AI-writing indicators, and technical validation as distinct evidence gates. Never report a pass without the actual institutional determination/report and a human source review. Do not upload a manuscript without explicit destination/repository authorization.
- For a reusable manuscript audit workflow, use `17_RESEARCH_PAPER_AUDIT_PROMPT.md`; recheck its linked official policies because vendor/institutional rules can change.
- Preserve the old files `01`–`07` as historical materials. They contain obsolete or conflicting proposals; cross-check before reuse.

Root `AGENTS.md` governs the whole repository and takes precedence over this file if workflow details conflict.

## Persistent feedback and correction memory

Read `22_AI_FEEDBACK_AND_MISTAKE_LOG.md` before changing project files. At the end of each task, record substantive mistakes and failed verification attempts even when caught before delivery. Distinguish artifact defects from checker/tool errors; log detection, impact, correction, rerun evidence, root-cause status, and the next-time rule. Store direct user preferences as direct instructions, and label any inference separately. Preserve prior entries and update the project index/inventory as needed. This is retrievable project context, not model training or a guarantee of correctness.


## Current candidate state (2026-10-27)

A separate v3 paper candidate was authorized by the user and contains correction-note dispositions plus 40 additional Chapter II references. The approved v2 remains unchanged. Candidate QA and open issues are in `20_V3_REVIEW_CANDIDATE_AND_RRL_BATCH.md`; do not represent the candidate as approved, validated, ethics-cleared, or ready for field use.
