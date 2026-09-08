from pathlib import Path
p=Path('outputs/AsterGT')
(p/'scripts/main.gd').write_text(r'''
extends Node3D
var car: GTCar
var world: GTWorld
var cam: GTCameraRig
var hud: GTHud
var traffic: GTTraffic
var audio: GTAudio
var started: bool=false
var mode: String="Free Drive"
var route_progress: float=0
var challenge_time: float=0
var challenge_text: String=""
var challenge_origin: float=0
var next_gate: float=0
var checkpoint: int=0
var gate: Node3D
var gate_visual: MeshInstance3D
var records={"top_speed":0.0,"zero_to_100":0.0,"time_trial":0.0}
var launch_time: float=-1
var launch_complete: bool=false
var challenge_done: bool=false
var last_route_progress: float=0
var wrong_way: bool=false
var graphics={"preset":2,"scale":1.0,"aa":1,"shadows":175.0,"reflections":1,"vegetation":.8,"traffic":12,"particles":1,"post":true,"mirror":1,"cap":120,"vsync":true,"fullscreen":false,"resolution":2}
var reflection: ReflectionProbe
var rain: CPUParticles3D
var spray: CPUParticles3D
var mirror_view: SubViewport
var mirror_camera: Camera3D
var mirror_container: SubViewportContainer
var runtime: float=0
var qa_mode: String=""
var qa_stage: int=0
var fps_samples: Array[float]=[]
var graphics_applied={}
var invulnerability: float=0
var last_engine_state: bool=true
func _ready() -> void:
 process_mode=Node.PROCESS_MODE_ALWAYS
 GTControls.initialize()
 world=GTWorld.new();world.process_mode=Node.PROCESS_MODE_PAUSABLE;add_child(world)
 car=GTCar.new();car.name="GT500";car.cfg.load_settings();car.transform=world.road_transform(1180,2.8);car.process_mode=Node.PROCESS_MODE_PAUSABLE;add_child(car)
 world.player=car;car.freeze=true;car.controls_enabled=false
 cam=GTCameraRig.new();cam.car=car;add_child(cam)
 var layer=CanvasLayer.new();add_child(layer)
 hud=GTHud.new();hud.game=self;layer.add_child(hud);car.notice.connect(hud.notify)
 audio=GTAudio.new();audio.car=car;audio.process_mode=Node.PROCESS_MODE_PAUSABLE;add_child(audio)
 traffic=GTTraffic.new();traffic.world=world;traffic.car=car;traffic.process_mode=Node.PROCESS_MODE_PAUSABLE;add_child(traffic)
 reflection=ReflectionProbe.new();reflection.size=Vector3(90,35,90);reflection.origin_offset=Vector3(0,2,0);reflection.max_distance=200;reflection.box_projection=false;reflection.update_mode=ReflectionProbe.UPDATE_ONCE;add_child(reflection)
 create_particles();create_mirror(layer);create_gate();load_preferences();apply_graphics();set_paint(car.paint)
 hud.show_home()
 for argument in OS.get_cmdline_user_args():
  if argument.begins_with("--capture="):qa_mode=argument.trim_prefix("--capture=")
  if argument=="--qa":qa_mode="qa"
  if argument.begins_with("--benchmark="):qa_mode=argument.trim_prefix("--benchmark=")+"_benchmark"
 print("ASTER_READY", "  route_km=",world.length/1000,"  vehicle=GT-500")
func _process(dt: float) -> void:
 runtime+=dt
 if not get_tree().paused:world.update_streaming(dt)
 cam.update(minf(dt,.05));audio.interior=cam.mode==3 and not cam.menu_preview
 if mirror_camera and mirror_container.visible:
  mirror_camera.global_transform=cam.camera.global_transform
  mirror_camera.global_position=car.global_position+Vector3.UP*1.25-car.global_basis.z*.25
  mirror_camera.look_at(mirror_camera.global_position+car.global_basis.z*30,Vector3.UP)
 if rain:
  rain.global_position=car.position+Vector3.UP*10;rain.emitting=world.weather==2 and graphics.particles>0 and started and not get_tree().paused
 if spray:
  spray.global_position=car.position+car.global_basis.z*1.3-Vector3.UP*.2
  spray.emitting=car.max_slip>.3 and car.speed_kph>20 and graphics.particles>0 and started and not get_tree().paused
 if not qa_mode.is_empty():run_qa(dt)
func _physics_process(dt: float) -> void:
 if not started or get_tree().paused:return
 route_progress=world.nearest(car.position).along
 invulnerability=maxf(0,invulnerability-dt)
 if car.position.y<world.sample(route_progress).y-18 or car.global_basis.y.dot(Vector3.UP)<.1 and car.speed_kph<8:
  if invulnerability<=0:recover();hud.notify("Recovered to the road")
 if mode!="Free Drive" and not challenge_done:
  if car.speed_kph>1 or challenge_time>0:challenge_time+=dt
  if mode=="High Speed":
   if launch_time<0 and car.throttle>.1:launch_time=challenge_time
   if not launch_complete and car.speed_kph>=100:
    launch_complete=true;var record=challenge_time-launch_time
    if records.zero_to_100<=0 or record<records.zero_to_100:records.zero_to_100=record;save_records()
    hud.notify("0–100 km/h: %.2f s"%record)
   challenge_text="TOP %.0f KM/H  ·  0–100 %s"%[records.top_speed,"%.2f s"%records.zero_to_100 if records.zero_to_100>0 else "—"]
  else:
   var target=world.sample(next_gate)
   if car.position.distance_to(target)<11 and (-car.global_basis.z).dot(world.direction(next_gate))>.1:
    checkpoint+=1;hud.notify("Checkpoint %d / 6"%checkpoint)
    if checkpoint==6:
     challenge_done=true;gate.hide();challenge_text="FINISHED  /  "+format_time(challenge_time)
     if mode=="Time Trial" and (records.time_trial==0 or challenge_time<records.time_trial):records.time_trial=challenge_time;save_records()
    else:next_gate=fposmod(challenge_origin+(checkpoint+1)*500,world.length);place_gate()
   if not challenge_done:
    var remaining=fposmod(next_gate-route_progress,world.length)
    challenge_text="GATE %d / 6  ·  %.0f M"%[checkpoint+1,remaining]
    if mode=="Checkpoints":
     var left=70+checkpoint*27-challenge_time
     challenge_text+="  ·  %ds LEFT"%left
     if left<=0:challenge_done=true;gate.hide();challenge_text="TIME EXPIRED";hud.notify("Time expired — choose a mode to retry")
 if car.speed_kph>records.top_speed:records.top_speed=car.speed_kph
 if int(runtime*10)%100==0:save_records()
func _unhandled_input(event: InputEvent) -> void:
 if not event is InputEventKey or not event.pressed or event.echo:return
 if event.is_action_pressed("pause"):
  if started:
   if get_tree().paused:resume()
   else:pause_game();hud.show_pause()
  else:hud.show_home()
  get_viewport().set_input_as_handled();return
 if event.is_action_pressed("help"):pause_game();hud.show_controls();return
 if event.is_action_pressed("setup"):pause_game();hud.show_setup();return
 if event.is_action_pressed("telemetry"):hud.debug=not hud.debug;return
 if not started or get_tree().paused:return
 if event.is_action_pressed("transmission"):car.toggle_transmission()
 if event.is_action_pressed("shift_up"):car.manual_shift(1)
 if event.is_action_pressed("shift_down"):car.manual_shift(-1)
 for action in {"park":"P","reverse":"R","neutral":"N","drive":"D"}:
  if event.is_action_pressed(action) and car.automatic:car.set_selector({"park":"P","reverse":"R","neutral":"N","drive":"D"}[action])
 if event.is_action_pressed("ignition"):car.engine_on=not car.engine_on;hud.notify("Engine running" if car.engine_on else "Engine off")
 if event.is_action_pressed("recover"):recover()
 if event.is_action_pressed("abs"):car.abs_enabled=not car.abs_enabled;hud.notify("ABS "+("ON" if car.abs_enabled else "OFF"))
 if event.is_action_pressed("tcs"):car.tcs_enabled=not car.tcs_enabled;hud.notify("TCS "+("ON" if car.tcs_enabled else "OFF"))
 if event.is_action_pressed("esc"):car.esc_enabled=not car.esc_enabled;hud.notify("ESC "+("ON" if car.esc_enabled else "OFF"))
 if event.is_action_pressed("assist"):car.auto_clutch=not car.auto_clutch;car.rev_match=car.auto_clutch;hud.notify("Clutch assistance "+("ON" if car.auto_clutch else "OFF"))
 if event.is_action_pressed("lights"):car.headlights=not car.headlights
 if event.is_action_pressed("highbeam"):car.highbeam=not car.highbeam;car.headlights=true
 if event.is_action_pressed("left_signal"):car.indicator=0 if car.indicator==-1 else -1
 if event.is_action_pressed("right_signal"):car.indicator=0 if car.indicator==1 else 1
 if event.is_action_pressed("hazards"):car.hazards=not car.hazards
 if event.is_action_pressed("camera"):cam.cycle();hud.notify(GTCameraRig.NAMES[cam.mode]+" camera")
 if event.is_action_pressed("weather"):world.weather=(world.weather+1)%3;world.update_weather()
 if event.is_action_pressed("time"):world.time_of_day=(world.time_of_day+1)%3;world.update_weather();car.headlights=world.time_of_day==2
func start_drive(selected_mode: String) -> void:
 mode=selected_mode;started=true;get_tree().paused=false;car.controls_enabled=true;car.freeze=false
 cam.menu_preview=false;cam.first=true;cam.update_visibility();hud.clear_menu()
 car.set_selector("D");car.automatic=true;car.engine_on=true
 var start_distance=1180.0
 car.recover(world.road_transform(start_distance,2.8));invulnerability=3
 challenge_time=0;checkpoint=0;challenge_done=false;launch_time=-1;launch_complete=false;challenge_origin=start_distance
 next_gate=start_distance+500;place_gate();gate.visible=mode in ["Time Trial","Checkpoints"]
 traffic.enabled=mode!="High Speed";traffic.set_density(int(graphics.traffic) if traffic.enabled else 0)
 hud.notify("W accelerate  ·  S brake  ·  A / D steer  ·  F1 help")
func pause_game() -> void:
 if started:get_tree().paused=true
 car.controls_enabled=false
func resume() -> void:
 get_tree().paused=false;car.controls_enabled=true;cam.menu_preview=false;cam.update_visibility();hud.clear_menu();save_preferences()
func to_garage() -> void:
 get_tree().paused=false;started=false;car.freeze=true;car.controls_enabled=false;car.linear_velocity=Vector3.ZERO
 car.global_transform=world.road_transform(1180,2.8);cam.menu_preview=true;cam.first=true;cam.update_visibility();gate.hide();hud.show_garage()
func recover() -> void:
 var near=world.nearest(car.position,true);var chosen=near.along
 for item in traffic.cars:
  if item.body.position.distance_to(world.sample(chosen))<15:chosen-=22
 car.recover(world.road_transform(chosen,2.8));invulnerability=4;cam.first=true
func create_gate() -> void:
 gate=Node3D.new();add_child(gate)
 var m=world.mat(Color("9cdbc0"),.3);m.emission_enabled=true;m.emission=Color("598c71");m.emission_energy_multiplier=.8
 for side in [-1,1]:world.box(gate,Vector3(side*5.1,2.6,0),Vector3(.16,5.2,.16),m)
 world.box(gate,Vector3(0,5.15,0),Vector3(10.3,.16,.16),m)
 var label=Label3D.new();label.text="CHECKPOINT";label.position=Vector3(0,5.8,0);label.font_size=64;label.pixel_size=.012;gate.add_child(label);gate.hide()
func place_gate() -> void:
 gate.transform=world.road_transform(next_gate,0);gate.position.y-=.8
func create_particles() -> void:
 rain=CPUParticles3D.new();rain.amount=700;rain.lifetime=1.2;rain.emission_shape=CPUParticles3D.EMISSION_SHAPE_BOX;rain.emission_box_extents=Vector3(17,2,17)
 rain.direction=Vector3(-.1,-1,0);rain.spread=2;rain.initial_velocity_min=18;rain.initial_velocity_max=26;rain.gravity=Vector3(0,-5,0);rain.local_coords=false
 var mesh=BoxMesh.new();mesh.size=Vector3(.012,.40,.012);rain.mesh=mesh
 var m=world.mat(Color(.67,.80,.90,.4));m.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA;m.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED;rain.material_override=m;add_child(rain);rain.emitting=false
 spray=CPUParticles3D.new();spray.amount=110;spray.lifetime=.8;spray.emission_shape=CPUParticles3D.EMISSION_SHAPE_BOX;spray.emission_box_extents=Vector3(.9,.05,.2);spray.direction=Vector3(0,1,1);spray.spread=40;spray.initial_velocity_min=1;spray.initial_velocity_max=3;spray.gravity=Vector3(0,.3,0);spray.local_coords=false
 var sphere=SphereMesh.new();sphere.radius=.06;sphere.height=.12;spray.mesh=sphere
 var smoke=world.mat(Color(.65,.69,.67,.22));smoke.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA;spray.material_override=smoke;add_child(spray);spray.emitting=false
func create_mirror(layer: CanvasLayer) -> void:
 mirror_container=SubViewportContainer.new();mirror_container.position=Vector2(770,156);mirror_container.size=Vector2(380,114);mirror_container.stretch=true;mirror_container.mouse_filter=Control.MOUSE_FILTER_IGNORE;layer.add_child(mirror_container)
 mirror_view=SubViewport.new();mirror_view.size=Vector2i(320,96);mirror_view.world_3d=get_world_3d();mirror_view.render_target_update_mode=SubViewport.UPDATE_ALWAYS;mirror_container.add_child(mirror_view)
 mirror_camera=Camera3D.new();mirror_camera.fov=82;mirror_camera.far=450;mirror_camera.near=.1;mirror_view.add_child(mirror_camera)
func apply_preset(i: int) -> void:
 graphics.preset=i;graphics.scale=[.70,.85,1.0,1.15][i];graphics.aa=[0,1,1,2][i];graphics.shadows=[0.0,100.0,175.0,300.0][i]
 graphics.reflections=[0,0,1,2][i];graphics.vegetation=[.25,.5,.8,1.25][i];graphics.traffic=[4,8,12,24][i];graphics.particles=[0,1,1,2][i];graphics.post=i>1;graphics.mirror=[0,0,1,2][i];apply_graphics()
func apply_graphics() -> void:
 get_viewport().scaling_3d_scale=clampf(graphics.scale,.5,1.5)
 get_viewport().msaa_3d=clampi(graphics.aa,0,3)
 world.sun.shadow_enabled=graphics.shadows>0;world.sun.directional_shadow_max_distance=maxf(25,graphics.shadows)
 world.environment.glow_enabled=graphics.post;world.environment.glow_intensity=.28
 world.environment.ssao_enabled=graphics.post;world.environment.ssao_radius=1.2;world.environment.ssao_intensity=.7
 world.environment.ssr_enabled=graphics.reflections>=2
 reflection.visible=graphics.reflections>0;reflection.position=car.position
 world.render_distance=[650.0,800.0,1000.0,1400.0][clampi(graphics.preset,0,3)]
 if graphics_applied.get("vegetation",-1)!=graphics.vegetation:world.set_density(graphics.vegetation)
 if graphics_applied.get("traffic",-1)!=graphics.traffic:traffic.set_density(int(graphics.traffic))
 rain.amount=1400 if graphics.particles==2 else 500
 mirror_container.visible=graphics.mirror>0 and started
 mirror_view.render_target_update_mode=SubViewport.UPDATE_ALWAYS if mirror_container.visible else SubViewport.UPDATE_DISABLED
 mirror_view.size=Vector2i(640,192) if graphics.mirror==2 else Vector2i(320,96)
 Engine.max_fps=graphics.cap
 DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED if graphics.vsync else DisplayServer.VSYNC_DISABLED)
 if DisplayServer.get_name()!="headless":
  if graphics_applied.get("fullscreen",null)!=graphics.fullscreen:DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN if graphics.fullscreen else DisplayServer.WINDOW_MODE_WINDOWED)
  if not graphics.fullscreen and graphics_applied.get("resolution",-1)!=graphics.resolution:
   DisplayServer.window_set_size([Vector2i(1280,720),Vector2i(1600,900),Vector2i(1920,1080),Vector2i(2560,1440)][clampi(graphics.resolution,0,3)])
 graphics_applied=graphics.duplicate()
func set_paint(color: Color) -> void:
 car.paint=color
 for node in car.body_visual.find_children("*","MeshInstance3D",true,false):
  for surface in range(node.mesh.get_surface_count()):
   var old=node.mesh.surface_get_material(surface)
   if old and "Paint" in old.resource_name:
    var m=old.duplicate();m.albedo_color=color;m.metallic=.68;m.roughness=.26
    m.normal_enabled=true;m.normal_texture=load("res://assets/paint_normal.png");m.normal_scale=.08
    node.set_surface_override_material(surface,m)
func power_hp() -> float:
 var peak=0.0
 for point in car.cfg.torque_curve:peak=maxf(peak,car.cfg.torque_at(point.x)*point.x/7127.0)
 return peak
func gear_max_speed(gear_no: int) -> float:return car.cfg.max_rpm/car.cfg.gear_ratios[gear_no-1]/car.cfg.final_drive*TAU*car.cfg.wheel_radius/60*3.6
func format_time(seconds: float) -> String:return "%02d:%05.2f"%[int(seconds/60),fmod(seconds,60)]
func save_records() -> void:
 var file=FileAccess.open("user://records.json",FileAccess.WRITE);if file:file.store_string(JSON.stringify(records))
func save_preferences() -> void:
 var d={"graphics":graphics,"mph":hud.use_mph,"mute":audio.muted,"paint":[car.paint.r,car.paint.g,car.paint.b]}
 var file=FileAccess.open("user://preferences.json",FileAccess.WRITE);if file:file.store_string(JSON.stringify(d))
 car.cfg.save_settings()
func load_preferences() -> void:
 if FileAccess.file_exists("user://records.json"):
  var d=JSON.parse_string(FileAccess.get_file_as_string("user://records.json"))
  if d is Dictionary:
   for k in records:
    if d.get(k) is float and is_finite(d[k]):records[k]=clampf(d[k],0,10000)
 if not FileAccess.file_exists("user://preferences.json"):return
 var d=JSON.parse_string(FileAccess.get_file_as_string("user://preferences.json"))
 if not d is Dictionary:return
 if d.get("graphics") is Dictionary:
  var g=d.graphics
  var ranges={"preset":[0,3],"scale":[.5,1.5],"aa":[0,3],"shadows":[0,350],"reflections":[0,2],"vegetation":[.1,1.5],"traffic":[0,36],"particles":[0,2],"mirror":[0,2],"cap":[0,240],"resolution":[0,3]}
  for k in ranges:
   if g.get(k) is float and is_finite(g[k]):
    var v=clampf(g[k],ranges[k][0],ranges[k][1]);graphics[k]=v if k in ["scale","shadows","vegetation"] else int(v)
  for k in ["post","vsync","fullscreen"]:
   if g.get(k) is bool:graphics[k]=g[k]
 if d.get("mph") is bool:hud.use_mph=d.mph
 if d.get("mute") is bool:audio.muted=d.mute
 if d.get("paint") is Array and d.paint.size()==3:
  if d.paint[0] is float and d.paint[1] is float and d.paint[2] is float:set_paint(Color(clampf(d.paint[0],0,1),clampf(d.paint[1],0,1),clampf(d.paint[2],0,1)))
func capture(label: String) -> void:
 if DisplayServer.get_name()=="headless":return
 await RenderingServer.frame_post_draw
 var image=get_viewport().get_texture().get_image();image.save_png("res://tests/"+label+".png")
 print("CAPTURED ",label)
func run_qa(dt: float) -> void:
 if qa_mode.ends_with("_benchmark"):
  if qa_stage==0 and runtime>2:
   apply_preset(["Low","Medium","High","Ultra"].find(qa_mode.trim_suffix("_benchmark")));graphics.vsync=false;graphics.cap=0;apply_graphics();start_drive("Free Drive");car.test_input={"throttle":.45};qa_stage=1;runtime=0
  if qa_stage==1 and runtime>5:fps_samples.append(1/maxf(dt,.0001))
  if qa_stage==1 and runtime>17:
   var sum=0.0
   for f in fps_samples:sum+=f
   var result={"preset":qa_mode,"resolution":"1920x1080","average_fps":sum/fps_samples.size(),"minimum_fps":fps_samples.min(),"frames":fps_samples.size(),"renderer":RenderingServer.get_current_rendering_method(),"adapter":RenderingServer.get_video_adapter_name()}
   var file=FileAccess.open("res://tests/"+qa_mode+".json",FileAccess.WRITE);file.store_string(JSON.stringify(result,"  "));print(result);get_tree().quit()
  return
 if qa_mode=="qa":
  if qa_stage==0 and runtime>4:capture("01_garage");qa_stage=1;runtime=0
  elif qa_stage==1 and runtime>1:start_drive("Free Drive");car.test_input={"throttle":.60};qa_stage=2;runtime=0
  elif qa_stage==2 and runtime>7:capture("02_driving");qa_stage=3;runtime=0;car.test_input={"brake":1.0}
  elif qa_stage==3 and runtime>3:cam.mode=2;cam.first=true;capture("03_hood");qa_stage=4;runtime=0
  elif qa_stage==4 and runtime>1:cam.mode=3;cam.first=true;cam.update_visibility();capture("04_cockpit");qa_stage=5;runtime=0
  elif qa_stage==5 and runtime>1:cam.mode=4;cam.first=true;cam.update_visibility();world.weather=2;world.time_of_day=2;world.update_weather();car.headlights=true;qa_stage=6;runtime=0
  elif qa_stage==6 and runtime>2:capture("05_rain_night");pause_game();hud.show_setup();qa_stage=7;runtime=0
  elif qa_stage==7 and runtime>1:capture("06_setup");qa_stage=8;runtime=0
  elif qa_stage==8 and runtime>1:
   print("QA_COMPLETE ",car.telemetry());get_tree().quit()
 else:
  if qa_stage==0 and runtime>4:
   if qa_mode=="drive":start_drive("Free Drive");car.test_input={"throttle":.5}
   if qa_mode=="side":start_drive("Free Drive");cam.mode=4;cam.orbit_yaw=PI/2;car.test_input={"brake":1.0}
   if qa_mode=="garage":hud.show_home()
   qa_stage=1;runtime=0
  if qa_stage==1 and runtime>3:capture(qa_mode);qa_stage=2;runtime=0
  if qa_stage==2 and runtime>1:get_tree().quit()
'''.strip()+'\n',encoding='utf-8')
s=(p/'project.godot').read_text().replace('"GL Compatibility"','"Forward Plus"').replace('renderer/rendering_method="gl_compatibility"','renderer/rendering_method="gl_compatibility"')
# The compatibility renderer is used for initial smoke; final renderer chosen after GPU test.
(p/'project.godot').write_text(s)
# Preserve the repeatable Blender production source in the deliverable.
import shutil
shutil.copy('work/build_models.py',p/'blender'/'build_models.py')
print('Main scene connected')
