from pathlib import Path
import pcbnew as p,json,argparse
ROOT=Path(__file__).resolve().parents[1];DES=ROOT/'design/reference_corrected';REP=ROOT/'reports/reference_corrected';REP.mkdir(exist_ok=True)
ap=argparse.ArgumentParser(description='Prepare critical power and reviewed USB routes; --power-only is an incomplete intermediate.')
ap.add_argument('--power-only',action='store_true')
args=ap.parse_args()
if not args.power_only and not (ROOT/'tools/route_corrected_usb.py').exists():
 raise SystemExit('Required USB helper is missing. Read CONTINUATION_PLAN.md; use --power-only only for explicitly incomplete power checks.')
b=p.LoadBoard(str(DES/'SHM_Node_R2_placement.kicad_pcb'));fps={f.GetReference():f for f in b.GetFootprints()}
def pt(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def pad(r,n):return next(a for a in fps[r].Pads() if a.GetNumber()==str(n))
def xy(a):return p.ToMM(a.GetPosition().x),p.ToMM(a.GetPosition().y)
def track(n,points,layer=p.F_Cu,w=.65):
 for a,z in zip(points,points[1:]):
  if a==z:continue
  t=p.PCB_TRACK(b);t.SetNetCode(n);t.SetStart(pt(*a));t.SetEnd(pt(*z));t.SetLayer(layer);t.SetWidth(p.FromMM(w));t.SetLocked(True);b.Add(t)
def via(n,q):
 v=p.PCB_VIA(b);v.SetNetCode(n);v.SetPosition(pt(*q));v.SetWidth(p.FromMM(.7));v.SetDrill(p.FromMM(.3));v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetViaType(p.VIATYPE_THROUGH);v.SetLocked(True);b.Add(v)
def pair(n,q,dx=.8):
 v=(q[0]+dx,q[1]);via(n,q);via(n,v);track(n,[q,v]);track(n,[q,v],p.B_Cu)
n=pad('U5',3).GetNetCode();a=xy(pad('C2',1));d=xy(pad('C3',1));pair(n,a);pair(n,d)
track(n,[xy(pad('U5',3)),a]);track(n,[a,(a[0],81),(d[0],66.3),d],p.B_Cu)
track(n,[d,(129,55.8),xy(pad('U1',2))])
n=pad('U5',1).GetNetCode();a=xy(pad('C1',1));d=xy(pad('F1',2));pair(n,a);pair(n,d)
track(n,[a,xy(pad('U5',1))]);track(n,[d,(150,84.3),(150,75),(a[0],75),a],p.B_Cu)
n=pad('F1',1).GetNetCode();a=xy(pad('F1',1));pair(n,a,-.8)
for r in ['A4','A9']:
 q=xy(pad('J1',r));v=(q[0]+.65,q[1]);via(n,v);track(n,[q,v],w=.4)
v1=xy(pad('J1','A4'));v2=xy(pad('J1','A9'));q1=(v1[0]+.65,v1[1]);q2=(v2[0]+.65,v2[1]);track(n,[q1,q2,(131.03,84.3),a],p.B_Cu)
# ESD VBUS support remains a narrow branch, not the main supply path.
# Lock the twelve local MPU support-capacitor connections before general routing.
# Equation-free geometric construction; SRC-01 typical circuit fixes the pin mapping.
for i,r in enumerate(['U2','U3','U4']):
 for pin,cap in [(13,6+i*4),(8,7+i*4),(10,8+i*4),(20,9+i*4)]:
  a=xy(pad(r,pin));z=xy(pad('C'+str(cap),1));n=pad(r,pin).GetNetCode()
  assert n==pad('C'+str(cap),1).GetNetCode(),(r,pin,cap,'net mismatch')
  points=[a,(a[0],a[1]+1),z] if pin==10 else [a,z]
  track(n,points,w=.2)
# USB pre-route function is added after separate review.
if not args.power_only:
 from route_corrected_usb import route_usb
 route_usb(b)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(DES/'SHM_Node_R2_preroute.kicad_pcb'),b)
dsn=REP/('SHM_Node_R2_power_only.dsn' if args.power_only else 'SHM_Node_R2.dsn')
assert p.ExportSpecctraDSN(b,str(dsn));print('Critical routing prepared; power_only=',args.power_only,'DSN=',dsn)
