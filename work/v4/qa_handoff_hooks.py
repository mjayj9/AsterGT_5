from pathlib import Path
p=Path(r'C:/Users/admin/Documents/Codex/2026-09-08/fable-5-1-vs-fable-at-4/outputs/AsterGT')
f=p/'scripts/driving_ui.gd';s=f.read_text(encoding='utf8')
s=s.replace('var capture_panel: Control','var capture_panel: Control\nvar mouse_menu: Button')
s=s.replace('func tr2(','''func _ready() -> void:
 super._ready()
 mouse_menu=Button.new();mouse_menu.text="메뉴";mouse_menu.focus_mode=Control.FOCUS_NONE;add_child(mouse_menu)
 mouse_menu.anchor_left=1;mouse_menu.anchor_right=1;mouse_menu.offset_left=-150;mouse_menu.offset_right=-40;mouse_menu.offset_top=138;mouse_menu.offset_bottom=183
 mouse_menu.pressed.connect(func():game.pause_game();show_pause())
func tr2(''')
s=s.replace(' super._process(dt)',' super._process(dt)\n mouse_menu.visible=game.started and page=="";mouse_menu.text=tr2("메뉴","Menu")')
s=s.replace(' rebind_action=a;slot_index=index;',' if DisplayServer.get_name()!="headless":DisplayServer.window_set_ime_active(false)\n rebind_action=a;slot_index=index;')
s=s.replace('func cancel_capture() -> void:\n','func cancel_capture() -> void:\n if DisplayServer.get_name()!="headless":DisplayServer.window_set_ime_active(true)\n')
s=s.replace(' var base=VehicleConfig.new()',' if game.car.cfg.profile!="Custom Sandbox":slider(col,"BoP mass · kg (default 1265)",game.car.cfg.mass_kg,1250,1265,5,func(v):game.car.cfg.mass_kg=v)\n var base=VehicleConfig.new()')
f.write_text(s,encoding='utf8')
f=p/'scripts/main.gd';s=f.read_text(encoding='utf8')
a=s.index('func recover() -> void:');b=s.index('func create_gate()',a)
s=s[:a]+'''func recover() -> void:
 var near=world.nearest(car.position,true)
 for attempt in range(32):
  var chosen=near.along-attempt*22
  var target=world.road_transform(chosen,2.8)
  var clear=true
  for item in traffic.cars:
   if item.body.global_position.distance_to(target.origin)<18:clear=false;break
  if clear:
   car.recover(target);invulnerability=4;cam.first=true
   GTQA.record("recovery",{"along_m":chosen,"reason":"explicit or overturn recovery"})
   return
 hud.notify("복구할 빈 도로 공간이 없습니다. 잠시 후 다시 시도하십시오.")
'''+s[b:]
s=s.replace(' if what==NOTIFICATION_APPLICATION_FOCUS_OUT:\n  GTControls.clear_held()',' if what==NOTIFICATION_APPLICATION_FOCUS_OUT:\n  if hud and not hud.rebind_action.is_empty():hud.cancel_capture()\n  GTControls.clear_held()')
f.write_text(s,encoding='utf8')
# Explicit fixture APIs for a separate QA operator, never invoked by normal startup.
f=p/'scripts/traffic_body.gd';s=f.read_text(encoding='utf8').replace('var cruise_mps: float=24','var cruise_mps: float=24\nvar controller_enabled: bool=true')
s=s.replace(' brake_amount=clampf(-accel/', ' if not controller_enabled:accel=0;steer_angle=0\n brake_amount=clampf(-accel/')
f.write_text(s,encoding='utf8')
f=p/'scripts/traffic.gd';s=f.read_text(encoding='utf8')
s+='''\nfunc spawn_qa_vehicle(at: Transform3D,mass_kg: float,velocity_mps: Vector3=Vector3.ZERO,spin_rad_s: Vector3=Vector3.ZERO,controller: bool=false) -> GTTrafficBody:
 var body=GTTrafficBody.new();body.world=world;body.tuning=tuning;body.spec=tuning.classes[1].duplicate(true)
 body.spec.mass_kg=clampf(mass_kg,800,8000);body.transform=at;body.controller_enabled=controller;body.cruise_mps=0
 body.route_distance=world.nearest(at.origin).along;add_child(body);body.linear_velocity=velocity_mps;body.angular_velocity=spin_rad_s
 cars.append({"body":body,"d":body.route_distance,"dir":1,"speed":0,"lane":2.8,"spec":body.spec,"velocity":velocity_mps,"spin":spin_rad_s,"far_clock":0.0,"qa_pinned":true})
 GTQA.record("qa_fixture",{"id":body.get_instance_id(),"mass_kg":body.mass,"controller":controller})
 return body
'''
s=s.replace('   if distance>maxf(tuning.far_release_m','   if not item.get("qa_pinned",false) and distance>maxf(tuning.far_release_m')
f.write_text(s,encoding='utf8')
print('QA fixture hook, safe recovery and menu fallback added')
