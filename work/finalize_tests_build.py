from pathlib import Path
p=Path('outputs/AsterGT')
f=p/'tests/physics_test.gd';s=f.read_text(encoding='utf-8')
s=s.replace('phase="decelerate";car.test_input={"throttle":0.0,"brake":1.0};elapsed=0','''phase="brake_setup";car.test_input={"brake":1.0};car.recover(Transform3D(Basis.IDENTITY,Vector3(0,.8,0)));elapsed=0''')
a=s.index('  "decelerate":');b=s.index('  "brake":',a)
s=s[:a]+'''  "brake_setup":
   if elapsed>1.5:
    car.linear_velocity=Vector3(0,0,-100.0/3.6)
    for w in car.wheels:w.omega=100.0/3.6/car.cfg.wheel_radius
    car.gear=3;car.rpm=100.0/3.6/car.cfg.wheel_radius*car.get_ratio()*60/TAU
    car.brake=0;car.throttle=0;car.test_input={"brake":1.0}
    brake_start_z=car.position.z;phase="brake";elapsed=0
    metrics["brake_start_speed_kph"]=100.0
''' +s[b:]
s=s.replace('if car.speed_kph<0.5:\n    metrics["100_to_0_distance_m"]','if elapsed>.05 and car.speed_kph<0.5:\n    metrics.checks["automatic_downshift"]=car.gear<3\n    metrics["100_to_0_distance_m"]')
f.write_text(s,encoding='utf-8')
f=p/'scripts/hud.gd';s=f.read_text(encoding='utf-8').replace('4.40','4.50');f.write_text(s,encoding='utf-8')
(p/'build_tools/build_windows.py').write_text('''"""Build the standalone Windows executable with a pinned Godot release template."""
from pathlib import Path
import argparse, subprocess, shutil, runpy
ROOT=Path(__file__).resolve().parents[1]
args=argparse.ArgumentParser()
args.add_argument('--godot',default=shutil.which('godot') or shutil.which('godot4'))
options=args.parse_args()
if not options.godot:raise SystemExit('Pass --godot with the Godot 4.6.3 executable path.')
template=ROOT/'build_tools/templates/windows_release_x86_64.exe'
if not template.exists():runpy.run_path(str(ROOT/'build_tools/fetch_template.py'),run_name='__main__')
preset=ROOT/'export_presets.cfg';original=preset.read_bytes()
output=ROOT.parent/'Windows'/'AsterGT.exe';output.parent.mkdir(exist_ok=True)
try:
    text=original.decode('utf-8-sig').replace('custom_template/release=""','custom_template/release="'+template.as_posix()+'"')
    preset.write_text(text,encoding='utf-8')
    subprocess.run([options.godot,'--headless','--path',str(ROOT),'--editor','--import','--quit'],check=True)
    subprocess.run([options.godot,'--headless','--path',str(ROOT),'--export-release','Windows Desktop',str(output)],check=True)
finally:
    preset.write_bytes(original)
print(output)
''',encoding='utf-8')
# Reuse the already verified official template for this build.
import shutil
(p/'build_tools/templates').mkdir(exist_ok=True)
shutil.copy('work/tools/windows_release_x86_64.exe',p/'build_tools/templates/windows_release_x86_64.exe')
