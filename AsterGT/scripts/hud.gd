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
 font=SystemFont.new();font.font_names=PackedStringArray(["Malgun Gothic","Noto Sans CJK KR","Arial"])
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
func txt(text: String,pos: Vector2,size_px: int,color: Color=Color("f2f2e8")) -> void:draw_string(font,pos,GTLanguage.text(text),HORIZONTAL_ALIGNMENT_LEFT,-1,size_px,color)
func _draw() -> void:
 if not game or not game.car:return
 var scale_factor=minf(size.x/1920.0,size.y/1080.0);var s=Vector2.ONE*scale_factor;draw_set_transform(Vector2((size.x-1920*scale_factor)*.5,0),0,s)
 var car: GTCar=game.car
 if page!="":
  if page=="home" or page=="garage":
   draw_rect(Rect2(1000,72,800,80),Color(.02,.05,.06,.72))
   txt("PORSCHE  /  992 GT3 R",Vector2(1040,110),24,white)
   txt("모델: MattDoesBlender · 6단 순차식" if GTControls.language=="ko" else "Model: MattDoesBlender · 6-speed",Vector2(1040,137),16,dim)
   draw_rect(Rect2(1010,886,795,104),Color(.02,.05,.06,.85))
   txt("POWER",Vector2(1045,918),15,dim);txt("%d hp"%game.power_hp(),Vector2(1045,961),32)
   txt("TORQUE",Vector2(1245,918),15,dim);txt("%d Nm"%game.car.cfg.torque_at(5800),Vector2(1245,961),32)
   txt("MASS",Vector2(1440,918),15,dim);txt("%d kg"%game.car.cfg.mass_kg,Vector2(1440,961),32)
   txt("DRIVE",Vector2(1650,918),15,dim);txt(game.car.cfg.drive_layout,Vector2(1650,961),32)
 else:
  draw_rect(Rect2(40,35,450,95),pane)
  txt("A S T E R",Vector2(62,75),28,accent)
  txt(GTLanguage.text(game.mode.to_upper())+"   /   "+game.world.ZONES[int(game.route_progress/game.world.length*5)%5],Vector2(62,110),17)
  draw_rect(Rect2(1440,35,440,95),pane)
  txt(GTLanguage.text(["CLEAR","OVERCAST","RAIN"][game.world.weather])+"  /  "+GTLanguage.text(["DAY","GOLDEN HOUR","NIGHT"][game.world.time_of_day]),Vector2(1465,77),22)
  txt("%0.2f km   •   %s"%[car.odometer/1000,GTLanguage.text(GTCameraRig.NAMES[game.cam.mode])],Vector2(1465,111),17,dim)
  if game.cam.mode!=3:
   # Compact analogue RPM arc and large physical speed/gear readout.
   draw_rect(Rect2(1470,710,410,315),pane)
   var center=Vector2(1670,880)
   draw_arc(center,130,deg_to_rad(205),deg_to_rad(335),64,Color("31464a"),15,true)
   draw_arc(center,130,deg_to_rad(205),deg_to_rad(205+130*clampf(car.rpm/car.cfg.max_rpm,0,1)),64,accent if car.rpm<car.cfg.redline_rpm else Color("ef8e68"),15,true)
   for k in range(10):
    var angle=deg_to_rad(205+130*k/9.0);var a=center+Vector2(cos(angle),sin(angle))*111
    txt(str(k),a+Vector2(-5,5),13,dim)
   var speed=car.speed_kph*.621371 if use_mph else car.speed_kph
   var speed_text="%03d"%roundi(speed);txt(speed_text,Vector2(1530,907),87)
   txt("MPH" if use_mph else "KM/H",Vector2(1540,938),16,dim)
   txt("%04d RPM"%car.rpm,Vector2(1527,992),18,accent)
   txt("R" if car.gear<0 else ("N" if car.gear==0 else str(car.gear)),Vector2(1765,899),67,accent)
   txt(("보조 " if car.automatic else "수동 ")+car.selector,Vector2(1750,937),16)
   txt("클러치 "+("보조" if car.auto_clutch else "수동")+(" · 레브매칭 " if GTControls.language=="ko" else " · Rev match ")+(("켜짐" if car.rev_match else "꺼짐") if GTControls.language=="ko" else ("On" if car.rev_match else "Off")),Vector2(1500,1016),14)
   if not car.engine_on:txt("시동 OFF · "+GTControls.key_text("ignition"),Vector2(1530,700),20,Color("efb768"))
   var x=1498
   for item in [["ABS",car.abs_enabled,car.abs_active],["TCS",car.tcs_enabled,car.tcs_active],["ESC",car.esc_enabled,car.esc_active]]:
    txt(item[0],Vector2(x,743),15,Color("f1be73") if item[2] else (accent if item[1] else Color("627274")));x+=75
   txt("HB" if car.handbrake else ("HI" if car.highbeam else "ON" if car.headlights else ""),Vector2(1790,743),15,Color("efb768"))
   for i in range(3):
    var value=[car.throttle,car.brake,car.clutch][i];var bx=1488+i*128
    draw_rect(Rect2(bx,1042,110,6),Color("304548"));draw_rect(Rect2(bx,1042,110*value,6),[accent,Color("ed9a77"),Color("aab9d8")][i])
    txt(["THROTTLE","BRAKE","CLUTCH"][i],Vector2(bx,1070),11,dim)
  else:
   draw_rect(Rect2(1440,944,440,75),pane)
   txt(("자동 변속 보조 " if car.automatic else "순차 수동 ")+car.selector+" / "+str(car.gear),Vector2(1460,975),20,accent)
   txt("클러치 "+("보조" if car.auto_clutch else "수동")+(" · 레브매칭 " if GTControls.language=="ko" else " · Rev match ")+(("켜짐" if car.rev_match else "꺼짐") if GTControls.language=="ko" else ("On" if car.rev_match else "Off")),Vector2(1460,1004),18)
  # Minimap uses the actual road samples, centered on actual player position.
  draw_rect(Rect2(40,760,295,265),pane)
  txt(("주행 경로 / %0.1f km" if GTControls.language=="ko" else "ROUTE / %0.1f km")%(game.world.length/1000),Vector2(61,791),16,accent)
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
  # Driving hints live in the requested help panel, not over the road.
  if car.indicator!=0 or car.hazards:
   if fmod(car.simulation_time,1)<.5:
    if car.indicator<0 or car.hazards:txt("<",Vector2(890,1000),34,accent)
    if car.indicator>0 or car.hazards:txt(">",Vector2(1010,1000),34,accent)
  if game.mode!="Free Drive":
   draw_rect(Rect2(710,35,500,100),pane)
   txt(game.challenge_text,Vector2(737,74),21,accent)
   txt(game.format_time(game.challenge_time),Vector2(737,114),30)
  if debug and not (self is GTV4Hud and get("onboarding_step")>=0):
   draw_rect(Rect2(44,160,565,630),pane)
   txt("LIVE TELEMETRY",Vector2(66,197),20,accent)
   var lines=["FPS  %d   /   Frame %.1f ms"%[Engine.get_frames_per_second(),1000.0/maxf(1,Engine.get_frames_per_second())],"Physics 120 Hz    Draw calls %d"%RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME),"RPM %d   Gear %d   Ratio %.2f"%[car.rpm,car.gear,car.get_ratio()],"Speed %.2f km/h   Yaw %.3f"%[car.speed_kph,car.angular_velocity.y],"Throttle %.2f  Brake %.2f"%[car.throttle,car.brake],"Steer %.2f   Clutch %.2f"%[car.steering,car.clutch],"Ground contacts %d / 4"%car.grounded]
   for i in range(4):lines.append("%s  %5.1f rad/s   %4d N   slip %+.2f"%[["FL","FR","RL","RR"][i],car.wheels[i].omega,car.wheels[i].load,car.wheels[i].slip])
   for i in range(4):lines.append("%s tire: %4.0f C / wear %4.1f%% / grip %.2f"%[["FL","FR","RL","RR"][i],car.wheels[i].temperature,car.wheels[i].wear*100,car.wheels[i].grip_factor])
   lines.append("Active terrain chunks %d"%game.world.active_tiles.size())
   for i in range(lines.size()):txt(lines[i],Vector2(66,236+i*33),18,white if i<7 else dim)
 if toast_time>0:
  var width=maxf(460,font.get_string_size(toast,HORIZONTAL_ALIGNMENT_LEFT,-1,24).x+65)
  draw_rect(Rect2((1920-width)/2,550,width,64),Color(.03,.08,.08,.95));txt(toast,Vector2((1920-width)/2+30,592),24,accent)
func label(parent: Node,text: String,size_px: int=24,color: Color=Color("f2f2e8")) -> Label:
 var l=Label.new();l.text=GTLanguage.text(text);l.add_theme_font_size_override("font_size",size_px);l.add_theme_color_override("font_color",color);parent.add_child(l);return l
func button(parent: Node,text: String,callback: Callable) -> Button:
 var b=Button.new();b.text=GTLanguage.text(text);b.custom_minimum_size=Vector2(0,58);b.alignment=HORIZONTAL_ALIGNMENT_LEFT;b.pressed.connect(callback);parent.add_child(b);return b
func clear_menu() -> void:
 for child in menu_root.get_children():child.queue_free()
 rebind_action="";page="";menu_root.mouse_filter=Control.MOUSE_FILTER_IGNORE
func menu_base(title: String,wide: bool=false) -> VBoxContainer:
 clear_menu();GTControls.set_context(GTControls.Context.PAUSED if game.started else GTControls.Context.MENU);page=title.to_lower();menu_root.mouse_filter=Control.MOUSE_FILTER_STOP
 var panel=Panel.new();panel.position=Vector2(38,32);panel.size=Vector2(minf(size.x-76,1000 if wide else 760),size.y-72)
 var style=StyleBoxFlat.new();style.bg_color=pane;style.corner_radius_top_left=12;style.corner_radius_top_right=12;style.corner_radius_bottom_left=12;style.corner_radius_bottom_right=12;panel.add_theme_stylebox_override("panel",style);menu_root.add_child(panel)
 var sc=ScrollContainer.new();sc.position=Vector2(76,61);sc.size=panel.size-Vector2(76,65);menu_root.add_child(sc)
 var col=VBoxContainer.new();col.size_flags_horizontal=Control.SIZE_EXPAND_FILL;col.add_theme_constant_override("separation",13);sc.add_child(col)
 label(col,"A S T E R    /    GRAND TOUR",22,accent)
 var heading=label(col,title,40,white);heading.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
 return col
func small(col: Node,text: String) -> void:
 var l=label(col,text,19,dim);l.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
func show_home() -> void:
 var col=menu_base("Grand Tour.");page="home"
 small(col,"A winding road. An open horizon. Your drive.")
 var gap=Control.new();gap.custom_minimum_size.y=28;col.add_child(gap)
 button(col,"주행 시작 / Drive                      →",func():show_drive())
 button(col,"차고 / Garage",func():show_garage())
 button(col,"차량 설정 / Vehicle Setup",func():show_setup())
 button(col,"그래픽 / Graphics",func():show_graphics())
 button(col,"키 설정 / Controls",func():show_controls())
 button(col,"종료 / Quit",func():game.finish())
 label(col,"THE ASTER ROUTE",17,accent)
 small(col,"%0.1f km of connected roads\nValleys, mountain passes and open highway."%(game.world.length/1000))
 small(col,"Keyboard driving • Physical tires • Six-speed GT")
func back(col: Node) -> void:button(col,"← Back",func():show_pause() if game.started else show_home())
func show_pause() -> void:
 var col=menu_base("Paused")
 button(col,"Resume drive                          →",func():game.resume())
 button(col,"차량 설정 / Vehicle Setup",func():show_setup())
 button(col,"그래픽 / Graphics",func():show_graphics())
 button(col,"Camera & Audio",func():show_camera())
 button(col,"운전 도움말 / Guide",func():call("show_guide"))
 button(col,"키 설정 / Controls",func():show_controls())
 button(col,"Change driving mode",func():show_drive())
 button(col,"Return to garage",func():game.to_garage())
 button(col,"종료 / Quit",func():game.finish())
func show_drive() -> void:
 var col=menu_base("Choose your drive")
 var modes={"Free Drive":"Explore the full route with traffic. No clock.","High Speed":"Flat highway: measure 0–100 and peak speed.","Time Trial":"A 3 km route. Ordered gates; stay on the road.","Checkpoints":"Reach six consecutive gates before time expires."}
 for mode in modes:
  button(col,mode+"     →",func():game.start_drive(mode))
  small(col,modes[mode])
 back(col)
func show_garage() -> void:
 var col=menu_base("Porsche 992 GT3 R");page="garage"
 small(col,"User-supplied 992 GT3 R model. Physics-driven wheels, brake discs, steering and suspension.")
 label(col,"PAINT FINISH",18,accent)
 var row=HBoxContainer.new();row.add_theme_constant_override("separation",10);col.add_child(row)
 for color in [Color("216d67"),Color("bfc8bc"),Color("8a302a"),Color("b78845"),Color("242d35")]:
  var b=button(row,"   ",func():game.set_paint(color));b.modulate=color.lightened(.35);b.custom_minimum_size=Vector2(90,60)
 label(col,"%d hp  /  %d Nm  /  %d kg"%[game.power_hp(),game.car.cfg.torque_at(5800),game.car.cfg.mass_kg],27)
 small(col,"0–100 km/h: approximately %.1f s\nGear-limited maximum: %.0f km/h\nBalanced brake bias; progressive, speed-sensitive steering."%[game.car.cfg.performance_estimate().zero_100_s,game.gear_max_speed(6)])
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
 for item in choices:o.add_item(GTLanguage.text(str(item)))
 o.select(clampi(current,0,choices.size()-1));o.item_selected.connect(callback);row.add_child(o)
func toggle(col: Node,title: String,active: bool,callback: Callable) -> void:
 var b=CheckButton.new();b.text=GTLanguage.text(title);b.button_pressed=active;b.custom_minimum_size.y=43;b.toggled.connect(callback);col.add_child(b)
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
 toggle(col,"Tire temperature and wear",game.car.cfg.tire_simulation,func(v):game.car.cfg.tire_simulation=v)
 toggle(col,"Manual engine stalling",game.car.cfg.stall_enabled,func(v):game.car.cfg.stall_enabled=v)
 button(col,"Service tires",func():game.car.service_tires())
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
 option(col,"Shadow quality",["512 / hard","1024 / soft","2048 / soft","4096 / soft"],game.graphics.shadow_quality,func(i):game.graphics.shadow_quality=i;game.apply_graphics())
 slider(col,"Shadow distance · m",game.graphics.shadows,0,350,25,func(v):game.graphics.shadows=v;game.apply_graphics())
 option(col,"Reflections",["Sky","Screen space","Screen space / high"],game.graphics.reflections,func(i):game.graphics.reflections=i;game.apply_graphics())
 slider(col,"Vegetation density",game.graphics.vegetation,.1,1.5,.1,func(v):game.graphics.vegetation=v;game.apply_graphics())
 slider(col,"Traffic count",game.graphics.traffic,0,36,2,func(v):game.graphics.traffic=int(v);game.apply_graphics())
 option(col,"Particles",["Off","Low","High"],game.graphics.particles,func(i):game.graphics.particles=i;game.apply_graphics())
 toggle(col,"Post-processing",game.graphics.post,func(v):game.graphics.post=v;game.apply_graphics())
 option(col,"Rear-view mirror",["Off","320 × 96","640 × 192"],game.graphics.mirror,func(i):game.graphics.mirror=i;game.apply_graphics())
 option(col,"Frame limit",["Unlimited","30","60","120"],[0,30,60,120].find(game.graphics.cap),func(i):game.graphics.cap=[0,30,60,120][i];game.apply_graphics())
 toggle(col,"VSync",game.graphics.vsync,func(v):game.graphics.vsync=v;game.apply_graphics())
 toggle(col,"Fullscreen",game.graphics.fullscreen,func(v):game.graphics.fullscreen=v;game.apply_graphics())
 option(col,"Window resolution",["1280 × 720","1600 × 900","1920 × 1080","2560 × 1440"],game.graphics.resolution,func(i):game.graphics.resolution=i;game.apply_graphics())
 button(col,"Save settings",func():
  if game.save_preferences():notify("Graphics preferences saved"))
 back(col)
func show_camera() -> void:
 var col=menu_base("Camera & audio",true)
 option(col,"Camera",GTCameraRig.NAMES,game.cam.mode,func(i):game.cam.mode=i;game.cam.first=true;show_camera())
 slider(col,"Field of view",game.cam.fovs[game.cam.mode],40,105,1,func(v):game.cam.fovs[game.cam.mode]=v)
 for i in range(3):slider(col,["Horizontal offset","Vertical offset","Forward / rear offset"][i],game.cam.offsets[game.cam.mode][i],GTCameraRig.MIN_OFFSETS[game.cam.mode][i],GTCameraRig.MAX_OFFSETS[game.cam.mode][i],.05,func(v):game.cam.offsets[game.cam.mode][i]=v)
 slider(col,"Camera vibration",game.cam.shake_strength,0,1,.05,func(v):game.cam.shake_strength=v)
 toggle(col,"멀미 감소 / Reduced motion",game.cam.reduced_motion,func(v):game.cam.reduced_motion=v)
 toggle(col,"선택 카메라 모두에 후방 미러 표시",game.mirror_all_cameras,func(v):game.mirror_all_cameras=v)
 toggle(col,"Mute audio",game.audio.muted,func(v):game.audio.muted=v)
 toggle(col,"Speed in mph",use_mph,func(v):use_mph=v)
 button(col,"Save camera settings",func():
  var err=game.cam.save_settings()
  var prefs_ok=game.save_preferences()
  if err!=OK:notify("저장 실패: "+error_string(err))
  elif prefs_ok:notify("Camera saved"))
 back(col)
func show_controls() -> void:pass
func _input(_event: InputEvent) -> void:pass
