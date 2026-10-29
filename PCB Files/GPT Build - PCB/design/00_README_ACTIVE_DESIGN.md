# Active corrected hardware design

Open [SHM_Node_R2.kicad_pro](SHM_Node_R2.kicad_pro). The [schematic](SHM_Node_R2.kicad_sch), [PCB](SHM_Node_R2.kicad_pcb), [spec](circuit_spec.json), [netlist](SHM_Node_R2.net), project settings and SHM_Local.pretty are one synchronized set. Do not separate a copied board from its matching project sidecar.

PCB SHA-256 `0ea352e982e6ccb87134d1d3dcef7bd3adb747efab5ba28b136cd1090f99540e`. Exact 12-edge, 79.50 × 50.45 mm SHM_PCB_New outline; four copper layers; 38 assembly placements, 11 test pads and three mechanical holes.

KiCad 10.0.6 ERC/DRC/connectivity/parity and independent checks pass under the recorded settings. [Validation manifest](../reports/reference_corrected/validation_20261029T145905461959Z/manifest.json) and [handoff](../docs/HANDOFF.md) state source hashes, commands, ignored checks and physical limits. This is a review/prototype design, not a fabrication release.

Run `tools/run_corrected_checks.py --active` with KiCad Python from the hardware-project root for new timestamped reports. `reference_corrected/` is retained staging; `superseded_wrong_83mm_outline/` is historical. Preserve both. No manuscript or firmware changes are implied.
