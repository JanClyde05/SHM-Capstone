"""Record hashes of completed audit evidence; does not rerun or modify CAD."""
from pathlib import Path
import datetime, hashlib,json,re
HW=Path(__file__).resolve().parents[2];ROOT=HW.parents[1]
OUT=HW/'reports/engineering_audit/20261029'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
g=json.loads((OUT/'geometry.json').read_text());m=json.loads((OUT/'math.json').read_text())
oldpath=HW/'reports/reference_corrected/validation_20261029T145905461959Z/manifest.json'
old=json.loads(oldpath.read_text())
comparison={name:{'recorded':want,'current':sha(Path(name)),'matches':sha(Path(name))==want} for name,want in old['sources'].items()}
assert all(x['matches'] for x in comparison.values()),'Current file differs from accepted CAD evidence'
sources={name:{'recorded':want,'current':sha(HW/name)} for name,want in g['inputs'].items()}
assert all(x['recorded']==x['current'] for x in sources.values())
assert g['script_sha256']==sha(HW/'tools/audit_engineering_geometry.py')
assert m['script_sha256']==sha(HW/'tools/audit_engineering_math.py')
assert g['inputs_unchanged']
relative_targets=[]
for doc in [HW/'docs/ENGINEERING_AUDIT_20261029.md',HW/'docs/ENGINEERING_AUDIT_PLAN.md']:
    for target in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
        if not target.startswith('http'):
            p=(doc.parent/target).resolve()
            # This manifest is about to be created.
            assert p.exists() or p==OUT/'manifest.json',str(p)
            relative_targets.append(str(p.relative_to(ROOT)))
paths=[p for p in OUT.iterdir() if p.is_file() and p.name!='manifest.json']
paths += [HW/'tools/audit_engineering_geometry.py',HW/'tools/audit_engineering_math.py',HW/'docs/ENGINEERING_AUDIT_PLAN.md',HW/'docs/ENGINEERING_AUDIT_20261029.md']
pdf=HW/'reports/engineering_audit/sources/AP7361C_rev5_2_mirror.pdf';paths.append(pdf)
record={'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Read-only engineering audit; no new CAD edits, physical tests or fabrication release',
 'tools':{'KiCad':g['tool'],'Python_for_geometry':g['python'],'Inkscape':'1.4.2 (f4327f4, 2025-05-13)','Poppler':'26.07.0'},
 'commands':[{'command':'C:/Program Files/KiCad/10.0/bin/python.exe tools/audit_engineering_geometry.py --output reports/engineering_audit/20261029','cwd':str(HW),'output_time_utc':g['time_utc'],'observed_exit_code':0},
 {'command':'C:/Program Files/KiCad/10.0/bin/python.exe tools/audit_engineering_math.py','cwd':str(HW),'output_time_utc':m['time_utc'],'observed_exit_code':0},
 {'command':'D:/Inkscape/bin/inkscape.com reports/engineering_audit/20261029/usb_reference_screen.svg --export-filename=reports/engineering_audit/20261029/usb_reference_screen.png','cwd':str(HW),'observed_exit_code':0},
 {'command':'pdftoppm -f 6 -l 6 -singlefile -scale-to 1500 -png reports/engineering_audit/sources/AP7361C_rev5_2_mirror.pdf reports/engineering_audit/sources/AP7361C_p6','cwd':str(HW),'observed_exit_code':0,'stderr':'No display font for Symbol / ArialUnicode; rendered table and footnote visually inspected'}],
 'earlier_CAD_manifest':str(oldpath.relative_to(ROOT)),'earlier_CAD_source_hash_comparison':comparison,'sources_unchanged_since_engineering_read':sources,
 'audit_file_sha256':{str(p.relative_to(ROOT)):sha(p) for p in paths},'relative_link_targets_checked':relative_targets,
 'results':{'geometry_script_completed':True,'math_script_completed':True,'CAD_sources_unchanged':True,'engineering_signoff':False,'finding_register':'ENG-01 through ENG-13 in docs/ENGINEERING_AUDIT_20261029.md'},
 'limits':['No stackup/field solver or electrical-delay proof','No powered USB/ESD/RF/I2C/EN/thermal/frequency measurements','No selected enclosure/fixture or complete DFM/MPN qualification','Diodes official PDF failed access; manufacturer-authored rev5-2 mirror inspected, revision freshness unresolved','ST official web reader succeeded; local PDF download timed out twice','Parallel agents did not complete due to usage limit; no independent-team signoff'],
 'manual_QA':['USB route/reference-screen PNG inspected','Regulator manufacturer-authored p6 thermal table and footnote visually read','Audit relative links and numeric report/table identities checked']}
(OUT/'manifest.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({'manifest':str(OUT/'manifest.json'),'CAD_sources_matched':len(comparison),'audit_artifacts_hashed':len(paths),'engineering_signoff':False},indent=2))
