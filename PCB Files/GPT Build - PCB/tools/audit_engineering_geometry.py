"""Read-only engineering geometry screen. Run with KiCad Python; never saves CAD.

Outputs measurements, not an electrical/mechanical compliance verdict. EQ-G01 is
Euclidean track length; EQ-G02 adds nominal board thickness per through transition.
Filled-plane coverage is sampled at <=0.05 mm along center/edges, not a field solver.
"""
from pathlib import Path
import argparse, datetime, hashlib, heapq, json, math, sys
import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def xy(q): return tuple(round(p.ToMM(v), 6) for v in [q.x,q.y])
def vec(q): return p.VECTOR2I(*(p.FromMM(v) for v in q))
def net(t): return t.GetNetname().lstrip('/')
def uid(t): return t.m_Uuid.AsString()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    args=ap.parse_args(); out=args.output.resolve(); out.mkdir(parents=True,exist_ok=True)
    boardpath=ROOT/'design/SHM_Node_R2.kicad_pcb'
    inputs=[boardpath, ROOT/'design/SHM_Node_R2.kicad_pro', ROOT/'design/SHM_Node_R2.kicad_sch',ROOT/'design/circuit_spec.json']
    before={str(f.relative_to(ROOT)):sha(f) for f in inputs}
    b=p.LoadBoard(str(boardpath)); fps={f.GetReference():f for f in b.GetFootprints()}
    pads=[q for f in fps.values() for q in f.Pads()]
    tracks=list(b.GetTracks()); vias=[t for t in tracks if isinstance(t,p.PCB_VIA)]
    gndvias=[v for v in vias if net(v)=='GND']
    usb=[t for t in tracks if net(t).startswith('USB_')]
    usbvias=[t for t in usb if isinstance(t,p.PCB_VIA)]
    segs=[t for t in usb if not isinstance(t,p.PCB_VIA)]
    assert len(segs)>0, 'No USB tracks: check normalized net names'
    assert all(t.GetClass()=='PCB_TRACK' for t in segs), 'Arc handling is not implemented'
    assert all(t.GetLayer() in [p.F_Cu,p.B_Cu] for t in segs)
    assert all(v.TopLayer()==p.F_Cu and v.BottomLayer()==p.B_Cu for v in usbvias)
    thickness=p.ToMM(b.GetDesignSettings().GetBoardThickness())
    def pad(r,n): return next(q for q in fps[r].Pads() if q.GetNumber()==str(n))
    def info(q): return {'ref':q.GetParentFootprint().GetReference(),'pad':q.GetNumber(),'net':net(q),'xy_mm':xy(q.GetPosition()),'size_mm':xy(q.GetSize()),'layers':[b.GetLayerName(l) for l in q.GetLayerSet().Seq()]}
    # Graph splits collinear tracks at all track endpoints, via centers and pad centers.
    # Pad copper interiors and component-internal conductors are intentionally excluded.
    def path(r1,n1,r2,n2,barrel=0):
        src,dst=pad(r1,n1),pad(r2,n2); assert src.GetNetCode()==dst.GetNetCode()
        ts=[t for t in usb if t.GetNetCode()==src.GetNetCode()]; points={p.F_Cu:set(),p.B_Cu:set()}; raw=[]; vs=[]
        for t in ts:
            if isinstance(t,p.PCB_VIA):
                v=xy(t.GetPosition()); vs.append((v,uid(t)))
                for l in points: points[l].add(v)
            else:
                l=t.GetLayer(); u=xy(t.GetStart());v=xy(t.GetEnd());raw.append((l,u,v,uid(t)));points[l].update([u,v])
        for q in pads:
            if q.GetNetCode()==src.GetNetCode():
                for l in points:
                    if q.IsOnLayer(l): points[l].add(xy(q.GetPosition()))
        graph={}
        def link(u,v,d,tr,ident):
            graph.setdefault(u,[]).append((v,d,tr,ident));graph.setdefault(v,[]).append((u,d,tr,ident))
        for l,u,v,ident in raw:
            length=math.dist(u,v)
            if length==0: continue
            on=[q for q in points[l] if abs(math.dist(u,q)+math.dist(q,v)-length)<1e-5]
            on.sort(key=lambda q:math.dist(u,q))
            for q,z in zip(on,on[1:]):link((l,*q),(l,*z),math.dist(q,z),0,ident)
        for q,ident in vs: link((p.F_Cu,*q),(p.B_Cu,*q),barrel,1,ident)
        start=(p.F_Cu,*xy(src.GetPosition())); goal=(p.F_Cu,*xy(dst.GetPosition()))
        best={start:(0,0)};prev={};todo=[(0,0,start)]
        while todo:
            d,vt,u=heapq.heappop(todo)
            if (d,vt)!=best[u]:continue
            if u==goal:
                nodes=[u]; ids=[]
                while u!=start:u,ident=prev[u];nodes.append(u);ids.append(ident)
                return {'length_mm':round(d,6),'via_transitions':vt,'nodes':list(reversed(nodes)),'item_uuids':list(reversed(ids))}
            for v,w,tr,ident in graph.get(u,[]):
                val=(d+w,vt+tr)
                if val<best.get(v,(math.inf,math.inf)):
                    best[v]=val;prev[v]=(u,ident);heapq.heappush(todo,(*val,v))
        raise RuntimeError(f'No explicit track-center path {r1}.{n1} -> {r2}.{n2}')
    endpoints={'A_DM':('J1','A7','R3','1'),'B_DM':('J1','B7','R3','1'),'A_DP':('J1','A6','R4','1'),'B_DP':('J1','B6','R4','1'),'MCU_DM':('R3','2','U1','13'),'MCU_DP':('R4','2','U1','14'),
               'A_DM_to_ESD':('J1','A7','U6','1'),'B_DM_to_ESD':('J1','B7','U6','1'),'A_DP_to_ESD':('J1','A6','U6','3'),'B_DP_to_ESD':('J1','B6','U6','3')}
    paths={k:path(*v) for k,v in endpoints.items()}
    barrelpaths={k:path(*v,barrel=thickness) for k,v in endpoints.items()}
    comparisons={s:{'planar_DM_minus_DP_mm':round(paths[s+'_DM']['length_mm']+paths['MCU_DM']['length_mm']-paths[s+'_DP']['length_mm']-paths['MCU_DP']['length_mm'],6),
                    'nominal_3D_DM_minus_DP_mm':round(barrelpaths[s+'_DM']['length_mm']+barrelpaths['MCU_DM']['length_mm']-barrelpaths[s+'_DP']['length_mm']-barrelpaths['MCU_DP']['length_mm'],6)} for s in ['A','B']}
    # Sample filled ground directly beneath each USB trace center and both edges.
    # Report holes separately near signal transitions, without declaring all such holes benign.
    planes={l:[z.GetFilledPolysList(l) for z in b.Zones() if not z.GetIsRuleArea() and z.IsOnLayer(l) and net(z)=='GND'] for l in [p.In1_Cu,p.In2_Cu]}
    coverage=[]; misses=[]
    for t in segs:
        u=xy(t.GetStart());v=xy(t.GetEnd());length=math.dist(u,v)
        if length<1e-6:continue
        l=t.GetLayer();ref=p.In1_Cu if l==p.F_Cu else p.In2_Cu
        w=p.ToMM(t.GetWidth());normal=(-(v[1]-u[1])/length,(v[0]-u[0])/length)
        count=max(1,math.ceil(length/.05));bad=[];centermiss=0
        for i in range(count+1):
            for off in [-w/2,0,w/2]:
                q=tuple(u[j]+(v[j]-u[j])*i/count+normal[j]*off for j in [0,1])
                if not any(poly.Contains(vec(q)) for poly in planes[ref]):
                    near=min((math.dist(q,xy(a.GetPosition())) for a in usbvias),default=math.inf)
                    rec={'xy_mm':[round(c,6) for c in q],'offset_mm':off,'nearest_USB_via_mm':round(near,6)}
                    bad.append(rec);misses.append({**rec,'track_uuid':uid(t),'net':net(t),'layer':b.GetLayerName(l),'reference':b.GetLayerName(ref)})
                    if off==0:centermiss+=1
        coverage.append({'uuid':uid(t),'net':net(t),'layer':b.GetLayerName(l),'reference':b.GetLayerName(ref),'start_mm':u,'end_mm':v,'width_mm':w,'length_mm':round(length,6),'sample_count':3*(count+1),'miss_count':len(bad),'center_miss_count':centermiss,'misses_farther_than_0_6mm_from_USB_via':sum(q['nearest_USB_via_mm']>.6 for q in bad)})
    returns=[]
    for v in usbvias:
        nearest=sorted(gndvias,key=lambda a:math.dist(xy(a.GetPosition()),xy(v.GetPosition())))[:2]
        returns.append({'net':net(v),'xy_mm':xy(v.GetPosition()),'uuid':uid(v),'ground_vias':[{'xy_mm':xy(a.GetPosition()),'distance_mm':round(math.dist(xy(a.GetPosition()),xy(v.GetPosition())),6),'uuid':uid(a)} for a in nearest]})
    tp=[];tprefs=sorted((r for r in fps if r.startswith('TP')),key=lambda r:int(r[2:]))
    for ref in tprefs:
        q=pad(ref,1);pos=xy(q.GetPosition()); others=[pad(r,1) for r in tprefs if r!=ref]
        gnds=[a for a in pads if net(a)=='GND' and a.IsOnLayer(p.B_Mask) and a is not q]
        nearest=min(gnds,key=lambda a:math.dist(pos,xy(a.GetPosition())))
        tp.append({**info(q),'has_back_mask_opening':q.IsOnLayer(p.B_Mask),'has_paste':q.IsOnLayer(p.B_Paste) or q.IsOnLayer(p.F_Paste),
                   'nearest_TP_center_mm':round(min(math.dist(pos,xy(a.GetPosition())) for a in others),6),'to_TP2_GND_center_mm':round(math.dist(pos,xy(pad('TP2',1).GetPosition())),6),
                   'nearest_exposed_back_GND_pad':{**info(nearest),'center_distance_mm':round(math.dist(pos,xy(nearest.GetPosition())),6)}})
    ss=json.loads((ROOT/'design/circuit_spec.json').read_text());parts=ss['components']
    caps=[c for c in parts if c['ref'].startswith('C') and 'VBUS_USB' in c['pins'].values()]
    pin2=pad('U6',2);ground_near=min(gndvias,key=lambda a:math.dist(xy(a.GetPosition()),xy(pin2.GetPosition())))
    drills=[]
    for q in pads:
        d=xy(q.GetDrillSize())
        if max(d)>0:drills.append({'ref':q.GetParentFootprint().GetReference(),'pad':q.GetNumber(),'drill_mm':d,'copper_size_mm':xy(q.GetSize()),'attribute':int(q.GetAttribute())})
    # RF rectangle comes from actual module F.Fab body/antenna lines, not its courtyard.
    u=fps['U1'];ux,uy=xy(u.GetPosition());assert u.GetOrientationDegrees()==0
    antenna_bounds=[ux-9,uy-12.75,ux+9,uy-6.75]
    fab=[g for g in u.GraphicalItems() if g.GetClass()=='PCB_SHAPE' and g.GetLayer()==p.F_Fab]
    assert any(abs(xy(g.GetStart())[1]-antenna_bounds[3])<1e-6 and abs(xy(g.GetEnd())[1]-antenna_bounds[3])<1e-6 for g in fab)
    antenna=p.SHAPE_RECT(*[p.FromMM(v) for v in [antenna_bounds[0],antenna_bounds[1],18,6]])
    outline=p.SHAPE_POLY_SET();assert b.GetBoardPolygonOutlines(outline,False)
    topedges=[g for g in b.GetDrawings() if g.GetLayer()==p.Edge_Cuts and g.GetShape()==p.SHAPE_T_SEGMENT and abs(xy(g.GetStart())[1]-53.55)<1e-6 and abs(xy(g.GetEnd())[1]-53.55)<1e-6]
    assert len(topedges)==1
    intrusion=[]
    for l in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]:
        for q in pads:
            if q.IsOnLayer(l) and q.GetEffectiveShape(l).Collide(antenna,0):intrusion.append({'type':'pad','ref':q.GetParentFootprint().GetReference(),'pad':q.GetNumber(),'layer':b.GetLayerName(l)})
        for t in tracks:
            if t.IsOnLayer(l) and t.GetEffectiveShape(l).Collide(antenna,0):intrusion.append({'type':'track/via','uuid':uid(t),'layer':b.GetLayerName(l)})
        for z in b.Zones():
            if not z.GetIsRuleArea() and z.IsOnLayer(l) and z.GetFilledPolysList(l).Collide(antenna,0):intrusion.append({'type':'fill','zone':z.GetZoneName(),'layer':b.GetLayerName(l)})
    def body_bbox(ref):
        shapes=[g for g in fps[ref].GraphicalItems() if g.GetClass()=='PCB_SHAPE' and g.GetLayer()==p.F_Fab]
        boxes=[g.GetBoundingBox() for g in shapes]
        return [min(p.ToMM(v.GetLeft()) for v in boxes),min(p.ToMM(v.GetTop()) for v in boxes),max(p.ToMM(v.GetRight()) for v in boxes),max(p.ToMM(v.GetBottom()) for v in boxes)]
    def box_distance(a,c):return math.hypot(max(a[0]-c[2],c[0]-a[2],0),max(a[1]-c[3],c[1]-a[3],0))
    sensor_clearance=[]
    for ref in ['U2','U3','U4']:
        x,y=xy(fps[ref].GetPosition());a=[x-2,y-2,x+2,y+2]
        for other in ['J1','J2','SW1','SW2','U1']:
            box=body_bbox(other);sensor_clearance.append({'imu':ref,'other':other,'fab_bbox_mm':box,'distance_from_nominal_4mm_IMU_body_mm':round(box_distance(a,box),6),'less_than_6mm':box_distance(a,box)<6})
    gap_pairs=[]
    for a in segs:
        if 'DM' not in net(a):continue
        au,av=xy(a.GetStart()),xy(a.GetEnd());al=math.dist(au,av)
        if al<2:continue
        e=((av[0]-au[0])/al,(av[1]-au[1])/al)
        for c in segs:
            if 'DP' not in net(c) or c.GetLayer()!=a.GetLayer():continue
            cu,cv=xy(c.GetStart()),xy(c.GetEnd());cl=math.dist(cu,cv)
            if cl<2:continue
            ce=((cv[0]-cu[0])/cl,(cv[1]-cu[1])/cl)
            if abs(e[0]*ce[1]-e[1]*ce[0])>1e-5:continue
            proj=sorted((sum((v[i]-au[i])*e[i] for i in [0,1]) for v in [cu,cv]));overlap=min(al,proj[1])-max(0,proj[0])
            distance=abs(e[0]*(cu[1]-au[1])-e[1]*(cu[0]-au[0]))
            if overlap>0 and distance<2:
                gap_pairs.append({'DM_uuid':uid(a),'DP_uuid':uid(c),'layer':b.GetLayerName(a.GetLayer()),'parallel_overlap_mm':round(overlap,6),'edge_gap_mm':round(distance-(p.ToMM(a.GetWidth())+p.ToMM(c.GetWidth()))/2,6)})
    result={'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tool':p.GetBuildVersion(),'python':sys.version,'script_sha256':sha(Path(__file__)),'inputs':before,
            'board':{'configured_thickness_mm':thickness,'explicit_stackup_in_file':'(stackup' in boardpath.read_text(),'layers':b.GetCopperLayerCount()},
            'USB':{'path_planar_EQ_G01':paths,'path_nominal_barrel_EQ_G02':barrelpaths,'endpoint_comparisons':comparisons,'track_count':len(segs),'via_count':len(usbvias),'widths_mm':sorted({p.ToMM(t.GetWidth()) for t in segs}),'reference_coverage':coverage,'reference_misses':misses,'return_vias':returns},
            'USB_long_parallel_spans':gap_pairs,
            'RF':{'module_origin_mm':[ux,uy],'antenna_body_region_mm':antenna_bounds,'nominal_boundary_overhang_mm':round(53.55-antenna_bounds[3],6),'intersects_baseboard':outline.Collide(antenna,0),'copper_intrusions':intrusion,'limits':'Nominal fabrication-art geometry only; exact feedpoint, dimensional/placement tolerances, housing, screws/cable/bridge metal and RF performance unresolved.'},
            'sensor_insertion_component_clearance':sensor_clearance,
            'testpoints':tp,'testpoint_missing_nets':sorted({'VBUS_USB','+5V_FUSED','EN','BOOT'}-{net(pad(r,1)) for r in tprefs}),
            'ESD':{'VBUS_direct_capacitors':caps,'GND_pad':info(pin2),'nearest_ground_via':{'xy_mm':xy(ground_near.GetPosition()),'center_distance_mm':round(math.dist(xy(ground_near.GetPosition()),xy(pin2.GetPosition())),6)}},
            'drills':drills,'minimum_track_width_mm':min(p.ToMM(t.GetWidth()) for t in tracks if not isinstance(t,p.PCB_VIA)),
            'limits':['Track-center graph excludes pad bodies and component/connector internal connections; it is not an electrical propagation model.','Nominal through barrel uses configured 1.6mm board thickness, not measured finished copper-layer distance or dielectric delay.','Plane samples are geometric screening only; antipads, return currents, lateral field extent and impedance require further analysis.','Ground-via distances and exposed pad geometry do not prove acceptable inductance or physical probe access.','No exact stackup, capacitance extraction, thermal model, RF model, prototype measurement or compliance test is supplied by this script.']}
    after={str(f.relative_to(ROOT)):sha(f) for f in inputs};result['inputs_unchanged']=before==after;assert result['inputs_unchanged']
    (out/'geometry.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    # Engineering visual: CAD USB traces plus sampled reference copper gaps, not a manufacturing plot.
    svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="121 65 18 22" width="900" height="1100">','<rect x="121" y="65" width="18" height="22" fill="white"/>']
    for t in segs:
        u=xy(t.GetStart());v=xy(t.GetEnd());color='#125ac2' if 'DP' in net(t) else '#a32620'
        svg.append(f'<path d="M {u[0]} {u[1]} L {v[0]} {v[1]}" fill="none" stroke="{color}" stroke-width="{p.ToMM(t.GetWidth())}"/>')
    for f in [fps[r] for r in ['J1','U6','R3','R4']]:
        for q in f.Pads():
            x,y=xy(q.GetPosition());w,h=xy(q.GetSize());svg.append(f'<circle cx="{x}" cy="{y}" r="0.17" fill="#777"/>')
        x,y=xy(f.GetPosition());svg.append(f'<text x="{x}" y="{y-.6}" font-size=".4">{f.GetReference()}</text>')
    for v in usbvias+gndvias:
        x,y=xy(v.GetPosition())
        if 121<x<139 and 65<y<87:svg.append(f'<circle cx="{x}" cy="{y}" r=".25" fill="none" stroke="{"#277733" if net(v)=="GND" else "#222"}" stroke-width=".07"/>')
    for m in misses:
        x,y=m['xy_mm'];svg.append(f'<circle cx="{x}" cy="{y}" r=".035" fill="#f20bc8"/>')
    svg.append('<text x="121.2" y="65.6" font-size=".37">D+ blue / D- red; green: GND vias; pink: plane misses</text></svg>')
    (out/'usb_reference_screen.svg').write_text('\n'.join(svg),encoding='utf-8')
    print(json.dumps({'output':str(out),'inputs_unchanged':result['inputs_unchanged'],'USB_endpoints':comparisons,'plane_samples':sum(x['sample_count'] for x in coverage),'plane_misses':len(misses),'far_misses':sum(x['nearest_USB_via_mm']>.6 for x in misses),'ESD':result['ESD']},indent=2))

if __name__=='__main__':main()
