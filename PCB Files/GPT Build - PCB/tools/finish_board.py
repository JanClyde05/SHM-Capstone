# Superseded outline: do not accidentally replace the corrected-reference work.
import sys
if __name__ == '__main__' and '--legacy-outline-override' not in sys.argv:
    raise SystemExit('STOP: legacy larger-outline generator. Read docs/CONTINUATION_PLAN.md; use the corrected-board tools. Historical reproduction requires --legacy-outline-override after backup.')
from pathlib import Path
import pcbnew as p, xml.etree.ElementTree as E,json,math,heapq
ROOT=Path(__file__).resolve().parents[1];DES=ROOT/'design'
b=p.LoadBoard(str(DES/'SHM_Node_R2_preroute.kicad_pcb'));assert p.ImportSpecctraSES(b,str(ROOT/'reports/SHM_Node_R2.ses'))
def mm(x):return p.FromMM(x)
def pt(x,y):return p.VECTOR2I(mm(x),mm(y))
def xy(o):return (p.ToMM(o.GetPosition().x),p.ToMM(o.GetPosition().y))
fps={f.GetReference():f for f in b.GetFootprints()}
def pad(ref,n):return next(a for a in fps[ref].Pads() if a.GetNumber()==str(n))
# Preserve actual Eeschema names, including individual unconnected pin nets.
r=E.parse(DES/'SHM_Node_R2.net').getroot();oldnets={n.GetNetname():n for n in b.GetNetsByNetcode().values()}
for ne in r.find('nets'):
 name=ne.attrib['name'];legacy=name.lstrip('/');n=oldnets.get(legacy)
 if n:n.SetNetname(name)
 else:n=p.NETINFO_ITEM(b,name);b.Add(n)
 for nd in ne:
  for a in fps[nd.attrib['ref']].Pads():
   if a.GetNumber()==nd.attrib['pin']:a.SetNet(n)
for c in r.find('components'):
 f=fps[c.attrib['ref']];f.SetValue(c.findtext('value'));lib,part=c.findtext('footprint').split(':');f.SetFPID(p.LIB_ID(lib,part))
 for field in c.find('fields'):
  if field.attrib['name']!='Footprint':f.SetField(field.attrib['name'],field.text or '')
 f.SetSheetfile('SHM_Node_R2.kicad_sch');f.SetSheetname('SHM_Node_R2')
 if f.GetReference().startswith('TP'):f.SetAttributes(f.GetAttributes() & ~p.FP_EXCLUDE_FROM_BOM)
 for field in f.GetFields():
  if field.GetName() not in ['Reference','Value']:field.SetVisible(False)
for ref in ['H1','H2','H3','H4']:
 f=fps[ref];f.SetAttributes(f.GetAttributes()|p.FP_BOARD_ONLY|p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES)
# Replace router ground detours with short local plane connections.
for t in list(b.GetTracks()):
 if t.GetNetname()=='GND':b.Remove(t)
netg=pad('U5',2).GetNetCode()
def track(net,points,layer=p.F_Cu,width=.2):
 for a,z in zip(points,points[1:]):
  if a==z:continue
  t=p.PCB_TRACK(b);t.SetNetCode(net);t.SetStart(pt(*a));t.SetEnd(pt(*z));t.SetWidth(mm(width));t.SetLayer(layer);b.Add(t)
def via(net,x,y,diam=.6,drill=.3):
 v=p.PCB_VIA(b);v.SetNetCode(net);v.SetPosition(pt(x,y));v.SetWidth(mm(diam));v.SetDrill(mm(drill));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);b.Add(v);return v
# Collision-checked local GND fanout: all copper layers for via, top for short trace.
outline=p.SHAPE_POLY_SET();assert b.GetBoardPolygonOutlines(outline,False)
obstacles=[]
for f in b.GetFootprints():
 for a in f.Pads():
  if a.GetNetCode()!=netg:obstacles.append(a)
for t in b.GetTracks():
 if t.GetNetCode()!=netg:obstacles.append(t)
edges=[s for s in b.GetDrawings() if s.GetLayer()==p.Edge_Cuts]
keepouts=[z for z in b.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowVias()]
def free_via(v):
 if not outline.Contains(v):return False
 if any(e.GetEffectiveShape().Collide(v,mm(.81)) for e in edges):return False
 if any(z.Outline().Collide(v,mm(.31)) for z in keepouts):return False
 for a in obstacles:
  layers=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu] if isinstance(a,p.PAD) or isinstance(a,p.PCB_VIA) else [a.GetLayer()]
  for layer in layers:
   if a.IsOnLayer(layer) and a.GetEffectiveShape(layer).Collide(v,mm(.46)):return False
 return True
def free_track(a,z):
 seg=p.SHAPE_SEGMENT(a,z,mm(.2))
 if any(k.Outline().Collide(seg,0) for k in keepouts):return False
 return not any(o.IsOnLayer(p.F_Cu) and o.GetEffectiveShape(p.F_Cu).Collide(seg,mm(.151)) for o in obstacles)
failed=[];gndvias=[];ground_positions=[]
for f in b.GetFootprints():
 for a in f.Pads():
  if a.GetNetCode()!=netg or a.GetAttribute()!=p.PAD_ATTRIB_SMD:continue
  # EP is already connected by the footprint's plated ground array.
  if f.GetReference()=='U1' and a.GetNumber()=='41':continue
  x,y=xy(a);done=False
  for prev in ground_positions:
   if math.dist((x,y),prev)<2 and free_track(a.GetPosition(),pt(*prev)):
    track(netg,[(x,y),prev]);done=True;break
  if done:continue
  for rad in [.8,1,1.2,1.5,1.8,2.2,2.7]:
   for ang in range(0,360,15):
    q=(round(x+rad*math.cos(math.radians(ang)),4),round(y+rad*math.sin(math.radians(ang)),4));v=pt(*q)
    if all(math.dist(q,prev)>.56 for prev in ground_positions) and free_via(v) and free_track(a.GetPosition(),v):
     via(netg,*q);track(netg,[(x,y),q]);ground_positions.append(q);gndvias.append({'ref':f.GetReference(),'pad':a.GetNumber(),'xy':q});done=True;break
   if done:break
  if not done:failed.append((f.GetReference(),a.GetNumber(),(x,y)))
# Join 3V3 branch to locked B.Cu trunk using clearance-checked grid search.
# This is geometric routing, not an electrical-performance proof.
net3=pad('R10',1).GetNetCode();obs3=[a for f in b.GetFootprints() for a in f.Pads() if a.GetNetCode()!=net3]+[t for t in b.GetTracks() if t.GetNetCode()!=net3]
def clear3(a,z,layer,width=.2):
 seg=p.SHAPE_SEGMENT(pt(*a),pt(*z),mm(width))
 if not outline.Contains(pt(*z)):return False
 if any(e.GetEffectiveShape().Collide(seg,mm(.5)) for e in edges):return False
 if any(k.Outline().Collide(seg,0) for k in keepouts):return False
 return not any(o.IsOnLayer(layer) and o.GetEffectiveShape(layer).Collide(seg,mm(.151)) for o in obs3)
def via3(q):
 for layer in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]:
  if not clear3(q,q,layer,.6):return False
 return True
starts=[];src=xy(pad('R10',1))
for dx in range(-6,7):
 for dy in range(-6,7):
  q=(136.5+dx*.25,86.75+dy*.25)
  if via3(q) and clear3(src,q,p.F_Cu):starts.append(q)
starts.sort(key=lambda q:math.dist(src,q))
goal=(142.75,88.0)
for begin in starts[:8]:
 queue=[(0,0,begin)];cost={begin:0};prev={};found=False
 while queue:
  _,g,q=heapq.heappop(queue)
  if g>cost[q]+1e-9:continue
  if q==goal:found=True;break
  for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]:
   z=(q[0]+dx*.25,q[1]+dy*.25)
   if not (125<=z[0]<=148 and 80<=z[1]<=96):continue
   ng=g+math.hypot(dx,dy)*.25
   if ng>=cost.get(z,1e9) or not clear3(q,z,p.B_Cu):continue
   cost[z]=ng;prev[z]=q;heapq.heappush(queue,(ng+math.dist(z,goal),ng,z))
 if found:
  points=[goal]
  while points[-1]!=begin:points.append(prev[points[-1]])
  points.reverse();via(net3,*begin);track(net3,[src,begin]);track(net3,points,p.B_Cu);print('3V3 branch connected',len(points),'segments');break
else:raise RuntimeError('No clearance-checked 3V3 branch route found')
# Outer GND copper, direct connections; inner planes retain dedicated return reference.
for layer in [p.F_Cu,p.B_Cu]:
 z=p.ZONE(b);z.SetLayer(layer);z.SetNetCode(netg);z.SetLocalClearance(mm(.2));z.SetMinThickness(mm(.2));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetZoneName('Outer GND '+b.GetLayerName(layer));o=z.Outline();o.NewOutline()
 for x,y in [(90,40),(178,40),(178,127),(90,127)]:o.Append(mm(x),mm(y))
 b.Add(z)
# Readable, physically separated silkscreen references, values remain on fabrication layer.
refs={'U1':(135,78),'U2':(132,110),'U3':(160,50),'U4':(102,50),'J1':(116,97),'SW1':(116.6,71),'SW2':(152,82),'R6':(146,83.5),'C3':(121.8,63.8),'C4':(124,69.6),'R3':(120.9,79.6),'R4':(120.9,82),'H2':(172,60),'TP1':(120.7,99.8)}
for i in range(3):
 x,y=xy(fps[['U2','U3','U4'][i]])
 refs[f'C{7+4*i}']=(x-2.5,y+4.4);refs[f'C{8+4*i}']=(x+3.8,y+4.4)
for i in range(4):refs[f'R{7+i}']=(129+i*2.5,88.8)
for ref,coords in refs.items():
 t=fps[ref].Reference();t.SetPosition(pt(*coords));t.SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T));t.SetTextSize(pt(.8,.8));t.SetTextThickness(mm(.12))
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(DES/'SHM_Node_R2.kicad_pcb'),b)
(ROOT/'reports/ground_fanout.json').write_text(json.dumps({'added_ground_vias':gndvias,'without_local_via':failed},indent=2))
print('Saved finished-routing candidate; local GND vias',len(gndvias),'without local via',failed)
