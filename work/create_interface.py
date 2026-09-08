from pathlib import Path
p=Path('outputs/AsterGT')
def write(name,s):f=p/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(s.strip()+'\n',encoding='utf-8')
write('scripts/camera_rig.gd',r'''
class_name GTCameraRig
extends Node3D
var car: GTCar
var camera: Camera3D
var mode: int=0
var offsets: Array[Vector3]=[Vector3(0,2.7,7.7),Vector3(0,.04,-2.48),Vector3(0,.75,-.9),Vector3(-.38,.74,-.05),Vector3(5,1.8,6)]
var fovs: Array[float]=[65,78,74,78,57]
var shake_strength: float=.14
var orbit_yaw: float=.55
var orbit_pitch: float=.20
var orbit_distance: float=7
var menu_preview: bool=true
var smoothed_yaw: float=0
var first: bool=true
const NAMES=["CHASE","BUMPER","HOOD","COCKPIT","ORBIT"]
func _ready() -> void:
 camera=Camera3D.new();camera.near=.05;camera.far=9000;add_child(camera);camera.make_current()
 load_settings()
func cycle() -> void:
 mode=(mode+1)%5;first=true;update_visibility()
func update_visibility() -> void:
 if not car or not car.body_visual:return
 for node in car.body_visual.find_children("*","MeshInstance3D",true,false):
  if "Windshield" in node.name or "Roof" in node.name:node.visible=not (mode==3 and not menu_preview)
func _unhandled_input(event: InputEvent) -> void:
 if mode!=4 or menu_preview:return
 if event is InputEventMouseMotion and Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT):
  orbit_yaw-=event.relative.x*.006;orbit_pitch=clampf(orbit_pitch+event.relative.y*.003,-.05,.8)
 if event is InputEventMouseButton and event.pressed:
  if event.button_index==MOUSE_BUTTON_WHEEL_UP:orbit_distance=maxf(3,orbit_distance-.5)
  if event.button_index==MOUSE_BUTTON_WHEEL_DOWN:orbit_distance=minf(15,orbit_distance+.5)
func update(dt: float) -> void:
 if not car:return
 var tr=car.global_transform;var target: Vector3;var look: Vector3
 if menu_preview:
  var dir=-tr.basis.z;var right=tr.basis.x
  target=tr.origin+dir*5.4+right*5.5+Vector3.UP*2.0
  look=tr.origin-tr.basis.x*1.4+Vector3.UP*.15
  camera.fov=47
 else:
  var yaw=car.rotation.y
  smoothed_yaw=lerp_angle(smoothed_yaw,yaw,1-exp(-7*dt)) if not first else yaw
  var b=Basis(Vector3.UP,smoothed_yaw)
  var rear=Input.is_action_pressed("look_back")
  if mode==0:
   target=tr.origin+b*offsets[0]
   if rear:target=tr.origin+b*Vector3(0,2.0,-7)
   look=tr.origin+b*Vector3(0,.9,-3 if not rear else 3)
  elif mode==4:
   target=tr.origin+b*Vector3(sin(orbit_yaw)*orbit_distance,1.2+sin(orbit_pitch)*orbit_distance,cos(orbit_yaw)*orbit_distance)
   look=tr.origin+Vector3.UP*.25
  else:
   target=tr*offsets[mode]
   look=target+(-tr.basis.z if not rear else tr.basis.z)*50+Vector3.UP*.1
  var collision_start=tr.origin+Vector3.UP*.65
  if mode in [0,4]:
   var ray=PhysicsRayQueryParameters3D.create(collision_start,target,1|4);ray.exclude=[car.get_rid()]
   var hit=car.get_world_3d().direct_space_state.intersect_ray(ray)
   if not hit.is_empty():target=hit.position+(collision_start-hit.position).normalized()*.3
  var shake=sin(car.simulation_time*29)*minf(car.speed_kph/200,1)*shake_strength*.04
  target.y+=shake
  camera.fov=lerpf(camera.fov,fovs[mode]+minf(car.speed_kph*.028,8),1-exp(-4*dt))
 camera.global_position=target if first or mode in [1,2,3] else camera.global_position.lerp(target,1-exp(-10*dt))
 camera.look_at(look,Vector3.UP);first=false
func save_settings() -> void:
 var d={"shake":shake_strength,"fovs":fovs,"offsets":[]}
 for v in offsets:d.offsets.append([v.x,v.y,v.z])
 var f=FileAccess.open("user://cameras.json",FileAccess.WRITE);if f:f.store_string(JSON.stringify(d))
func load_settings() -> void:
 if not FileAccess.file_exists("user://cameras.json"):return
 var d=JSON.parse_string(FileAccess.get_file_as_string("user://cameras.json"))
 if not d is Dictionary:return
 if d.get("shake") is float:shake_strength=clampf(d.shake,0,1)
 if d.get("fovs") is Array and d.fovs.size()==5:
  for i in range(5):
   if d.fovs[i] is float:fovs[i]=clampf(d.fovs[i],40,105)
 if d.get("offsets") is Array and d.offsets.size()==5:
  for i in range(5):
   if d.offsets[i] is Array and d.offsets[i].size()==3:
    var a=d.offsets[i]
    if a[0] is float and a[1] is float and a[2] is float:offsets[i]=Vector3(clampf(a[0],-12,12),clampf(a[1],-.1,6),clampf(a[2],-12,12))
''')
write('scripts/traffic.gd',r'''
class_name GTTraffic
extends Node3D
var world: GTWorld
var car: GTCar
var cars: Array[Dictionary]=[]
var density: int=12
var enabled: bool=true
var clock: float=0
var rng=RandomNumberGenerator.new()
func _ready() -> void:
 rng.seed=1240
func set_density(count: int) -> void:
 density=clampi(count,0,36)
 for item in cars:item.body.queue_free()
 cars.clear()
 for i in range(density):
  var body=CharacterBody3D.new();body.collision_layer=4;body.collision_mask=1|2|4;add_child(body)
  var cs=CollisionShape3D.new();var shape=BoxShape3D.new();shape.size=Vector3(1.8,.90,4.25);cs.shape=shape;body.add_child(cs)
  var m=StandardMaterial3D.new();m.albedo_color=[Color("809690"),Color("d0c9b8"),Color("953e35"),Color("324b68"),Color("aeaaa0")][i%5];m.metallic=.55;m.roughness=.3
  world.box(body,Vector3(0,-.05,0),Vector3(1.84,.55,4.3),m)
  var glass=world.mat(Color("223945"),.16,.5)
  world.box(body,Vector3(0,.43,.1),Vector3(1.52,.48,2.0),glass)
  world.box(body,Vector3(0,.71,.15),Vector3(1.57,.08,1.6),m)
  for x in [-.88,.88]:
   for z in [-1.28,1.30]:
    var cylinder=CylinderMesh.new();cylinder.top_radius=.34;cylinder.bottom_radius=.34;cylinder.height=.21
    var wheel=world.add_mesh(body,cylinder,world.mat(Color("15181b")),Vector3(x,-.27,z));wheel.rotation.z=PI/2
  var tail=world.mat(Color("ad2424"),.3);tail.emission_enabled=true;tail.emission=Color("a41313")
  for x in [-.62,.62]:world.box(body,Vector3(x,.08,2.16),Vector3(.38,.1,.025),tail)
  var dir=1 if i%3!=0 else -1
  var at=world.nearest(car.position).along+rng.randf_range(100,650)*(1 if i%2==0 else -1)
  cars.append({"body":body,"d":at,"dir":dir,"speed":rng.randf_range(14,25),"cruise":rng.randf_range(19,29),"lane":2.8*dir,"target_lane":2.8*dir,"overtake_timer":0.0})
  body.global_transform=world.road_transform(at,2.8*dir);if dir<0:body.rotate_y(PI)
func _physics_process(dt: float) -> void:
 if not enabled or not car:return
 clock+=dt
 var player_d=world.nearest(car.position).along
 for item in cars:
  var body: CharacterBody3D=item.body
  var distance=body.position.distance_to(car.position)
  if distance>900:
   body.visible=false
   if fmod(clock+item.d,1)<dt:
    item.d=player_d+rng.randf_range(420,780)*(1 if rng.randf()>.5 else -1)
    body.global_transform=world.road_transform(item.d,item.dir*2.8)
    if item.dir<0:body.rotate_y(PI)
   continue
  body.visible=true
  var front=-body.global_basis.z
  var origin=body.position+Vector3.UP*.1
  var ray=PhysicsRayQueryParameters3D.create(origin,origin+front*(12+item.speed*1.6),2|4);ray.exclude=[body.get_rid()]
  var hit=body.get_world_3d().direct_space_state.intersect_ray(ray)
  var target_speed=item.cruise
  item.overtake_timer=maxf(0,item.overtake_timer-dt)
  if not hit.is_empty():
   var gap=origin.distance_to(hit.position)
   target_speed=clampf((gap-6)*.65,0,item.cruise)
   if item.dir>0 and gap>12 and gap<38 and item.overtake_timer<=0:
    var clear=true
    for other in cars:
     if other.dir<0 and other.body.position.distance_to(body.position)<180:clear=false
    if car.position.distance_to(body.position)<60 and (car.position-body.position).dot(body.global_basis.x)<-1:clear=false
    if clear:item.target_lane=-2.8;item.overtake_timer=5.0
  if item.overtake_timer<=0:item.target_lane=item.dir*2.8
  item.lane=move_toward(item.lane,item.target_lane,1.3*dt)
  item.speed=move_toward(item.speed,target_speed,(5 if target_speed<item.speed else 2)*dt)
  item.d=fposmod(item.d+item.speed*dt*item.dir,world.length)
  var tr=world.road_transform(item.d,item.lane);tr.origin.y-=.09
  var delta=tr.origin-body.position
  body.velocity=delta/dt
  body.move_and_slide()
  body.basis=tr.basis if item.dir>0 else tr.basis.rotated(tr.basis.y,PI)
  # Reproject after a real collision so AI cannot drift through the player.
  if body.get_slide_collision_count()>0:
   item.d=world.nearest(body.position).along;item.speed=minf(item.speed,5)
''')
write('scripts/hud.gd',r'''
class_name GTHud
extends Control
var game
var menu_root: Control
var font: Font
var toast: String=""
var toast_time: float=0
var debug: bool=false
var use_mph: bool=false
var page: String=""
var rebind_action: String=""
var rebind_button: Button
var accent=Color("96d3b0")
var ink=Color("101c20")
var white=Color("f2f2e8")
var dim=Color("9caead")
var pane=Color(.025,.055,.067,.94)
func _ready() -> void:
 process_mode=Node.PROCESS_MODE_ALWAYS
 set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
 mouse_filter=Control.MOUSE_FILTER_IGNORE
 font=ThemeDB.fallback_font
 var theme=Theme.new();theme.default_font=font;theme.default_font_size=24
 theme.set_color("font_color","Label",white)
 theme.set_color("font_color","Button",white)
 for state in ["normal","hover","pressed","focus"]:
  var style=StyleBoxFlat.new();style.bg_color=Color("253b3f") if state=="normal" else Color("426758")
  style.corner_radius_top_left=6;style.corner_radius_top_right=6;style.corner_radius_bottom_left=6;style.corner_radius_bottom_right=6
  style.content_margin_left=20;style.content_margin_right=20;style.content_margin_top=12;style.content_margin_bottom=12
  if state=="focus":style.border_width_left=2;style.border_color=accent
  theme.set_stylebox(state,"Button",style)
 self.theme=theme
 menu_root=Control.new();menu_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT);add_child(menu_root)
func _process(dt: float) -> void:
 toast_time=maxf(0,toast_time-dt);queue_redraw()
func notify(message: String) -> void:toast=message;toast_time=3.2
func txt(text: String,pos: Vector2,size_px: int,color: Color=Color("f2f2e8")) -> void:draw_string(font,pos,text,HORIZONTAL_ALIGNMENT_LEFT,-1,size_px,color)
func _draw() -> void:
 if not game or not game.car:return
 var s=size/Vector2(1920,1080);draw_set_transform(Vector2.ZERO,0,s)
 var car: GTCar=game.car
 if page!="":
  if page=="home" or page=="garage":
   draw_rect(Rect2(1000,72,800,80),Color(.02,.05,.06,.72))
   txt("VIRIDIAN  /  GT-500",Vector2(1040,110),24,white)
   txt("HANDCRAFTED GRAND TOURER     •     6-SPEED",Vector2(1040,137),16,dim)
   draw_rect(Rect2(1010,886,795,104),Color(.02,.05,.06,.85))
   txt("POWER",Vector2(1045,918),15,dim);txt("%d hp"%game.power_hp(),Vector2(1045,961),32)
   txt("TORQUE",Vector2(1245,918),15,dim);txt("%d Nm"%game.car.cfg.torque_at(5800),Vector2(1245,961),32)
   txt("MASS",Vector2(1440,918),15,dim);txt("%d kg"%game.car.cfg.mass_kg,Vector2(1440,961),32)
   txt("DRIVE",Vector2(1650,918),15,dim);txt(game.car.cfg.drive_layout,Vector2(1650,961),32)
 else:
  draw_rect(Rect2(40,35,450,95),pane)
  txt("A S T E R",Vector2(62,75),28,accent)
  txt(game.mode.to_upper()+"   /   "+game.world.ZONES[int(game.route_progress/game.world.length*5)%5],Vector2(62,110),17)
  draw_rect(Rect2(1440,35,440,95),pane)
  txt(["CLEAR","OVERCAST","RAIN"][game.world.weather]+"  /  "+["DAY","GOLDEN HOUR","NIGHT"][game.world.time_of_day],Vector2(1465,77),22)
  txt("%0.2f km   •   %s"%[car.odometer/1000,GTCameraRig.NAMES[game.cam.mode]],Vector2(1465,111),17,dim)
  # Compact analogue RPM arc and large physical speed/gear readout.
  draw_rect(Rect2(1470,710,410,315),pane)
  var center=Vector2(1670,880)
  draw_arc(center,130,deg_to_rad(205),deg_to_rad(335),64,Color("31464a"),15,true)
  draw_arc(center,130,deg_to_rad(205),deg_to_rad(205+130*clampf(car.rpm/car.cfg.max_rpm,0,1)),64,accent if car.rpm<car.cfg.redline_rpm else Color("ef8e68"),15,true)
  for k in range(8):
   var angle=deg_to_rad(205+130*k/7.0);var a=center+Vector2(cos(angle),sin(angle))*111
   txt(str(k),a+Vector2(-5,5),13,dim)
  var speed=car.speed_kph*.621371 if use_mph else car.speed_kph
  var speed_text="%03d"%roundi(speed);txt(speed_text,Vector2(1530,907),87)
  txt("MPH" if use_mph else "KM/H",Vector2(1540,938),16,dim)
  txt("%04d RPM"%car.rpm,Vector2(1527,992),18,accent)
  txt("R" if car.gear<0 else ("N" if car.gear==0 else str(car.gear)),Vector2(1765,899),67,accent)
  txt(("AUTO "+car.selector) if car.automatic else "MANUAL",Vector2(1750,937),16)
  var x=1498
  for item in [["ABS",car.abs_enabled,car.abs_active],["TCS",car.tcs_enabled,car.tcs_active],["ESC",car.esc_enabled,car.esc_active]]:
   txt(item[0],Vector2(x,743),15,Color("f1be73") if item[2] else (accent if item[1] else Color("627274")));x+=75
  txt("HB" if car.handbrake else ("HI" if car.highbeam else "ON" if car.headlights else ""),Vector2(1790,743),15,Color("efb768"))
  for i in range(3):
   var value=[car.throttle,car.brake,car.clutch][i];var bx=1488+i*128
   draw_rect(Rect2(bx,1042,110,6),Color("304548"));draw_rect(Rect2(bx,1042,110*value,6),[accent,Color("ed9a77"),Color("aab9d8")][i])
   txt(["THROTTLE","BRAKE","CLUTCH"][i],Vector2(bx,1070),11,dim)
  # Minimap uses the actual road samples, centered on actual player position.
  draw_rect(Rect2(40,760,295,265),pane)
  txt("ROUTE  /  %0.1f KM"%(game.world.length/1000),Vector2(61,791),16,accent)
  var mapcenter=Vector2(187,907);var points=PackedVector2Array()
  var b=Basis(Vector3.UP,-car.rotation.y)
  for i in range(0,game.world.road_points.size(),2):
   var local=b*(game.world.road_points[i]-car.position)
   var point=mapcenter+Vector2(local.x,local.z)*.14
   if absf(point.x-mapcenter.x)<127 and absf(point.y-mapcenter.y)<97:points.append(point)
   else:
    if points.size()>1:draw_polyline(points,Color("788e89"),5,true)
    points.clear()
  if points.size()>1:draw_polyline(points,Color("788e89"),5,true)
  draw_colored_polygon(PackedVector2Array([mapcenter+Vector2(0,-11),mapcenter+Vector2(8,9),mapcenter+Vector2(0,5),mapcenter+Vector2(-8,9)]),accent)
  txt("C  CAMERA    F1  HELP    ESC  MENU",Vector2(42,1060),16,dim)
  if car.indicator!=0 or car.hazards:
   if fmod(car.simulation_time,1)<.5:
    if car.indicator<0 or car.hazards:txt("<",Vector2(890,1000),34,accent)
    if car.indicator>0 or car.hazards:txt(">",Vector2(1010,1000),34,accent)
  if game.mode!="Free Drive":
   draw_rect(Rect2(710,35,500,100),pane)
   txt(game.challenge_text,Vector2(737,74),21,accent)
   txt(game.format_time(game.challenge_time),Vector2(737,114),30)
  if debug:
   draw_rect(Rect2(44,160,470,510),pane)
   txt("LIVE TELEMETRY",Vector2(66,197),20,accent)
   var lines=["FPS  %d   /   Frame %.1f ms"%[Engine.get_frames_per_second(),1000.0/maxf(1,Engine.get_frames_per_second())],"Physics 120 Hz    Draw calls %d"%RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME),"RPM %d   Gear %d   Ratio %.2f"%[car.rpm,car.gear,car.get_ratio()],"Speed %.2f km/h   Yaw %.3f"%[car.speed_kph,car.angular_velocity.y],"Throttle %.2f  Brake %.2f"%[car.throttle,car.brake],"Steer %.2f   Clutch %.2f"%[car.steering,car.clutch],"Ground contacts %d / 4"%car.grounded]
   for i in range(4):lines.append("%s  %5.1f rad/s   %4d N   slip %+.2f"%[["FL","FR","RL","RR"][i],car.wheels[i].omega,car.wheels[i].load,car.wheels[i].slip])
   lines.append("Active terrain chunks %d"%game.world.active_tiles.size())
   for i in range(lines.size()):txt(lines[i],Vector2(66,236+i*33),18,white if i<7 else dim)
 if toast_time>0:
  var width=maxf(460,font.get_string_size(toast,HORIZONTAL_ALIGNMENT_LEFT,-1,24).x+65)
  draw_rect(Rect2((1920-width)/2,620,width,64),Color(.03,.08,.08,.95));txt(toast,Vector2((1920-width)/2+30,662),24,accent)
func label(parent: Node,text: String,size_px: int=24,color: Color=Color("f2f2e8")) -> Label:
 var l=Label.new();l.text=text;l.add_theme_font_size_override("font_size",size_px);l.add_theme_color_override("font_color",color);parent.add_child(l);return l
func button(parent: Node,text: String,callback: Callable) -> Button:
 var b=Button.new();b.text=text;b.custom_minimum_size=Vector2(0,58);b.alignment=HORIZONTAL_ALIGNMENT_LEFT;b.pressed.connect(callback);parent.add_child(b);return b
func clear_menu() -> void:
 for child in menu_root.get_children():child.queue_free()
 rebind_action="";page="";menu_root.mouse_filter=Control.MOUSE_FILTER_IGNORE
func menu_base(title: String,wide: bool=false) -> VBoxContainer:
 clear_menu();page=title.to_lower();menu_root.mouse_filter=Control.MOUSE_FILTER_STOP
 var panel=Panel.new();panel.position=Vector2(38,32);panel.size=Vector2(910 if wide else 760,994)
 var style=StyleBoxFlat.new();style.bg_color=pane;style.corner_radius_top_left=12;style.corner_radius_top_right=12;style.corner_radius_bottom_left=12;style.corner_radius_bottom_right=12;panel.add_theme_stylebox_override("panel",style);menu_root.add_child(panel)
 var sc=ScrollContainer.new();sc.position=Vector2(76,61);sc.size=Vector2(833 if wide else 684,923);menu_root.add_child(sc)
 var col=VBoxContainer.new();col.size_flags_horizontal=Control.SIZE_EXPAND_FILL;col.add_theme_constant_override("separation",13);sc.add_child(col)
 label(col,"A S T E R    /    GRAND TOUR",22,accent)
 label(col,title,52,white)
 return col
func small(col: Node,text: String) -> void:
 var l=label(col,text,19,dim);l.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
func show_home() -> void:
 var col=menu_base("Grand Tour.");page="home"
 small(col,"A winding road. An open horizon. Your drive.")
 var gap=Control.new();gap.custom_minimum_size.y=28;col.add_child(gap)
 button(col,"Drive                                  →",func():show_drive())
 button(col,"Garage",func():show_garage())
 button(col,"Vehicle Setup",func():show_setup())
 button(col,"Graphics",func():show_graphics())
 button(col,"Controls",func():show_controls())
 button(col,"Quit",func():game.get_tree().quit())
 label(col,"THE ASTER ROUTE",17,accent)
 small(col,"%0.1f km of connected roads\nValleys, mountain passes and open highway."%(game.world.length/1000))
 small(col,"Keyboard driving • Physical tires • Six-speed GT")
func back(col: Node) -> void:button(col,"← Back",func():show_pause() if game.started else show_home())
func show_pause() -> void:
 var col=menu_base("Paused")
 button(col,"Resume drive                          →",func():game.resume())
 button(col,"Vehicle Setup",func():show_setup())
 button(col,"Graphics",func():show_graphics())
 button(col,"Camera & Audio",func():show_camera())
 button(col,"Controls",func():show_controls())
 button(col,"Change driving mode",func():show_drive())
 button(col,"Return to garage",func():game.to_garage())
 button(col,"Quit",func():game.get_tree().quit())
func show_drive() -> void:
 var col=menu_base("Choose your drive")
 var modes={"Free Drive":"Explore the full route with traffic. No clock.","High Speed":"Flat highway: measure 0–100 and peak speed.","Time Trial":"A 3 km route. Ordered gates; stay on the road.","Checkpoints":"Reach six consecutive gates before time expires."}
 for mode in modes:
  button(col,mode+"     →",func():game.start_drive(mode))
  small(col,modes[mode])
 back(col)
func show_garage() -> void:
 var col=menu_base("The GT-500");page="garage"
 small(col,"A front-engine grand tourer with an original sculpted body, forged wheels and a saddle interior.")
 label(col,"PAINT FINISH",18,accent)
 var row=HBoxContainer.new();row.add_theme_constant_override("separation",10);col.add_child(row)
 for color in [Color("216d67"),Color("bfc8bc"),Color("8a302a"),Color("b78845"),Color("242d35")]:
  var b=button(row,"   ",func():game.set_paint(color));b.modulate=color.lightened(.35);b.custom_minimum_size=Vector2(90,60)
 label(col,"%d hp  /  %d Nm  /  %d kg"%[game.power_hp(),game.car.cfg.torque_at(5800),game.car.cfg.mass_kg],27)
 small(col,"0–100 km/h: approximately %.1f s\nGear-limited maximum: %.0f km/h\nBalanced brake bias; progressive, speed-sensitive steering."%[4.29*game.car.cfg.mass_kg/1520/maxf(.3,game.car.cfg.torque_scale),game.gear_max_speed(6)])
 small(col,"Estimates vary with surface, gearing and driving aids.")
 button(col,"Vehicle setup",func():show_setup())
 button(col,"Take it for a drive                    →",func():show_drive())
 back(col)
func slider(col: Node,title: String,value: float,minval: float,maxval: float,step: float,callback: Callable) -> void:
 var row=HBoxContainer.new();col.add_child(row)
 var l=label(row,title,22);l.size_flags_horizontal=Control.SIZE_EXPAND_FILL
 var val=label(row,"%.2f"%value,21,accent);val.custom_minimum_size.x=100;val.horizontal_alignment=HORIZONTAL_ALIGNMENT_RIGHT
 var s=HSlider.new();s.min_value=minval;s.max_value=maxval;s.step=step;s.value=value;s.custom_minimum_size.y=24;col.add_child(s)
 s.value_changed.connect(func(v):val.text="%.2f"%v;callback.call(v))
func option(col: Node,title: String,choices: Array,current: int,callback: Callable) -> void:
 var row=HBoxContainer.new();col.add_child(row);var l=label(row,title,22);l.size_flags_horizontal=Control.SIZE_EXPAND_FILL
 var o=OptionButton.new();o.custom_minimum_size=Vector2(240,48)
 for item in choices:o.add_item(str(item))
 o.select(clampi(current,0,choices.size()-1));o.item_selected.connect(callback);row.add_child(o)
func toggle(col: Node,title: String,active: bool,callback: Callable) -> void:
 var b=CheckButton.new();b.text=title;b.button_pressed=active;b.custom_minimum_size.y=43;b.toggled.connect(callback);col.add_child(b)
func show_setup() -> void:
 var col=menu_base("Vehicle setup",true)
 small(col,"Changes apply safely while paused. Tune, then resume your drive.")
 option(col,"Preset",["Street","GT","Drift","Wet","Eco"],0,func(i):game.car.cfg.preset(["Street","GT","Drift","Wet","Eco"][i]);game.car.abs_enabled=true;game.car.tcs_enabled=true;game.car.esc_enabled=true;show_setup();notify("Preset applied"))
 option(col,"Driven wheels",["RWD","FWD","AWD"],["RWD","FWD","AWD"].find(game.car.cfg.drive_layout),func(i):game.car.cfg.drive_layout=["RWD","FWD","AWD"][i])
 var titles={"torque_scale":"Engine torque multiplier","max_rpm":"Maximum RPM","mass_kg":"Vehicle mass · kg","final_drive":"Final drive ratio","brake_torque":"Total brake torque · Nm","brake_bias":"Front brake proportion","max_steer":"Low-speed steering · degrees","steer_rate":"Steering input rate","steer_return":"Steering return rate","spring":"Spring stiffness · N/m","bump_damping":"Compression damping · Ns/m","rebound_damping":"Rebound damping · Ns/m","ride_height":"Suspension rest length · m","grip_front":"Front tire friction","grip_rear":"Rear tire friction","downforce":"Downforce coefficient","abs_strength":"ABS intervention","tcs_strength":"TCS intervention","esc_strength":"ESC intervention"}
 for key in titles:
  var limits=VehicleConfig.RANGES[key]
  slider(col,titles[key],game.car.cfg.get(key),limits[0],limits[1],limits[2],func(v):game.car.cfg.set(key,v);game.car.cfg.sanitize())
 label(col,"TRANSMISSION RATIOS",20,accent)
 for i in range(6):slider(col,"Gear "+str(i+1),game.car.cfg.gear_ratios[i],.5,4.5,.02,func(v):game.car.cfg.gear_ratios[i]=v)
 toggle(col,"Automatic clutch assistance",game.car.auto_clutch,func(v):game.car.auto_clutch=v)
 toggle(col,"Rev matching assistance",game.car.rev_match,func(v):game.car.rev_match=v)
 button(col,"Save user preset",func():game.car.cfg.save_settings();notify("Vehicle preset saved"))
 button(col,"Load user preset",func():notify("Preset loaded" if game.car.cfg.load_settings() else "No valid saved preset");show_setup())
 button(col,"Restore Street defaults",func():game.car.cfg.preset("Street");show_setup())
 back(col)
func show_graphics() -> void:
 var col=menu_base("Graphics",true)
 small(col,"Rendering controls are independent of vehicle performance.")
 option(col,"Quality preset",["Low","Medium","High","Ultra"],game.graphics.preset,func(i):game.apply_preset(i);show_graphics())
 slider(col,"Render scale",game.graphics.scale,.5,1.5,.05,func(v):game.graphics.scale=v;game.apply_graphics())
 option(col,"Anti-aliasing",["Off","2× MSAA","4× MSAA","8× MSAA"],game.graphics.aa,func(i):game.graphics.aa=i;game.apply_graphics())
 slider(col,"Shadow distance · m",game.graphics.shadows,0,350,25,func(v):game.graphics.shadows=v;game.apply_graphics())
 option(col,"Reflections",["Sky","Probe","Screen space + probe"],game.graphics.reflections,func(i):game.graphics.reflections=i;game.apply_graphics())
 slider(col,"Vegetation density",game.graphics.vegetation,.1,1.5,.1,func(v):game.graphics.vegetation=v;game.apply_graphics())
 slider(col,"Traffic count",game.graphics.traffic,0,36,2,func(v):game.graphics.traffic=int(v);game.apply_graphics())
 option(col,"Particles",["Off","Low","High"],game.graphics.particles,func(i):game.graphics.particles=i;game.apply_graphics())
 toggle(col,"Post-processing",game.graphics.post,func(v):game.graphics.post=v;game.apply_graphics())
 option(col,"Rear-view mirror",["Off","320 × 96","640 × 192"],game.graphics.mirror,func(i):game.graphics.mirror=i;game.apply_graphics())
 option(col,"Frame limit",["Unlimited","30","60","120"],[0,30,60,120].find(game.graphics.cap),func(i):game.graphics.cap=[0,30,60,120][i];game.apply_graphics())
 toggle(col,"VSync",game.graphics.vsync,func(v):game.graphics.vsync=v;game.apply_graphics())
 toggle(col,"Fullscreen",game.graphics.fullscreen,func(v):game.graphics.fullscreen=v;game.apply_graphics())
 option(col,"Window resolution",["1280 × 720","1600 × 900","1920 × 1080","2560 × 1440"],game.graphics.resolution,func(i):game.graphics.resolution=i;game.apply_graphics())
 button(col,"Save settings",func():game.save_preferences();notify("Graphics preferences saved"))
 back(col)
func show_camera() -> void:
 var col=menu_base("Camera & audio",true)
 option(col,"Camera",GTCameraRig.NAMES,game.cam.mode,func(i):game.cam.mode=i;game.cam.first=true;show_camera())
 slider(col,"Field of view",game.cam.fovs[game.cam.mode],40,105,1,func(v):game.cam.fovs[game.cam.mode]=v)
 for i in range(3):slider(col,["Horizontal offset","Vertical offset","Forward / rear offset"][i],game.cam.offsets[game.cam.mode][i],[-12,-.1,-12][i],[12,6,12][i],.05,func(v):game.cam.offsets[game.cam.mode][i]=v)
 slider(col,"Camera vibration",game.cam.shake_strength,0,1,.05,func(v):game.cam.shake_strength=v)
 toggle(col,"Mute audio",game.audio.muted,func(v):game.audio.muted=v)
 toggle(col,"Speed in mph",use_mph,func(v):use_mph=v)
 button(col,"Save camera settings",func():game.cam.save_settings();game.save_preferences();notify("Camera preferences saved"))
 back(col)
func show_controls() -> void:
 var col=menu_base("Controls",true)
 small(col,"Select a binding, then press a key. Duplicate bindings are rejected. Orbit camera: right-drag to rotate; wheel to zoom.")
 for action in GTControls.BINDINGS:
  var row=HBoxContainer.new();col.add_child(row);var l=label(row,GTControls.LABELS[action],22);l.size_flags_horizontal=Control.SIZE_EXPAND_FILL
  var b=button(row,GTControls.key_text(action),func():pass);b.custom_minimum_size=Vector2(255,49)
  b.pressed.connect(func():rebind_action=action;rebind_button=b;b.text="Press a key…")
 button(col,"Camera & audio",func():show_camera())
 back(col)
func _input(event: InputEvent) -> void:
 if rebind_action!="" and event is InputEventKey and event.pressed and not event.echo:
  var error=GTControls.rebind(rebind_action,event.physical_keycode)
  if error!="":notify(error)
  rebind_button.text=GTControls.key_text(rebind_action);rebind_action="";get_viewport().set_input_as_handled()
''')
print('Camera, traffic and UI written')
