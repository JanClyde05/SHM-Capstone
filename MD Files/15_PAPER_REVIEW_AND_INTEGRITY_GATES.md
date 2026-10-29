# Research paper review: evidence, ethics, and integrity gates

Review date: 2026-10-26 (Asia/Manila). Target: `Documents/The Real Research Paper/GPT Paper/SHM_Research_Aligned_Revision_Draft_v2.docx`.

## Decision summary

**Review status: partial, with material blockers. Do not represent the manuscript as fully verified, ethics-cleared, Turnitin-cleared, or ready for formal data collection.** The proposal is carefully scoped in many places, but the evidence currently available does not close the protocol-to-firmware, research-ethics, privacy, site-permission, front-matter, and full-source review gates below.

This is an audit record, not an ethics-board decision, Turnitin report, plagiarism verdict, or guarantee that the document contains no false statement. “100% verified” and “hallucination-free” are not achievable certifications for a research proposal. The enforceable rule is: every material claim has traceable provenance and a bounded status; an unresolved material fact is not silently upgraded to fact or used to justify implementation or data collection.

## Scope and artifact provenance

| Item | Finding |
|---|---|
| Current draft | `SHM_Research_Aligned_Revision_Draft_v2.docx`, 537,524 bytes; SHA-256 `B09C741309444DAB16ACA6957250217CB776E310C20459820547AA747264CB42`. |
| Draft status | Its handoff describes it as a proposal-stage review draft, approved on 2026-10-24, with further revisions then deferred. The user's current request authorizes this audit. The DOCX itself was not edited. |
| Earlier draft | `SHM_Research_Aligned_Revision_Draft.docx`, 753,466 bytes; retained as historical comparison only. It is not the current version. |
| Nearby source documents | `README.md`, `REVISION_PLAN.md`, and `AI_HANDOFF.md` provide revision history and design intent. They are evidence of prior decisions, not independent proof that a claim or test is true. |
| Extracted content | 340 body blocks, approximately 12,571 words, 7 tables, 2 Word sections; includes front matter, Chapters I–V, and 60 reference-list entries. Existing handoff records a 65-page Word render. |
| Method | Read the DOCX text and tables using `python-docx` 1.2.0; inspected Office Math XML for equations; compared relevant statements with active firmware/configuration and the current code handoff; checked selected sources on their publisher, agency, regulator, standards, or manufacturer sites. |
| Layout limitation | A fresh full PDF render/visual review was not completed in this audit. The bundled renderer lacked LibreOffice and the Word automation export attempt did not produce a PDF. The prior handoff records a partial visual QA of selected pages/equations, not a complete new-page-by-page check. Re-render the final review copy in Word before submission. |
| Source-review limitation | This pass is comprehensive in scope but not full-text verification of every sentence against every one of the 60 references. DOI/title matching and an in-text citation scan are identity/completeness checks, not proof that each citation supports its exact sentence. Use the [claim register](16_PAPER_CLAIM_AND_DECISION_LEDGER.md) and [reference audit](10_RESEARCH_REFERENCE_AUDIT.md). |
| Data searched | No raw Buntun field dataset, completed study results, institutional REC determination/clearance letter, site authorization, or Turnitin Similarity/AI Writing report was located in the reviewed current project artifacts. This means “not located,” not proof that none exists elsewhere. |

## Paper-folder map

| File | Role / status |
|---|---|
| `SHM_Research_Aligned_Revision_Draft_v2.docx` | Active proposal-stage review draft; preserve as the approved v2 source until a new revision is deliberately prepared. |
| `SHM_Research_Aligned_Revision_Draft.docx` | Earlier review copy; not the active manuscript. |
| `REVISION_PLAN.md` | Describes v2 edits, confirmed design intent, source list, and earlier partial layout QA. It predates the active firmware details captured below. |
| `AI_HANDOFF.md` | Prior assistant handoff. Its “further revisions deferred” note is historical; the current user request now authorizes an audit, not a claim of institutional acceptance. |
| `README.md` | Folder entry point. |

## Section-by-section review

### Front matter — needs correction/author confirmation

- The Approval Sheet says “recommended for final defense,” has a blank grade and panel placeholders `ENGR. GIVEN M. LAST NAME`, and shows a dean acceptance date of September 2, 2026. The rest of the paper and handoff describe a proposal-stage draft. No signed approval/defense record was located. **Status: unresolved and internally inconsistent in appearance.** Confirm the required CSU stage/template with the adviser or department; do not invent names, dates, grades, or signatures. Remove the sheet from a proposal copy or retain only an institution-approved blank form, as the adviser directs.
- Dedication and Acknowledgement contain generic template instructions rather than author-written text. **Status: verified from DOCX text; editorial defect.** Do not invent personal acknowledgements. Confirm whether to omit those sections for a proposal or wait for author-provided text.
- Title uses “Localized” and “Real-Time.” The operational definitions and current code do not substantiate the broad meanings in the glossary; see the ledger. This is a scope/terminology issue, not an established false result.

### Abstract and Chapter I — mostly cautious; several claims need narrowing

- The abstract correctly describes one PCB, three co-located IMUs, one proposed station, sequential polling, 10-minute sessions, a concurrent count, pilot-defined labels, an FFT-bin output, and the absence of field results. It appropriately excludes damage diagnosis and safety claims.
- “Since no prior instrumented baseline exists for Buntun Bridge” is an unbounded absence claim. The project search only supports that the team has not located an appropriate documented baseline in the sources reviewed. Narrow and date/scope the sentence.
- “Localized” is defined as cost-efficient, locally accessible, non-proprietary hardware that is feasible in resource-limited settings. The paper supplies no bill-of-materials cost comparison, local supply/maintenance evidence, or affordability study. The system may use accessible components, but that feasibility claim is **unverified**. Define “localized” by the one-site/local deployment if that is the intended meaning, or add reproducible cost and availability evidence.
- “Real-Time Monitoring” is defined as continuous or near-instantaneous processing. The firmware returns live status and latest readings/window output during an active session, but the session-level ten-window summary is finalized after capture and traffic-count submission. The achieved end-to-end latency has not been measured. Define the term as the observed update behavior (including window latency), quantify it in bench tests, or qualify/remove “real-time” in the title.
- Regional bridge-failure accounts are appropriately contextualized and the paper says they do not show the prototype could predict a collapse. Preserve attribution and dates. The Cabagan PNA report says the cause assessment was underway; it cannot support a proven causal mechanism or an earlier missed warning. Piggatan wording should remain explicitly preliminary/attributed.

### Chapter II — good limits in places; citation support is unevenly verified

- The strongest boundary is that a largest FFT peak is a measured spectral feature, not necessarily a natural frequency, unique mode, damage indicator, or safety threshold. Keep that limitation throughout the thesis and title/abstract.
- The description of OMA, peak picking, FDD, and SSI is supported in broad terms by the cited review and bridge case study, but the current embedded method performs single-bin peak selection. It is not a full OMA/FDD/SSI implementation.
- Chen et al. (2017) is a bridge OMA precedent, not validation of this three-IMU, sequential, single-board setup. Oth and Picozzi’s 60-second PSD windows are a precedent, not proof that this project’s 60-second FFT windows are adequate.
- Giermann et al. (2025) is relevant to low-cost sensor deployment and measurement limitations, but is focused on static/tilt-oriented monitoring and must not be used as direct dynamic/modal-frequency or FFT validation. Its exact role in the literature narrative should be narrowed.
- Hidalgo-Fort et al.’s reported <1.72% error belongs only to its own sensors, reference system, test setup, and conditions. The manuscript reports it as a result of that paper; do not imply it transfers to this prototype.
- The local research-gap paragraph correctly says the sources reviewed do not establish that no other Philippine study exists. Preserve this scope. The local literature scan is not an exhaustive national registry search, so do not strengthen it into “first” or “no previous study.”
- Study-specific checks for Komarizadehasl/LARA, Hasani, Park, Meng, Camara, Gaviña, Payawal, Lau, and PCIEERD USHER are recorded as P40–P49 in the [claim ledger](16_PAPER_CLAIM_AND_DECISION_LEDGER.md). Some cited items were verified from publisher abstracts/records rather than directly reviewed full text; those details remain bounded accordingly.
- Buntun bridge background should remain attributed to the Philippine Information Agency feature, not presented as the result of a current engineering inspection. The 15-ton restriction in PNA is a dated 2025 report; re-check the responsible DPWH office for current conditions before field planning.

### Chapter III — major method/code and readiness gates

- The methods correctly state one fixed station, one board, three co-located sensors, sequential acquisition, local traffic groups, and no bridge-wide modal array. Field station and mounting remain approximate/unapproved. Site permission and safety clearance are prospective; no proof of receipt was found.
- **Valid-window acceptance conflict:** the paper says the session estimate is the median of valid 60-second estimates. It also requires ten windows to be present, but does not clearly require all ten estimates per axis to be analytically valid. Current firmware has `SHM_MIN_VALID_WINDOWS = 10` and only calculates the session median when `n >= 10` (`config.h`, `session.cpp`). This is stricter than “median of the valid windows” if fewer than ten otherwise-valid windows could be accepted by the protocol. Decide whether to require ten valid windows in the paper/QC rules or authorize a lower per-axis minimum in firmware and state it in the protocol. Preserve rejection reasons and do not silently change after pilot data.
- **Window-function conflict:** the manuscript says the fixed window will be selected during the pilot. Current firmware fixes a symmetric Hann window in its processing/configuration identity (`session.cpp`; DSP implementation). Either state the fixed symmetric Hann as a locked method and pilot-check its behavior, or design and implement a real selection/freeze mechanism before claiming the choice is pilot-selected.
- **Analysis band and timing remain pilot/configuration values:** `config.h` defaults to 0.5–20 Hz, nominal 100 Hz, 500 microseconds interval tolerance, and 3% sample-rate tolerance. Some settings can be frozen through the interface. The paper appropriately says final values will be recorded, but final prose must use the actual frozen campaign configuration and show that the band lies below measured Nyquist. A default is not field validation.
- **Meaning of “real time”:** `/api/live` exposes session state, latest raw readings, and the most recently completed window’s estimate while capture is active; the final result needs ten valid windows and is finalized at session close/count submission. The manuscript should distinguish this live preview from finalized session summaries and report measured update/processing latency.
- **Privacy/data management gap:** the setup UI requires the operator’s full name and `session.cpp` stores it as `operator`. The ethical paragraph only says road-user identifiers are unnecessary; it does not disclose this operator field, retention/access/deletion, backup/security controls, or the handling of incidental faces/plates in photos/video. Review the UI’s need for a real name; prefer a coded role/operator ID if adequate. If a name or identifiable imagery remains, document purpose, access, safeguards, retention/deletion, and consult CSU’s privacy officer/DPO. Do not claim the entire project processes no personal information.
- **Safety:** the paper includes safe-location, PPE, no-obstruction, site-authorization and emergency-procedure concepts. The controls remain generic and prospective. The field-specific risk assessment should locate the observer/operator, define traffic-side hazards and communications, assess mounting/cable retention, and document stop-work/emergency conditions with the site authority. No permission or safe access is established by the manuscript.
- **Data stewardship:** paper says save raw records and field logs but does not provide an adequate study-specific access, storage, backup, retention, deletion, de-identification, or incident-response schedule. Add the institutional plan before collection. The current embedded storage constraints and firmware handoff also matter to completeness; do not promise long-term retention until capacity and export/backup are measured.
- **Statistics:** the paper properly treats five sessions/group as a practical target, not a power calculation, and makes inference conditional on a sample-size plan and assumptions. Traffic is naturally observed, not randomized; between-category findings are association/descriptive differences, not causal traffic effects. Time, temperature, weather, road-surface, vehicle mix, and direction may co-vary; collect and report relevant context, and avoid claiming traffic alone caused frequency changes.
- The statistical chapter contemplates ANOVA separately across nine channel-axis outcomes. If these are confirmatory, predefine the primary outcome/test family and account for multiplicity; otherwise report the set as exploratory and do not treat unadjusted isolated p-values as confirmatory. See P50 in the [claim ledger](16_PAPER_CLAIM_AND_DECISION_LEDGER.md).
- **Baseline logic:** session-level estimates, not windows/axes/channels, are the inferential units. The `x̄ ± s` spread and separate `±2s` review heuristic are appropriately distinguished from confidence/prediction bounds, safety limits, or damage criteria. Keep that distinction.

### Chapters IV–V — proposal placeholders, no study results

The draft explicitly says that no measured field results exist and reserves the results/conclusion for completed work. This is appropriate for a proposal-stage draft. Do not replace these placeholders with fabricated examples or projected outcomes. After data collection, report actual valid/excluded sessions, exclusions, settings, group cutoffs, and raw-to-summary analysis lineage.

### References and citations — partially checked, not fully cleared

- The manuscript contains 60 reference entries; prior audit reports 37 DOI-bearing entries whose title metadata matched Crossref. Metadata agreement does not verify full source content or correct use in the paper.
- A pattern-based scan found 47 apparently cited entries and 13 apparently uncited entries (listed in `10_RESEARCH_REFERENCE_AUDIT.md`). Manually confirm against all body text, captions, tables, citation fields, and the final render before resolving. Do not delete references just because a simple parser misses a corporate or narrative citation.
- Prior link checker outcomes for 23 non-DOI links were 9 HTTP 200, 4 HTTP 404, 7 HTTP 403, and 3 client/TLS failures. These results do not mean 403/TLS failures are false sources; the InvenSense reference URL was reported broken and should be replaced with a live manufacturer source only after confirming the intended document/version. Recheck all links at final submission.
- The work still needs exact sentence-to-source checking for all cited claims, reference-style conformity to the current CSU template, missing page/issue/URLs where required, and a manual citation/bibliography reconciliation. Do not infer a citation is suitable from its title or DOI.

## Ethical-review gate

**Status: no ethics clearance or institutional determination located; applicability is not self-determined.** The manuscript involves engineering measurements on an active bridge and a human observer/operator, but it describes no recruitment, interview, intervention, or intended collection of identifiable road-user data. That description alone does not decide whether institutional ethics review, exemption, or a written determination is required. The 2022 Philippine National Ethical Guidelines address research involving human participants and health/health-related research; ask the current CSU research/ethics office or designated adviser to classify this specific engineering protocol before field work. Do not self-issue an exemption. Site/bridge authority permission is a separate required gate, not a substitute for ethics review.

The [2022 PHREB National Ethical Guidelines](https://www.pchrd.dost.gov.ph/wp-content/uploads/2023/05/2022-NEGRIHP_Official-Gazatte_Ver-5-1.pdf) provide the national framework. Their human-participant review provisions must not be overstated as automatically governing every non-health engineering study; the institution decides applicability under its current rules. The official [CSU Office of the Vice President for Research, Development and Extension directory](https://csu.edu.ph/university-officials) is a starting point for obtaining the current procedure; a current CSU ethics-review process/accreditation page was not located in this audit.

The [Philippine Data Privacy Act](https://privacy.gov.ph/data-privacy-act-/), [Implementing Rules](https://privacy.gov.ph/implementing-rules-regulations-data-privacy-act-2012/), and [NPC Advisory Opinion 2019-017](https://privacy.gov.ph/wp-content/uploads/2019/10/v15BRedacted5D20Advisory20Opinion20No.202019-017.pdf) describe purpose, proportionality, confidentiality, and safeguards; the NPC specifically cautions that research is not a blanket waiver of all privacy duties. The operator’s full-name field and any identifiable imagery require a documented institutional privacy decision and safeguards. The paper should state the data categories, purpose, authorized access, storage/backup location, retention/deletion, and incident contact or procedure that CSU approves.

## Turnitin / similarity / AI-writing gate

**Status: no report was found or generated. No Turnitin pass/fail or AI-authorship conclusion is available.** No third-party submission was made in this audit.

- Turnitin describes the Similarity score as a percentage of matching text, not a plagiarism verdict; it says no single score is universally acceptable and requires human review. See [Turnitin’s Similarity FAQ](https://helpcenter.turnitin.com/hc/en-us/articles/27811925295501-Does-Turnitin-check-for-plagiarism-and-what-is-a-good-Similarity-score) and [score interpretation guide](https://guides.turnitin.com/hc/en-us/articles/23435833938701-Understanding-the-similarity-score).
- The AI Writing indicator is separate from similarity. Turnitin says its AI model can misidentify text and should not be the sole basis for adverse action; its guide suppresses precise scores/highlights below 20% to reduce misinterpretation. See [AI Writing Report guidance](https://guides.turnitin.com/hc/en-us/articles/22774058814093-Using-the-AI-Writing-Report). An AI detector cannot prove authorship, non-authorship, or academic misconduct.
- Model versions change. Turnitin's [release notes](https://guides.turnitin.com/hc/en-us/articles/28294949544717-AI-writing-detection-model) list an English-model update on October 14, 2026 and say existing reports are not retroactively updated. If the university requires an AI report, record its generation date and displayed model/version context; an older report may not reflect a later model.
- Submission configuration matters. Turnitin offers general repository, private institution repository, or no-store options depending on institutional settings; repository choices change future comparisons and may affect later self-matches. See [official assignment settings](https://guides.turnitin.com/hc/en-us/articles/36214251672973-Standard-assignment-settings). Do not upload an unpublished thesis until the institution/owner chooses an authorized account and repository setting with the intended retention consequences.
- The reviewed DOCX is approximately 12.6k words and English; that is within Turnitin’s currently documented 300–30,000-word AI-report text range, but file eligibility does not mean a report exists or is valid. The exact account, license, filters, assignment settings, index, and report are unknown.
- A legitimate clearance review requires the actual report, its assignment/account/settings, date/model version where shown, exclusions, source matches, and human inspection of matched passages against the source. Repair citation, quotation, attribution, and source fidelity—not wording to evade a detector. Preserve genuine drafts/version history and source notes as authorship/process evidence.

## False-information and scholarly-integrity disposition

The currently visible high-risk statements and wording changes are itemized in the [claim and decision ledger](16_PAPER_CLAIM_AND_DECISION_LEDGER.md). In brief:

1. Narrow the “no baseline exists” claim to a dated search result.
2. Define or substantiate “localized” and “real-time.”
3. Resolve manuscript-to-firmware window validity and window-function conflicts.
4. Disclose or remove the operator name and complete data-management details.
5. Confirm the Approval Sheet stage, names, grade, signatures, and date; remove generic dedication/acknowledgment instructions or supply author-approved text.
6. Complete source-level citation review; resolve likely uncited references and broken links only after manual confirmation.
7. Preserve proposal-stage language until actual physical/field evidence and institutional/site approvals exist.

## Research and implementation loop for this paper

1. Keep v2 immutable; use it as the baseline and record its hash.
2. Obtain adviser/owner answers for the methodological choices in `16` and a current institutional determination for ethics/privacy requirements.
3. For every proposed manuscript or firmware change, log the original sentence/code behavior, evidence, decision owner, exact revision, and acceptance check before editing.
4. Make changes only in a new review copy (e.g. v3), preserve v2, and mark uncertainty visibly rather than fill it with guesses.
5. Re-run claim/citation reconciliation, code-to-method mapping, plagiarism/similarity human review if an authorized report is supplied, and full Word-render layout review on the exact final hash.
6. Do not start formal bridge data collection until written site authority clearance, safe method, institutional ethics/privacy determination, final frozen protocol/configuration, and bench verification are all documented.

## Sources checked online for this review

- [PHREB 2022 National Ethical Guidelines (official PCHRD-hosted PDF)](https://www.pchrd.dost.gov.ph/wp-content/uploads/2023/05/2022-NEGRIHP_Official-Gazatte_Ver-5-1.pdf)
- [Data Privacy Act (National Privacy Commission)](https://privacy.gov.ph/data-privacy-act-/); [implementing rules](https://privacy.gov.ph/implementing-rules-regulations-data-privacy-act-2012/)
- [NPC Advisory Opinion 2019-017 on research and personal-data processing](https://privacy.gov.ph/wp-content/uploads/2019/10/v15BRedacted5D20Advisory20Opinion20No.202019-017.pdf)
- [Turnitin Similarity FAQ](https://helpcenter.turnitin.com/hc/en-us/articles/27811925295501-Does-Turnitin-check-for-plagiarism-and-what-is-a-good-Similarity-score); [AI Writing Report guide](https://guides.turnitin.com/hc/en-us/articles/22774058814093-Using-the-AI-Writing-Report); [AI model release notes](https://guides.turnitin.com/hc/en-us/articles/28294949544717-AI-writing-detection-model); [repository/settings guide](https://guides.turnitin.com/hc/en-us/articles/36214251672973-Standard-assignment-settings)
- [CSU official research-office directory](https://csu.edu.ph/university-officials)
- Technical, bridge-history, methods and statistical sources are individually bounded in the [reference audit](10_RESEARCH_REFERENCE_AUDIT.md) and the [claim ledger](16_PAPER_CLAIM_AND_DECISION_LEDGER.md).


## V3 candidate note (2026-10-27)

The v3 paper candidate was created under a later direct user instruction and is documented in `20_V3_REVIEW_CANDIDATE_AND_RRL_BATCH.md`. This file's earlier integrity findings describe the approved v2 and remain relevant unless rechecked against v3. V3 is not approved and has not received ethics/privacy, site/safety, Turnitin, AI-writing, full-source, or physical/field clearance.
