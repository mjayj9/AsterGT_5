from pathlib import Path
p=Path('outputs/AsterGT')
(p/'export_presets.cfg').write_text('''[preset.0]
name="Windows Desktop"
platform="Windows Desktop"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter="tests/*,docs/*,blender/*,build_tools/*,*.md"
export_path="../Windows/AsterGT.exe"
script_export_mode=2
[preset.0.options]
custom_template/debug=""
custom_template/release=""
binary_format/embed_pck=true
binary_format/architecture="x86_64"
texture_format/s3tc_bptc=true
texture_format/etc2_astc=false
application/modify_resources=false
codesign/enable=false
''',encoding='utf-8')
(p/'icon.svg').write_text('''<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256"><rect width="256" height="256" rx="48" fill="#132b2d"/><path d="M42 197L109 51h38l67 146h-39l-17-40H96l-17 40zM109 125h36l-18-45z" fill="#96d3b0"/><path d="M120 167h15v20h-15zm0 33h15v19h-15z" fill="#ecb481"/></svg>''',encoding='utf-8')
f=p/'project.godot';s=f.read_text(encoding='utf-8-sig').replace('config/features=', 'config/icon="res://icon.svg"\nconfig/features=');f.write_text(s,encoding='utf-8')
f=p/'blender/build_models.py';s=f.read_text(encoding='utf-8').replace("ROOT=Path(__file__).resolve().parents[1]/'outputs'/'AsterGT'","ROOT=Path(__file__).resolve().parents[1]");f.write_text(s,encoding='utf-8')
f=p/'scripts/main.gd';s=f.read_text(encoding='utf-8').replace('4.29','4.40');f.write_text(s,encoding='utf-8')
f=p/'scripts/hud.gd';s=f.read_text(encoding='utf-8').replace('4.29','4.40');f.write_text(s,encoding='utf-8')
f=p/'scripts/traffic.gd';s=f.read_text(encoding='utf-8').replace('tr.origin.y-=.09','tr.origin.y-=.19');f.write_text(s,encoding='utf-8')
(p/'build_tools').mkdir(exist_ok=True)
asset_source=Path('work/create_world.py').read_text(encoding='utf-8-sig').split("write('scripts/controls.gd'")[0]
asset_source=asset_source.replace("p=Path('outputs/AsterGT')","p=Path(__file__).resolve().parents[1]")
asset_source+="\nimport shutil\nshutil.copy(p/'assets/wind.wav',p/'assets/roll.wav')\n"
(p/'build_tools/generate_audio_textures.py').write_text(asset_source,encoding='utf-8')
(p/'build_tools/fetch_template.py').write_text(Path('work/fetch_template.py').read_text(encoding='utf-8-sig').replace("folder=Path('work/tools')","folder=Path(__file__).resolve().parent/'templates'"),encoding='utf-8')
(p/'build_tools/.gdignore').write_text('')
(p/'licenses').mkdir(exist_ok=True)
print('Release preset and reproducible source tools prepared')
