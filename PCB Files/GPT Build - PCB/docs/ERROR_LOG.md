# Design and tool issue log

Updated2026-10-29. **Current issue REF-04: wrong reference outline; correction in progress.** The earlier entries below retain their originalOctober26 checkpoint. Later zero-active-violation checks for the old R2 are recorded in `../../MD Files/14_CAD_VALIDATION_SNAPSHOT.md`; they do not establish conformity to the clarified reference. Some working report filenames were overwritten during iteration, so timestamps distinguish observations. A correction in progress is not a passing recheck.

| ID | Evidence | Issue | Action / current verification |
| --- | --- | --- | --- |
| REF-04 | User correction2026-10-28 plus `reports/reference/reference_correction_20261028.json` | Saved R2 copied larger parent Thesis outline, while user intended only rootSHM_PCB_New79.50 x50.45mm centerline geometry | Prior larger-outline decision superseded. Root is remapping layout/routing to intended reference; prior geometric acceptance invalidated, fresh checks required |
| REF-05 | Old footprint geometry and official Espressif module-placement guidance, checked2026-10-29 | Original module position leaves0.25mm of the footprint-defined antenna area over the compact baseboard | Recommend moving module centerY from60.55 to≤60.30, subject to all pads/courtyards/keepout and manufacturing review; see ANTENNA_PLACEMENT_REVIEW. No final placement or RF qualification claimed |
| REF-01 | Old board inventory command | KiCad10 `LIB_ID.GetUniString()` does not exist | Corrected to `GetUniStringLibId()`; all three inventories completed |
| REF-02 | Initial Inkscape command | `Gio::DBus::Error` during SVG raster request | Later executable invocation produced PNGs asynchronously; files opened and visually inspected |
| REF-03 | Multiple pcbnew board loads | Duplicate image-handler warnings | Inventories completed; no source save occurred |
| SCH-01 | `reports/erc_initial.json` | Six off-grid endpoint warnings and three missing `SHM_Local` footprint-library warnings | Current schematic/library setup changed; latest inspected `erc_current.json` dated2026-10-25T12:49:57 reports zero listed errors/warnings; schematic edits onOct26 require renewed ERC |
| SCH-02 | `reports/erc_current.json` ignored checks | Single-global-label, four-way-junction, SPICE-model and footprint-filter checks are ignored by project configuration | Preserve this qualification when reporting ERC; manual review and footprint/pin validation remain necessary |
| PCB-01 | `reports/drc_placement.json` | Initial placement had courtyard, keepout, hole/edge clearance, drill-range and silk issues plus125 unconnected items | Intermediate placement only. Later preroute report has a different reduced issue set; verify each resolved category against final source rather than assuming broad clearance success |
| PCB-02 | Earlier `reports/drc_preroute.json` dated2026-10-25T12:44:37, contents observed before replacement | Three GND/+3V3 shorting-item errors and three soldermask-bridge errors | Integration corrected C2/C3 pad-orientation/power-routing conflict; replacement report dated12:48:16 has zero listed errors, with115 unconnected items still separate |
| PCB-03 | Earlier preroute report | One courtyard overlap and one PTH-inside-courtyard error | Integration moved J2/SW2; the12:48:16 replacement report lists neither error |
| PCB-04 | Replacement preroute report dated12:48:16 | Thirteen silk-overlap warnings, ten silk-over-copper warnings, one library-footprint mismatch warning | Final silkscreen/footprint review and rerun pending; no blanket suppression justified here |
| PCB-05 | Same preroute report |115 unconnected items | Board had not completed routing; a finished image is not connectivity evidence |
| ROUTE-01 | `reports/routing.log` ending2026-10-25T12:59:27 | Autorouter/optimizer completed with16 unrouted connections and18 internal violations; SES saved | `COMPLETED` is process completion, not routing acceptance. Integration imported the session into KiCad onOct26; actual post-import DRC is required |
| ROUTE-02 | Earlier routing-log contents observed12:47:50 | Freerouting trace normalization reached2000 iterations for +3V3; further normalization suppressed for that candidate | Subsequent route run replaced the working log. Inspect actual imported power geometry; the earlier warning is historical, not proof of a remaining fault |

## Intermediate DRC counts

`drc_placement.json`:43 listed errors (20 courtyard overlaps,12 drill-range,4 items-in-keepout,4 hole-clearance,2 copper-edge and1 clearance);41 warnings (21 silk-overlap,14 silk-over-copper,6 silk-edge);125 unconnected items reported separately.

Earlier `drc_preroute.json` observed at12:44:37:8 listed errors (3 shorting-items,3 soldermask-bridge,1 courtyard-overlap,1 PTH-inside-courtyard);24 warnings (12 silk-overlap,11 silk-over-copper,1 library-footprint mismatch);115 unconnected items reported separately. That working file was replaced. Current inspected replacement at12:48:16:zero listed errors,24 warnings (13 silk-overlap,10 silk-over-copper,1 library-footprint mismatch),115 unconnected items separately. Neither represents final post-routing acceptance.

## Completion rule

Append the actual fix, affected source revision/hash and fresh report filename for each remaining electrical, routing and readability issue. Preserve failed report files. Do not infer a fixed problem merely because its count disappeared after changing a rule, excluding a check, suppressing an item or modifying a footprint. Explain deliberate library modifications and verify them against the manufacturer drawing.

Manual engineering items such as USB pair geometry/stackup, LDO thermal behavior, mounting rigidity and physical sensor timing are tracked in ELECTRICAL_DECISIONS and PROTOTYPE_BRINGUP. Their absence from DRC is not a pass.


## Finisher preparation review — 2026-10-29

Before running on the corrected routed board, source review found that candidate via checks excluded same-net copper and therefore also omitted same-net drilled-hole spacing. The proposed correction checks every existing drilled pad and via independently of net, including the actual new drill size. Bounded KiCad10.0.6 API reads confirmed `GetEffectiveHoleShape().Collide` and `PCB_VIA.GetDrillValue`. The source was updated; final routed-board DRC is still pending, so this is prevention of a detected algorithm gap, not a claimed observed hole violation on the corrected final board.

The prepared finisher also omitted schematic parity in its internal DRC and reused report filenames. It now includes `--schematic-parity`, treats parity issues as unsuccessful completion, and saves each run's reports in its own `reports/reference_corrected/finish_<UTC>/` folder. This preserves failures after reruns. Silkscreen reference placement now checks edge clearance as well as corners inside the outline. Details/hashes: `reports/reference_corrected/finisher_review_20261029.json`.

## USB and compact preroute correction — 2026-10-29

The first two manual USB drafts had six copper clearance errors near the Type-C pads. `usb_drc_v1.json` and `usb_drc_v2.json` are preserved. Moving the connector escape bends outward cleared the nearby CC/SBU/data pads without relaxing the 0.15 mm clearance rule. `usb_drc_v3.json` has zero copper errors. The combined regenerated placement (including inward-facing bypass pads) plus power/USB preroute was rechecked in `preroute_usb_v3_drc.json`: zero errors, 21 silkscreen warnings, 102 unconnected items. These are intermediate results; full routing, return-path/length review, final DRC and physical checks remain separate.

Next-time rule: escape fine-pitch connector pads straight beyond neighboring pad extents before bending; check actual copper outlines, not center-to-center coordinates. Preserve each failure report and do not transfer a clean report to regenerated files without another check.

## USB v5 pre-routing checkpoint — 2026-10-29

After the local support-capacitor tracks and USB refinement, `preroute_usb_v4_support_drc.json` reported one clearance error: a new GND return via at (130.20,78.65) had 0.145 mm clearance to VBUS against the unchanged 0.150 mm rule. Moving that via 0.05 mm right resolved it. Actual `preroute_usb_v5_support_drc.json`: zero errors, 21 silk warnings, 90 unconnected items. The earlier failed report is retained. USB v4's standalone reroute failed through KiCad's loaded-track removal path; `usb_v4_drc.json` checked stale input and is explicitly invalid as v4 acceptance. The helper now refuses existing USB copper; regenerate from placement.

Read-only graph measurements on the saved v5 preroute are in `usb_v5_geometry.json`: endpoint planar mismatch +0.074840 mm for A contacts and -0.078714 mm for B contacts, including module-side copper but excluding via barrels, pads and resistor internals. D- uses two transitions; D+ uses four for A contacts and two for B contacts. Four D+ vias remain versus five previously. This is improved planar geometry, not electrical-delay matching or USB compliance. Return vias were added at the connector crossover; final filled-plane review remains required. `measure_usb_geometry.py` reproduces this bounded measurement.

### Finisher ground-removal API correction

The finisher used the same Python `BOARD.Remove` wrapper implicated by the USB reroute's invalid pad-container failure. Before actual finishing, a read-only historical-board fixture removed 69 unlocked GND items through `RemoveNative`, retained the detached wrappers, rebuilt connectivity and still read all six U6 pads; no files were saved. The finisher now uses that native removal path and keeps detached objects alive until its bounded process exits. Actual final runtime remains a separate gate. This is a targeted correction of a reproduced API risk, not an observed final-board failure.

### First compact SES import stopped by exact coordinate guard

The first finisher run stopped before saving because R1, R2 and H3 X positions rounded upward by one KiCad internal unit (1 nm) through DSN/SES conversion. All 105 locked copper objects were exactly preserved. Read-only before/after coordinates confirmed there was no rotation, side change or larger movement. The finisher now records and restores only a maximum one-IU translation; larger movement or any side/rotation change still fails. The failed run's import_integrity.json is retained. Acceptance requires the rerun to show original placements restored and critical copper unchanged.

### Local bridge search stopped for endpoint correction

The third finisher run was stopped during its bounded grid search after saving the before-bridge and first-bridge reports. Its intermediate board and hash were retained in that run directory. The search used only the DRC item's representative coordinate, which can be the fine-pitch IC end of a track; a 0.25 mm grid may miss the narrow escape corridor even when the same track's capacitor end is accessible. Revise the search to use endpoints/midpoints of the actual disconnected same-net objects and cache obstacle geometry; keep all clearance/edge/keepout checks unchanged. Rerun from the unchanged preroute/SES and require final DRC before acceptance.

Correction to the preceding search note: the process finished just before the attempted stop; Stop-Process reported no such process. It was not interrupted. The actual final result of finish_20261029T101807_234143Z is zero violations and one unconnected item, with zero tab vias accepted. The retained intermediate was earlier in that same completed run. Read actual final reports above any earlier progress assumption. The endpoint-search review remains applicable only to the last actual unresolved gap.

The single remaining actual gap is between U4 VLOGIC/C15 and VDD/C14 copper. Both DRC coordinates pointed to the IC ends of locked support tracks; selecting their capacitor endpoints gives access without changing nets or copper. This bounded endpoint correction is now implemented. All initial thermal-via alternatives were blocked by UART/I2C B.Cu routes; read-only collision checks found clear positions farther right at x154.25/154.65. The finisher will check edge/drill/keepout/track rules again and use short 0.6 mm top links. Final acceptance requires actual DRC and recorded via count. The pre-correction board is retained as SHM_Node_R2_before_final_gap.kicad_pcb; subsequent runs now snapshot every saved board beside each DRC report.

### Alternate input lacked a project sidecar; default CAD rules replaced intended settings

The final-gap run achieved zero unconnected items and eight regulator tab vias but reported 223 violations under unintended default settings (0.20 mm net clearance and 0.30 mm minimum drill, among others). Its alternate input was a copied .kicad_pcb without a matching .kicad_pro, so KiCad loaded defaults and SaveBoard propagated them to the output project. This is a workflow failure, not permission to change rules to hide copper issues. Preserved the wrong default project with the failed report and restored the exact documented preroute project settings (0.15 mm clearance, 0.20 mm minimum drill for module ground vias, 0.10 mm silk clearance). The alternate input now has the same sidecar. Add a preflight sidecar requirement and explicit baseline-rule gates before validating again. Prior failed reports remain intact; final clean status is pending renewed checks on the restored project.

### First independent-audit runtime found two verifier defects

The 20261029T102726587400Z validation has zero ERC violations and zero DRC violations/unconnected/parity issues with restored rules, but its independent audit raised 361 false failures. Of these, 312 came from using SHAPE_RECT(point, size) where KiCad's two-vector overload means opposite corners; the rectangle extended back to (3.08,3.08) instead of being a 3.08 mm square. Another 49 came from comparing the SWIG UTF8 footprint-name wrapper with Python `!=`; the equality/inequality wrapper behavior was inconsistent. Fixed the rectangle using explicit X,Y,width,height integers with a dimension assertion, and compared full library IDs after string conversion. No board geometry changed to satisfy these false findings. Preserve the failed audit; rerun the complete checker and record actual results.

### Final label review and raster export failure

Four reference fields (R1, R8, U1, J1) were hidden under component bodies in the clean pre-polish board. The separate polish_corrected_labels.py moves only these fields. R1's first two positions triggered silk/mask clearance warnings, preserved in validation_20261029T145553220206Z and validation_20261029T145644891866Z. Final checks follow the third position. One concurrent Inkscape top PNG export failed with Gio::DBus::Error; a sequential retry succeeded. Use sequential raster exports on this setup. Native SVG and PNG files were inspected; no physical dimensions or performance are inferred from rendering.

## Final bounded acceptance — 2026-10-29

After all retained failures and label retries, `reports/reference_corrected/validation_20261029T145905461959Z/manifest.json` records active CAD gate passed with zero findings, unchanged source hashes and baseline rules/ignored checks. All 233 numbered pads, 148 intended spec endpoints and the exact reference outline pass the independent audit. This closes CAD errors recorded for the final artifact only. Physical gates remain open. A stale BOM header hash was corrected after checking all 49 CSV references/quantities against current spec; no purchasing claims were added.

## Engineering audit follow-up — 2026-10-29

**Direct user preference:** Continue substantive engineering verification, including mathematics, differential routing, RF, test points and wider checks. Explain what was actually verified; keep retrievable equations, sources and closure criteria. This is a direct request, not an inferred approval of fabrication or physical performance.

**M-PCB-ENG-SCOPE:** The prior planar mismatch metric was explicitly limited but insufficient to answer electrical length matching. New read-only graph reproduces it and adds nominal through-via depth: A contacts change from +0.074839mm planar D−−D+ to −3.125161mm under the1.6mm depth assumption. No CAD was altered to conceal the mismatch. Next-time rule: report layer transitions, path exclusions and stackup together with every differential-length claim.

**M-PCB-ENG-PLACEMENT:** A clean configured DRC did not check the manufacturer's insertion-component spacing. A new body-envelope screen found J2 about5.18mm fromU3 (5.13mm including artwork stroke). The chosen conservative body-edge interpretation and exact-part uncertainty are explicit. Correction remains pending; do not mark this physically closed. Next-time rule: translate applicable component-specific assembly/placement guidance into a separate acceptance review.

**M-PCB-ENG-TOOLS:** Read-only probes initially filtered USB names without removing a leading slash, so no tracks were printed; corrected normalization and asserted a nonempty set in the saved checker. Two exploratory KiCad API calls failed: GetStart on PCB_TEXT and GetName on ZONE. Filtered PCB_SHAPE and used GetZoneName; subsequent geometry run completed. Optional fitz import was unavailable, so used installed Poppler26.07.0. Poppler warned about Symbol/ArialUnicode fonts; inspected the generated regulator p6 and confirmed the table/footnote legible. No failed tool result was used as design evidence; no CAD was mutated by these attempts.

**M-PCB-ENG-REVIEW:** Parallel reviewers stopped at the usage limit, so no three-reviewer signoff is claimed. The primary agent completed the bounded checks. Source-fetch timeouts/403 and the explicitly identified regulator-PDF mirror are logged in the engineering report. Next-time rule: preserve access/tool limitations and verify narrow facts with available primary content without inventing unavailable results.

Evidence: `PCB Files/GPT Build - PCB/docs/ENGINEERING_AUDIT_20261029.md` and `reports/engineering_audit/20261029/`. Active CAD hashes remained unchanged. Open electrical, mechanical, thermal, impedance and physical gates remain listed in ENG-01–ENG-13.

