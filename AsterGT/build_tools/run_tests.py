"""Run the supplied Godot vehicle tests and retain logs/results."""
from pathlib import Path
import argparse, json, shutil, subprocess
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--godot', default=shutil.which('godot') or shutil.which('godot4'))
p.add_argument('--compare-frame-rates', action='store_true')
p.add_argument('--full-route', action='store_true', help='Also drive full dry and wet loops without teleporting')
a = p.parse_args()
if not a.godot:
    p.error('Pass --godot with a Godot 4.6.3 executable path.')
logs = ROOT / 'tests' / 'logs'
logs.mkdir(exist_ok=True)
def run(name, args):
    with (logs / (name + '.log')).open('w', encoding='utf-8') as out:
        result = subprocess.run([a.godot, '--headless', '--path', str(ROOT), *args],
                                stdout=out, stderr=subprocess.STDOUT, timeout=600)
    if result.returncode:
        raise SystemExit(f'{name} failed ({result.returncode}); see {logs}')
def check(name):
    data = json.loads((ROOT / 'tests' / (name + '_results.json')).read_text(encoding='utf-8-sig'))
    failed = [key for key, passed in data['checks'].items() if not passed]
    print(f"{name}: {len(data['checks']) - len(failed)} / {len(data['checks'])} passed", flush=True)
    if failed:
        raise SystemExit('Failed: ' + ', '.join(failed))
    return data
run('import', ['--editor', '--import', '--quit'])
for name in ['physics', 'dynamics', 'integration', 'upgrade']:
    run(name, ['--fixed-fps', '60', '--script', f'res://tests/{name}_test.gd', '--', '--test-profile'])
    check(name)
if a.compare_frame_rates:
    values = []
    for fps in [30, 60, 120]:
        run(f'physics_{fps}', ['--fixed-fps', str(fps), '--script', 'res://tests/physics_test.gd', '--', '--test-profile'])
        result = check('physics')
        shutil.copy2(ROOT / 'tests/physics_results.json', ROOT / f'tests/physics_{fps}.json')
        values.append([result['zero_to_100_s'], result['100_to_0_distance_m']])
    for i in range(2):
        assert max(v[i] for v in values) - min(v[i] for v in values) < 0.01
    print('30 / 60 / 120 render step comparison passed')
if a.full_route:
    for wet in [False, True]:
        name = 'continuous_route_wet' if wet else 'continuous_route'
        extra = ['--wet'] if wet else []
        run(name, ['--fixed-fps', '60', '--script', 'res://tests/continuous_route_test.gd', '--', '--test-profile', *extra])
        check(name)
print('All tests passed. Logs:', logs)
