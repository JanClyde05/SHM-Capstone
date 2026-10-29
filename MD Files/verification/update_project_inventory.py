"""Rebuild the repository inventory; presence/size is not content validation."""
from pathlib import Path
import datetime

root=Path(__file__).resolve().parents[2]
out=root/'MD Files/13_PROJECT_FILE_INVENTORY.md'
paths=sorted((p for p in root.rglob('*') if '.git' not in p.relative_to(root).parts),key=lambda p:str(p).lower())
dirs=[p for p in paths if p.is_dir()]
files=[p for p in paths if p.is_file() and p!=out]
date=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec='seconds')
lines=['# Project file inventory','',f'Generated {date} (Asia/Manila) from the project root. Presence/size is not validation. Git internals and this inventory are excluded.','',f'Directories: {len(dirs)}. Files listed: {len(files)}. Total listed bytes: {sum(p.stat().st_size for p in files):,}.','','## Directory tree','','```text','.']
for p in dirs:
 rel=p.relative_to(root);lines.append('  '*len(rel.parts)+rel.name)
lines+=['```','','## File inventory','','| Project-relative path | Bytes |','|---|---:|']
for p in files:lines.append(f'| `{p.relative_to(root).as_posix()}` | {p.stat().st_size:,} |')
out.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(f'{len(dirs)} directories; {len(files)} files; {out}')
