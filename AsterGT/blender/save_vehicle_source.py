import bpy
from pathlib import Path
root=Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(root/'assets/porsche_992_gt3_r.glb'))
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(root/'blender/porsche_992_gt3_r_rigged.blend'))
