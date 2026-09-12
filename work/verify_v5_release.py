from pathlib import Path
import subprocess,os,json,hashlib,datetime
r=Path(__file__).resolve().parents[1];exe=r/'outputs/Windows-v5/AsterGT-v5.exe'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
results={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'v5':{'path':str(exe),'bytes':exe.stat().st_size,'sha256':sha(exe)},'smoke':[]}
env=os.environ.copy();env['APPDATA']=str(r/'work/v5-release-profile');Path(env['APPDATA']).mkdir(exist_ok=True)
for renderer in ['headless','vulkan']:
 log=r/f'work/v5-release-{renderer}.log'
 cmd=[str(exe),'--log-file',str(log)]
 if renderer=='headless':cmd+=['--headless']
 cmd+=['--','--v4-smoke']
 cp=subprocess.run(cmd,env=env,timeout=60,capture_output=True)
 text=log.read_text(encoding='utf-8',errors='replace')
 results['smoke'].append({'renderer':renderer,'exit':cp.returncode,'ready':'ASTER_READY' in text,'errors':[x for x in text.splitlines() if 'ERROR' in x or 'WARNING' in x]})
candidate=r.parent/'fable-5-1-vs-fable-at-4-pre-qa'
evidence=r.parent/'fable-5-1-vs-fable-at-4-pre-qa-results/evidence'
start=json.loads((evidence/'candidate-start.json').read_text(encoding='utf-8-sig'))
changed=[];existing={str(f.relative_to(candidate)).replace('\\','/') for f in candidate.rglob('*') if f.is_file()}
expected={}
for entry in start:
 name=entry['path'].replace('\\','/');expected[name]=entry
 f=candidate/name
 if not f.exists() or f.stat().st_size!=entry['bytes'] or sha(f)!=entry['sha256']:changed.append(name)
results['original_candidate']={'files':len(start),'changed_or_missing':changed,'added':sorted(existing-set(expected))}
oldexe=candidate/'outputs/Windows-v4-pre-qa/AsterGT-v4-pre-qa.exe'
results['original_candidate']['exe_sha256']=sha(oldexe)
results['original_candidate']['exe_bytes']=oldexe.stat().st_size
original_user=Path(os.environ['APPDATA'])/'AsterGT-v4'
userstart=json.loads((evidence/'original-user-start.json').read_text(encoding='utf-8-sig'))
results['original_v4_preferences_changed']=[e['path'] for e in userstart if not (original_user/e['path']).exists() or sha(original_user/e['path'])!=e['sha256']]
results['status']='PASS' if not changed and not results['original_candidate']['added'] and not results['original_v4_preferences_changed'] and all(s['exit']==0 and s['ready'] and not s['errors'] for s in results['smoke']) else 'FAIL'
(r/'work/v5-release-verification.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(results,ensure_ascii=False,indent=2))
