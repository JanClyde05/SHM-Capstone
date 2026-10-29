# Revision Plan — SHM Thesis Review Draft v2

**Status update 2026-10-24:** The user approved v2, deferred future paper revisions and authorized firmware development. The revision map below is retained as the record of the paper work. Firmware status is in Code Files/GPT Build/docs/HANDOFF.md; no DOCX changes were made in that firmware turn.

**Current output:** `SHM_Research_Aligned_Revision_Draft_v2.docx` in this folder. The earlier review copy `SHM_Research_Aligned_Revision_Draft.docx` remains as a prior draft. The source thesis and manuscript-format template were not edited.

**Scope:** Make necessary edits to align the paper with the user’s developmental study, preliminary single-board design, fixed roadway-deck station, traffic-count method, FFT peak selection, descriptive baseline, and desired monochrome diagrams. Do not invent research results, final hardware settings, site approval, or numeric traffic cutoffs.

## User-confirmed design and method

| Topic | v2 proposal | Evidence, limits, and remaining work |
|---|---|---|
| Sensor hardware | One PCB carries the ESP32-S3 and three co-located triaxial MPU-6050 IMU ICs. These are three onboard channels on one rigid board, not three bridge locations or a spatial array. | Read-only inspection of the preliminary PCB schematic/layout and schematic PDF informed the description. The board is not treated as a validated assembled unit. Bench-check the final board and channel addressing. |
| USB-C | The one board’s USB-C receptacle is for the external field supply and ESP32-S3 programming. Planned field summaries use the separate wireless path. | The preliminary schematic shows a USB-C receptacle, supply/regulator path, D+/D− and ESP32-S3. Espressif documents USB serial/programming functions. Verify the assembled power and data path before deployment. |
| Firmware environment | Arduino IDE on ESP32-S3. The scan sequence is channel 1 X/Y/Z, then channel 2 X/Y/Z, then channel 3 X/Y/Z, repeating. Timestamp each reading and retain channel, axis, sample index and scan-cycle ID. | The readings are sequential and linked by scan-cycle ID; they are not simultaneous. Do not substitute PlatformIO or describe scan-cycle correlation as simultaneity. |
| Station | Keep the board at one predeclared roadway-deck station marked approximately in Figure 2. Record surveyed station, lane/transverse offset, mounting method, board orientation and safe work location; keep them fixed across comparison sessions. | The red map marker is approximate, not a surveyed coordinate or an approved attachment point. Obtain written authorization and safety clearance before field deployment. |
| Traffic observation | Each session is exactly 10 minutes (600 seconds). A separate observer concurrently tallies vehicle passages at a safe viewpoint. Record total count `C` and rate `r = C/(10 min)` in vehicles/minute. End on time, never when a target vehicle count is reached. | FHWA defines volume as vehicles passing a point during a predefined interval and documents 10-minute increments. This supports the chosen fixed interval, not a universal optimum. The project should pilot-check practicality and tally reliability. |
| Traffic labels | Keep `NEAR_ZERO`, `MEDIUM`, and `HEAVY` as study-local descriptive count bands. From equal-duration pilot counts sorted ascending, freeze `c₁ = C_(⌈m/3⌉)` and `c₂ = C_(⌈2m/3⌉)`. Assign `NEAR_ZERO` for `C ≤ c₁`, `MEDIUM` for `c₁ < C ≤ c₂`, and `HEAVY` for `C > c₂`. | No numeric cutoffs can be stated until local pilot counts exist. `NEAR_ZERO` means the lowest observed count band and can include nonzero counts. If ties collapse cutoffs or leave a group empty, repeat/adjust the pilot protocol and freeze the rule before formal data collection. Never tune categories after viewing frequency outcomes. |
| FFT window and summary | A 10-minute session contains ten consecutive 60-second analysis windows. For each channel-axis window, check timing, remove the mean, apply the fixed pilot-selected window, compute the FFT magnitude, and select the largest positive-frequency bin within the predeclared band. Use the median of valid window estimates as that session’s channel-axis result. | Nominal bin spacing for a uniformly sampled 60-second record is `Δf = 1/60 ≈ 0.0167 Hz`. Confirm measured per-channel `fₛ`, sample count `N`, timing tolerance, usable band and embedded memory/runtime in the pilot. One-minute windowing is a published precedent, not proof of universal sufficiency. |
| Session target and inference | Keep five valid 10-minute sessions in each local traffic group as a practical completion target only. Primary analysis is descriptive by group, onboard channel and axis. | Five sessions/group is not a power calculation or evidence of statistical sufficiency. Any confirmatory comparison requires a documented sample-size calculation, suitable independent session observations and supported assumptions. Otherwise report category differences as exploratory. NIST notes sample size depends on significance level, power and population variation. |
| Baseline and review band | Compute session-level mean `x̄`, sample standard deviation `s`, and descriptive interval `x̄ ± s` separately for each traffic group/channel/axis. Keep a separate review band `x̄ ± k_review s`, default `k_review = 2`; an exceedance prompts human review only. | `x̄ ± s` describes observed spread. The two-standard-deviation band is a project heuristic, not a confidence/prediction interval, safety limit, or damage threshold. The independent unit is a field session; do not count windows, axes, or co-located channels as independent session replicates. |

## Section-by-section revision map

| Paper location | v2 change | Boundary |
|---|---|---|
| Abstract and keywords | State one board, three co-located IMUs, one fixed roadway-deck station, concurrent vehicle tally during 10-minute sessions, local pilot-defined traffic groups, 60-second FFT windows and no field results. | No completed results or verified natural-mode claims. |
| Chapter I | Reconcile the problem, objectives, significance, scope and terms with local roadway-deck frequency monitoring and one PCB. | Do not imply a spatial mode-shape measurement, bridge-wide modal survey or diagnosis. |
| Chapter II | Keep three local traffic labels and connect time-windowed traffic counts, bridge ambient vibration and operating-condition caveats to verified sources. | No universal traffic thresholds or civil-engineering load classes. |
| Chapter III, §§3.2–3.4; Figure 2 | Define one approximate planned roadway-deck station; require site survey, approval and fixed board orientation. | Map marker is not surveyed or authorized. |
| Chapter III, §§3.4–3.7; Tables 1–2 | Describe one PCB, USB-C external power/programming, separate wireless path, sequential channel polling, fixed 10-minute session, concurrent manual count, validity checks and metadata. | Hardware, scan rate, mounting and site-specific details remain bench/pilot/approval items. |
| Chapter III, §3.8 | Use sorted pilot counts and nearest-rank empirical tertiles to freeze the two local numeric cutoffs before formal sessions. | Numeric cutoffs are intentionally pending local counts. |
| Chapter III, §3.9 | Keep FFT peak selection, define uniform-timing and positive-frequency-bin checks, and retain the one-minute session/window relationship. | Do not replace it with Welch PSD or claim peak picking uniquely identifies a structural mode. |
| Chapter III, §§3.10–3.13 | Distinguish `x̄ ± s` descriptive spread from the separate default `±2s` review heuristic; make inference conditional on a defensible sample-size plan and assumptions; define system performance checks without claiming calibration accuracy. | No damage/safety claim. |
| Figures 1, 3 and 4 | Replace the relevant diagrams with black-and-white IPO, single-board block diagram and fixed-session/processing flowchart. | Figure 2 remains the approximate map reference. |
| Chapters IV–V | Replace copied thesis-template instructions with an objective-aligned results outline and explicit proposal-stage note. No result, conclusion, or recommendation is fabricated. | Complete these sections from actual data only. |
| Appendices | Remove the template’s generic “Guide to Appendices” and “Typical Appendix Contents” instructions; no actual appendix material was supplied for this draft. | Add study-specific appendices later if needed and cite them in the manuscript. |
| References and page lists | Retain relevant references, add sources needed for traffic/session/sample-size claims, and refresh the visible table/figure page lists. | Keep claims no stronger than the linked source. |

## Equation and algorithm review

- Word-native equation objects are retained for FFT bin spacing and frequency-bin mapping, the DFT/selected peak, count-rate and pilot-tertile cutoffs, mean and sample standard deviation, baseline interval, coefficient of variation, configurable review band, and significance level.
- The displayed sample-standard-deviation equation includes the radical, summation bounds, squared deviations and `n − 1` denominator. The displayed cutoff equation uses ceiling/nearest-rank indices. The formulas were visually reviewed in Word-rendered pages.
- The FFT uses a finite, uniformly sampled channel-axis window. The paper requires the measured per-channel sample rate and actual `N` to determine bin spacing; it does not infer sufficient resolution from the nominal 60-second window alone.
- The baseline unit is the session-level median of valid 60-second peak estimates. Treat window estimates inside one session and X/Y/Z or onboard channels within one session as linked observations.
- The review band is explicitly a heuristic. No claim equates `±2s` with 95% coverage or a calibrated bridge condition threshold.

## Source checks

- [FHWA Traffic Monitoring Guide 2022, traffic data methodologies](https://www.fhwa.dot.gov/policyinformation/tmguide/tmg_2022/traffic-data-methodologies.cfm) — interval traffic counts and documented 10-minute increments.
- [FHWA Traffic Monitoring Guide 2013, traffic monitoring theory](https://www.fhwa.dot.gov/policyinformation/tmguide/tmg_2013/traffic-monitoring-theory.cfm) — manual visual traffic counts and recording methods.
- [FHWA manual traffic count guidebook](https://www.fhwa.dot.gov/clas/ctip/traffic_monitoring_guidebook/ch_4.aspx) — field tally/counter procedures.
- [Oth & Picozzi (2012), ambient vibration test of Adolphe Bridge](https://doi.org/10.1155/2012/876174) — one-minute PSD windows as a documented precedent, not a universal sufficiency claim.
- [NIST/SEMATECH sample-size guidance](https://www.itl.nist.gov/div898/handbook/prc/section2/prc222.htm) — sample size depends on test risk/power and variability; this source was added for the inference limitation.
- [Espressif ESP32-S3 serial connection documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/get-started/establish-serial-connection.html) — USB serial/programming context.
- [InvenSense MPU-6000/MPU-6050 product specification](https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Datasheet.pdf) — manufacturer sensor-family reference; final assembled-board behavior still needs bench verification.

These links are also listed in the v2 paper’s references where cited. Earlier SHM literature sources were retained where relevant; do not add references solely to enlarge the bibliography.

## Final validation record

- Microsoft Word exported the current v2 DOCX to a temporary PDF for layout inspection; the bundled renderer could not find LibreOffice. The final Word-rendered document has **65 pages**.
- Visually inspected the current page lists, IPO/block/flow figures, traffic cutoff equation, baseline equations (including the sample-standard-deviation radical and denominator), and revised statistics/results pages.
- Visible page references in the current render: Figure 1 p. 6; Figure 2 p. 30; Figure 3 p. 33; Figure 4 p. 41; Table 1 p. 32; Table 2 p. 39. The Word contents field was refreshed after Chapters IV–V were revised.
- The proposal-stage results outline contains no claimed findings. The generic appendix template text has been removed.
- Original thesis, manuscript template, and firmware/code folders were not edited in this turn. v1 draft remains in this folder as a prior copy.

## Next approval boundary

The user approved `SHM_Research_Aligned_Revision_Draft_v2.docx` and firmware work has resumed in the separate GPT Build folder using Arduino IDE and the approved method. Preserve this DOCX pending a future paper-revision request. Before formal collection, still resolve the site authorization/survey, final board checks, pilot sample timing/band, and numeric traffic cutoffs.
