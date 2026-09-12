from pathlib import Path
import subprocess,json,time,hashlib,re,os
q=Path(r'C:/Users/admin/Documents/Codex/2026-09-08/fable-5-1-vs-fable-at-4-pre-qa');p=q/'outputs/AsterGT';work=q/'work/preqa';out=q/'outputs/Windows-v4-pre-qa';out.mkdir(exist_ok=True)
godot=Path('C:/Tools/Godot/4.6.3-dotnet/Godot_v4.6.3-stable_mono_win64/Godot_v4.6.3-stable_mono_win64_console.exe');exe=out/'AsterGT-v4-pre-qa.exe'
si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
report={'scope':'Pre-QA blocker correction','final_qa_performed':False,'driving_tuning_performed':False,'steps':[]}
def digest(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def save(): (work/'PRE_QA_GATE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
def run_step(name,args,timeout=180):
 start=time.time()
 result=subprocess.run(args,capture_output=True,startupinfo=si,timeout=timeout)
 text=(result.stdout+result.stderr).decode('utf8',errors='replace')
 (work/(name+'.log')).write_text(text,encoding='utf8')
 errors=re.findall(r'(?m)^.*(?:SCRIPT ERROR:|Parse Error:|ERROR:).*$' ,text)
 step={'name':name,'return_code':result.returncode,'duration_s':round(time.time()-start,3),'errors':errors,'log':str(work/(name+'.log'))}
 if name=='executable_startup':
  engine=(work/'executable_engine.log').read_text(encoding='utf-8-sig')
  errors+=re.findall(r'(?m)^.*(?:SCRIPT ERROR:|Parse Error:|ERROR:).*$' ,engine)
  step['startup_marker']='ASTER_READY' in text+engine
 report['steps'].append(step);save();print(json.dumps(step),flush=True)
 if result.returncode or errors or (name=='executable_startup' and not step['startup_marker']):raise SystemExit('Pre-QA gate requires correction.')
base=[str(godot),'--headless','--path',str(p)]
run_step('headless_import',base+['--log-file',str(work/'import_engine.log'),'--editor','--import','--quit'])
for name,script in [('contact_regression','contact_regression.gd'),('telemetry_regression','telemetry_regression.gd')]:
 run_step(name,base+['--log-file',str(work/(name+'_engine.log')),'--script','res://tests/preqa/'+script],30)
 report[name]=json.loads((p/'tests/preqa'/(name+'.json')).read_text())
 if not report[name]['pass']:save();raise SystemExit(name+' failed')
folder=work/'atomic-store';folder.mkdir(exist_ok=True)
target=folder/('settings-'+str(time.time_ns())+'.json');temp=Path(str(target)+'.tmp')
atomic=[]
for revision in [1,2]:
 payload=json.dumps({'schema_version':4,'revision':revision}).encode()
 with temp.open('wb') as f:f.write(payload);f.flush();os.fsync(f.fileno())
 result=subprocess.run([str(p/'runtime_tools/AtomicReplace.exe'),str(temp),str(target)],startupinfo=si,capture_output=True,timeout=10)
 ok=result.returncode==0 and target.read_bytes()==payload and not temp.exists()
 atomic.append({'operation':'first_create' if revision==1 else 'replace_existing','return_code':result.returncode,'pass':ok,'sha256':digest(target) if target.is_file() else None})
 if not ok:report['atomic_store']=atomic;save();raise SystemExit('Native atomic store operation failed')
report['atomic_store']={'scope':'production native helper create and replace; atomicity reviewed in source, not a power-loss test','results':atomic};save();print(json.dumps(report['atomic_store']),flush=True)
run_step('windows_export',base+['--log-file',str(work/'export_engine.log'),'--export-release','Windows Desktop',str(exe)])
run_step('executable_startup',[str(exe),'--headless','--log-file',str(work/'executable_engine.log'),'--','--v4-smoke'],30)
report['executable']={'path':str(exe),'bytes':exe.stat().st_size,'sha256':digest(exe)}
report['READY_FOR_PRE_QA_GATE']=True
save();print(json.dumps({'READY_FOR_PRE_QA_GATE':True,'executable':report['executable']}),flush=True)
