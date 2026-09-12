import subprocess,os,pathlib,sys,time
r=pathlib.Path(__file__).resolve().parents[1];p=r/'outputs/AsterGT'
env=os.environ.copy();env['APPDATA']=str(r/('work/v5-test-user-'+str(time.time_ns())));pathlib.Path(env['APPDATA']).mkdir(exist_ok=True)
exe=r'C:\Tools\Godot\4.6.3-dotnet\Godot_v4.6.3-stable_mono_win64\Godot_v4.6.3-stable_mono_win64_console.exe'
name=sys.argv[1] if len(sys.argv)>1 else 'v5_regression'
cmd=[exe,'--path',str(p),'--script',f'res://tests/{name}.gd','--log-file',str(r/f'work/{name}.log')]
if '--render' not in sys.argv:cmd+=['--headless']
cmd+=['--','--test-profile']
cp=subprocess.run(cmd,env=env,timeout=180)
raise SystemExit(cp.returncode)
