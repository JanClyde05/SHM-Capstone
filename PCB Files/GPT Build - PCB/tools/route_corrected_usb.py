"""Manual USB routing for the corrected compact PCB.
Design geometry only: provisional widths/gap, not a verified 90-ohm stackup.
Uses a short bottom crossover to join Type-C mirrored data pads, flow-through
ESD pads, and paired bottom routes to the series resistors near the module.
Run on a fresh power-only board. Standalone creates a separate review copy,
but refuses an input that already contains USB routes: KiCad 10.0.6 SWIG
Remove(track) invalidated unrelated footprint pad containers in a reroute test.
"""
from pathlib import Path
import pcbnew as p,math,json
ROOT=Path(__file__).resolve().parents[1]
def route_usb(b):
 fps={f.GetReference():f for f in b.GetFootprints()}
 def mm(x):return p.FromMM(x)
 def pt(x,y):return p.VECTOR2I(mm(x),mm(y))
 def pad(r,n):return next(a for a in fps[r].Pads() if a.GetNumber()==str(n))
 def xy(a):return p.ToMM(a.GetPosition().x),p.ToMM(a.GetPosition().y)
 usb_names={'USB_DM','USB_DP','USB_DM_MCU','USB_DP_MCU'}
 if any(t.GetNetname().lstrip('/') in usb_names for t in b.GetTracks()):
  raise RuntimeError('USB copper already exists: regenerate from placement with prepare_corrected_routing.py; do not remove loaded tracks through this SWIG reroute path.')
 fps['U6'].SetPosition(pt(133,80.3))
 def tr(n,pts,layer=p.F_Cu,w=.2):
  for a,z in zip(pts,pts[1:]):
   if a==z:continue
   if any(not isinstance(t,p.PCB_VIA) and t.GetNetCode()==n and t.GetLayer()==layer and
          t.GetStart()==pt(*a) and t.GetEnd()==pt(*z) for t in b.GetTracks()):continue
   t=p.PCB_TRACK(b);t.SetNetCode(n);t.SetStart(pt(*a));t.SetEnd(pt(*z));t.SetWidth(mm(w));t.SetLayer(layer);t.SetLocked(True);b.Add(t)
 def via(n,q):
  if any(isinstance(v,p.PCB_VIA) and v.GetNetCode()==n and v.GetPosition()==pt(*q) for v in b.GetTracks()):return
  v=p.PCB_VIA(b);v.SetNetCode(n);v.SetPosition(pt(*q));v.SetWidth(mm(.6));v.SetDrill(mm(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetLocked(True);b.Add(v)
 dm=pad('U6',1).GetNetCode();dp=pad('U6',3).GetNetCode();g=pad('U6',2).GetNetCode()
 # Type-C mirrored pins joined near connector. D- stays top; D+ bridge bottom.
 tr(dm,[xy(pad('J1','B7')),(129.65,79.55),(129.85,79.35),xy(pad('U6',1))])
 tr(dm,[xy(pad('J1','A7')),(129.65,80.55),(129.8,80.7),(130.95,80.7),(130.95,79.35)])
 tr(dp,[xy(pad('J1','A6')),(130.25,80.05)]);via(dp,(130.25,80.05))
 tr(dp,[xy(pad('J1','B6')),(129.65,81.05),(129.95,81.35),(130.25,81.35)]);via(dp,(130.25,81.35))
 tr(dp,[(130.25,80.05),(130.25,81.35)],p.B_Cu)
 tr(dp,[(130.25,81.35),xy(pad('U6',3))])
 # Same-net copper across the flow-through pads is deliberately short and straight.
 tr(dm,[xy(pad('U6',1)),xy(pad('U6',6))]);tr(dp,[xy(pad('U6',3)),xy(pad('U6',4))])
 vdm=(134.85,79.05);vdp=(134.85,81.25)
 tr(dm,[xy(pad('U6',6)),(134.55,79.35),vdm]);via(dm,vdm)
 tr(dp,[xy(pad('U6',4)),vdp]);via(dp,vdp)
 rdm=(125.35,70.3);rdp=(125.35,72.0)
 via(dm,rdm);via(dp,rdp)
 tr(dm,[rdm,xy(pad('R3',1))]);tr(dp,[rdp,xy(pad('R4',1))])
 # Main pair: 0.20mm edge gap vertically, about 0.1536mm on 45-degree portions.
 # Fanout shortened for planar matching; via delay/impedance still unverified.
 tr(dm,[rdm,(125.35,69.53539),(127.78539,69.53539),(128.55,70.3),(133.2,74.95),(133.2,77.6),(134.65,79.05),vdm],p.B_Cu)
 tr(dp,[rdp,(129.75,72),(132.8,75.05),(132.8,78.2),(134.85,80.25),vdp],p.B_Cu)
 for r,pn in [('R3',13),('R4',14)]:
  n=pad(r,2).GetNetCode();a=xy(pad(r,2));z=xy(pad('U1',pn));tr(n,[a,(129.3,a[1]),z])
 # Short ESD ground return and return vias near data layer transitions.
 tr(g,[xy(pad('U6',2)),(132.65,80.3)],w=.25);via(g,(132.65,80.3))
 for q in [(135.3,78.45),(135.4,82.0),(124.6,70.8),(124.6,72.6)]:via(g,q)
 for q in [(130.25,78.65),(131.0,78.65),(130.25,82.15),(131.05,82.15)]:via(g,q)
 return {'U6_position':[133,80.3],'USB_width_mm':.2,'vertical_paired_edge_gap_mm':.2,'diagonal_paired_edge_gap_mm':.153553,'planar_endpoint_mismatch_engineering_goal_mm':.2,'limitations':['Actual impedance requires selected stackup.','Planar track lengths exclude via depth and component internal path.','Full USB source/power/ESD/physical compliance not established.']}
if __name__=='__main__':
 des=ROOT/'design/reference_corrected';rep=ROOT/'reports/reference_corrected';b=p.LoadBoard(str(des/'SHM_Node_R2_preroute.kicad_pcb'))
 log=route_usb(b);b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());out=des/'SHM_Node_R2_usb_review.kicad_pcb';p.SaveBoard(str(out),b)
 (rep/'usb_route_review.json').write_text(json.dumps(log,indent=2));print(out)
