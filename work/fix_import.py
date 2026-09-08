from pathlib import Path
p=Path('outputs/AsterGT')
f=p/'scripts/world.gd';s=f.read_text(encoding='utf-8').replace('Environment.REFLECTED_SOURCE_SKY','Environment.REFLECTED_LIGHT_SOURCE_SKY');f.write_text(s,encoding='utf-8')
(p/'blender'/'.gdignore').write_text('')
import shutil
shutil.copy('work/build_models.py',p/'blender'/'build_models.py')
s=(p/'project.godot').read_text(encoding='utf-8').replace('renderer/rendering_method="gl_compatibility"','renderer/rendering_method="gl_compatibility"')
(p/'project.godot').write_text(s,encoding='utf-8')
