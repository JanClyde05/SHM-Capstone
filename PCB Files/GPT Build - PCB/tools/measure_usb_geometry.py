"""Read-only planar USB route graph measurement; not electrical-delay/impedance proof."""
from pathlib import Path
import argparse, hashlib, json, math, heapq, datetime
import pcbnew as p

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--board',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 b=p.LoadBoard(str(a.board));fps={f.GetReference():f for f in b.GetFootprints()}
 def xy(q):return (round(p.ToMM(q.x),6),round(p.ToMM(q.y),6))
 def pad(r,n):return next(q for q in fps[r].Pads() if q.GetNumber()==str(n))
 def graph(net):
  tracks=[t for t in b.GetTracks() if t.GetNetCode()==net];points={}
  segs=[];vias=[]
  for t in tracks:
   if isinstance(t,p.PCB_VIA):
    q=xy(t.GetPosition());vias.append(q)
    for l in [p.F_Cu,p.B_Cu]:points.setdefault(l,set()).add(q)
   else:
    l=t.GetLayer();u=xy(t.GetStart());v=xy(t.GetEnd());segs.append((l,u,v));points.setdefault(l,set()).update([u,v])
  edges={}
  def link(u,v,d,tr=0):edges.setdefault(u,[]).append((v,d,tr));edges.setdefault(v,[]).append((u,d,tr))
  for l,u,v in segs:
   length=math.dist(u,v)
   if length==0:continue
   on=[q for q in points[l] if abs(math.dist(u,q)+math.dist(q,v)-length)<.00001]
   on.sort(key=lambda q:math.dist(u,q))
   for q,z in zip(on,on[1:]):link((l,*q),(l,*z),math.dist(q,z))
  for q in vias:link((p.F_Cu,*q),(p.B_Cu,*q),0,1)
  return edges,{'total_track_mm':sum(math.dist(u,v) for l,u,v in segs),'via_count':len(vias)}
 def path(r1,n1,r2,n2):
  src=pad(r1,n1);dst=pad(r2,n2);assert src.GetNetCode()==dst.GetNetCode()
  g,total=graph(src.GetNetCode());start=(p.F_Cu,*xy(src.GetPosition()));goal=(p.F_Cu,*xy(dst.GetPosition()))
  todo=[(0,0,start)];best={start:(0,0)}
  while todo:
   d,t,u=heapq.heappop(todo)
   if (d,t)!=best[u]:continue
   if u==goal:return {'planar_track_mm':round(d,6),'via_transitions':t,'net':src.GetNetname(),'net_inventory':total}
   for v,w,vt in g.get(u,[]):
    score=(d+w,t+vt)
    if score<best.get(v,(math.inf,math.inf)):best[v]=score;heapq.heappush(todo,(*score,v))
  raise RuntimeError(f'No explicit track graph path {r1}.{n1} to {r2}.{n2}; pad-internal connections may require separate analysis')
 paths={label:path(*v) for label,v in {'A_DM':('J1','A7','R3','1'),'B_DM':('J1','B7','R3','1'),'A_DP':('J1','A6','R4','1'),'B_DP':('J1','B6','R4','1'),'MCU_DM':('R3','2','U1','13'),'MCU_DP':('R4','2','U1','14')}.items()}
 report={'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'board':str(a.board.resolve()),'sha256':hashlib.sha256(a.board.read_bytes()).hexdigest(),'paths':paths,'endpoint_planar_mismatch_mm':{s:round(paths[s+'_DM']['planar_track_mm']+paths['MCU_DM']['planar_track_mm']-paths[s+'_DP']['planar_track_mm']-paths['MCU_DP']['planar_track_mm'],6) for s in ['A','B']},'limits':['Planar tracks only; via barrel depth, pad shapes, resistor internals and coupling excluded.','Negative mismatch means D+ is longer.','No USB compliance, electrical delay or 90-ohm impedance established.']}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
