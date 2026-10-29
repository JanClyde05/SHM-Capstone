# Superseded outline: do not accidentally replace the corrected-reference work.
import sys
if __name__ == '__main__' and '--legacy-outline-override' not in sys.argv:
    raise SystemExit('STOP: legacy larger-outline generator. Read docs/CONTINUATION_PLAN.md; use the corrected-board tools. Historical reproduction requires --legacy-outline-override after backup.')
from pathlib import Path
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1];DES=ROOT/'design'
b=p.LoadBoard(str(DES/'SHM_Node_R2_placement.kicad_pcb'))
fps={f.GetReference():f for f in b.GetFootprints()}
def mm(x):return p.FromMM(x)
def pt(x,y):return p.VECTOR2I(mm(x),mm(y))
def pad(ref,num):return next(x for x in fps[ref].Pads() if x.GetNumber()==str(num))
def xy(pad):return (p.ToMM(pad.GetPosition().x),p.ToMM(pad.GetPosition().y))
def track(net,points,layer=p.F_Cu,width=.2):
 for a,z in zip(points,points[1:]):
  if a==z:continue
  t=p.PCB_TRACK(b);t.SetNetCode(net);t.SetStart(pt(*a));t.SetEnd(pt(*z));t.SetWidth(mm(width));t.SetLayer(layer);t.SetLocked(True);b.Add(t)
def via(net,x,y):
 v=p.PCB_VIA(b);v.SetNetCode(net);v.SetPosition(pt(x,y));v.SetWidth(mm(.7));v.SetDrill(mm(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetLocked(True);b.Add(v)
# Main 3V3 distribution: 0.65 mm trunk, direct short connections at LDO and module.
n=pad('U5',3).GetNetCode()
track(n,[xy(pad('U5',3)),xy(pad('C2',1))],width=.65)
a=xy(pad('C2',1));d=xy(pad('C3',1))
via(n,*a);via(n,*d)
track(n,[a,(142.75,88),(122.75,68),d],p.B_Cu,.65)
track(n,[d,(123.5,65.8),xy(pad('U1',2))],width=.65)
# Short damping-resistor-to-module sections, kept on top layer.
for r,up in [('R3',13),('R4',14)]:
 n=pad(r,2).GetNetCode();a=xy(pad(r,2));z=xy(pad('U1',up))
 track(n,[a,(z[0]-.6,a[1]),(z[0],z[1])],width=.2)
# Fill inner reference planes before DSN so the router sees plane connectivity.
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
p.SaveBoard(str(DES/'SHM_Node_R2_preroute.kicad_pcb'),b)
ok=p.ExportSpecctraDSN(b,str(ROOT/'reports/SHM_Node_R2.dsn'))
print('DSN export',ok)
