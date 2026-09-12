from pathlib import Path
import zipfile,hashlib,json,re
root=Path.cwd();out=root/'outputs';source=out/'AsterGT'
for name,folder in [('AsterGT-Source.zip',source),('AsterGT-Windows.zip',out/'Windows')]:
 target=out/name
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(folder.rglob('*')):
   rel=p.relative_to(folder)
   if not p.is_file() or any(x in ['.godot','__pycache__','templates'] for x in rel.parts) or p.suffix=='.blend1':continue
   z.write(p,Path(folder.name)/rel)
 with zipfile.ZipFile(target) as z:
  assert z.testzip() is None
  names=set(z.namelist())
  if folder==source:
   for item in ['project.godot','scenes/main.tscn','README.md','blender/aster_gt.blend','blender/wheel.blend','assets/aster_gt.glb','docs/TEST_REPORT.md','export_presets.cfg','tests/native/08_graphics.png']:
    assert 'AsterGT/'+item in names,item
  else:
   assert 'Windows/AsterGT.exe' in names
 print(name,round(target.stat().st_size/1024/1024,2),'MiB',len(names),'files')
paths=[out/'AsterGT-Source.zip',out/'AsterGT-Windows.zip',out/'Windows/AsterGT.exe']
lines=[hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(out).as_posix() for p in paths]
(out/'SHA256SUMS.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
# Check source documentation relative links and required result sets.
bad=[]
for p in [source/'README.md',* (source/'docs').glob('*.md')]:
 for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8-sig')):
  if '://' not in link and not link.startswith('#') and not (p.parent/link.split('#')[0]).exists():bad.append((str(p),link))
assert not bad,bad
for name in ['physics','dynamics','integration']:
 d=json.loads((source/'tests'/(name+'_results.json')).read_text());assert all(d['checks'].values())
print('ZIP CRC checks, deliverables, document links and all results verified.')
print('\n'.join(lines))
