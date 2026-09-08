from pathlib import Path
p=Path('outputs/AsterGT')
def edit(name,fn):f=p/name;f.write_text(fn(f.read_text(encoding='utf-8')),encoding='utf-8')
edit('scripts/world.gd',lambda s:s.replace('Vector3(0,0,-1800),Vector3(350,18,-2800),Vector3(1400,65,-3200),Vector3(2500,135,-2600)','Vector3(0,0,-1800),Vector3(0,0,-3500),Vector3(350,18,-4200),Vector3(1400,65,-4400),Vector3(2500,135,-3600)').replace('environment.fog_density=.00055;','environment.fog_sky_affect=.12;environment.fog_density=.00055;').replace('sky_material.sky_curve=.18','sky_material.sky_curve=.40').replace('Color("567f9a")','Color("416d8d")'))
edit('scripts/car.gd',lambda s:s.replace('var cfg = VehicleConfig.new()','var cfg = preload("res://config/street.tres").duplicate()').replace('var chassis_base_y: float=0','var chassis_base_y: float=0\nvar visual_lamps: Array[Dictionary]=[]\nvar steering_wheel: Node3D\nvar calipers: Array[Node3D]=[]').replace(' build_visuals()',' build_visuals()\n cache_details()').replace('var coupled_rpm=maxf(cfg.idle_rpm,axle_rpm)','var coupled_rpm=maxf(cfg.idle_rpm if automatic or auto_clutch else 350,axle_rpm)').replace('var torque=cfg.torque_at(rpm)*effective_throttle','var torque=cfg.torque_at(rpm)*effective_throttle\n if not automatic and not auto_clutch:torque*=clampf(rpm/cfg.idle_rpm,.3,1.0)').replace('wheel_visuals[i].rotation=Vector3(-w.spin,steer_angle if i<2 else 0,0)','wheel_visuals[i].rotation=Vector3(-w.spin,steer_angle if i<2 else 0,0)\n  if calipers.size()>i:\n   calipers[i].position=wheel_visuals[i].position\n   calipers[i].rotation.y=steer_angle if i<2 else 0').replace('func _process(_delta: float) -> void:\n for k in light_nodes: light_nodes[k].visible=headlights;light_nodes[k].spot_range=120 if highbeam else 65','''func _process(_delta: float) -> void:
 for k in light_nodes:
  light_nodes[k].visible=headlights;light_nodes[k].spot_range=120 if highbeam else 65
  light_nodes[k].light_energy=5 if highbeam else 3
 if steering_wheel:steering_wheel.rotation.z=steering*.75
 for item in visual_lamps:
  var intensity=.04
  if item.kind=="head":intensity=2.0 if headlights else .6
  if item.kind=="tail":intensity=4.0 if brake>.08 else (.7 if headlights else .16)
  if item.kind=="signal":intensity=2.2 if fmod(simulation_time,1)<.5 and (hazards or indicator==item.side) else .02
  item.material.emission_energy_multiplier=intensity
func cache_details() -> void:
 var model=body_visual
 steering_wheel=Node3D.new();body_visual.add_child(steering_wheel);steering_wheel.position=Vector3(-.38,.49,-.33)
 for node in model.find_children("*","MeshInstance3D",true,false):
  if node.name.begins_with("Steering"):
   node.reparent(steering_wheel,true)
  var kind=""
  if node.name.begins_with("Headlight_"):kind="head"
  if node.name.begins_with("Taillight_"):kind="tail"
  if "Signal_" in node.name:kind="signal"
  if kind!="":
   var original=node.mesh.surface_get_material(0)
   if original is StandardMaterial3D:
    var material=original.duplicate();node.material_override=material;material.emission_enabled=true
    visual_lamps.append({"material":material,"kind":kind,"side":-1 if "-1" in str(node.name) else 1})
 for i in range(4):
  for node in wheel_visuals[i].find_children("*","MeshInstance3D",true,false):
   if "BrakeCaliper" in node.name:node.hide()
  var pivot=Node3D.new();add_child(pivot);calipers.append(pivot)
  var node=MeshInstance3D.new();var mesh=BoxMesh.new();mesh.size=Vector3(.04,.13,.08);node.mesh=mesh
  var m=StandardMaterial3D.new();m.albedo_color=Color("bb6338");m.metallic=.5;node.material_override=m
  node.position=Vector3(-.15 if i%2==0 else .15,0,.17);pivot.add_child(node);pivot.position=wheel_visuals[i].position
'''))
# Put real dashboard in cockpit rather than an unobstructed duplicate hood view.
edit('scripts/camera_rig.gd',lambda s:s.replace('Vector3(-.38,.74,-.05)','Vector3(-.38,.70,.48)').replace('var look: Vector3','var look: Vector3'))
# Don't overlay mirror on menus. Isolate screenshot states across render frames.
edit('scripts/main.gd',lambda s:s.replace('if mirror_camera and mirror_container.visible:', '''mirror_container.visible=graphics.mirror>0 and started and hud.page==""
 mirror_view.render_target_update_mode=SubViewport.UPDATE_ALWAYS if mirror_container.visible else SubViewport.UPDATE_DISABLED
 if mirror_camera and mirror_container.visible:'''))
f=p/'scripts/main.gd';s=f.read_text(encoding='utf-8');a=s.index(' if qa_mode=="qa":');b=s.index('\n else:\n  if qa_stage==0',a)
s=s[:a]+''' if qa_mode=="qa":
  if runtime<1.2:return
  runtime=0
  match qa_stage:
   0:
    if world.active_tiles.size()<25:return
    capture("01_garage")
   1:start_drive("Free Drive");car.test_input={"throttle":.6};runtime=-5
   2:capture("02_driving");car.test_input={"brake":1.0};runtime=-2
   3:cam.mode=1;cam.first=true;cam.update_visibility()
   4:capture("03_bumper")
   5:cam.mode=2;cam.first=true;cam.update_visibility()
   6:capture("04_hood")
   7:cam.mode=3;cam.first=true;cam.update_visibility()
   8:capture("05_cockpit")
   9:cam.mode=4;cam.first=true;cam.update_visibility();world.weather=2;world.time_of_day=2;world.update_weather();car.headlights=true
   10:capture("06_rain_night")
   11:pause_game();hud.show_setup()
   12:capture("07_setup")
   13:hud.show_graphics()
   14:capture("08_graphics")
   15:print("QA_COMPLETE ",car.telemetry());get_tree().quit()
  qa_stage+=1''' +s[b:];f.write_text(s,encoding='utf-8')
