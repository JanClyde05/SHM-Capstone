# USB geometry revision v4 — proposed before execution

2026-10-29, candidate-only change. Source: `tools/route_corrected_usb.py`; baseline `preroute_usb_v3_drc.json` has zero copper errors, 21 silkscreen warnings, 102 unconnected items. Those incomplete-route counts are not final acceptance.

## Proposed coordinates and rationale

1. Remove redundant D+ via at (131.1, 81.35). Keep the B.Cu crossover between (130.25, 80.05) and (130.25, 81.35), then route F.Cu directly from the latter to U6 pin3 (131.8625, 81.25). This removes one data via without changing the circuit.
2. Shorten the D− main-path fanout: replace the corner (125.35, 68.8)/(127.05, 68.8) with (125.35, 69.53539)/(127.78539, 69.53539). The diagonal remains on its existing line. Predicted planar reduction about 1.0400 mm; goal is less than 0.2 mm endpoint planar mismatch in both connector orientations. This is an engineering geometry goal, not a manufacturer numeric tolerance, electrical-delay result, or controlled-impedance claim.
3. Add GND return-via pairs near the connector crossover at (130.2,78.65)/(131.0,78.65) and (130.25,82.15)/(131.05,82.15), subject to actual DRC. Keep each through via 0.6 mm diameter/0.3 mm drill. Inner planes provide ground connection after fill; these coordinates are not yet validated.
4. Avoid duplicating already present locked GND segments/vias when the helper is rerun over its own input. Preserve the previous review artifact and report before replacement.
5. Correct source/report wording: 0.20 mm edge gap on the vertical parallel portion; approximately 0.1536 mm on its 45-degree portions. Width/gap remains provisional pending a fabricator stackup.

## Acceptance

Run helper only to its separate review board. Save unique v4 DRC with refill; require no new copper/edge/courtyard errors, no USB unconnected items. Recalculate graph endpoint lengths and via transitions from saved board; report exclusions. Preserve v3 evidence. Root must regenerate the fresh preroute only after accepting this review; do not alter placement/preroute here. No schematic, firmware, original reference, or manuscript changes.

## Execution deviation and failed-check history

The first standalone v4 run failed before saving because removing loaded USB tracks through `pcbnew.BOARD.Remove(t)` caused unrelated `U6.Pads()` to return a non-iterable `SwigPyObject`; a minimal reproduction confirmed the same failure. Prior review board was preserved. The accidentally launched `usb_v4_drc.json` checked the stale prior review board and **is invalid as v4 acceptance**. The helper now rejects existing USB copper before any mutation. Root will regenerate its fresh preparation from placement, where no USB removal is necessary, then run a uniquely named DRC. This is a tool/rerun failure, not evidence that the proposed route passed or failed clearance.

Next-time rule: never run the USB helper on previously routed input. Rebuild fresh placement/power preparation; preserve routed manual work instead of invoking a destructive regeneration blindly.
