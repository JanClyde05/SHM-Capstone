"""Run and hash corrected-candidate CAD checks. Does not establish physical performance.
Does not rebuild or promote design files. Preserve timestamped results for every run.
"""
from pathlib import Path
import argparse,subprocess,json,hashlib,datetime,sys
ROOT=Path(__file__).resolve().parents[1];DES=ROOT/'design/reference_corrected'
CLI=Path('C:/Program Files/KiCad/10.0/bin/kicad-cli.exe')
# KiCad 10.0.6 baseline keys observed in retained ERC/DRC reports, not new suppressions.
ALLOWED_IGNORED={
 'erc.json':{'single_global_label','four_way_junction','simulation_model_issue','footprint_filter'},
 'drc.json':{'missing_courtyard','track_not_centered_on_via','tuning_profile_track_geometries','footprint_filters_mismatch','footprint_type_mismatch'}}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def explicit_exclusions(value,path='project'):
    found=[]
    if isinstance(value,dict):
        for key,item in value.items():
            location=path+'.'+key
            if key in {'exclusions','drc_exclusions','erc_exclusions'} and item:found.append({'path':location,'value':item})
            found.extend(explicit_exclusions(item,location))
    elif isinstance(value,list):
        for i,item in enumerate(value):found.extend(explicit_exclusions(item,path+f'[{i}]'))
    return found

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--active',action='store_true',help='Check promoted design/ files instead of the staging candidate')
    args=parser.parse_args();design=ROOT/'design' if args.active else DES
    board=design/'SHM_Node_R2.kicad_pcb';sch=design/'SHM_Node_R2.kicad_sch';project=design/'SHM_Node_R2.kicad_pro'
    if not board.exists() or not sch.exists():raise SystemExit('Final corrected candidate is not present; do not audit an intermediate as final')
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    rep=ROOT/'reports/reference_corrected'/('validation_'+stamp);rep.mkdir(parents=True)
    version=subprocess.run([str(CLI),'--version'],capture_output=True,text=True)
    sources=[board,sch,project,design/'circuit_spec.json',design/'SHM_Node_R2.net',Path(__file__).resolve(),ROOT/'tools/verify_corrected_board.py']
    settings=json.loads(project.read_text());rules=settings.get('board',{}).get('design_settings',{}).get('rules',{})
    expected_rules={'min_clearance':.15,'min_track_width':.15,'min_via_diameter':.6,'min_through_hole_diameter':.2,'min_hole_clearance':.15,'min_copper_edge_clearance':.5,'min_silk_clearance':.1}
    rule_mismatches={k:{'expected':v,'actual':rules.get(k)} for k,v in expected_rules.items() if rules.get(k)!=v}
    default=next((c for c in settings.get('net_settings',{}).get('classes',[]) if c.get('name')=='Default'),{})
    if default.get('clearance')!=.15:rule_mismatches['default_net_clearance']={'expected':.15,'actual':default.get('clearance')}
    manifest={'started_utc':stamp,'tool':version.stdout.strip(),'tool_version_exit_code':version.returncode,
        'expected_documented_rules':expected_rules,'project_rule_mismatches':rule_mismatches,
        'scope':'CAD rules/geometry/net definitions and configured-constraint checks only','commands':[],
        'sources':{str(path):sha(path) for path in sources},
        'allowed_ignored_check_keys':{k:sorted(v) for k,v in ALLOWED_IGNORED.items()},
        'explicit_project_exclusions':explicit_exclusions(json.loads(project.read_text()))}
    commands=[
        ([str(CLI),'sch','erc','--format','json','--severity-all','--exit-code-violations','-o',str(rep/'erc.json'),str(sch)],'erc.json'),
        ([str(CLI),'pcb','drc','--format','json','--severity-all','--all-track-errors','--exit-code-violations','--refill-zones','--schematic-parity','-o',str(rep/'drc.json'),str(board)],'drc.json'),
        ([sys.executable,str(ROOT/'tools/verify_corrected_board.py'),'--board',str(board),'--output',str(rep/'independent_audit.json')],'independent_audit.json')]
    for command,filename in commands:
        start=datetime.datetime.now(datetime.timezone.utc).isoformat()
        result=subprocess.run(command,capture_output=True,text=True)
        (rep/(filename+'.log')).write_text(result.stdout+result.stderr,encoding='utf-8')
        record={'argv':command,'started_utc':start,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':result.returncode,'report':filename}
        if (rep/filename).exists():record['sha256']=sha(rep/filename)
        manifest['commands'].append(record)
    issues={}
    for filename in ['erc.json','drc.json','independent_audit.json']:
        path=rep/filename
        if not path.exists():issues[filename]={'missing_report':True};continue
        try:data=json.loads(path.read_text())
        except (ValueError,OSError) as exc:issues[filename]={'unreadable_report':str(exc)};continue
        row={};issues[filename]=row
        if filename in ALLOWED_IGNORED:
            required={'ignored_checks','included_severities','kicad_version'}|({'sheets'} if filename=='erc.json' else {'violations','unconnected_items','schematic_parity'})
            row['missing_report_fields']=sorted(required-set(data))
            ignored={item.get('key') for item in data.get('ignored_checks',[])}
            row['ignored_check_set_changed']=ignored!=ALLOWED_IGNORED[filename]
            row['ignored_checks']=data.get('ignored_checks',[])
            row['severity_coverage_incomplete']=not {'error','warning'}.issubset(data.get('included_severities',[]))
            row['tool_version_mismatch']=data.get('kicad_version')!='10.0.6'
        if filename=='erc.json':
            row['violations_including_exclusions']=sum(len(s.get('violations',[])) for s in data.get('sheets',[]))+len(data.get('violations',[]))
            row['malformed_sheet_reports']=sum('violations' not in s for s in data.get('sheets',[]))
        elif filename=='drc.json':
            row.update({k:len(data.get(k,[])) for k in ['violations','unconnected_items','schematic_parity']})
        else:
            row['missing_report_fields']=sorted({'failures','rule_area_checks','native_usb_contract','reserved_module_pads_checked'}-set(data))
            row['failures']=len(data.get('failures',[]))
    manifest['results']=issues
    manifest['source_unchanged_during_checks']=all(Path(path).exists() and sha(Path(path))==h for path,h in manifest['sources'].items())
    manifest['limits']=['No bench/field validation','No fabricator stackup or controlled-impedance proof','No thermal/ESD/USB compliance claim','The five DRC and four ERC baseline ignored categories remain disabled and are listed explicitly; this is not all possible checks enabled']
    passed=version.returncode==0 and version.stdout.strip()=='10.0.6' and not rule_mismatches and not manifest['explicit_project_exclusions'] and all(c['exit_code']==0 for c in manifest['commands']) and manifest['source_unchanged_during_checks'] and all(not value for row in issues.values() for key,value in row.items() if key!='ignored_checks')
    manifest['cad_gate_passed']=passed
    (rep/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({'reports':str(rep),'results':issues,'source_unchanged':manifest['source_unchanged_during_checks'],'cad_gate_passed':passed},indent=2))
    return 0 if passed else 2

if __name__=='__main__':raise SystemExit(main())
