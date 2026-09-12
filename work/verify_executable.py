from pathlib import Path
import subprocess,json
root=Path.cwd();exe=root/'outputs/Windows/AsterGT.exe';out=root/'outputs/Verification';out.mkdir(exist_ok=True)
for quality in ['Low','Medium','High','Ultra']:
 log=root/'work/logs'/('release_benchmark_'+quality+'.log')
 run=subprocess.run([str(exe),'--log-file',str(log),'--','--benchmark='+quality,'--qa-output='+out.as_posix()],cwd=exe.parent,timeout=90)
 result=json.loads((out/(quality+'_benchmark.json')).read_text())
 print('BENCHMARK',quality,'exit',run.returncode,'avg',round(result['average_fps'],1),'min',round(result['minimum_fps'],1),flush=True)
 assert run.returncode==0
log=root/'work/logs/release_verified.log'
run=subprocess.run([str(exe),'--log-file',str(log),'--','--qa','--qa-output='+out.as_posix()],cwd=exe.parent,timeout=110)
print('RELEASE_QA_EXIT',run.returncode,flush=True)
assert run.returncode==0
