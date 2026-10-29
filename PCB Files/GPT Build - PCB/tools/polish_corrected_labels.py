"""Final silk-only correction after the finisher; four labels must clear bodies.
Run on the corrected candidate only. Requires renewed DRC/visual review.
"""
from pathlib import Path
import pcbnew as p
root=Path(__file__).resolve().parents[1]
path=root/'design/reference_corrected/SHM_Node_R2.kicad_pcb'
b=p.LoadBoard(str(path));fps={f.GetReference():f for f in b.GetFootprints()}
for ref,(x,y) in {'R1':(129.5,74.4),'R8':(136.5,74.1),'U1':(152.2,58.4),'J1':(123.5,74.2)}.items():
 t=fps[ref].Reference();t.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)))
p.SaveBoard(str(path),b)
print('Moved four reference labels; geometry/net routing unchanged. Recheck required.')
