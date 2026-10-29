# 06 — Data Collection Protocol (Buntun Bridge): three traffic levels

You only need three datasets. This protocol collects exactly those, in a way that matches Chapter III (§3.5, §3.7, §3.8, §3.11–3.13) and gives Chapter IV what it needs.

| Level code | Plain name | What it represents |
|---|---|---|
| `NEAR_ZERO` | Almost zero vehicle volume | Ambient response: wind/micro-tremor, few or no vehicles on the span |
| `MEDIUM` | Medium / normal volume | Typical daytime flow |
| `HEAVY` | Heavy traffic | Peak flow, queueing/congestion, many large vehicles |

## 1. Operational definitions (thesis §3.8: define by observation, not an arbitrary universal count)

Classify each session by **observed vehicle count rate** over the session (vehicles/min on the monitored lanes, both directions), not by clock time alone. The clock window is only for planning.

| Level | Rule (placeholders — fix from the pilot, then freeze) | Planning window (placeholder) |
|---|---|---|
| NEAR_ZERO | rate ≤ **R0** veh/min (proposed R0 = 1; ≈ ≤ 10 vehicles in 10 min) [Guessing] | pre-dawn / late night, or when traffic is held; needs safe access |
| MEDIUM | R0 < rate ≤ **R1** [Guessing] | mid-morning / midday, weekday |
| HEAVY | rate > R1 **or** queueing on the span [Guessing] | weekday AM/PM peaks; harvest-season trucking days |

How to set R0/R1: during the pilot, take 10-min tallies at 6–10 different times; set R1 at the boundary between the middle and upper thirds of observed rates; R0 as the "almost empty" cut. Write the values into `config.h` and Chapter III Table 2 **before** baseline sessions.

Notes:
- Buntun Bridge has a 15-ton limit (since March 2025). "Heavy" therefore means **high volume / congestion and many buses/jeepneys/trucks within the limit**, not overloaded trucks. Record large-vehicle counts separately.
- Flood closures (e.g., typhoon days) produce zero traffic but add wind and high water; they are **not** NEAR_ZERO sessions. Tag or skip them.
- If a session's observed rate falls outside its planned level, relabel it by the observed rate (document it); do not discard it for that reason.

## 2. Sampling plan

| Item | Plan | Basis |
|---|---|---|
| Valid sessions per level | **≥ 5** (target 6–8 to absorb rejections) | thesis §3.5 |
| Total | ≥ 15 valid; plan 18–24 attempts | — |
| Session length | **600 s** for all levels (≈ 28 Welch segments of 40.96 s, 50 % overlap); set after pilot | `04` §4 |
| Days | Spread over ≥ 3 different days; each level on ≥ 2 days; include ≥ 1 weekday and ≥ 1 weekend per level when feasible | thesis §3.5 |
| Order | Do not collect all of one level first; interleave levels so temperature/season does not coincide with one level | confounding control |
| Fallback if time-limited | 3/3/3 valid sessions, labeled **PROVISIONAL** in Chapter IV with the reduced n stated | honesty rule §3.8 |

Low n warning [Certain]: with n = 5 per group, ANOVA has low power — report effect sizes and confidence intervals, and avoid claiming "no difference" from a non-significant result.

## 3. Pilot (before any baseline session)

Purpose: freeze every setting that the thesis requires to be fixed in advance.
1. **Bench noise floor (T-03):** 30 min static on a rigid floor → PSD noise floor, RMS per axis, `fs_est` stability.
2. **Bench known-frequency test (T-04):** spring/pendulum and a small oscillator → verify f_d accuracy and CV over 10 repeats.
3. **Bridge pilot:** 3 × 10-min records at different traffic conditions at the intended mounting spot; inspect spectra.
4. **Decide and freeze:** analysis band `[BAND_LO, BAND_HI]`, `SNR_MIN_DB`, `NOISE_RMS_MAX_G`, accel range (is any record clipping at ±2 g?), session length, R0/R1, mounting location/orientation.
5. Commit `config.h`, tag `analysis-freeze-v1`. **Pilot data are excluded from the baseline** (state this in the thesis).

## 4. Field procedure per session (maps to thesis §3.7)

Roles: **Operator** (device, phone UI) and **Observer** (traffic tally, weather, safety). Two people minimum.

0. Before the day: written authorization in hand (Q3); batteries/power bank charged; spare cables; log sheets; tally clicker; tripod for phone video; measuring tape; PPE (vest, helmet, gloves); weather check.
1. **Site inspection:** confirm the mount point, safe working spot, no lane obstruction; photograph the sensor location and orientation (X = longitudinal, Y = transverse, Z = vertical).
2. **Install:** secure the node rigidly; verify nothing flexes (tap test: all 3 IMUs agree). Do not move it between sessions of the same campaign unless logged.
3. **Connect:** phone to the node's Wi-Fi; open the dashboard; the phone sets the node clock.
4. **Precheck (10 s stationary):** must pass (no clipping, noise below ceiling, 3 IMUs present).
5. **Start session:** choose the *planned* level, enter operator/weather, press Start. The observer starts the tally (and video) at the same moment.
6. **During:** no touching the node, no walking on the member/deck near the sensor, note unusual events (stopped heavy vehicle, congestion, work crew, strong gust).
7. **Stop:** at 600 s the node finalizes. Observer reports the counts; Operator enters `veh_per_min`, large-vehicle count, notes.
8. **Verdict check:** device QC flags + observed rate vs level definitions. Accept or reject with a **reason code** (never "looked odd").
9. **Back up:** download raw + summary to a laptop immediately; verify file size/CRC; second copy to cloud/USB. Do not delete from the node until verified.
10. Repeat per the sampling plan.

Safety rules: never obstruct a lane; stay in designated safe areas; no work in heavy rain, lightning, or high wind; no night work without authorization and lighting; nobody climbs members. Photos/videos must avoid identifiable people and plates (thesis §3.14).

## 5. Field log sheet columns (`field/log_sheet_template.csv`)

`session_id, date, start_time, end_time, planned_level, observed_level, veh_total, veh_per_min, motorcycle_tricycle, car_suv_van, jeepney_bus, truck, direction_notes, weather_sky, rain(Y/N), wind(calm/light/moderate/strong), temp_c, humidity_pct, river_level_note, mount_photo_id, operator, observer, device_fw, hw_rev, config_hash, qc_precheck, qc_flags, accepted(Y/N), reject_reason, notes`

## 6. Acceptance / QC (thesis §3.13)

Exclude only for a recorded technical reason: `PRECHECK_FAIL`, `CLIPPING`, `FIFO_GAP` (gap inside the analysed record), `FS_OUT_OF_TOL`, `SENSOR_DETACH`, `COMM_FAIL`, `OPERATOR_ABORT`, `OTHER_<text>`.
- `NO_VALID_PEAK` (SNR below threshold) is **a result, not an exclusion**: report the share of sessions per level with a valid peak. This is expected to be lowest in `NEAR_ZERO`.
- Unusual high/low f_d is never a reason to exclude. Investigate technical causes first; otherwise keep it and show it.

## 7. Analysis plan (offline, `tools/analyze_campaign.py`)

1. Descriptives per level and axis (vertical axis primary): n, mean, s (n−1), min, max, **CV**; per-IMU spread; `peak_snr_db`; RMS acceleration (descriptive only).
2. **Baseline:** pooled over all accepted sessions and per level: `x̄ ± s` (thesis Eq. 3), CV (Eq. 4), plus alert band `x̄ ± k·s` (k = 2 default).
3. **Hypothesis test:** H0: mean f_d equal across the three levels. One-way ANOVA, α = 0.05.
   - Assumptions: residual diagnostics (plots, Shapiro–Wilk as supporting evidence only), Levene's test, outliers.
   - If not supported → Kruskal–Wallis. State the basis for the choice and the actual n.
   - Post-hoc if omnibus significant: Tukey HSD (ANOVA) or Dunn with Holm correction (KW).
   - Effect size: η² (ANOVA) or ε² (KW), with a confidence interval or bootstrap interval.
4. Reliability (thesis §3.12): CV across sessions within a level; bench repeatability (T-04); fs_est drift; per-IMU peak agreement.
5. Interpretation guardrails (thesis §2.5, §3.3): a significant difference means traffic level is associated with the measured dominant frequency; it **does not** indicate damage. A value outside the baseline means "review", nothing more.

## 8. Expected physical behavior (to sanity-check results, not to force them)

Vehicle mass on a bridge can lower measured frequencies slightly, and traffic raises excitation amplitude (Kim et al., 2003; Chang et al., 2014; Zhou & Sun, 2019 — all in your manuscript's reference list). So: higher RMS and higher SNR from NEAR_ZERO → HEAVY is expected [Likely]; a small downward frequency shift under HEAVY is plausible but **not guaranteed** for a 1.4 km steel truss [Guessing]. Report whatever you find.

## 9. Thesis edits required by this protocol and the new design (`thesis/chapter3_sync.md`)

| Section | Current text | Change |
|---|---|---|
| §3.1 step 4/9 | "predefined traffic conditions"; ANOVA | three levels NEAR_ZERO / MEDIUM / HEAVY |
| §3.4 | "the MEMS IMU" (singular) | three IMUs on one rigid node, spectra averaged; Table 1 filled from the final hardware/firmware |
| §3.5 | peak vs off-peak, weekday/weekend | ≥ 5 valid sessions per level; days/weekday–weekend coverage; pilot excluded |
| §3.8 + Table 2 | peak/off-peak, time windows | observed-rate definitions with frozen R0/R1; add rows for level, veh/min, large-vehicle count |
| §3.9 | single FFT; Eq. 1–2 with nominal fs | Welch (N = 4096, 50 % overlap, Hann), per-axis, per-IMU then averaged; fs = **measured** `fs_est`; peak rule + parabolic interpolation + SNR criterion; band frozen after pilot |
| §3.10 | baseline x̄ ± s, CV | per level and pooled; add alert band x̄ ± k·s with k stated |
| §3.11 | ANOVA; Kruskal–Wallis | three groups, post-hoc, effect size |
| §3.12 | repeatability | add bench T-04 and fs_est stability |
| §3.13 | QC | list the reason codes |
| Figures 2–3 | block diagram, flow chart | redraw to match the final system (FIFO, fs_est, Welch, session, SD) |
| Chapter IV skeleton | template placeholders | 4.2 Objective 1 (system development + bench validation + noise floor); 4.3 Objective 2 (baseline by traffic level + ANOVA/KW); 4.4 Objective 3 (dashboard evaluation: screenshots, update rate, latency, functional checklist) |
| Housekeeping | two "Figure 1" in List of Figures; headings after 3.10 unnumbered in the body but numbered in the TOC; two reference links ending `?utm_source=chatgpt.com` (Cornwell et al. 1999; Welch 1967) | renumber; strip the tracking parameter; verify every cited DOI resolves and every listed reference is cited |
| Scope text | unchanged | keep: no damage diagnosis; internal baseline; single site |
