from pathlib import Path
p=Path(r'C:/Users/admin/Documents/Codex/2026-09-08/fable-5-1-vs-fable-at-4/outputs/AsterGT')
f=p/'scripts/main.gd';s=f.read_text(encoding='utf8')
s=s.replace('arg=="--test-profile"','arg=="--test-profile" or arg=="--v4-smoke"')
s=s.replace(' print("ASTER_READY",',' if "--v4-smoke" in OS.get_cmdline_user_args():call_deferred("finish")\n print("ASTER_READY",')
f.write_text(s,encoding='utf8')
f=p/'scripts/traffic.gd';s=f.read_text(encoding='utf8').replace('preload("res://assets/v4/traffic_lod0.glb")','preload("res://assets/v4/traffic_lod1.glb")');f.write_text(s,encoding='utf8')
f=p/'export_presets.cfg';s=f.read_text(encoding='utf8').replace('config/*.json"','config/*.json,runtime_tools/*.exe"');f.write_text(s,encoding='utf8')
(p/'runtime_tools').mkdir(exist_ok=True)
