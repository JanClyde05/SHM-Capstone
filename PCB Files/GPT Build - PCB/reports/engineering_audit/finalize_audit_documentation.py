"""Append bounded engineering-audit findings, preserving prior document history."""
from pathlib import Path
import datetime, hashlib, json, zipfile
ROOT=Path(__file__).resolve().parents[4]
HW=ROOT/'PCB Files/GPT Build - PCB'
marker='Engineering audit follow-up — 2026-10-29'
report=HW/'docs/ENGINEERING_AUDIT_20261029.md'
core='''The deeper read-only audit found issues beyond configured ERC/DRC: USB A-contact transition imbalance (4 D+ versus 2 D−), missing explicit impedance stackup, no local capacitor directly on the ESD VBUS net, J2-to-U3 nominal body separation about 5.18 mm (5.13 mm conservative F.Fab box) against the TDK 6 mm insertion-component guidance, and unresolved thermal/probe-access qualification. Nominal antenna overhang is 0.10 mm with no recorded tolerance budget. These are engineering concerns, not observed prototype failures. Active PCB remains unchanged at SHA-256 `0ea352e982e6ccb87134d1d3dcef7bd3adb747efab5ba28b136cd1090f99540e`; the earlier configured CAD pass remains bounded evidence.'''
hwblock=f'''## {marker}

Read [ENGINEERING_AUDIT_20261029.md](ENGINEERING_AUDIT_20261029.md) and its [plan](ENGINEERING_AUDIT_PLAN.md) before the next CAD edit. {core}

New evidence: `reports/engineering_audit/20261029/geometry.json`, `math.json`, and USB plane-screen SVG/PNG; reproducible tools `audit_engineering_geometry.py` and `audit_engineering_math.py`. Start with the report's ordered corrections and acceptance criteria. The audit did not change CAD, firmware or paper, and does not authorize fabrication.

'''
changes={}
for rel in ['docs/HANDOFF.md','docs/CONTINUATION_PLAN.md','docs/PROJECT_MAP.md']:
    changes[HW/rel]=('top',hwblock)
changes[HW/'README.md']=('top',hwblock.replace('(ENGINEERING_', '(docs/ENGINEERING_'))
for rel in ['docs/LAYOUT_REVIEW.md','docs/AUDIT_ELECTRICAL.md']:
    changes[HW/rel]=('append',hwblock)
central=f'''## {marker}

Hardware review: [engineering audit](../PCB%20Files/GPT%20Build%20-%20PCB/docs/ENGINEERING_AUDIT_20261029.md), [scope/plan](../PCB%20Files/GPT%20Build%20-%20PCB/docs/ENGINEERING_AUDIT_PLAN.md). {core}

The report maps ENG-01–ENG-13 to file evidence, source IDs E1–E9, equation IDs and closure steps. `tools/audit_engineering_geometry.py` measures paths, reference-fill samples, antenna geometry, test pads and insertion-component proximity; `tools/audit_engineering_math.py` records conditional power/thermal/I2C/RC arithmetic. Data is in `PCB Files/GPT Build - PCB/reports/engineering_audit/20261029/`. No physical tests or new CAD edits were performed.

'''
for rel in ['00_README.md','08_PROJECT_MAP_AND_SOURCE_OF_TRUTH.md','09_VERIFICATION_LEDGER.md','14_CAD_VALIDATION_SNAPSHOT.md']:
    changes[ROOT/'MD Files'/rel]=('append',central)
changes[ROOT/'MD Files/12_EXECUTION_PLAN.md']=('append',central+'''Next hardware work is bounded by the audit: plan a separate candidate for ESD bypass and header clearance; select real stackup/remaining parts; revise USB with balanced transitions and verified geometry; resolve power/source/ambient and mounting/access limits. Synchronize schematic/spec/netlist/BOM, then rerun ERC/DRC/parity and independent checks. A nominal barrel-length correction is not permission to add arbitrary meanders. Physical qualification remains a separate gate.

''')
sourceblock=f'''## {marker}

Source register E1–E9 and exact application limits are in hardware `docs/ENGINEERING_AUDIT_20261029.md`. Reopened official Espressif layout/module v1.8/reset guidance; ST USBLC6-2 rev7 §2.3/Fig17 and AN5225 rev7 §4 Tables6–7; TDK MPU rev3.4 pp14/16/18/42–43; TI SLVA689A (October2026); Littelfuse1206L (February2024). These support component guidance and conditional calculations, not this board's field performance.

The official Diodes AP7361C PDF timed out in the web reader and returned403 in the direct client. Read manufacturer-authored DS37274 rev5-2 (October2020) from a separately identified mirror; saved source/hash in `reports/engineering_audit/sources/source_files.json`. Rendered p6 confirmed110°C/W is for a minimum-pad reference condition. Official-current revision freshness is partially verified; do not treat mirror availability as proof of revision currency. ST local PDF fetch timed out twice although its official web reader worked. Source access failures are retained, not reported as successful downloads.

The 100nF ESD bypass and ≥6mm insertion-component guidance lead to proposed corrections, not empirical failure claims. Equation outputs are verified only under declared inputs. The approved paper and firmware were untouched.

'''
changes[ROOT/'MD Files/10_RESEARCH_REFERENCE_AUDIT.md']=('append',sourceblock)
changes[HW/'docs/RESEARCH_LEDGER.md']=('append',sourceblock)
mistakes=f'''## {marker}

**Direct user preference:** Continue substantive engineering verification, including mathematics, differential routing, RF, test points and wider checks. Explain what was actually verified; keep retrievable equations, sources and closure criteria. This is a direct request, not an inferred approval of fabrication or physical performance.

**M-PCB-ENG-SCOPE:** The prior planar mismatch metric was explicitly limited but insufficient to answer electrical length matching. New read-only graph reproduces it and adds nominal through-via depth: A contacts change from +0.074839mm planar D−−D+ to −3.125161mm under the1.6mm depth assumption. No CAD was altered to conceal the mismatch. Next-time rule: report layer transitions, path exclusions and stackup together with every differential-length claim.

**M-PCB-ENG-PLACEMENT:** A clean configured DRC did not check the manufacturer's insertion-component spacing. A new body-envelope screen found J2 about5.18mm fromU3 (5.13mm including artwork stroke). The chosen conservative body-edge interpretation and exact-part uncertainty are explicit. Correction remains pending; do not mark this physically closed. Next-time rule: translate applicable component-specific assembly/placement guidance into a separate acceptance review.

**M-PCB-ENG-TOOLS:** Read-only probes initially filtered USB names without removing a leading slash, so no tracks were printed; corrected normalization and asserted a nonempty set in the saved checker. Two exploratory KiCad API calls failed: GetStart on PCB_TEXT and GetName on ZONE. Filtered PCB_SHAPE and used GetZoneName; subsequent geometry run completed. Optional fitz import was unavailable, so used installed Poppler26.07.0. Poppler warned about Symbol/ArialUnicode fonts; inspected the generated regulator p6 and confirmed the table/footnote legible. No failed tool result was used as design evidence; no CAD was mutated by these attempts.

**M-PCB-ENG-REVIEW:** Parallel reviewers stopped at the usage limit, so no three-reviewer signoff is claimed. The primary agent completed the bounded checks. Source-fetch timeouts/403 and the explicitly identified regulator-PDF mirror are logged in the engineering report. Next-time rule: preserve access/tool limitations and verify narrow facts with available primary content without inventing unavailable results.

Evidence: `PCB Files/GPT Build - PCB/docs/ENGINEERING_AUDIT_20261029.md` and `reports/engineering_audit/20261029/`. Active CAD hashes remained unchanged. Open electrical, mechanical, thermal, impedance and physical gates remain listed in ENG-01–ENG-13.

'''
changes[ROOT/'MD Files/22_AI_FEEDBACK_AND_MISTAKE_LOG.md']=('append',mistakes)
changes[HW/'docs/ERROR_LOG.md']=('append',mistakes)
backup=HW/'reports/engineering_audit/documentation_before_audit_followup_20261029.zip'
if not backup.exists():
    with zipfile.ZipFile(backup,'x',zipfile.ZIP_DEFLATED) as z:
        for path in changes:z.write(path,path.relative_to(ROOT))
updated=[]
for path,(mode,block) in changes.items():
    old=path.read_text(encoding='utf-8-sig')
    if marker in old:continue
    if mode=='top':
        first,sep,rest=old.partition('\n');new=first+'\n\n'+block+rest.lstrip('\n')
    else:new=old.rstrip()+'\n\n'+block
    path.write_text(new,encoding='utf-8');updated.append(str(path.relative_to(ROOT)))
record={'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'changed_documentation':updated,'backup':str(backup.relative_to(ROOT)),'scope':'Audit documentation only; no CAD, paper or firmware edits'}
(HW/'reports/engineering_audit/documentation_update.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record,indent=2))
