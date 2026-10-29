"""Read-only board/netlist/reference-outline audit; writes a JSON evidence report.

Geometric and metadata checks do not prove electrical or physical performance.
This script independently reads KiCad output instead of importing board generators.
"""
from pathlib import Path
import argparse,collections,datetime,hashlib,json,math,re,xml.etree.ElementTree as E
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1]
DES=ROOT/'design/reference_corrected'
REF=ROOT.parent/'Reference PCB (OLD Version)/Thesis/SHM_PCB_New/SHM_PCB_New.kicad_pcb'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def coord(v):return [round(p.ToMM(v.x),6),round(p.ToMM(v.y),6)]

def duplicates(values):return sorted(k for k,v in collections.Counter(values).items() if v>1)

def audit_physical_constraints(board,fps,failures):
    """Check documented CAD constraints, not actual mechanical/electrical performance."""
    copper_layers=set(p.LSET.AllCuMask(4).Seq())
    if board.GetCopperLayerCount()!=4:failures.append({'issue':'copper_layer_count_not_four'})
    areas=collections.defaultdict(list)
    for z in board.Zones():
        if z.GetIsRuleArea():areas[z.GetZoneName()].append(z)
    records=[]
    def rule(name,points,zone_fills,pads):
        found=areas.get(name,[])
        if len(found)!=1:
            failures.append({'issue':'rule_area_missing_or_duplicate','name':name,'count':len(found)});return
        z=found[0];outline=z.Outline()
        actual=[tuple(coord(outline.CVertex(i))) for i in range(outline.VertexCount())]
        # 2 nm coordinate-rounding tolerance only; compare as a multiset to avoid
        # order ambiguity between symmetric polygon vertices with near-equal X.
        expected=[(round(x,6),round(y,6)) for x,y in points];remaining=list(expected)
        geometry_ok=len(actual)==len(expected)
        for q in actual:
            match=next((i for i,r in enumerate(remaining) if all(abs(a-b)<=.000002 for a,b in zip(q,r))),None)
            if match is None:geometry_ok=False
            else:remaining.pop(match)
        geometry_ok=geometry_ok and not remaining
        flags={'tracks':z.GetDoNotAllowTracks(),'vias':z.GetDoNotAllowVias(),
               'zone_fills':z.GetDoNotAllowZoneFills(),'pads':z.GetDoNotAllowPads()}
        want={'tracks':True,'vias':True,'zone_fills':zone_fills,'pads':pads}
        layers=set(z.GetLayerSet().Seq())
        if not geometry_ok:failures.append({'issue':'rule_area_geometry_changed','name':name})
        if flags!=want:failures.append({'issue':'rule_area_flags_changed','name':name,'actual':flags,'expected':want})
        if layers!=copper_layers:failures.append({'issue':'rule_area_layers_changed','name':name,'actual':sorted(layers)})
        records.append({'name':name,'geometry_matches':geometry_ok,'flags':flags,'layers':sorted(layers)})
    def rect(x1,y1,x2,y2):return [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]
    for name in ['U2','U3','U4']:
        if name not in fps:continue
        f=fps[name];x,y=coord(f.GetPosition());core=p.SHAPE_RECT(
            p.FromMM(x-1.54),p.FromMM(y-1.54),p.FromMM(3.08),p.FromMM(3.08))
        assert core.BBox().GetWidth()==p.FromMM(3.08) and core.BBox().GetHeight()==p.FromMM(3.08),'Incorrect core rectangle constructor'
        rule(name+' die: no tracks or vias; ground plane allowed',rect(x-1.54,y-1.54,x+1.54,y+1.54),False,False)
        # Check all board pads, not only pad 25 or even only the IMU footprint.
        for owner in board.GetFootprints():
            for pad in owner.Pads():
                for layer in sorted(copper_layers|{p.F_Paste,p.B_Paste}):
                    if pad.IsOnLayer(layer) and pad.GetEffectiveShape(layer).Collide(core,0):
                        failures.append({'issue':'copper_or_paste_pad_in_imu_core','imu':name,'ref':owner.GetReference(),'pad':pad.GetNumber(),'layer':board.GetLayerName(layer)})
        graphics=list(board.GetDrawings())+[g for owner in board.GetFootprints() for g in owner.GraphicalItems()]
        for g in graphics:
            if g.GetLayer() not in copper_layers|{p.F_Paste,p.B_Paste}:continue
            if hasattr(g,'GetEffectiveShape') and g.GetEffectiveShape(g.GetLayer()).Collide(core,0):
                failures.append({'issue':'copper_or_paste_artwork_in_imu_core','imu':name,'uuid':g.m_Uuid.AsString(),'layer':board.GetLayerName(g.GetLayer())})
    rule('Antenna region and surrounding clearance',rect(114.9,17,162.9,53.55),True,True)
    for name in ['H1','H2','H3']:
        if name not in fps:failures.append({'issue':'mounting_hole_missing','ref':name});continue
        x,y=coord(fps[name].GetPosition())
        rule('M3 fastener copper clearance '+name,[(x+3.3*math.cos(a*math.pi/16),y+3.3*math.sin(a*math.pi/16)) for a in range(32)],True,False)
    for layer in [p.In1_Cu,p.In2_Cu]:
        if not any(not z.GetIsRuleArea() and z.IsOnLayer(layer) and z.GetNetname().lstrip('/')=='GND' for z in board.Zones()):
            failures.append({'issue':'inner_ground_reference_zone_missing','layer':board.GetLayerName(layer)})
    return records
def edge_signature(board):
    result=[]
    for s in board.GetDrawings():
        if s.GetLayer()!=p.Edge_Cuts:continue
        entry={'shape':str(s.GetShape()),'start':coord(s.GetStart()),'end':coord(s.GetEnd())}
        if s.GetShape()==p.SHAPE_T_ARC:entry['mid']=coord(s.GetArcMid())
        if s.GetShape()==p.SHAPE_T_CIRCLE:entry['center']=coord(s.GetCenter());entry['radius_mm']=p.ToMM(s.GetRadius())
        result.append(entry)
    return sorted(result,key=lambda v:json.dumps(v,sort_keys=True))

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--board',type=Path,default=DES/'SHM_Node_R2.kicad_pcb')
    ap.add_argument('--output',type=Path,default=ROOT/'reports/reference_corrected/geometric_net_audit.json')
    args=ap.parse_args();boardpath=args.board.resolve();assert boardpath.exists()
    assert boardpath.parent in {DES.resolve(),(ROOT/'design').resolve()},'Inspect active design or corrected staging directory only; never archived boards'
    parent_dir = boardpath.parent
    netfile=parent_dir/'SHM_Node_R2.net';specfile=parent_dir/'circuit_spec.json'
    b=p.LoadBoard(str(boardpath));ref=p.LoadBoard(str(REF));tree=E.parse(netfile).getroot();spec=json.loads(specfile.read_text())
    allfps=list(b.GetFootprints());fps={f.GetReference():f for f in allfps};specparts={c['ref']:c for c in spec['components']}
    failures=[];expected={};checked=0
    xmlrefs=[c.attrib['ref'] for c in tree.find('components')]
    for source,refs in [('pcb',[f.GetReference() for f in allfps]),('spec',[c['ref'] for c in spec['components']]),('xml',xmlrefs)]:
        if duplicates(refs):failures.append({'issue':'duplicate_references','source':source,'refs':duplicates(refs)})
    if set(xmlrefs)!=set(specparts):failures.append({'issue':'spec_xml_component_set_differs','xml_only':sorted(set(xmlrefs)-set(specparts)),'spec_only':sorted(set(specparts)-set(xmlrefs))})
    extra=set(fps)-set(xmlrefs)-{'H1','H2','H3'}
    if extra:failures.append({'issue':'unexpected_board_components','refs':sorted(extra)})
    for ne in tree.find('nets'):
        for node in ne:
            endpoint=(node.attrib['ref'],node.attrib['pin'])
            if endpoint in expected:failures.append({'issue':'duplicate_xml_endpoint','ref':endpoint[0],'pin':endpoint[1]})
            expected[endpoint]=ne.attrib['name']
    for (name,pn),net in expected.items():
        if name in fps and not any(pad.GetNumber()==pn for pad in fps[name].Pads()):
            failures.append({'issue':'xml_endpoint_missing_from_footprint','ref':name,'pad':pn,'net':net})
    # Independent spec-to-Eeschema check, including intended connected net values.
    spec_endpoints=0
    for name,c in specparts.items():
        for pn,want in c['pins'].items():
            got=expected.get((name,pn),'').lstrip('/')
            if got!=want:failures.append({'issue':'spec_xml_net_mismatch','ref':name,'pad':pn,'spec':want,'xml':got})
            spec_endpoints+=1
    firmware=ROOT.parents[1]/'Code Files/GPT Build/firmware/SHM_Capstone/hardware_profile.h'
    fw=firmware.read_text()
    def array(name):
        m=re.search(r'\b'+name+r'\[\d+\]\s*=\s*\{([^}]+)\}',fw)
        if not m:raise ValueError('Missing firmware array '+name)
        return [int(v.strip(),0) for v in m.group(1).split(',')]
    mapping={name:array(name) for name in ['SHM_SDA','SHM_SCL','SHM_INT','SHM_BUS','SHM_ADDRESS']}
    # Manufacturer module pad numbers, source SRC-02 table3-1.
    gpio_to_pad={4:'4',5:'5',6:'6',8:'12',9:'17',10:'18',11:'19'}
    for bus in range(2):
        for typ in ['SDA','SCL']:
            gpio=mapping['SHM_'+typ][bus];pn=gpio_to_pad.get(gpio);want=f'I2C{bus}_{typ}'
            if specparts['U1']['pins'].get(pn)!=want:failures.append({'issue':'firmware_bus_mapping','bus':bus,'signal':typ,'gpio':gpio})
    for i,refdes in enumerate(['U2','U3','U4']):
        pins=specparts[refdes]['pins'];bus=mapping['SHM_BUS'][i]
        checks={'23':f'I2C{bus}_SCL','24':f'I2C{bus}_SDA','12':f'IMU{i+1}_INT','9':'+3V3' if mapping['SHM_ADDRESS'][i]==0x69 else 'GND'}
        for pn,want in checks.items():
            if pins.get(pn)!=want:failures.append({'issue':'firmware_imu_mapping','ref':refdes,'pad':pn})
        if mapping['SHM_ADDRESS'][i] not in [0x68,0x69]:failures.append({'issue':'unsupported_i2c_address','ref':refdes})
        pn=gpio_to_pad.get(mapping['SHM_INT'][i])
        if specparts['U1']['pins'].get(pn)!=f'IMU{i+1}_INT':failures.append({'issue':'firmware_interrupt_mapping','ref':refdes})
    # SRC-02/SRC-03/SRC-07: explicit native USB and N16R8 reserved-pin contract.
    usb_contract={'U1':{'13':'USB_DM_MCU','14':'USB_DP_MCU'},
                  'R3':{'1':'USB_DM','2':'USB_DM_MCU'},'R4':{'1':'USB_DP','2':'USB_DP_MCU'},
                  'U6':{'1':'USB_DM','6':'USB_DM','3':'USB_DP','4':'USB_DP','2':'GND','5':'VBUS_USB'},
                  'J1':{'A6':'USB_DP','B6':'USB_DP','A7':'USB_DM','B7':'USB_DM'}}
    for name,pins in usb_contract.items():
        for pn,want in pins.items():
            if specparts.get(name,{}).get('pins',{}).get(pn)!=want:
                failures.append({'issue':'native_usb_contract_mismatch','ref':name,'pad':pn,'expected':want})
    for pn in ['28','29','30']:
        if pn in specparts['U1']['pins']:failures.append({'issue':'n16r8_reserved_pin_connected_in_spec','pad':pn})
        for pad in fps.get('U1',[]).Pads() if 'U1' in fps else []:
            if pad.GetNumber()==pn and pad.GetNetname() and not pad.GetNetname().startswith('unconnected-'):
                failures.append({'issue':'n16r8_reserved_pin_connected_on_board','pad':pn,'net':pad.GetNetname()})
    for c in tree.find('components'):
        name=c.attrib['ref'];f=fps.get(name)
        if f is None:failures.append({'issue':'missing_component','ref':name});continue
        if f.GetValue()!=c.findtext('value'):failures.append({'issue':'value_mismatch','ref':name,'board':f.GetValue(),'schematic':c.findtext('value')})
        if str(f.GetFPID().GetUniStringLibId())!=c.findtext('footprint'):failures.append({'issue':'footprint_mismatch','ref':name})
        for pad in f.Pads():
            pn=pad.GetNumber()
            if not pn:continue
            want=expected.get((name,pn));got=pad.GetNetname()
            if want is None:
                if got:failures.append({'issue':'unexpected_pad_net','ref':name,'pad':pn,'board':got})
            elif want!=got:failures.append({'issue':'pad_net_mismatch','ref':name,'pad':pn,'board':got,'schematic':want})
            checked+=1
        for pn in specparts.get(name,{}).get('pins',{}):
            if not any(a.GetNumber()==pn for a in f.Pads()):failures.append({'issue':'connected_pin_missing_from_footprint','ref':name,'pad':pn})
    edges=edge_signature(b);reference_edges=edge_signature(ref)
    if edges!=reference_edges:failures.append({'issue':'reference_edge_geometry_differs','candidate_edge_count':len(edges),'reference_edge_count':len(reference_edges)})
    outline=p.SHAPE_POLY_SET();outline_valid=b.GetBoardPolygonOutlines(outline,False)
    if not outline_valid:failures.append({'issue':'outline_invalid'})
    for name in ['U2','U3','U4']:
        if name not in fps:continue
        f=fps[name]
        if f.IsFlipped() or abs(f.GetOrientationDegrees())>.001:failures.append({'issue':'imu_board_orientation_differs','ref':name,'rotation_deg':f.GetOrientationDegrees(),'flipped':f.IsFlipped()})
        if any(a.GetNumber()=='25' for a in f.Pads()):failures.append({'issue':'mpu_has_forbidden_center_pad','ref':name})
        if len(list(f.Pads()))!=24:failures.append({'issue':'mpu_pad_count_not_24','ref':name})
    constraint_records=audit_physical_constraints(b,fps,failures)
    connected_names=[n.GetNetname() for n in b.GetNetsByNetcode().values()]
    if len(connected_names)!=len(set(connected_names)):failures.append({'issue':'duplicate_net_names'})
    net_lengths={}
    for t in b.GetTracks():
        name=t.GetNetname();row=net_lengths.setdefault(name,{'track_length_mm':0,'via_count':0,'layers':set(),'widths_mm':set()})
        if isinstance(t,p.PCB_VIA):row['via_count']+=1;continue
        row['track_length_mm']+=p.ToMM(t.GetLength());row['layers'].add(b.GetLayerName(t.GetLayer()));row['widths_mm'].add(round(p.ToMM(t.GetWidth()),4))
    for row in net_lengths.values():
        row['track_length_mm']=round(row['track_length_mm'],4);row['layers']=sorted(row['layers']);row['widths_mm']=sorted(row['widths_mm'])
    report={'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tool':p.GetBuildVersion(),
            'board':str(boardpath),'board_sha256':sha(boardpath),'reference':str(REF),'reference_sha256':sha(REF),
            'netlist_sha256':sha(netfile),'spec_sha256':sha(specfile),'checked_numbered_pads':checked,'spec_endpoints_checked':spec_endpoints,'firmware_sha256':sha(firmware),'firmware_arrays':mapping,
            'outline_matches_correct_reference':edges==reference_edges,'outline_valid':bool(outline_valid),
            'rule_area_checks':constraint_records,'native_usb_contract':usb_contract,'reserved_module_pads_checked':['28','29','30'],
            'reference_edge_geometry':reference_edges,'failures':failures,'net_copper_inventory':net_lengths,
            'limits':['Net membership, CAD constraints and reference geometry only; connectivity must also pass KiCad DRC.','MPU core check rejects pad/artwork copper and paste inside the documented 3.08mm square; planes are allowed, track/via exclusion is additionally checked by KiCad DRC.','Ground-zone presence does not establish continuous return paths.','Track-length totals count all branches, not terminal-to-terminal electrical lengths.','No impedance/current-capacity, physical assembly, thermal, RF, timing or field performance claim.']}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'failures':len(failures),'numbered_pads':checked,'outline_match':edges==reference_edges,'report':str(args.output)}))
    return 1 if failures else 0
if __name__=='__main__':raise SystemExit(main())
