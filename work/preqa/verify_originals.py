from pathlib import Path
import hashlib,json
q=Path(r'C:/Users/admin/Documents/Codex/2026-09-08/fable-5-1-vs-fable-at-4-pre-qa');before=json.loads((q/'work/preqa/originals_before.json').read_text())
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while data:=f.read(1024*1024):h.update(data)
 return h.hexdigest()
result={'method':'SHA-256 of every file in both original trees, before vs after; names and byte counts also checked','originals':{},'pass':True}
for name,files in before.items():
 root=q.parent/name;current={f.relative_to(root).as_posix():f for f in root.rglob('*') if f.is_file()}
 added=sorted(set(current)-set(files));removed=sorted(set(files)-set(current));changed=[]
 for rel,entry in files.items():
  if rel in current and (current[rel].stat().st_size!=entry['bytes'] or digest(current[rel])!=entry['sha256']):changed.append(rel)
 ok=not added and not removed and not changed;result['pass']=result['pass'] and ok
 result['originals'][name]={'files':len(files),'added':added,'removed':removed,'changed':changed,'pass':ok}
 print(name,'unchanged',ok,'files',len(files),flush=True)
(q/'work/preqa/ORIGINALS_PRESERVED.json').write_text(json.dumps(result,indent=2),encoding='utf8')
raise SystemExit(0 if result['pass'] else 1)
