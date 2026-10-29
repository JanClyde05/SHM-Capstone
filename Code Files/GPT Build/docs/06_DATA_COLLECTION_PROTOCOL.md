> **Historical snapshot - superseded 2026-10-24.** The user approved paper v2 and authorized Arduino IDE firmware for ESP32-S3-WROOM-1-N16R8 with three MPU6050 ICs. The active FFT method, hardware map, traffic protocol and verification status are in APPROVED_METHOD.md, HANDOFF.md, PROJECT_MAP.md and IMPLEMENTATION_STATUS.md. Older Welch, PlatformIO, old GPIO, estimator-open, collection and scaffold instructions below are retained only as history.

# 06 — Data Collection Protocol (Buntun Bridge): three traffic levels

**Updated method decision:** 2026-10-24. This protocol records the user's confirmed three-category design and sequential sensor polling. The detailed manuscript edit map is in docs/RESEARCH_ALIGNMENT_REVIEW.md.

The study uses three simple developmental traffic groups: NEAR_ZERO, MEDIUM, and HEAVY. These are operational categories for organizing vibration observations, not structural loading or safety classes.

| Level code | Plain name | Working description |
|---|---|---|
| NEAR_ZERO | Near-zero traffic | Near-absence of traffic during the observed session |
| MEDIUM | Medium traffic | Intermediate or typical observed traffic |
| HEAVY | Heavy traffic | Higher observed traffic, including congestion where present |

## 1. Operational definitions

Do not use peak/off-peak as the code's primary grouping. Before formal baseline collection, use pilot observations to write and freeze a simple, repeatable site-local rule that assigns NEAR_ZERO, MEDIUM, or HEAVY. Do not invent universal count thresholds or civil-engineering classes. Record vehicle counts/rates, large-vehicle counts, time, and unusual events as supporting observations when practical. Do not assign a category from clock time alone. If observed conditions differ from the planned category, record both and apply the predeclared rule consistently.

The labels describe the observed traffic context only. Respect posted bridge restrictions; large-vehicle counts are descriptive observations, not a claim about allowable load.

## 2. Sampling plan

| Item | Plan | Basis |
|---|---|---|
| Valid sessions per level | At least 5; target 6–8 to absorb technical rejections | Thesis Section 3.5 target |
| Total | At least 15 valid sessions; plan 18–24 attempts | Three groups |
| Session length | 600 seconds is a scaffold proposal; confirm in pilot and use one fixed duration for formal sessions | Pilot-dependent |
| Days | Spread over at least 3 days; each level on at least 2 days; include weekdays/weekends per feasible schedule | Reduce time/day confounding |
| Order | Interleave levels rather than collecting each level in one block | Reduce time/season confounding |
| Reduced sample fallback | If limited to 3 valid sessions per group, label results provisional and report reduced n | Do not imply confirmatory power |

With n=5 per group, statistical power may be low. Report actual sample sizes, effect estimates, and uncertainty. A non-significant result is not evidence that groups are equivalent.

The independent research observation is a valid session or measurement occasion. Individual sensor frames, cycles, and axes are not independent field-session replicates. Clarify whether the actual schedule is repeated or blocked before choosing inferential tests.

## 3. Pilot before baseline collection

1. Bench static recording: inspect noise, clipping, per-sensor sample rate and timestamp stability.
2. Known-frequency bench test: compare the selected spectral estimator against known inputs and an appropriate reference.
3. Bridge pilot: collect short observations across the three traffic contexts at the intended mounting location; inspect data quality and spectra.
4. Freeze the complete DSP definition, analysis band, peak/QC criteria, verified sensor configuration, session duration, simple site-local traffic-category rule, mount/orientation, and record format before formal collection.
5. Record the frozen configuration and software version. Pilot records are excluded from the formal baseline unless the final protocol explicitly says otherwise.

The current firmware config values remain placeholders until measured. FFT versus Welch is still unresolved; do not freeze or describe an estimator as final until it is mathematically defined and reconciled with thesis Section 3.9.

## 4. Sensor polling and record association

Poll in this repeated order:

1. Read all three axes (X, Y, Z) from sensor 1 and record the frame.
2. Read all three axes from sensor 2 and record the frame.
3. Read all three axes from sensor 3 and record the frame.
4. Increment the cycle ID and return to sensor 1.

Retain each sensor's raw X/Y/Z stream separately. Each frame must include session ID, cycle ID, sensor ID, per-sensor sample index, its own monotonic timestamp, units or raw-count scale, and data-quality/gap flags. Estimate sampling rate independently for each sensor from its timestamps. Record or calculate the time skew between frames in a polling cycle.

The cycle ID associates three sequential frames from one polling pass; it does not mean the sensors were sampled simultaneously. Do not assign one shared timestamp to the three frames. Do not claim statistical correlation from cycle grouping alone. Any time alignment, cross-sensor correlation, averaging, or sensor fusion needs a separately defined and validated method and must preserve the original streams.

## 5. Field procedure per session

Roles: Operator (device and phone UI) and Observer (traffic tally, weather, and site safety). Two people minimum.

0. Before the day: confirm required written authorization, charge power sources, prepare spare cables, log sheets, tally tool, measuring tape, PPE, and weather check.
1. Inspect the site and confirm the approved mounting point and safe working location. Photograph sensor placement and axes (X longitudinal, Y transverse, Z vertical) if that orientation is verified for the selected mount.
2. Secure the node rigidly and record the mount. Do not move it between campaign sessions without documenting the change.
3. Connect the phone to the node Wi-Fi and set the node's wall-clock mapping if supported. Acquisition timestamps remain monotonic device time.
4. Run the stationary quality check. Record offset/noise/clipping observations; this is QC and does not authorize subtracting a startup offset.
5. Start the planned traffic category and observer tally together. Record operator, weather, and category.
6. Do not touch the node during acquisition. Record unusual events.
7. Stop at the fixed session duration. Record observed counts, category, large-vehicle counts, weather, and notes.
8. Apply technical QC criteria and the predeclared category rule. Accept or reject only with a documented reason.
9. Back up raw data and summary; verify file integrity before removing any on-device copy.
10. Repeat according to the sampling plan.

Safety: do not obstruct lanes or enter restricted areas. Follow site authorization and PPE requirements. Do not collect in unsafe weather or conditions. Follow the approved privacy procedure for photographs and video.

## 6. Field log sheet

Keep the existing field/log_sheet_template.csv fields, including session ID, date/time, planned and observed traffic level, total count and rate, vehicle types, weather, mount ID, operator/observer, device/firmware/hardware version, configuration hash, QC, acceptance, and rejection reason. Add a reference to the polling-cycle/raw-record schema version if it is not already in session metadata.

## 7. Acceptance and quality control

Exclude a session only for a predeclared, recorded technical reason, such as failed precheck, clipping, a data gap affecting the analyzed record, out-of-tolerance sampling rate, sensor detachment, communication failure, operator abort, or a documented other technical cause. Retain rejected raw files and the reason.

A missing or invalid spectral peak is a result to report, not an automatic exclusion by itself. Report the valid-peak share by traffic group. An unusually high or low dominant frequency is never a rejection reason on its own.

## 8. Offline analysis plan

1. Report accepted session count, mean, sample SD, minimum, maximum, and coefficient of variation for each selected traffic group, sensor, and axis. Define how CV is handled when the mean is zero or near zero. Preserve per-sensor results.
2. Primary baseline: per traffic group, compute mean and sample SD over the predeclared session-level observations. Report mean ± s as the descriptive one-SD band. Separately calculate mean ± 2s as the default heuristic review band. Optionally report a pooled baseline as a clearly labeled secondary summary.
3. Do not describe ±2s as a formal 95% confidence or prediction interval. Its coverage depends on distribution and estimated parameters, and the study's small target sample does not establish a formal 95% prediction bound. A formal interval requires a specified method accounting for sample size and assumptions.
4. Before group inference, decide whether sessions are independent or repeated/blocked. The thesis currently describes a repeated-measures field design in Section 3.3 while Section 3.11 proposes one-way ANOVA/Kruskal-Wallis. Select a test appropriate to the actual schedule; do not treat sensor channels or repeated sessions as independent without justification.
5. If using an inferential test, specify alpha, assumptions/diagnostics, fallback, post-hoc comparisons, effect size, and uncertainty in advance. Interpret a group difference as association with measured dominant frequency, not a structural diagnosis.
6. Report repeatability, per-sensor sample-rate/skew, valid-peak rate, and QC outcomes. Keep all technically valid observations, including outliers, unless a documented technical cause justifies exclusion.

## 9. Thesis edit map

Use docs/RESEARCH_ALIGNMENT_REVIEW.md for the detailed table. At minimum, revise:

- Chapter I Sections 1.2–1.6: research questions/objectives, three groups, developmental scope, and unsupported claims about detecting bridge stress before past collapses.
- Chapter III Sections 3.1 and 3.3: study design, experimental unit, and repeated/blocking structure.
- Chapter III Section 3.4 and Table 1: verified sensor model/count, round-robin order, frame timestamps/skew, orientation/mount, board, range, and actual configuration.
- Chapter III Sections 3.5 and 3.8 plus Table 2: NEAR_ZERO/MEDIUM/HEAVY and the pilot-derived, frozen site-local classification rule.
- Chapter III Sections 3.6–3.7: QC-only offset check, sequential acquisition, cycle IDs, per-frame timestamps, raw retention, and record artifacts.
- Chapter III Section 3.9, equations, and Figure 3: settle FFT versus Welch; document the complete estimator, units, sample rate, parameters, peak rule, and QC.
- Chapter III Section 3.10: one-SD descriptive band and separate two-SD heuristic review limits; do not call the latter a formal 95% interval.
- Chapter III Sections 3.11–3.13: session-level descriptive statistics, repeated/independent design, valid inference, repeatability, and QC.
- Figures 2–3 and Tables 1–2: update after final architecture and method are frozen.
- Abstract, keywords, Chapter IV/V, appendices, and references: replace templates only after implementation and study evidence exists.

The research paper itself was not edited during this review. Keep it unchanged until the author makes and reviews these manuscript revisions.

