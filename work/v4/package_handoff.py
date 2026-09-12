from pathlib import Path
import json,hashlib,shutil
v4=Path(__file__).resolve().parents[2];p=v4/'outputs/AsterGT';out=v4/'outputs/Windows-v4';v3=v4.with_name('fable-5-1-vs-fable-at-3')/'outputs/AsterGT'
notice=p/'licenses/PORSCHE_MODEL.md'
text=notice.read_text(encoding='utf-8-sig')
if '## v4 modifications' not in text:
 text+='\n## v4 modifications\n\nBlenderMCP used for 4.619m length / 2.507m wheelbase correction, wheel radius / symmetric pivots and fixed suspension references, PBR scalar correction, normal/tangent export, material/mesh consolidation, four LODs, six compound convex proxies and four-direction damage morphs. New files: assets/v4/porsche_lod0.glb through porsche_lod3.glb and blender/v4/porsche_gt3_v4.blend. Original vehicle files remain preserved. These adaptations retain MattDoesBlender credit, the source link and CC BY-NC-SA 4.0 (noncommercial, attribution, share-alike).\n'
 notice.write_text(text,encoding='utf8')
for name in ['CONTROLS.md','VEHICLE_PHYSICS.md','TRAFFIC_COLLISION.md','BLENDER_MCP_LOG.md','CHANGELOG_V4.md','QA_SETUP.md','LICENSE']:
 shutil.copy2(p/name,out/name)
for item in (p/'licenses').iterdir():
 if item.is_file():
  (out/'licenses').mkdir(exist_ok=True);shutil.copy2(item,out/'licenses'/item.name)
(out/'README.md').write_text('ASTER GT3 v4 — AsterGT-v4.exe 실행.\n\nQA logging: AsterGT-v4.exe -- --telemetry-logging\n\n최종 QA는 수행하지 않았습니다. QA_SETUP.md와 LICENSE를 참고하십시오.\n',encoding='utf8')
hash_file=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
manifest={'active_source':str(p),'active_executable':str(out/'AsterGT-v4.exe'),'final_qa_performed':False,'original_assets_preserved':{},'new_assets':{},'changed_source_files':[]}
for name in ['assets/porsche_992_gt3_r.glb','assets/porsche_rig.json','blender/porsche_992_gt3_r_rigged.blend']:
 manifest['original_assets_preserved'][name]={'sha256_v3':hash_file(v3/name),'sha256_v4_original_copy':hash_file(p/name),'identical':hash_file(v3/name)==hash_file(p/name)}
for folder in ['scripts','config']:
 for f in (p/folder).rglob('*'):
  if f.is_file() and f.suffix in ['.gd','.json','.tres']:
   rel=f.relative_to(p)
   if not (v3/rel).exists() or hash_file(f)!=hash_file(v3/rel):manifest['changed_source_files'].append(str(rel).replace('\\','/'))
for f in (p/'assets/v4').iterdir():
 if f.suffix in ['.glb','.json','.wav']:manifest['new_assets'][f.name]={'bytes':f.stat().st_size,'sha256':hash_file(f)}
manifest['executable_sha256']=hash_file(out/'AsterGT-v4.exe')
manifest['smoke_record']=json.loads((v4/'work/v4/SMOKE_CHECK.json').read_text())
(v4/'DELIVERY_V4.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
shutil.copy2(v4/'work/v4/SMOKE_CHECK.json',out/'SMOKE_CHECK.json')
print(json.dumps({'preserved':{k:v['identical'] for k,v in manifest['original_assets_preserved'].items()},'changed_source_count':len(manifest['changed_source_files']),'exe_bytes':(out/'AsterGT-v4.exe').stat().st_size,'sha256':manifest['executable_sha256']},ensure_ascii=False))
