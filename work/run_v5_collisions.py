from pathlib import Path
import json,subprocess,os,math
r=Path(__file__).resolve().parents[1];p=r/'outputs/AsterGT';out=r/'work/v5-collisions';out.mkdir(exist_ok=True)
source=r.parent/'fable-5-1-vs-fable-at-4-pre-qa-gate-work/qa-gate/collision_gate.gd'
s=source.read_text(encoding='utf-8').replace('# QA fixture only. Production classes are instantiated unchanged. No InputEvent','# v5 development regression fixture. Production v5 classes. No InputEvent')
s=s.replace('"C2": intended_a_kph=100; mass_b=1580','"D1": intended_a_kph=30; mass_b=1200; target_basis=Basis(Vector3.UP,deg_to_rad(30))\n  "C2": intended_a_kph=100; mass_b=1580')
s=s.replace('condition in ["C3","C5"]','condition in ["D1","C3","C5"]')
s=s.replace(' d["id"]=body.get_instance_id();',' d["local_damage_patches"]=body.damage.visuals.patches.duplicate(true)\n d["id"]=body.get_instance_id();')
(p/'tests/v5_collision.gd').write_text(s,encoding='utf-8')
exe=r'C:\Tools\Godot\4.6.3-dotnet\Godot_v4.6.3-stable_mono_win64\Godot_v4.6.3-stable_mono_win64_console.exe'
summary=[]
for condition in ['C1','D1','C3','C4']:
 path=out/(condition+'.jsonl');log=out/(condition+'.log')
 cmd=[exe,'--headless','--path',str(p),'--script','res://tests/v5_collision.gd','--log-file',str(log),'--','--condition='+condition,'--output='+str(path)]
 env=os.environ.copy();env['APPDATA']=str(out/'profile');Path(env['APPDATA']).mkdir(exist_ok=True)
 cp=subprocess.run(cmd,env=env,timeout=50,capture_output=True,text=True,encoding='utf-8',errors='replace')
 rows=[json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
 states=[x['data'] for x in rows if x['kind']=='state'];end=next(x['data'] for x in rows if x['kind']=='fixture_end')
 pair={int(end['a']['id']),int(end['b']['id'])}
 events=[x['data'] for x in rows if x['kind']=='production_contact' and {int(x['data']['self_id']),int(x['data']['other_id'])}==pair]
 record={'condition':condition,'exit':cp.returncode,'pair_events':len(events),'sources':sorted(set(x.get('energy_source','') for x in events)),'a_patches':len(end['a']['local_damage_patches']),'b_patches':len(end['b']['local_damage_patches']),'a_damage':end['a']['damage'],'b_damage':end['b']['damage'],'max_radius_m':max([float(x['radius']) for b in ['a','b'] for x in end[b]['local_damage_patches']]+[0]),'max_depth_m':max([float(x['depth']) for b in ['a','b'] for x in end[b]['local_damage_patches']]+[0]),'target_recovery':any(x['b'].get('mode')=='Recovery' for x in states),'finite':all(math.isfinite(float(v)) for x in states for b in ['a','b'] for v in x[b]['position_world_m']),'errors':[ln for ln in cp.stderr.splitlines() if 'ERROR' in ln]}
 record['status']='PASS' if cp.returncode==0 and len(events)>0 and record['a_patches']>0 and record['b_patches']>0 and record['finite'] and not record['errors'] else 'FAIL'
 summary.append(record);print(json.dumps(record,ensure_ascii=False),flush=True)
(out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
raise SystemExit(0 if all(x['status']=='PASS' for x in summary) else 1)
