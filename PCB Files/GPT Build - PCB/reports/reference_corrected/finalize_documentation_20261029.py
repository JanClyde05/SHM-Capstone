"""Dated documentation reconciliation after the accepted active-board check.
Retains prior documents in a ZIP. Does not modify CAD, firmware or manuscripts.
"""
from pathlib import Path
import csv,datetime,hashlib,json,zipfile,re
R=Path(__file__).resolve().parents[2];P=R.parents[1];D=R/'design';M=P/'MD Files'
V=R/'reports/reference_corrected/validation_20261029T145905461959Z'
manifest=json.loads((V/'manifest.json').read_text());assert manifest['cad_gate_passed']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(Path(p))==h for p,h in manifest['sources'].items())
audit=json.loads((V/'independent_audit.json').read_text());h=sha(D/'SHM_Node_R2.kicad_pcb')
vrel=V.relative_to(R).as_posix();now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec='seconds')
targets=[R/'README.md',R/'AGENTS.md',R/'docs/HANDOFF.md',R/'docs/PROJECT_MAP.md',R/'docs/CONTINUATION_PLAN.md',D/'00_README_ACTIVE_DESIGN.md',D/'DESIGN_MANIFEST.json',D/'reference_corrected/README.md',R/'previews/00_README_ACTIVE_PREVIEWS.md',R/'BOM.md']
archive=R/'archive/documentation_before_final_handoff_20261029.zip'
if not archive.exists():
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for p in targets:
   if p.exists():z.write(p,p.relative_to(R).as_posix())
def write(p,s):p.write_text(s.rstrip()+'\n',encoding='utf-8')
def append(p,s):write(p,p.read_text(encoding='utf-8').rstrip()+'\n\n'+s)
result=f'''## Accepted compact CAD checkpoint — 2026-10-29

**Verified for configured CAD checks:** KiCad 10.0.6 reports zero ERC violations, zero DRC violations, zero unconnected items and zero schematic-parity issues. Independent audit: zero failures; 233 numbered pads and 148 intended spec endpoints checked; exact 12-edge reference geometry retained (79.50 × 50.45 mm). This is a prototype/review design, **not a fabrication release or physical validation**.

Active PCB SHA-256: `{h}`. Evidence: `{vrel}/manifest.json`, with commands, source/report hashes, unchanged-source checks, rule values and disabled-category lists. Four baseline ERC categories and five baseline DRC categories remain ignored; no new suppressions or explicit exclusions were accepted. The clean result is bounded by those settings.

Current electrical source is `design/SHM_Node_R2.kicad_sch`, `.net`, `circuit_spec.json`; current board/project/local library are beside them. `design/reference_corrected/` retains reproducible staging inputs and the same final board. The old wrong 83.6 mm board is preserved in `design/superseded_wrong_83mm_outline/`. Earlier reports and hashes remain historical evidence, not current acceptance.
'''
handoff=f'''# Hardware continuation handoff

Updated {now} (Asia/Manila).

{result}
## Completed and checked

- Correct reference silhouette, four copper layers, three MPU6050 devices with common orientation, exact current firmware net contract, native USB-C and N16R8 module.
- Locked main power/USB and 12 local sensor support-capacitor connections. Eight regulator tab vias with 0.60 mm top links, approximately 2.2–2.6 mm long, join ground planes. These dimensions do not establish thermal margin.
- Finished local supply/interrupt gaps, ground fills and silk clearance. Final visual pass moved R1/R8/U1/J1 labels out from under component bodies. Native top/bottom renders and 2D plots were reviewed; the schematic remains the checked, orderly repeated-block layout.
- USB endpoint planar mismatch +0.074839 mm (A contacts), -0.078715 mm (B contacts), including module-side copper. D- has two transitions; D+ has four for A contacts and two for B contacts. This excludes via barrel, pad and component effects and does not establish electrical delay or impedance. See `reports/reference_corrected/usb_active_final_geometry.json`.
- Final candidate and active validation both passed. Exact active files were checked with `tools/run_corrected_checks.py --active`; no manual source change occurred during checks.

## Start here next time

1. Read project AGENTS and MD00/08/12/22; then CONTINUATION_PLAN, this handoff, LAYOUT_REVIEW, RESEARCH_LEDGER and ERROR_LOG. Current user instructions override historic plans.
2. Open `design/SHM_Node_R2.kicad_pro`. Confirm the manifest/source hashes before editing. Do not open the archived wrong-outline project as current.
3. For read-only verification run KiCad Python on `tools/run_corrected_checks.py --active`. Reports are timestamped; preserve failures. Do not rerun generators merely to view the board.
4. For reproduction, preserve manual work first. Build/prepare corrected placement; route the saved DSN; finish the SES using a matching project sidecar. The accepted correction lineage also retains `SHM_Node_R2_before_final_gap.kicad_pcb` plus `.kicad_pro`; finishing that input with `--skip-ses`, followed by `polish_corrected_labels.py`, reproduces the last geometric operations. Rerun all appropriate checks after any regeneration; regenerated UUIDs or router paths need not be byte-identical. Never use the legacy larger-outline writers.
5. Resolve supplier stackup/USB impedance, remaining passive/switch/header MPNs, stencil/DFM, cable/enclosure/fastener clearance and mounting interface before a fabrication release. Then follow PROTOTYPE_BRINGUP for actual assembly/power/thermal/USB/I2C/DRDY/FIFO/noise/frequency-reference evidence.

## Checks not performed and assumptions

No powered hardware, fabricator DFM, controlled-impedance calculation/measurement, ESD/USB compliance, thermal load test, sensor calibration, mechanical transfer or field test was performed. No purchasing or fabrication submission occurred. Four layers, regulator/support parts and three-hole mounting pattern are documented engineering choices; supplier and fixture details remain open. Generic MPU 3D bodies are approximate visual models. Paper, firmware and original reference CAD were not edited in this continuation.

No CAD generation or routing process is intentionally left running at this handoff. Failed checks and tool defects are preserved in ERROR_LOG and MD22; do not interpret an earlier failed status as the current result or erase it after a pass.
'''
old=(R/'docs/HANDOFF.md').read_text();write(R/'docs/HANDOFF.md',handoff+'\n## Preserved earlier checkpoints\n\n'+old)
write(R/'README.md',f'''# SHM frequency-acquisition hardware

The active KiCad design uses ESP32-S3-WROOM-1-N16R8, three bare MPU6050 ICs and one USB-C power/programming connection. It retains the user's **SHM_PCB_New 79.50 × 50.45 mm** silhouette.

Open [the KiCad project](design/SHM_Node_R2.kicad_pro), [schematic](design/SHM_Node_R2.kicad_sch), or [PCB](design/SHM_Node_R2.kicad_pcb). See [top preview](previews/active_pcb_3d_top.png) and [schematic PDF](previews/SHM_Node_R2_schematic.pdf).

**CAD checks pass; fabrication qualification remains open.** KiCad 10.0.6 ERC/DRC/connectivity/parity and the independent audit report zero findings under documented settings. [Exact evidence]({vrel}/manifest.json) records hashes, commands and ignored checks. PCB SHA-256: `{h}`.

Read [HANDOFF](docs/HANDOFF.md), [CONTINUATION_PLAN](docs/CONTINUATION_PLAN.md), [PROJECT_MAP](docs/PROJECT_MAP.md), [LAYOUT_REVIEW](docs/LAYOUT_REVIEW.md), [RESEARCH_LEDGER](docs/RESEARCH_LEDGER.md), [ERROR_LOG](docs/ERROR_LOG.md), [BOM](BOM.md) and [PROTOTYPE_BRINGUP](docs/PROTOTYPE_BRINGUP.md). The old wrong-outline board is preserved in `design/superseded_wrong_83mm_outline/`; staging history is in `design/reference_corrected/`.

Supplier stackup/USB impedance, remaining exact part selections, thermal/assembly/mounting review and all physical tests remain open. No bench or field performance is claimed. Arduino firmware and the approved paper are unchanged by this hardware continuation.
''')
p=R/'AGENTS.md';s=p.read_text();a=s.index('The compact candidate is in');z=s.index('\n\nConfirmed hardware:',a)
s=s[:a]+'''The active corrected compact board is `design/SHM_Node_R2.kicad_pcb` with its matching project, schematic, netlist/spec and SHM_Local.pretty library. The previous wrong outline is archived in `design/superseded_wrong_83mm_outline/`. `design/reference_corrected/` retains staging/reproduction files and the accepted candidate. Read HANDOFF for final hashes and reports. The old build_board.py, prepare_routing.py and finish_board.py are guarded legacy writers; do not use them for active work. Corrected generators write staging files and can discard later edits, so preserve manual changes first. Any copied alternate PCB input must include a matching .kicad_pro sidecar with the reviewed rules. Run `run_corrected_checks.py --active` for the active project. Electrical edits require synchronized schematic/spec/netlist/local libraries and renewed checks.''' +s[z:];write(p,s)
p=R/'docs/PROJECT_MAP.md';s=p.read_text();write(p,'# Project navigation map\n\n'+result+'''## Current navigation

| File / folder | Use |
|---|---|
| `design/SHM_Node_R2.kicad_pro`, `.kicad_sch`, `.kicad_pcb` | Active editable corrected project |
| `design/DESIGN_MANIFEST.json` | Exact active file hashes and current report link |
| `design/reference_corrected/` | Staging, saved inputs and final candidate; not the default editing location |
| `design/superseded_wrong_83mm_outline/`, `archive/` | Preserved superseded design and recovery snapshots |
| `tools/run_corrected_checks.py --active` | Timestamped active ERC/DRC/independent verification |
| `tools/build_corrected_board.py`, `prepare_corrected_routing.py`, `route_corrected_usb.py` | Placement/critical-route generators; not safe over unpreserved manual work |
| `tools/finish_corrected_board.py`, `polish_corrected_labels.py` | Routing import, local repairs, planes and final four reference labels |
| `tools/verify_corrected_board.py`, `measure_usb_geometry.py` | Independent consistency/geometry and bounded USB path metrics |
| `docs/HANDOFF.md`, `CONTINUATION_PLAN.md`, `LAYOUT_REVIEW.md` | Current results, next actions and engineering limits |
| `docs/RESEARCH_LEDGER.md`, `ELECTRICAL_DECISIONS.md`, `ERROR_LOG.md` | Primary sources, choices and retained failures |
| `BOM.md`, `BOM.csv`, `docs/PROTOTYPE_BRINGUP.md` | Engineering parts list and unperformed physical checks |
| `previews/00_README_ACTIVE_PREVIEWS.md` | Current visual artifact index; other preview names may be historic |

## Earlier map snapshots (historical)

'''+s)
p=R/'docs/CONTINUATION_PLAN.md';s=p.read_text();write(p,'# PCB continuation plan and recovery instructions\n\n'+result+'''**Current phase status:** A–G are complete for the bounded CAD deliverable and documentation. H remains open: supplier/assembly/physical qualification. Earlier phase tables below record planning history and are superseded by this result and HANDOFF. Do not rerun a completed generator as an automatic next step. Any new edit requires its own logged plan, source verification and appropriate rerun. The active checker command is `KiCad-python tools/run_corrected_checks.py --active`; omitting --active checks staging.

## Preserved planning and execution history

'''+s)
write(D/'reference_corrected/README.md',f'''# Corrected-reference staging and reproduction history

The active editing location is the parent `design/`. This staging directory retains placement/preroute, saved local-gap input with project sidecar, and final candidate. The final candidate matches active PCB SHA-256 `{h}`. Earlier intermediates are incomplete and must not be fabricated. Read `../../docs/HANDOFF.md` and `CONTINUATION_PLAN.md` before regeneration. The earlier wrong outline is in the parent's `superseded_wrong_83mm_outline/` directory.
''')
write(D/'00_README_ACTIVE_DESIGN.md',f'''# Active corrected hardware design

Open [SHM_Node_R2.kicad_pro](SHM_Node_R2.kicad_pro). The [schematic](SHM_Node_R2.kicad_sch), [PCB](SHM_Node_R2.kicad_pcb), [spec](circuit_spec.json), [netlist](SHM_Node_R2.net), project settings and SHM_Local.pretty are one synchronized set. Do not separate a copied board from its matching project sidecar.

PCB SHA-256 `{h}`. Exact 12-edge, 79.50 × 50.45 mm SHM_PCB_New outline; four copper layers; 38 assembly placements, 11 test pads and three mechanical holes.

KiCad 10.0.6 ERC/DRC/connectivity/parity and independent checks pass under the recorded settings. [Validation manifest](../{vrel}/manifest.json) and [handoff](../docs/HANDOFF.md) state source hashes, commands, ignored checks and physical limits. This is a review/prototype design, not a fabrication release.

Run `tools/run_corrected_checks.py --active` with KiCad Python from the hardware-project root for new timestamped reports. `reference_corrected/` is retained staging; `superseded_wrong_83mm_outline/` is historical. Preserve both. No manuscript or firmware changes are implied.
''')
dm=json.loads((D/'DESIGN_MANIFEST.json').read_text());dm['updated_at']=now
dm['file_hashes_sha256']={p.name:sha(p) for p in [D/n for n in ['SHM_Node_R2.kicad_pcb','SHM_Node_R2.kicad_sch','SHM_Node_R2.kicad_pro','circuit_spec.json','SHM_Node_R2.net','fp-lib-table']]}
dm['local_library_hashes']={p.name:sha(p) for p in (D/'SHM_Local.pretty').glob('*.kicad_mod')}
dm['validation_manifest']=vrel+'/manifest.json';dm['validation_scope']='Configured CAD checks only; baseline ignored categories listed in validation manifest'
dm['physical_status']='Unverified; supplier stackup, parts/assembly, thermal, USB, sensor and field qualification open'
write(D/'DESIGN_MANIFEST.json',json.dumps(dm,indent=2))
write(R/'previews/00_README_ACTIVE_PREVIEWS.md',f'''# Active visual previews

Updated {now}. Active PCB SHA-256 `{h}`. Native KiCad geometry was used, not an AI-generated design image.

| File | Scope |
|---|---|
| [active_pcb_3d_top.png](active_pcb_3d_top.png) | Latest top render, 1600 × 1100; final labels visible |
| [active_pcb_3d_bottom.png](active_pcb_3d_bottom.png) | Latest bottom render, 1600 × 1100 |
| [active_pcb_top.svg](active_pcb_top.svg) | Latest top copper/silkscreen/edge plot |
| [active_pcb_bottom.svg](active_pcb_bottom.svg) | Bottom plot; unchanged by four front-label moves |
| [active_schematic.png](active_schematic.png), [active_schematic.svg](active_schematic.svg), [SHM_Node_R2_schematic.pdf](SHM_Node_R2_schematic.pdf) | Unchanged current schematic exports |

Other preview filenames retain intermediate/history artifacts and must not be assumed current. The wrong-outline previews are archived in `../design/superseded_wrong_83mm_outline/previews/`. Generic MPU 3D models are approximate visual packages, not verified manufacturer mechanical models. Rendering does not establish fabrication, thermal, USB, RF or measurement performance.
''')
rows=list(csv.DictReader((R/'BOM.csv').open(encoding='utf-8-sig')));refs=[r.strip() for row in rows for r in row['References'].split(',')];spec=json.loads((D/'circuit_spec.json').read_text())
assert len(refs)==49 and len(set(refs))==49 and set(refs)=={c['ref'] for c in spec['components']}
assert all(int(row['Quantity'])==len(row['References'].split(',')) for row in rows)
p=R/'BOM.md';s=p.read_text();s=re.sub(r'Generated 2026-10-26 from `design/circuit_spec.json`\. Source SHA256: `[^`]+`\.',f'Reconciled 2026-10-29 against `design/circuit_spec.json` and all 49 CSV references/quantities. Source SHA256: `{sha(D/"circuit_spec.json")}`. Earlier header hash was stale; component content was unchanged.',s);write(p,s)
append(R/'docs/LAYOUT_REVIEW.md',result+'''Final visual scope: inspected top/bottom copper plots, latest 1600×1100 top/bottom native 3D renders and the unchanged full schematic export. No crossing/overlap was inferred from images alone; actual connectivity and clearance checks are in the manifest. Eight regulator tab vias and the four visible reference-label corrections are present. Selected stackup, actual impedance, mounting/cable envelope and physical thermal/measurement qualification remain open.
''')
append(R/'docs/ERROR_LOG.md',f'''## Final bounded acceptance — 2026-10-29

After all retained failures and label retries, `{vrel}/manifest.json` records active CAD gate passed with zero findings, unchanged source hashes and baseline rules/ignored checks. All 233 numbered pads, 148 intended spec endpoints and the exact reference outline pass the independent audit. This closes CAD errors recorded for the final artifact only. Physical gates remain open. A stale BOM header hash was corrected after checking all 49 CSV references/quantities against current spec; no purchasing claims were added.
''')
central=f'''## Final corrected PCB CAD delivery — 2026-10-29

Active artifact: `PCB Files/GPT Build - PCB/design/SHM_Node_R2.kicad_pcb`, SHA-256 `{h}`. The four final reference-label moves change the earlier promoted hash `804D5B67...`; components, pad nets, copper and outline are unchanged by those moves. Old source/report hashes are historical.

Exact evidence: `PCB Files/GPT Build - PCB/{vrel}/manifest.json`. KiCad 10.0.6 ERC/DRC/connectivity/parity and independent audit: zero findings; 233 numbered pads, 148 spec endpoints, firmware mappings, native USB/reserved pins, actual MPU center copper/paste and rule areas checked. Exact SHM_PCB_New 12-edge 79.50 × 50.45 mm outline. Baseline four ERC/five DRC ignored categories remain explicitly listed; no explicit exclusions/new suppressions. Report commands, timestamps and source/report hashes are retained.

Current recovery/navigation: hardware `docs/HANDOFF.md`, `CONTINUATION_PLAN.md`, `PROJECT_MAP.md`, `LAYOUT_REVIEW.md`, `RESEARCH_LEDGER.md`, `ERROR_LOG.md`, `BOM.md` and `PROTOTYPE_BRINGUP.md`. Active native files are in `design/`; staging in `design/reference_corrected/`; wrong 83 mm history in `design/superseded_wrong_83mm_outline/`. Run `tools/run_corrected_checks.py --active` for active files. Do not run legacy writers or regenerate over later manual work.

Remaining gates: fabricator stackup/USB impedance, exact remaining parts and DFM/stencil, enclosure/cable/mounting, thermal/current/USB/I2C/DRDY/FIFO, reference-frequency and field tests. No physical validation or fabrication release is claimed. Paper and firmware were not edited during this continuation. Top/bottom native renders and copper plots were visually inspected, and the existing schematic layout remains unchanged.
'''
for n in ['00_README.md','08_PROJECT_MAP_AND_SOURCE_OF_TRUTH.md','09_VERIFICATION_LEDGER.md','12_EXECUTION_PLAN.md']:
 append(M/n,central)
p=M/'14_CAD_VALIDATION_SNAPSHOT.md';write(p,'# KiCad validation snapshot\n\n'+central+'\n## Earlier snapshots (historical)\n\n'+p.read_text())
append(M/'22_AI_FEEDBACK_AND_MISTAKE_LOG.md',f'''### M-PCB-2026-10-29-CLOSE — Final rerun and handoff reconciliation

The accepted active check is `{vrel}/manifest.json`: zero findings, expected rules, unchanged sources and zero independent failures. Four body-hidden labels were corrected and the final R1 placement passed. Prior failures remain retained. Hardware HANDOFF/AGENTS/README/map still described a not-yet-promoted board after another saved checkpoint had promoted it; compared hashes before edits, confirmed the active/candidate identity, and reconciled those stale instructions. Preserved prior documentation ZIP. Next-time rule: re-read actual files after interruption, reconcile promotion status, and report current evidence separately from historical checkpoints. No physical gates were closed by these CAD checks.
''')
append(M/'10_RESEARCH_REFERENCE_AUDIT.md','''## Hardware-source recheck — 2026-10-29

Hardware-only continuation re-opened [Espressif S3 layout USB guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html) and [ST USBLC6-2 DS4260 rev7](https://www.st.com/resource/en/datasheet/usblc6-2.pdf). Verified scope: manufacturer USB routing guidance and ST flow-through pin diagram. These do not validate this board's impedance, thermal margin, ESD/USB compliance or research measurement accuracy. Exact application and limits are in hardware RESEARCH_LEDGER and LAYOUT_REVIEW. No manuscript citation or claim was changed in this hardware pass.
''')
report={'updated_at':now,'active_pcb_sha256':h,'validation_manifest':str(V/'manifest.json'),'documentation_archive':str(archive),'bom_reference_count':len(refs),'physical_validation':'not performed','firmware_or_paper_edits':'none in this continuation'}
write(R/'reports/reference_corrected/final_documentation_checkpoint.json',json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
