# Superseded outline: do not accidentally replace the corrected-reference work.
import sys
if __name__ == '__main__' and '--legacy-outline-override' not in sys.argv:
    raise SystemExit('STOP: legacy larger-outline generator. Read docs/CONTINUATION_PLAN.md; use the corrected-board tools. Historical reproduction requires --legacy-outline-override after backup.')
"""Build placement/net-correlated board. Run with KiCad 10 bundled Python.
Rebuilds placement; it intentionally does not overwrite a routed final board.
Source of connectivity: circuit_spec.json; compare with exported netlist separately.
"""
from pathlib import Path
import json, math, uuid
import pcbnew as p

ROOT=Path(__file__).resolve().parents[1]
DES=ROOT/'design'; LIB=Path('C:/Program Files/KiCad/10.0/share/kicad/footprints')
SPEC=json.loads((DES/'circuit_spec.json').read_text())
def mm(v): return p.FromMM(v)
def pt(x,y): return p.VECTOR2I(mm(x),mm(y))
local=DES/'SHM_Local.pretty'; local.mkdir(exist_ok=True)
# SRC-01 recommended land pattern: 0.35 mm width, 0.80/0.85 length,
# 0.50 pitch, 4.80 overall. No center copper or paste, per section 11.4.2.
fp=['(footprint "MPU6050_QFN24_NoCenterPad" (version 20241229) (generator "pcbnew") (layer "F.Cu") (attr smd)',
'(descr "MPU6050 manufacturer land: 0.35 wide, 0.8 normal /0.85 corner; 4.8 extent; no center copper/paste")',
'(fp_text reference "REF**" (at 0 -3.5) (layer "F.SilkS") (effects (font (size 0.8 0.8)(thickness 0.12))))',
'(fp_text value "MPU-6050" (at 0 3.5) (layer "F.Fab") (effects (font (size 0.8 0.8)(thickness 0.12))))',
'(fp_rect (start -2.65 -2.65)(end 2.65 2.65)(stroke(width 0.05)(type default))(fill none)(layer "F.CrtYd"))',
'(fp_rect (start -2 -2)(end 2 2)(stroke(width 0.1)(type default))(fill none)(layer "F.Fab"))',
'(fp_circle (center -2.7 -2.7)(end -2.5 -2.7)(stroke(width 0.12)(type default))(fill none)(layer "F.SilkS"))']
for n in range(1,25):
    corner=n in (1,6,7,12,13,18,19,24); length=.85 if corner else .8
    c=2.4-length/2; a=(n-1)%6; t=-1.25+.5*a
    if n<=6: xy=(-c,t); size=(length,.35)
    elif n<=12: xy=(t,c); size=(.35,length)
    elif n<=18: xy=(c,-t); size=(length,.35)
    else: xy=(-t,-c); size=(.35,length)
    fp.append(f'(pad "{n}" smd rect (at {xy[0]} {xy[1]}) (size {size[0]} {size[1]}) (layers "F.Cu" "F.Paste" "F.Mask"))')
fp.append(')')
(local/'MPU6050_QFN24_NoCenterPad.kicad_mod').write_text('\n'.join(fp))
(DES/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "SHM_Local")(type "KiCad")(uri "${KIPRJMOD}/SHM_Local.pretty")(options "")(descr "Project-local verified MPU6050 land pattern")))\n')

b=p.BOARD(); b.SetCopperLayerCount(4)
ds=b.GetDesignSettings();ds.m_MinClearance=mm(.15);ds.m_TrackMinWidth=mm(.15);ds.m_CopperEdgeClearance=mm(.5)
ds.m_ViasMinSize=mm(.6);ds.m_MinThroughDrill=mm(.3) if hasattr(ds,'m_MinThroughDrill') else None
nc=ds.m_NetSettings.GetDefaultNetclass();nc.SetClearance(mm(.15));nc.SetTrackWidth(mm(.2));nc.SetViaDiameter(mm(.6));nc.SetViaDrill(mm(.3))
old=p.LoadBoard(str(ROOT.parent/'Reference PCB (OLD Version)/Thesis/Thesis.kicad_pcb'))
for item in old.GetDrawings():
    if item.GetLayer()==p.Edge_Cuts:
        clone=item.Duplicate();clone.SetWidth(mm(.05));b.Add(clone)
names=sorted({net for c in SPEC['components'] for net in c['pins'].values()})
nets={}
for i,name in enumerate(names,1):
    n=p.NETINFO_ITEM(b,name,i);b.Add(n);nets[name]=n

# Same physical orientation for all three triaxial channels.
placements={'U1':(135,70,0),'U2':(135,114,0),'U3':(163,54,0),'U4':(105,54,0),
 'U5':(148,89,0),'U6':(123.7,91,0),'J1':(116,91,-90),'J2':(151,67,0),
 'C1':(141.8,86.7,0),'C2':(141.8,91.3,180),'C3':(121.8,65.8,180),'C4':(123,68.1,0),'C5':(120.5,71.5,0),
 'R1':(122.8,86.5,90),'R2':(122.8,96,90),'R3':(123.6,79.8,0),'R4':(123.6,82.2,0),
 'R5':(119,68.5,0),'R6':(148.2,82,0),'R7':(129,86,90),'R8':(131.5,86,90),'R9':(134,86,90),'R10':(136.5,86,90),
 'F1':(129,94,0),'SW1':(118.6,76,0),'SW2':(150,77.5,0)}
for i,ref in enumerate(['U2','U3','U4']):
    x,y,_=placements[ref]
    # Local bypasses immediately outside their package edges, with pad 1 toward IC.
    placements[f'C{6+i*4}']=(x+4.4,y+1.25,0)
    placements[f'C{7+i*4}']=(x-.75,y+4.4,90)
    placements[f'C{8+i*4}']=(x+1.8,y+4.4,90)
    placements[f'C{9+i*4}']=(x+.75,y-4.4,-90)
for i in range(1,12): placements[f'TP{i}']=(123+(i-1)%6*4.5,98.7+(i-1)//6*3.5,0)
fps={}
for c in SPEC['components']:
    ref=c['ref'];lib,name=c['footprint'].split(':');path=local if lib=='SHM_Local' else LIB/(lib+'.pretty')
    f=p.FootprintLoad(str(path),name)
    if not f: raise RuntimeError('Missing footprint '+c['footprint'])
    f.SetFPID(p.LIB_ID(lib,name));f.SetReference(ref);f.SetValue(c['value']);x,y,rot=placements[ref]
    f.SetPosition(pt(x,y));f.SetOrientationDegrees(rot)
    f.SetPath(p.KIID_PATH('/'+SPEC['schematic_uuid']+'/'+c['uuid']))
    for pad in f.Pads():
        if pad.GetNumber() in c['pins']: pad.SetNet(nets[c['pins'][pad.GetNumber()]])
    f.Value().SetVisible(False);f.Reference().SetTextSize(pt(.8,.8));f.Reference().SetTextThickness(mm(.12))
    if ref=='U1':
        for g in f.GraphicalItems():
            if g.GetLayer()==p.F_SilkS and p.ToMM(g.GetBoundingBox().GetTop())<62.2:g.SetLayer(p.F_Fab)
    b.Add(f);fps[ref]=f

def area(points,name,tracks=True,vias=True,copper=False,pads=False):
    z=p.ZONE(b);z.SetIsRuleArea(True);z.SetLayerSet(p.LSET.AllCuMask(4));z.SetZoneName(name)
    z.SetDoNotAllowTracks(tracks);z.SetDoNotAllowVias(vias);z.SetDoNotAllowZoneFills(copper);z.SetDoNotAllowPads(pads)
    z.SetDoNotAllowFootprints(False);o=z.Outline();o.NewOutline()
    for x,y in points:o.Append(mm(x),mm(y))
    b.Add(z)
def rect(x1,y1,x2,y2):return [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]
for ref in ['U2','U3','U4']:
    x,y,_=placements[ref];area(rect(x-1.54,y-1.54,x+1.54,y+1.54),ref+' die: no tracks or vias; ground plane allowed')
# Antenna physical overhang plus 15 mm lateral surroundings. No active copper.
area(rect(111,27,159,62.1),'Antenna region and surrounding clearance',copper=True,pads=True)
for i,(x,y) in enumerate([(128,119),(169,60),(99,60),(150,98)],1):
    f=p.FootprintLoad(str(LIB/'MountingHole.pretty'),'MountingHole_3.2mm_M3');f.SetReference('H'+str(i));f.SetValue('M3 NPTH');f.SetPosition(pt(x,y));f.Value().SetVisible(False);b.Add(f)
    area([(x+3.3*math.cos(a*math.pi/16),y+3.3*math.sin(a*math.pi/16)) for a in range(32)],'M3 fastener copper clearance H'+str(i),copper=True,pads=False)

def text(value,x,y,size=1,layer=p.F_SilkS):
    t=p.PCB_TEXT(b);t.SetText(value);t.SetPosition(pt(x,y));t.SetTextSize(pt(size,size));t.SetTextThickness(mm(.15));t.SetLayer(layer);t.SetMirrored(layer==p.B_SilkS);b.Add(t)
text('SHM NODE R2',135,94,1.3,p.B_SilkS)
text('N16R8 / 3 x XYZ',135,97,1,p.B_SilkS)
for i,ref in enumerate(['U2','U3','U4'],1):
    x,y,_=placements[ref];text('IMU'+str(i)+' XYZ',x,y-7,1);text('+X >  +Y ^',x,y+8,.8)

# Inner layers are continuous GND references; outer copper fill is added after routing.
for layer in [p.In1_Cu,p.In2_Cu]:
    z=p.ZONE(b);z.SetLayer(layer);z.SetNet(nets['GND']);z.SetLocalClearance(mm(.2));z.SetMinThickness(mm(.2));z.SetPadConnection(p.ZONE_CONNECTION_FULL)
    z.SetZoneName('Ground reference '+b.GetLayerName(layer));o=z.Outline();o.NewOutline()
    for x,y in rect(90,40,178,127):o.Append(mm(x),mm(y))
    b.Add(z)
out=DES/'SHM_Node_R2_placement.kicad_pcb';p.SaveBoard(str(out),b)
# Explicit project rules; no exclusions or suppressed DRC issues.
proj={'meta':{'filename':'SHM_Node_R2.kicad_pro','version':1},'board':{'design_settings':{'rules':{'min_clearance':.15,'min_track_width':.15,'min_via_diameter':.6,'min_through_hole_diameter':.2,'min_hole_clearance':.15,'min_copper_edge_clearance':.5,'min_silk_clearance':.1}}},'net_settings':{'classes':[{'name':'Default','clearance':.15,'track_width':.2,'via_diameter':.6,'via_drill':.3,'diff_pair_width':.25,'diff_pair_gap':.15,'diff_pair_via_gap':.25,'wire_width':6,'bus_width':12,'line_style':0,'schematic_color':'rgba(0, 0, 0, 0)','pcb_color':'rgba(0, 0, 0, 0)'}],'meta':{'version':4}}}
(DES/'SHM_Node_R2.kicad_pro').write_text(json.dumps(proj,indent=2))
(DES/'SHM_Node_R2_placement.kicad_pro').write_text(json.dumps(proj,indent=2))
print('Placement saved:',out,'components',len(fps),'plus 4 mounting holes')
