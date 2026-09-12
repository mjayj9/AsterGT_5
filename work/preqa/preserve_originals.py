from pathlib import Path
import hashlib,json,time
q=Path(r'C:/Users/admin/Documents/Codex/2026-09-08/fable-5-1-vs-fable-at-4-pre-qa')
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while data:=f.read(1024*1024):h.update(data)
 return h.hexdigest()
result={}
for name in ['fable-5-1-vs-fable-at-3','fable-5-1-vs-fable-at-4']:
 root=q.parent/name; rows={}
 for f in root.rglob('*'):
  if f.is_file():rows[f.relative_to(root).as_posix()]={'bytes':f.stat().st_size,'sha256':digest(f)}
 result[name]=rows
 print(name,len(rows),flush=True)
(q/'work/preqa/originals_before.json').write_text(json.dumps(result,indent=2),encoding='utf8')
