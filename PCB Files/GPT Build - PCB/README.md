# SHM frequency-acquisition hardware

## Engineering audit follow-up — 2026-10-29

Read [ENGINEERING_AUDIT_20261029.md](docs/ENGINEERING_AUDIT_20261029.md) and its [plan](docs/ENGINEERING_AUDIT_PLAN.md) before the next CAD edit. The deeper read-only audit found issues beyond configured ERC/DRC: USB A-contact transition imbalance (4 D+ versus 2 D−), missing explicit impedance stackup, no local capacitor directly on the ESD VBUS net, J2-to-U3 nominal body separation about 5.18 mm (5.13 mm conservative F.Fab box) against the TDK 6 mm insertion-component guidance, and unresolved thermal/probe-access qualification. Nominal antenna overhang is 0.10 mm with no recorded tolerance budget. These are engineering concerns, not observed prototype failures. Active PCB remains unchanged at SHA-256 `0ea352e982e6ccb87134d1d3dcef7bd3adb747efab5ba28b136cd1090f99540e`; the earlier configured CAD pass remains bounded evidence.

New evidence: `reports/engineering_audit/20261029/geometry.json`, `math.json`, and USB plane-screen SVG/PNG; reproducible tools `audit_engineering_geometry.py` and `audit_engineering_math.py`. Start with the report's ordered corrections and acceptance criteria. The audit did not change CAD, firmware or paper, and does not authorize fabrication.

The active KiCad design uses ESP32-S3-WROOM-1-N16R8, three bare MPU6050 ICs and one USB-C power/programming connection. It retains the user's **SHM_PCB_New 79.50 × 50.45 mm** silhouette.

Open [the KiCad project](design/SHM_Node_R2.kicad_pro), [schematic](design/SHM_Node_R2.kicad_sch), or [PCB](design/SHM_Node_R2.kicad_pcb). See [top preview](previews/active_pcb_3d_top.png) and [schematic PDF](previews/SHM_Node_R2_schematic.pdf).

**CAD checks pass; fabrication qualification remains open.** KiCad 10.0.6 ERC/DRC/connectivity/parity and the independent audit report zero findings under documented settings. [Exact evidence](reports/reference_corrected/validation_20261029T145905461959Z/manifest.json) records hashes, commands and ignored checks. PCB SHA-256: `0ea352e982e6ccb87134d1d3dcef7bd3adb747efab5ba28b136cd1090f99540e`.

Read [HANDOFF](docs/HANDOFF.md), [CONTINUATION_PLAN](docs/CONTINUATION_PLAN.md), [PROJECT_MAP](docs/PROJECT_MAP.md), [LAYOUT_REVIEW](docs/LAYOUT_REVIEW.md), [RESEARCH_LEDGER](docs/RESEARCH_LEDGER.md), [ERROR_LOG](docs/ERROR_LOG.md), [BOM](BOM.md) and [PROTOTYPE_BRINGUP](docs/PROTOTYPE_BRINGUP.md). The old wrong-outline board is preserved in `design/superseded_wrong_83mm_outline/`; staging history is in `design/reference_corrected/`.

Supplier stackup/USB impedance, remaining exact part selections, thermal/assembly/mounting review and all physical tests remain open. No bench or field performance is claimed. Arduino firmware and the approved paper are unchanged by this hardware continuation.
