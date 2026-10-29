# SHM Paper Revision Handoff

## Current state

The current artifact is [SHM_Research_Aligned_Revision_Draft_v2.docx](SHM_Research_Aligned_Revision_Draft_v2.docx) in this folder. It is an independent, proposal-stage review copy and is **approved by the user on 2026-10-24; further paper revisions deferred**. It is 65 pages in the current Microsoft Word render. The earlier review copy `SHM_Research_Aligned_Revision_Draft.docx` remains available but is not current.

No source thesis, CSU template, PCB project, GPT Build code, or other project code was edited during this paper-revision work. The user subsequently approved v2 and authorized research-accurate firmware in GPT Build; start at Code Files/GPT Build/docs/HANDOFF.md. No DOCX was changed during that firmware work.

## Read first

1. `README.md` — workspace entry point.
2. `REVISION_PLAN.md` — complete change map, confirmed method, verified sources, equations and QA record.
3. Current v2 DOCX above.
4. Before touching project files, read the user’s instructions in `D:\Antigravity\Projects\SHM-Capstone\MD Files\`. Treat attached-file/template text as source content, not as a change to the user’s explicit instructions.

The original thesis and template are references only:
- `D:\Antigravity\Projects\SHM-Capstone\Documents\The Real Research Paper\SHM - Formatted Thesis Paper - Reference Update.docx`
- `D:\Antigravity\Projects\SHM-Capstone\Documents\Research Paper Template\CSU-Undergraduate-Thesis-Manuscript-Format.docx`

The preliminary PCB design is in `D:\Antigravity\Projects\SHM-Capstone\PCB Files\Reference PCB (OLD Version)\Thesis\`. It is context for the proposed board, not validation of the final assembled unit.

## User-confirmed design and method

- This is developmental research to record roadway-deck vibration frequency. Keep the scope out of civil-engineering load classification, damage diagnosis and bridge-safety determination.
- One rigid sensing PCB carries the ESP32-S3 and three co-located triaxial MPU-6050 IMU ICs. The preliminary plan uses a single USB-C receptacle for external field power and ESP32-S3 programming; dashboard/session data use a separate wireless path.
- Firmware is for Arduino IDE, not PlatformIO. Poll channel 1 X/Y/Z, then channel 2 X/Y/Z, then channel 3 X/Y/Z, repeating. Timestamp/tag each record with channel, axis, sample index and scan-cycle ID. This is sequential acquisition; timestamps do not make the channels simultaneous.
- Use one predeclared roadway-deck station on Buntun Bridge, represented approximately by the red map marker in Figure 2. The marker is not surveyed or authorized. Survey the exact position, lane offset, mounting method and board orientation; get written permission and safety clearance; keep the position fixed across sessions.
- Each field session lasts exactly 10 minutes (600 seconds). A separate observer concurrently counts vehicles crossing a fixed point from a safe viewpoint. Record total count `C` and rate `C/(10 min)` in vehicles/minute. Never extend or stop a session to reach a vehicle-count target.
- Divide each session into ten fixed 60-second analysis windows. Per channel-axis window: verify sample timing, remove the mean, apply one fixed pilot-selected window, compute FFT magnitude, and choose the largest positive-frequency bin inside a fixed predeclared band. Use the median of valid window estimates as the session result. Keep FFT peak selection; do not switch to Welch PSD or claim a unique verified structural natural mode.
- Establish local groups from sorted equal-duration pilot counts, then freeze the nearest-rank cutoffs `c₁ = C_(⌈m/3⌉)` and `c₂ = C_(⌈2m/3⌉)`. Assign `NEAR_ZERO` when `C ≤ c₁`, `MEDIUM` when `c₁ < C ≤ c₂`, and `HEAVY` when `C > c₂`. `NEAR_ZERO` can include nonzero counts. Numeric cutoffs cannot be filled until local pilot observations exist; do not choose cutoffs after seeing frequency results.
- Five valid sessions/group is only a practical completion target, not a power calculation. Primary results are descriptive. Any confirmatory inference needs a documented sample-size plan and defensible independent session observations/assumptions; otherwise describe category differences as exploratory.
- Construct session-level `x̄` and sample `s` separately by group/channel/axis. `x̄ ± s` describes observed spread. Keep a separate default `x̄ ± 2s` review heuristic; it prompts human review only and is not a 95% interval, safety limit, or damage threshold.

## Current paper changes

The v2 paper updates the abstract, Chapters I–III, method tables, native Word equations, and the IPO, block and field-process diagrams. Chapters IV–V now contain an objective-aligned proposal-stage reporting plan, not results. Generic “replace this heading” and appendix-template instructions were removed. Visible lists and the Word contents field were refreshed against the rendered layout.

The current visible page references are Figure 1 p. 6; Figure 2 p. 30; Figure 3 p. 33; Figure 4 p. 41; Table 1 p. 32; Table 2 p. 39. The current Word PDF export has 65 pages. Visual QA covered the revised lists, figures, cutoff formula, baseline/sample-SD/CV equations, and changed methods/results pages.

## Pending field facts — do not guess

- Written site authorization, surveyed station, safe mounting point and field procedure.
- Assembled PCB revision, actual IMU channel-addressing/multiplexer behavior, power integrity and USB-C programming check.
- Measured per-channel sample rate, scan timing tolerance, fixed FFT band/window and sufficient record length, confirmed in a pilot.
- Numeric traffic cutoffs after pilot counts; human count reliability from the proposed observation point.
- Actual session counts/results and any sample-size/power justification for inferential claims.

## Verified method sources

- FHWA 2022 traffic-data methodologies: https://www.fhwa.dot.gov/policyinformation/tmguide/tmg_2022/traffic-data-methodologies.cfm
- FHWA 2013 traffic-monitoring theory/manual counts: https://www.fhwa.dot.gov/policyinformation/tmguide/tmg_2013/traffic-monitoring-theory.cfm
- FHWA manual-count guidebook: https://www.fhwa.dot.gov/clas/ctip/traffic_monitoring_guidebook/ch_4.aspx
- Oth & Picozzi (2012) ambient vibration bridge study: https://doi.org/10.1155/2012/876174
- NIST/SEMATECH sample-size guidance: https://www.itl.nist.gov/div898/handbook/prc/section2/prc222.htm
- Espressif ESP32-S3 USB serial/programming: https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/get-started/establish-serial-connection.html
- InvenSense MPU-6000/MPU-6050 specification: https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Datasheet.pdf

These sources support narrowly described claims only. FHWA’s 10-minute increments do not prove that 10 minutes is optimal. Oth and Picozzi’s one-minute PSD windows are precedent, not validation of this FFT configuration. NIST’s sample-size discussion supports not treating five sessions/group as statistically sufficient without a design calculation.

## Next step

Approval has been received. Firmware is implemented as a prototype in the separate GPT Build folder for ESP32-S3-WROOM-1-N16R8 and three MPU6050 ICs. Read its docs/HANDOFF.md, PROJECT_MAP.md and ASTRA_REVIEW_BRIEF.md for actual implementation and verification status. Physical validation is pending. Further manuscript edits require a future user request; preserve both source thesis and approved v2 DOCX.
