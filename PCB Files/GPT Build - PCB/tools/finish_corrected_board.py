"""Finish the corrected-reference candidate, never the earlier root CAD board.

Planned 2026-10-28 after owner corrected mechanical reference to
Reference PCB (OLD Version)/Thesis/SHM_PCB_New/.
Acceptance: preserve positions/critical locked copper, match exported schematic
metadata, connect local ground to planes, use actual outline for fills/labels,
then record DRC. Only DRC-reported power gaps may receive bounded geometric
bridges. Failure to find a bridge is recorded, not hidden by an exclusion.
No claim of fabrication readiness, impedance, current capacity or field validity.

Run only after corrected preroute and SES are prepared:
  KiCad-python tools/finish_corrected_board.py --run
Inputs: design/reference_corrected/SHM_Node_R2_preroute.kicad_pcb,
        reports/reference_corrected/SHM_Node_R2.ses, sibling XML .net.
Output: design/reference_corrected/SHM_Node_R2.kicad_pcb only.
"""
from pathlib import Path
import argparse, datetime, hashlib, heapq, itertools, json, math, subprocess
import xml.etree.ElementTree as ET
import pcbnew as p

ROOT=Path(__file__).resolve().parents[1]
DES=ROOT/'design/reference_corrected'
REP=ROOT/'reports/reference_corrected'
CLI=Path('C:/Program Files/KiCad/10.0/bin/kicad-cli.exe')
LAYERS=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]
def mm(v):return p.FromMM(v)
def pt(x,y):return p.VECTOR2I(mm(x),mm(y))
def xy(o):return (p.ToMM(o.GetPosition().x),p.ToMM(o.GetPosition().y))
def hashfile(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def copper_signature(t):
    """Exact net/geometry check; UUIDs are intentionally not an identity gate."""
    if isinstance(t,p.PCB_VIA):
        return ('via',t.GetNetname(),t.GetPosition().x,t.GetPosition().y,
                t.GetWidth(p.F_Cu),t.GetDrillValue(),t.TopLayer(),t.BottomLayer())
    # Direction does not change the physical segment.
    ends=sorted([(t.GetStart().x,t.GetStart().y),(t.GetEnd().x,t.GetEnd().y)])
    return ('track',t.GetNetname(),*ends,t.GetWidth(),t.GetLayer())
def placement_signature(b):
    return {f.GetReference():(f.GetPosition().x,f.GetPosition().y,f.GetOrientationDegrees(),f.IsFlipped())
            for f in b.GetFootprints()}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--run',action='store_true',help='explicitly execute candidate finishing')
    ap.add_argument('--skip-ses',action='store_true',help='input is already routed')
    ap.add_argument('--input',type=Path,default=DES/'SHM_Node_R2_preroute.kicad_pcb')
    args=ap.parse_args()
    if not args.run:ap.error('Preparation only: add --run after corrected routing inputs are ready')
    source=args.input.resolve();assert source.is_relative_to(DES.resolve()),'Input must be corrected candidate'
    project_source=source.with_suffix('.kicad_pro')
    assert project_source.exists(),'Input needs matching .kicad_pro; otherwise KiCad loads defaults and can replace output rules'
    out=DES/'SHM_Node_R2.kicad_pcb';netfile=DES/'SHM_Node_R2.net';ses=REP/'SHM_Node_R2.ses'
    assert source!=out.resolve(),'Use a separate routed/preroute source; do not overwrite input'
    assert source.exists() and netfile.exists()
    REP.mkdir(parents=True,exist_ok=True)
    run_dir=REP/('finish_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ'))
    run_dir.mkdir()
    log={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'tool':p.GetBuildVersion(),'input':str(source),'input_sha256':hashfile(source),
         'input_project_sha256':hashfile(project_source),
         'netlist_sha256':hashfile(netfile),'ground_vias':[],'ground_unresolved':[],
         'power_bridges':[],'power_unresolved':[],'silk_unresolved':[],
         'thermal_layout_unresolved':[],
         'scope':'CAD geometry/connectivity only; no electrical or physical performance validation'}
    b=p.LoadBoard(str(source))
    # Planned import acceptance: the router may add copper, but must not move a
    # part or replace a locked critical route. A historical read-only KiCad10
    # import fixture preserved both; repeat on this exact candidate below.
    before_positions=placement_signature(b)
    before_locked={copper_signature(t) for t in b.GetTracks() if t.IsLocked()}
    if not args.skip_ses:
        assert ses.exists(),'Missing corrected-reference SES'
        assert p.ImportSpecctraSES(b,str(ses)),'SES import failed'
        log['ses_sha256']=hashfile(ses)
    after_locked={copper_signature(t) for t in b.GetTracks() if t.IsLocked()}
    # DSN/SES decimal conversion rounded three X coordinates by one KiCad IU
    # (1 nm) in the first actual import. Restore only this bounded quantization;
    # larger movement or any orientation/side change still fails the guard.
    import_positions=placement_signature(b);rounding_restored=[]
    for f in b.GetFootprints():
        r=f.GetReference();old=before_positions[r];new=import_positions[r]
        if old!=new and old[2:]==new[2:] and max(abs(old[i]-new[i]) for i in [0,1])<=1:
            rounding_restored.append({'ref':r,'before':old,'imported':new,'unit':'KiCad IU = 1 nm'})
            f.SetPosition(p.VECTOR2I(old[0],old[1]))
    log['import_integrity']={'placement_preserved':before_positions==placement_signature(b),
                             'restored_one_nm_rounding':rounding_restored,
                             'locked_copper_before':len(before_locked),
                             'locked_copper_after':len(after_locked),
                             'missing_locked_copper':[list(s) for s in before_locked-after_locked]}
    (run_dir/'import_integrity.json').write_text(json.dumps(log['import_integrity'],indent=2)+'\n',encoding='utf-8')
    assert log['import_integrity']['placement_preserved'],'SES import changed component placement'
    assert not log['import_integrity']['missing_locked_copper'],'SES import changed locked critical copper'
    fps={f.GetReference():f for f in b.GetFootprints()}
    original_positions={r:(xy(f),f.GetOrientationDegrees()) for r,f in fps.items()}
    tree=ET.parse(netfile).getroot();oldnets={n.GetNetname():n for n in b.GetNetsByNetcode().values()}
    for ne in tree.find('nets'):
        name=ne.attrib['name'];n=oldnets.get(name) or oldnets.get(name.lstrip('/'))
        if n:n.SetNetname(name)
        else:n=p.NETINFO_ITEM(b,name);b.Add(n)
        for nd in ne:
            for a in fps[nd.attrib['ref']].Pads():
                if a.GetNumber()==nd.attrib['pin']:a.SetNet(n)
    for c in tree.find('components'):
        f=fps[c.attrib['ref']];f.SetValue(c.findtext('value'))
        lib,part=c.findtext('footprint').split(':');f.SetFPID(p.LIB_ID(lib,part))
        for field in c.find('fields'):
            if field.attrib['name']!='Footprint':f.SetField(field.attrib['name'],field.text or '')
        f.SetSheetfile('SHM_Node_R2.kicad_sch');f.SetSheetname('SHM_Node_R2')
        if f.GetReference().startswith('TP'):f.SetAttributes(f.GetAttributes() & ~p.FP_EXCLUDE_FROM_BOM)
        for field in f.GetFields():
            if field.GetName() not in ['Reference','Value']:field.SetVisible(False)
    for ref,f in fps.items():
        if ref.startswith('H'):f.SetAttributes(f.GetAttributes()|p.FP_BOARD_ONLY|p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES)
    netg=next(n.GetNetCode() for n in b.GetNetsByNetcode().values() if n.GetNetname()=='GND')
    outline=p.SHAPE_POLY_SET();assert b.GetBoardPolygonOutlines(outline,False),'Invalid corrected outline'
    edges=[s for s in b.GetDrawings() if s.GetLayer()==p.Edge_Cuts]
    keepouts=[z for z in b.Zones() if z.GetIsRuleArea()]
    allpads=[a for f in b.GetFootprints() for a in f.Pads()]

    def track(net,points,layer=p.F_Cu,width=.2):
        for a,z in zip(points,points[1:]):
            if a==z:continue
            t=p.PCB_TRACK(b);t.SetNetCode(net);t.SetStart(pt(*a));t.SetEnd(pt(*z));t.SetWidth(mm(width));t.SetLayer(layer);b.Add(t)
    def via(net,q,diam=.6,drill=.3):
        v=p.PCB_VIA(b);v.SetNetCode(net);v.SetPosition(pt(*q));v.SetWidth(mm(diam));v.SetDrill(mm(drill));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);b.Add(v);return v
    def obstacles(net):return [a for a in allpads if a.GetNetCode()!=net]+[t for t in b.GetTracks() if t.GetNetCode()!=net]
    def clear_segment(a,z,layer,width,obs,clearance=.151):
        av,zv=pt(*a),pt(*z);shape=p.SHAPE_SEGMENT(av,zv,mm(width))
        if not outline.Contains(av) or not outline.Contains(zv):return False
        if any(e.GetEffectiveShape().Collide(shape,mm(.5)) for e in edges):return False
        if any(k.IsOnLayer(layer) and k.GetDoNotAllowTracks() and k.Outline().Collide(shape,0) for k in keepouts):return False
        return not any(o.IsOnLayer(layer) and o.GetEffectiveShape(layer).Collide(shape,mm(clearance)) for o in obs)
    def clear_via(q,obs,diam=.6,drill=.3):
        v=pt(*q)
        if not outline.Contains(v):return False
        # Hole spacing applies even to same-net holes, which copper clearance omits.
        hole_gap=.251
        for a in allpads:
            if a.GetDrillSize().x and a.GetEffectiveHoleShape().Collide(v,mm(drill/2+hole_gap)):return False
        for other in b.GetTracks():
            if isinstance(other,p.PCB_VIA) and math.dist(q,xy(other))<(drill+p.ToMM(other.GetDrillValue()))/2+hole_gap:return False
        if any(e.GetEffectiveShape().Collide(v,mm(.5+diam/2)) for e in edges):return False
        if any(k.GetDoNotAllowVias() and k.Outline().Collide(v,mm(diam/2+.01)) for k in keepouts):return False
        return not any(o.IsOnLayer(layer) and o.GetEffectiveShape(layer).Collide(v,mm(diam/2+.151)) for o in obs for layer in LAYERS)

    # Keep deliberately locked critical ground returns; remove router's loose ground detours.
    # Keep detached wrappers alive until this bounded process exits. The Python
    # Remove ownership wrapper corrupted cached footprint pad containers during
    # the USB reroute experiment; RemoveNative passed a read-only 69-item fixture.
    detached_ground=[t for t in b.GetTracks() if t.GetNetCode()==netg and not t.IsLocked()]
    for t in detached_ground:b.RemoveNative(t)
    b.BuildConnectivity()
    log['removed_unlocked_ground_items']=len(detached_ground)
    obs=obstacles(netg)
    grounds=[xy(t) for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetCode()==netg]
    # E-04: add multiple short thermal paths from the AP7361C grounded tab to
    # planes. Eight is our layout target, not a manufacturer thermal rating.
    # Keep all drills outside the solder pad; no unreviewed via-in-pad process.
    tab=max([a for a in fps['U5'].Pads() if a.GetNumber()=='2' and a.GetNetCode()==netg],
            key=lambda a:a.GetSize().x*a.GetSize().y)
    tabbox=tab.GetBoundingBox();tx,ty=xy(tab);right=p.ToMM(tabbox.GetRight())
    thermal={'reference':'U5','pad':'2','tab_center_mm':[tx,ty],
             'via_diameter_mm':.6,'drill_mm':.3,'top_link_width_mm':.6,
             'target_count':8,'minimum_layout_count':4,'created':[], 'rejected':[],
             'qualification':'Engineering layout target only; no measured thermal-performance claim.'}
    thermal_choices=[]
    for col in [.5,1.3,2.1,2.5]:
        for dy in [-1.2,-.4,.4,1.2]:
            q=(round(right+col,4),round(ty+dy-(.4 if col==2.5 else 0),4));thermal_choices.append((q,(right-.1,q[1])))
    for dx in [-.35,.45]:
        for dy in [-2.4,2.4,-3.2,3.2]:
            q=(round(tx+dx,4),round(ty+dy,4));thermal_choices.append((q,(q[0],round(ty+math.copysign(1.8,dy),4))))
    for q,anchor in thermal_choices:
            if len(thermal['created'])>=8:break
            if clear_via(q,obs) and clear_segment(anchor,q,p.F_Cu,.6,obs):
                via(netg,q);track(netg,[anchor,q],p.F_Cu,.6);grounds.append(q)
                thermal['created'].append({'xy_mm':q,'anchor_mm':anchor,'link_length_mm':round(math.dist(anchor,q),4)})
            else:thermal['rejected'].append(q)
    thermal['created_count']=len(thermal['created']);log['regulator_thermal_vias']=thermal
    if thermal['created_count']<thermal['minimum_layout_count']:
        log['thermal_layout_unresolved'].append('U5: fewer than four collision-checked tab thermal vias; revise placement/routing.')
    seen=set()
    for f in b.GetFootprints():
        for a in f.Pads():
            if a.GetNetCode()!=netg or a.GetAttribute()!=p.PAD_ATTRIB_SMD:continue
            if f.GetReference()=='U1' and a.GetNumber()=='41':continue # module footprint plated ground array
            x,y=xy(a);key=(x,y);padlayer=p.B_Cu if a.IsOnLayer(p.B_Cu) and not a.IsOnLayer(p.F_Cu) else p.F_Cu
            if key in seen:continue
            seen.add(key);done=False
            for q in grounds:
                if math.dist(key,q)<2 and clear_segment(key,q,padlayer,.2,obs):track(netg,[key,q],padlayer);done=True;break
            if done:continue
            for radius in [.8,1,1.2,1.5,1.8,2.2,2.7]:
                for angle in range(0,360,15):
                    q=(round(x+radius*math.cos(math.radians(angle)),4),round(y+radius*math.sin(math.radians(angle)),4))
                    if all(math.dist(q,g)>.61 for g in grounds) and clear_via(q,obs) and clear_segment(key,q,padlayer,.2,obs):
                        via(netg,q);track(netg,[key,q],padlayer);grounds.append(q)
                        log['ground_vias'].append({'ref':f.GetReference(),'pad':a.GetNumber(),'xy_mm':q});done=True;break
                if done:break
            if not done:log['ground_unresolved'].append({'ref':f.GetReference(),'pad':a.GetNumber(),'xy_mm':key})

    # Derive the plane extent from the actual corrected outline. KiCad clips fills at Edge.Cuts.
    bbox=b.GetBoardEdgesBoundingBox();x0,y0=p.ToMM(bbox.GetX()),p.ToMM(bbox.GetY());x1=x0+p.ToMM(bbox.GetWidth());y1=y0+p.ToMM(bbox.GetHeight())
    detached_zones=[z for z in b.Zones() if not z.GetIsRuleArea() and z.GetZoneName().startswith('Corrected outer GND')]
    for z in detached_zones:b.RemoveNative(z)
    for layer in [p.F_Cu,p.B_Cu]:
        z=p.ZONE(b);z.SetLayer(layer);z.SetNetCode(netg);z.SetLocalClearance(mm(.2));z.SetMinThickness(mm(.2));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetZoneName('Corrected outer GND '+b.GetLayerName(layer));o=z.Outline();o.NewOutline()
        for x,y in [(x0-1,y0-1),(x1+1,y0-1),(x1+1,y1+1),(x0-1,y1+1)]:o.Append(mm(x),mm(y))
        b.Add(z)

    def save_and_drc(tag):
        b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(out),b)
        (run_dir/f'board_{tag}.kicad_pcb').write_bytes(out.read_bytes())
        report=run_dir/f'drc_corrected_{tag}.json'
        result=subprocess.run([str(CLI),'pcb','drc','--format','json','--schematic-parity','-o',str(report),str(out)],capture_output=True,text=True)
        assert result.returncode==0 and report.exists(),result.stdout+result.stderr
        return json.loads(report.read_text()),report

    def bridge(issue):
        """Only connect a genuine DRC-reported same-net power gap, no old fixed coordinates."""
        ids={o.m_Uuid.AsString():o for o in allpads+list(b.GetTracks())}
        it=issue.get('items',[])
        if len(it)!=2:return False
        os=[ids.get(i.get('uuid')) for i in it]
        if any(o is None for o in os):return False
        if os[0].GetNetCode()!=os[1].GetNetCode():return False
        net=os[0].GetNetCode();name=os[0].GetNetname()
        if name.lstrip('/') not in ['+3V3','+5V_FUSED','VBUS_USB','IMU1_INT']:return False
        start=(it[0]['pos']['x'],it[0]['pos']['y']);goal=(it[1]['pos']['x'],it[1]['pos']['y'])
        # A DRC representative point can be the fine-pitch IC end of a locked
        # support track. Its opposite endpoint is the accessible capacitor end.
        # This only selects another point on the same disconnected copper item.
        if isinstance(os[0],p.PCB_TRACK) and not isinstance(os[0],p.PCB_VIA):
            q=os[0].GetEnd();start=(p.ToMM(q.x),p.ToMM(q.y))
        if isinstance(os[1],p.PCB_TRACK) and not isinstance(os[1],p.PCB_VIA):
            q=os[1].GetEnd();goal=(p.ToMM(q.x),p.ToMM(q.y))
        sl=[l for l in [p.F_Cu,p.B_Cu] if os[0].IsOnLayer(l)];gl=[l for l in [p.F_Cu,p.B_Cu] if os[1].IsOnLayer(l)]
        obs=obstacles(net);width=.2 if name.lstrip('/')=='IMU1_INT' else .25
        # Prefer a direct bridge before adding vias or a grid route.
        for layer in sl:
            if layer in gl and clear_segment(start,goal,layer,width,obs):
                track(net,[start,goal],layer,width);log['power_bridges'].append({'net':name,'points':[start,goal],'layer':b.GetLayerName(layer),'width_mm':width,'vias':0});return True
        step=.25;counter=itertools.count();heap=[];cost={};prev={};steps=0
        xmin,xmax=min(start[0],goal[0])-8,max(start[0],goal[0])+8;ymin,ymax=min(start[1],goal[1])-8,max(start[1],goal[1])+8
        for layer in sl:
            for dx in [-1,0,1]:
                for dy in [-1,0,1]:
                    q=(round(start[0]/step)*step+dx*step,round(start[1]/step)*step+dy*step,layer)
                    if clear_segment(start,q[:2],layer,width,obs):
                        g=math.dist(start,q[:2]);cost[q]=g;prev[q]=None;heapq.heappush(heap,(g+math.dist(q[:2],goal),next(counter),q))
        found=None
        while heap and steps<50000:
            _,_,q=heapq.heappop(heap);steps+=1;g=cost[q]
            if q[2] in gl and math.dist(q[:2],goal)<.55 and clear_segment(q[:2],goal,q[2],width,obs):found=q;break
            for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
                z=(q[0]+dx*step,q[1]+dy*step,q[2]);ng=g+math.hypot(dx,dy)*step
                if not(xmin<=z[0]<=xmax and ymin<=z[1]<=ymax) or ng>=cost.get(z,1e12):continue
                if not clear_segment(q[:2],z[:2],q[2],width,obs):continue
                cost[z]=ng;prev[z]=q;heapq.heappush(heap,(ng+math.dist(z[:2],goal),next(counter),z))
            other=p.B_Cu if q[2]==p.F_Cu else p.F_Cu;z=(q[0],q[1],other);ng=g+3
            if ng<cost.get(z,1e12) and clear_via(q[:2],obs,.6,.3):cost[z]=ng;prev[z]=q;heapq.heappush(heap,(ng+math.dist(z[:2],goal),next(counter),z))
        if found is None:return False
        points=[found]
        while prev[points[-1]] is not None:points.append(prev[points[-1]])
        points.reverse();track(net,[start,points[0][:2]],points[0][2],width);nv=0
        for a,z in zip(points,points[1:]):
            if a[2]!=z[2]:via(net,a[:2],.6,.3);nv+=1
            else:track(net,[a[:2],z[:2]],a[2],width)
        track(net,[points[-1][:2],goal],points[-1][2],width)
        log['power_bridges'].append({'net':name,'grid_points':points,'width_mm':width,'vias':nv,'search_steps':steps});return True

    drc,_=save_and_drc('before_bridge')
    for attempt in range(8):
        gaps=drc.get('unconnected_items',[])
        if not gaps:break
        repaired=False
        for issue in gaps:
            if bridge(issue):repaired=True;break
        if not repaired:break
        drc,_=save_and_drc(f'bridge_{attempt+1}')
    log['power_unresolved']=drc.get('unconnected_items',[])

    # Move only the pin-1 artwork clear of the compact upper edge; pads unchanged.
    for g in fps['U1'].GraphicalItems():
        if g.GetLayer()==p.F_SilkS and g.GetShape()==p.SHAPE_T_POLY and p.ToMM(g.GetBoundingBox().GetTop())<53.7:
            g.Move(pt(0,.1))
    # Place reference labels using actual copper-mask/edge and already placed text geometry.
    placed=[];silk=[g for f in fps.values() for g in f.GraphicalItems() if g.GetLayer() in [p.F_SilkS,p.B_SilkS]]
    silk += [d for d in b.GetDrawings() if d.GetLayer() in [p.F_SilkS,p.B_SilkS]]
    for ref,f in sorted(fps.items(),key=lambda v:(not v[0].startswith('U'),v[0])):
        silklayer=p.B_SilkS if f.IsFlipped() else p.F_SilkS;masklayer=p.B_Mask if f.IsFlipped() else p.F_Mask
        t=f.Reference();oldpos=t.GetPosition();t.SetVisible(True);t.SetLayer(silklayer);t.SetMirrored(f.IsFlipped());t.SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T));t.SetTextSize(pt(.8,.8));t.SetTextThickness(mm(.12));x,y=xy(f);done=False
        # Retain source location when clear, otherwise try nearby radial positions.
        choices=[(p.ToMM(oldpos.x),p.ToMM(oldpos.y))]
        choices += [(x+radius*math.cos(math.radians(a)),y+radius*math.sin(math.radians(a))) for radius in [2,2.8,3.6,4.5,5.5,7,9,11] for a in [270,90,180,0,225,315,135,45]]
        for q in choices:
            t.SetPosition(pt(*q));bb=t.GetBoundingBox();clear=p.BOX2I(bb.GetOrigin(),bb.GetSize());clear.Inflate(mm(.18))
            corners=[clear.GetOrigin(),p.VECTOR2I(clear.GetRight(),clear.GetTop()),p.VECTOR2I(clear.GetRight(),clear.GetBottom()),p.VECTOR2I(clear.GetLeft(),clear.GetBottom())]
            if not all(outline.Contains(c) for c in corners):continue
            if any(e.GetEffectiveShape().Collide(p.SHAPE_RECT(clear),mm(.1)) for e in edges):continue
            if any(clear.Intersects(a.GetBoundingBox()) for a in allpads if a.IsOnLayer(masklayer)):continue
            if any(clear.Intersects(g.GetBoundingBox()) for g in silk+placed if g.GetLayer()==silklayer):continue
            placed.append(t);done=True;break
        if not done:t.SetPosition(oldpos);placed.append(t);log['silk_unresolved'].append(ref)
        f.Value().SetVisible(False)
    assert original_positions=={r:(xy(f),f.GetOrientationDegrees()) for r,f in fps.items()},'Component placement changed unexpectedly'
    drc,report=save_and_drc('final')
    log.update({'output':str(out),'output_sha256':hashfile(out),'drc_report':str(report),
                'unconnected_count':len(drc.get('unconnected_items',[])),
                'violation_count':len(drc.get('violations',[])),
                'schematic_parity_count':len(drc.get('schematic_parity',[])),
                'run_directory':str(run_dir),
                'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
    (run_dir/'finish_log.json').write_text(json.dumps(log,indent=2)+'\n',encoding='utf-8')
    (REP/'finish_corrected_log.json').write_text(json.dumps(log,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:log[k] for k in ['output','unconnected_count','violation_count','silk_unresolved','thermal_layout_unresolved']}))
    # Candidate is retained for diagnosis; no violation is suppressed by this script.
    return 0 if not(drc.get('unconnected_items') or drc.get('violations') or drc.get('schematic_parity') or log['thermal_layout_unresolved']) else 2

if __name__=='__main__':raise SystemExit(main())
