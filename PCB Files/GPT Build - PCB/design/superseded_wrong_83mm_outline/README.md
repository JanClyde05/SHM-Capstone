# SUPERSEDED / WRONG OUTLINE PCB DESIGN (DO NOT USE)

> **WARNING TO ALL USERS AND AI AGENTS:**
> The files in this directory are **SUPERSEDED AND INCORRECT**. Do NOT use these files for fabrication, review, or firmware correlation.

---

### Why were these files moved here?
These files represent an earlier attempt at routing `SHM_Node_R2` that mistakenly used the top-level `Thesis.kicad_pcb` board outline (16 edge primitives, ~83.61 × 83.12 mm) instead of the user's intended compact thesis reference board.

On **October 28, 2026**, the user explicitly clarified that the only authoritative geometric reference is:
[`PCB Files/Reference PCB (OLD Version)/Thesis/SHM_PCB_New/SHM_PCB_New.kicad_pcb`](file:///d:/Antigravity/Projects/SHM-Capstone/PCB%20Files/Reference%20PCB%20(OLD%20Version)/Thesis/SHM_PCB_New/SHM_PCB_New.kicad_pcb) (12 edge primitives, 79.50 × 50.45 mm).

Consequently, this 83.6 mm layout was **contradicted and superseded**.

---

### Where is the REAL, CURRENT, and CORRECTED design?
The active, corrected design files are located in the parent directory:
* **Active KiCad Project:** [`PCB Files/GPT Build - PCB/design/SHM_Node_R2.kicad_pro`](file:///d:/Antigravity/Projects/SHM-Capstone/PCB%20Files/GPT%20Build%20-%20PCB/design/SHM_Node_R2.kicad_pro)
* **Active Schematic:** [`PCB Files/GPT Build - PCB/design/SHM_Node_R2.kicad_sch`](file:///d:/Antigravity/Projects/SHM-Capstone/PCB%20Files/GPT%20Build%20-%20PCB/design/SHM_Node_R2.kicad_sch)
* **Active PCB Layout:** [`PCB Files/GPT Build - PCB/design/SHM_Node_R2.kicad_pcb`](file:///d:/Antigravity/Projects/SHM-Capstone/PCB%20Files/GPT%20Build%20-%20PCB/design/SHM_Node_R2.kicad_pcb)
* **Active Circuit Spec:** [`PCB Files/GPT Build - PCB/design/circuit_spec.json`](file:///d:/Antigravity/Projects/SHM-Capstone/PCB%20Files/GPT%20Build%20-%20PCB/design/circuit_spec.json)

---

### Files Archived in This Directory:
* `SHM_Node_R2_superseded_83mm.kicad_pcb` (SHA-256: `DA80B01E83B4625F8C970DF54883DBA27B5402EBCA027CB8A6274129E32A0E54` — wrong 83.6mm board)
* `SHM_Node_R2_drc_clean_checkpoint.kicad_pcb`
* `SHM_Node_R2_placement.*` (superseded placement files)
* `SHM_Node_R2_preroute.*` (superseded preroute files)
* `previews/` (subfolder holding superseded visual exports: `routed_board_top.png`, `routed_board_top.svg`, `routed_top.svg`, `placement.png`, `placement.svg`, etc.)

