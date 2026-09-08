from pathlib import Path
p=Path('outputs/AsterGT')
f=p/'scripts/camera_rig.gd';s=f.read_text(encoding='utf-8').replace('Vector3(-.38,.70,.48)','Vector3(-.38,.80,.22)').replace('if "Windshield" in node.name or "Roof" in node.name:','if "Windshield" in node.name or "Roof" in node.name or "SideWindow" in node.name or "RearGlass" in node.name:');f.write_text(s,encoding='utf-8')
f=p/'scripts/car.gd';s=f.read_text(encoding='utf-8').replace('lamp.spot_angle=24;lamp.light_energy=3;','lamp.spot_angle=30;lamp.rotation_degrees.x=-4;lamp.light_energy=8;').replace('light_nodes[k].light_energy=5 if highbeam else 3','light_nodes[k].light_energy=14 if highbeam else 8');f.write_text(s,encoding='utf-8')
f=p/'scripts/main.gd';s=f.read_text(encoding='utf-8').replace('car.global_position+Vector3.UP*1.25-car.global_basis.z*.25','car.global_position+Vector3.UP*1.15+car.global_basis.z*2.45')
s=s.replace('get_tree().quit()','finish()')
s+='''
func finish() -> void:
 set_process(false);set_physics_process(false)
 get_tree().paused=false
 mirror_container.texture=null
 for node in get_children():node.queue_free()
 await get_tree().process_frame
 await get_tree().process_frame
 await get_tree().process_frame
 get_tree().quit()
'''
s=s.replace('world.environment.ssao_enabled=graphics.post','world.environment.ssao_enabled=graphics.post and RenderingServer.get_current_rendering_method()=="forward_plus"').replace('world.environment.ssr_enabled=graphics.reflections>=2','world.environment.ssr_enabled=graphics.reflections>=2 and RenderingServer.get_current_rendering_method()=="forward_plus"')
f.write_text(s,encoding='utf-8')
f=p/'scripts/hud.gd';s=f.read_text(encoding='utf-8').replace('game.get_tree().quit()','game.finish()');f.write_text(s,encoding='utf-8')
