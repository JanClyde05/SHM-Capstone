# Engineering audit plan — 2026-10-29

User request: continue checking actual design mathematics, differential routing, RF placement, test points and related engineering concerns. This pass reads the active CAD and produces reproducible measurements and an issue/closure matrix; it does not modify CAD, firmware or the approved paper.

## Inputs and boundaries

Active board: `design/SHM_Node_R2.kicad_pcb`, expected SHA-256 `0ea352e982e6ccb87134d1d3dcef7bd3adb747efab5ba28b136cd1090f99540e`, with matching schematic, project and circuit specification. Existing configured CAD checks are recorded in `reports/reference_corrected/validation_20261029T145905461959Z/`. The correct old outline is the root SHM_PCB_New project. Historical clean reports are not electrical qualification.

## Work and acceptance criteria

1. USB: independently reproduce track lengths; include the actual via transition counts and a clearly labeled nominal barrel-length sensitivity calculation. Inspect layer pair, width/gap, connector stubs, ESD flow-through, series-resistor position, return vias and filled reference copper. A sampled copper check is only a geometric screen, not a field solver or proof of impedance. Impedance acceptance requires a selected fabrication stackup and suitable field-solver/fabricator evidence for 90 ohms ±10%; electrical qualification requires prototype tests.
2. RF: verify module/antenna location against the actual outline and keepouts. Separate nominal footprint geometry from module/placement/routing tolerances and final housing, cable, fastener and roadway proximity. Apply module guidance rather than bare-chip antenna-matching instructions. RF signoff needs end-product range/throughput evidence.
3. Power: verify regulator pinout and capacitor values; derive labeled dissipation/thermal, I2C rise-time/sink-current and EN RC equations. Identify missing worst-case load, source/cable, effective capacitance, ambient and thermal-resistance inputs. No assumed copper stackup or nominal load can become a pass result.
4. Test/assembly: inventory exposed test pads, nets, face, spacing and distances to ground; check coverage for bring-up and practical access. Mechanical access requires the intended probe, mounting and enclosure. Review small clearances, die keepouts, mounting and passive/connector part selection.
5. Record primary URLs, document versions/sections, access failures and support limits. Retain scripts/JSON evidence, issue priorities and exact closure steps. Verify source hashes unchanged and refresh MD index, ledgers, feedback log and inventory.

## Execution note

Parallel USB, RF/testpoint and power reviewers were requested. Their sessions stopped at the account usage limit; only a partial USB observation was returned. The primary agent continues the audit. Do not describe it as three completed independent reviews.
