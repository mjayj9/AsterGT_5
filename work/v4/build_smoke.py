from pathlib import Path
import subprocess,json,time,hashlib,re
v4=Path(__file__).resolve().parents[2];p=v4/'outputs/AsterGT'
godot=Path('C:/Tools/Godot/4.6.3-dotnet/Godot_v4.6.3-stable_mono_win64/Godot_v4.6.3-stable_mono_win64_console.exe')
exe=v4/'outputs/Windows-v4/AsterGT-v4.exe';exe.parent.mkdir(exist_ok=True)
si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
results={'scope':'syntax/import/export/minimal startup and orderly shutdown ONLY','final_qa_performed':False,'performance_tests_performed':False,'collision_tests_performed':False,'demo_video_created':False,'steps':[]}
steps=[('import',[str(godot),'--headless','--path',str(p),'--editor','--import','--quit']),('export',[str(godot),'--headless','--path',str(p),'--export-release','Windows Desktop',str(exe)]),('executable_startup',[str(exe),'--headless','--log-file',str(v4/'work/v4/package_smoke_engine.log'),'--','--v4-smoke'])]
for name,args in steps:
 start=time.time()
 result=subprocess.run(args,capture_output=True,startupinfo=si,timeout=180 if name!='executable_startup' else 30)
 text=(result.stdout+result.stderr).decode('utf8',errors='replace')
 log=v4/'work/v4'/('smoke_'+name+'.log');log.write_text(text,encoding='utf8')
 errors=re.findall(r'(?m)^.*(?:SCRIPT ERROR:|Parse Error:|ERROR:).*$' ,text)
 if name=='executable_startup' and (v4/'work/v4/package_smoke_engine.log').exists():
  engine=(v4/'work/v4/package_smoke_engine.log').read_text(encoding='utf-8-sig')
  errors+=re.findall(r'(?m)^.*(?:SCRIPT ERROR:|Parse Error:|ERROR:).*$' ,engine)
  text+=engine
 record={'step':name,'return_code':result.returncode,'duration_s':round(time.time()-start,3),'errors':errors,'log':str(log),'startup_marker':('ASTER_READY' in text) if name=='executable_startup' else None}
 results['steps'].append(record)
 print(json.dumps(record),flush=True)
 if result.returncode or errors or (name=='executable_startup' and 'ASTER_READY' not in text):
  (v4/'work/v4/SMOKE_CHECK.json').write_text(json.dumps(results,indent=2),encoding='utf8')
  raise SystemExit('Smoke check requires correction; no QA verdict issued.')
results['executable']={'path':str(exe),'bytes':exe.stat().st_size,'sha256':hashlib.sha256(exe.read_bytes()).hexdigest()}
(v4/'work/v4/SMOKE_CHECK.json').write_text(json.dumps(results,indent=2),encoding='utf8')
print('BUILD_SMOKE_ONLY_COMPLETE')
