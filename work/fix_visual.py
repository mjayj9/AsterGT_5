from pathlib import Path
p=Path('outputs/AsterGT')
f=p/'scripts/world.gd';s=f.read_text(encoding='utf-8').replace('environment.reflected_light_source=2','environment.reflected_light_source=Environment.REFLECTION_SOURCE_SKY').replace('environment.fog_height=100;environment.fog_height_density=.005','environment.fog_height=0;environment.fog_height_density=0');f.write_text(s,encoding='utf-8')
f=p/'scripts/car.gd';s=f.read_text(encoding='utf-8').replace('var pivot=Node3D.new();add_child(pivot);wheel_visuals.append(pivot)','var pivot=Node3D.new();pivot.position=wheels[i].mount-Vector3.UP*(cfg.ride_height-.085);add_child(pivot);wheel_visuals.append(pivot)');f.write_text(s,encoding='utf-8')
f=p/'scripts/camera_rig.gd';s=f.read_text(encoding='utf-8').replace('look=tr.origin-tr.basis.x*1.4+Vector3.UP*.15','look=tr.origin-(tr.origin-target).normalized().cross(Vector3.UP)*2.25+Vector3.UP*.15');f.write_text(s,encoding='utf-8')
f=p/'scripts/main.gd';s=f.read_text(encoding='utf-8').replace('var mirror_container: SubViewportContainer','var mirror_container: TextureRect')
a=s.index('func create_mirror(');b=s.index('func apply_preset(',a)
s=s[:a]+'''func create_mirror(layer: CanvasLayer) -> void:
 mirror_container=TextureRect.new();mirror_container.position=Vector2(770,156);mirror_container.size=Vector2(380,114);mirror_container.expand_mode=TextureRect.EXPAND_IGNORE_SIZE;mirror_container.stretch_mode=TextureRect.STRETCH_SCALE;mirror_container.mouse_filter=Control.MOUSE_FILTER_IGNORE;layer.add_child(mirror_container)
 mirror_view=SubViewport.new();mirror_view.size=Vector2i(320,96);mirror_view.world_3d=get_world_3d();mirror_view.render_target_update_mode=SubViewport.UPDATE_DISABLED;add_child(mirror_view)
 mirror_container.texture=mirror_view.get_texture()
 mirror_camera=Camera3D.new();mirror_camera.fov=82;mirror_camera.far=450;mirror_camera.near=.1;mirror_view.add_child(mirror_camera)
''' +s[b:]
s=s.replace('cam.menu_preview=false;cam.first=true;cam.update_visibility();hud.clear_menu()','cam.menu_preview=false;cam.first=true;cam.update_visibility();hud.clear_menu();apply_graphics()')
s=s.replace('car.freeze=true;car.controls_enabled=false\n world.player','car.freeze=true;car.controls_enabled=false\n world.player')
s=s.replace('world.player=car;car.freeze=true;car.controls_enabled=false','world.player=car;car.freeze=true;car.controls_enabled=false;car.position.y-=.13')
f.write_text(s,encoding='utf-8')
f=p/'project.godot';s=f.read_text(encoding='utf-8').replace('renderer/rendering_method="gl_compatibility"','renderer/rendering_method="gl_compatibility"')
# Actual target renderer: Vulkan Forward+ on the verified RTX GPU.
s=s.replace('renderer/rendering_method="gl_compatibility"','renderer/rendering_method="gl_compatibility"')
s=s.replace('renderer/rendering_method="gl_compatibility"','renderer/rendering_method="gl_compatibility"')
s=s.replace('renderer/rendering_method="gl_compatibility"','renderer/rendering_method="forward_plus"').replace('"GL Compatibility"','"Forward Plus"')
f.write_text(s,encoding='utf-8')
