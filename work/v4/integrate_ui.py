from pathlib import Path
p=Path(r'C:/Users/admin/Documents/Codex/2026-09-08/fable-5-1-vs-fable-at-4/outputs/AsterGT')
f=p/'scripts/main.gd';s=f.read_text(encoding='utf-8-sig').replace('var hud: GTHud','var hud: GTV4Hud').replace('hud=GTHud.new()','hud=GTV4Hud.new()')
s=s.replace('var last_engine_state: bool=true','var last_engine_state: bool=true\nvar qa_logger: GTQA\nvar mirror_all_cameras: bool=false')
s=s.replace(' hud.show_home()',' hud.show_home()\n qa_logger=GTQA.new();qa_logger.game=self;qa_logger.process_mode=Node.PROCESS_MODE_PAUSABLE;add_child(qa_logger)\n if not GTControls.load_message.is_empty():hud.notify(GTControls.load_message)',1)
a=s.index('func _unhandled_input(');b=s.index('func start_drive(',a)
s=s[:a]+'''func _input(event: InputEvent) -> void:
 if not hud:return
 if hud.capture_event(event):get_viewport().set_input_as_handled();return
 if event is InputEventKey:
  GTControls.release_event(event)
  if hud.page=="controls" and not is_instance_valid(hud.modal):hud.diagnose(event)
func _unhandled_input(event: InputEvent) -> void:
 if not hud or is_instance_valid(hud.modal):return
 if not event is InputEventKey:return
 var action=GTControls.recognize(event)
 if action.is_empty():return
 get_viewport().set_input_as_handled()
 if action=="pause":
  if started:
   if get_tree().paused:resume()
   else:pause_game();hud.show_pause()
  else:hud.show_home()
  return
 if action=="help":pause_game();hud.show_guide();return
 if action=="setup":pause_game();hud.show_setup();return
 if action=="performance":pause_game();hud.show_performance();return
 if action=="telemetry":hud.debug=not hud.debug;return
 if not started or get_tree().paused or not GTControls.driving():return
 match action:
  "transmission":car.toggle_transmission();save_preferences()
  "shift_up":car.manual_shift(1)
  "shift_down":car.manual_shift(-1)
  "park":car.set_selector("P")
  "reverse":car.set_selector("R")
  "neutral":car.set_selector("N")
  "drive":car.set_selector("D")
  "ignition":car.toggle_ignition()
  "recover":recover()
  "abs":car.abs_enabled=not car.abs_enabled;hud.notify("ABS "+str(car.abs_enabled));save_preferences()
  "tcs":car.tcs_enabled=not car.tcs_enabled;hud.notify("TCS "+str(car.tcs_enabled));save_preferences()
  "esc":car.esc_enabled=not car.esc_enabled;hud.notify("ESC "+str(car.esc_enabled));save_preferences()
  "assist":car.auto_clutch=not car.auto_clutch;hud.notify("자동 클러치 "+str(car.auto_clutch));save_preferences()
  "rev_match":car.rev_match=not car.rev_match;hud.notify("레브매칭 "+str(car.rev_match));save_preferences()
  "lights":car.headlights=not car.headlights
  "highbeam":car.highbeam=not car.highbeam;car.headlights=true
  "left_signal":car.indicator=0 if car.indicator==-1 else -1
  "right_signal":car.indicator=0 if car.indicator==1 else 1
  "hazards":car.hazards=not car.hazards
  "camera":cam.cycle();hud.notify(GTCameraRig.NAMES[cam.mode])
  "weather":world.weather=(world.weather+1)%3;world.update_weather()
  "time":world.time_of_day=(world.time_of_day+1)%3;world.update_weather();car.headlights=world.time_of_day==2
'''+s[b:]
s=s.replace(' car.set_selector("D");car.automatic=true;car.engine_on=true',' car.selector="D";car.gear=1;car.engine_on=true\n if mode=="High Speed":car.cfg.preset("High Speed")\n GTControls.set_context(GTControls.Context.DRIVING)')
s=s.replace(' hud.notify("W accelerate  ·  S brake  ·  A / D steer  ·  F1 help")',' if not hud.onboarding_done:hud.start_onboarding()\n else:hud.notify("가속 "+GTControls.key_text("throttle")+" · 도움말 "+GTControls.key_text("help"))')
s=s.replace('func pause_game() -> void:\n','func pause_game() -> void:\n GTControls.set_context(GTControls.Context.PAUSED if started else GTControls.Context.MENU)\n')
s=s.replace('func resume() -> void:\n','func resume() -> void:\n GTControls.set_context(GTControls.Context.ONBOARDING if hud.onboarding_step>=0 else GTControls.Context.DRIVING)\n')
s=s.replace('func to_garage() -> void:\n','func to_garage() -> void:\n save_preferences();GTControls.set_context(GTControls.Context.MENU)\n if is_instance_valid(hud.onboarding):hud.onboarding.hide()\n')
s=s.replace(' cam.update(minf(dt,.05));audio.interior=', ''' if started and not get_tree().paused:
  var target_context=GTControls.Context.ONBOARDING if hud.onboarding_step>=0 else GTControls.Context.PHOTO_ORBIT if cam.mode==4 else GTControls.Context.DRIVING
  GTControls.set_context(target_context)
 if is_instance_valid(hud.onboarding):hud.onboarding.visible=started and hud.page=="" and not get_tree().paused
 cam.update(minf(dt,.05));audio.interior=''')
s=s.replace('mirror_container.visible=graphics.mirror>0 and started and hud.page==""','mirror_container.visible=graphics.mirror>0 and started and hud.page=="" and (cam.mode==3 or mirror_all_cameras)')
s=s.replace('mirror_container.position=Vector2(770,156);mirror_container.size=Vector2(380,114);','mirror_container.anchor_left=.5;mirror_container.anchor_right=.5;mirror_container.offset_left=-190;mirror_container.offset_right=190;mirror_container.offset_top=150;mirror_container.offset_bottom=264;mirror_container.flip_h=true;')
s=s.replace('mirror_container.visible=graphics.mirror>0 and started\n','mirror_container.visible=graphics.mirror>0 and started and (cam.mode==3 or mirror_all_cameras)\n')
a=s.index('func save_preferences()');b=s.index('func load_preferences()',a)
s=s[:a]+'''func save_preferences() -> void:
 if automation_run:return
 var d={"schema_version":4,"graphics":graphics,"mph":hud.use_mph,"mute":audio.muted,"paint":[car.paint.r,car.paint.g,car.paint.b],"auto_shift_assist":car.automatic,"auto_clutch":car.auto_clutch,"rev_match":car.rev_match,"abs":car.abs_enabled,"tcs":car.tcs_enabled,"esc":car.esc_enabled,"language":GTControls.language,"onboarding_done":hud.onboarding_done,"mirror_all_cameras":mirror_all_cameras}
 var err=GTSafeStore.save_json("user://preferences.json",d)
 var cfg_error=car.cfg.save_settings()
 if err!=OK or cfg_error!=OK:hud.notify("설정 저장 실패: "+error_string(err if err!=OK else cfg_error))
'''+s[b:]
needle=' if d.get("mph") is bool:hud.use_mph=d.mph'
s=s.replace(needle,''' for pair in [["auto_shift_assist","automatic"],["auto_clutch","auto_clutch"],["rev_match","rev_match"],["abs","abs_enabled"],["tcs","tcs_enabled"],["esc","esc_enabled"]]:
  if d.get(pair[0]) is bool:car.set(pair[1],d[pair[0]])
 if d.get("language") in ["ko","en"]:GTControls.language=d.language
 if d.get("onboarding_done") is bool:hud.onboarding_done=d.onboarding_done
 if d.get("mirror_all_cameras") is bool:mirror_all_cameras=d.mirror_all_cameras
'''+needle)
s=s.replace('func _notification(what: int) -> void:\n','func _notification(what: int) -> void:\n if what==NOTIFICATION_APPLICATION_FOCUS_OUT:\n  GTControls.clear_held()\n  if started:pause_game();hud.show_pause()\n')
f.write_text(s,encoding='utf8')
f=p/'scripts/hud.gd';s=f.read_text(encoding='utf-8-sig')
s=s[:s.index('func show_controls()')]+'''func show_controls() -> void:pass
func _input(_event: InputEvent) -> void:pass
'''
s=s.replace('font=ThemeDB.fallback_font','font=SystemFont.new();font.font_names=PackedStringArray(["Malgun Gothic","Noto Sans CJK KR","Arial"])')
s=s.replace('var s=size/Vector2(1920,1080);draw_set_transform(Vector2.ZERO,0,s)','var scale_factor=minf(size.x/1920.0,size.y/1080.0);var s=Vector2.ONE*scale_factor;draw_set_transform(Vector2((size.x-1920*scale_factor)*.5,0),0,s)')
s=s.replace('for k in range(8):','for k in range(10):').replace('130*k/7.0','130*k/9.0')
s=s.replace('txt(("AUTO "+car.selector) if car.automatic else "MANUAL",Vector2(1750,937),16)','txt(("보조 " if car.automatic else "수동 ")+car.selector,Vector2(1750,937),16)\n  txt("클러치 "+("보조" if car.auto_clutch else "수동")+" · RM "+str(car.rev_match),Vector2(1500,1016),14)')
s=s.replace('txt("ENGINE OFF · ENTER",','txt("시동 OFF · "+GTControls.key_text("ignition"),')
s=s.replace('txt("C  CAMERA    F1  HELP    ESC  MENU",Vector2(42,1060),16,dim)','txt(GTControls.key_text("camera")+" 카메라  "+GTControls.key_text("help")+" 도움말  "+GTControls.key_text("pause")+" 메뉴",Vector2(42,1060),16,dim)')
s=s.replace('if debug:\n','if debug and not (self is GTV4Hud and onboarding_step>=0):\n')
# Reduce instrument duplication in cockpit: full physical instruments + compact assistance status.
a=s.index('  # Compact analogue');b=s.index('  # Minimap',a)
block=s[a:b]
s=s[:a]+'  if game.cam.mode!=3:\n'+''.join(' '+line+'\n' for line in block.splitlines())+'''  else:
   draw_rect(Rect2(1440,944,440,75),pane)
   txt(("자동 변속 보조 " if car.automatic else "순차 수동 ")+car.selector+" / "+str(car.gear),Vector2(1460,975),20,accent)
   txt("클러치 "+("보조" if car.auto_clutch else "수동")+" · RM "+str(car.rev_match),Vector2(1460,1004),18)
'''+s[b:]
s=s.replace('draw_rect(Rect2((1920-width)/2,620,width,64)','draw_rect(Rect2((1920-width)/2,550,width,64)').replace('Vector2((1920-width)/2+30,662)','Vector2((1920-width)/2+30,592)')
s=s.replace('var panel=Panel.new();panel.position=Vector2(38,32);panel.size=Vector2(910 if wide else 760,994)','var panel=Panel.new();panel.position=Vector2(38,32);panel.size=Vector2(minf(size.x-76,1000 if wide else 760),size.y-72)')
s=s.replace('sc.size=Vector2(833 if wide else 684,923)','sc.size=panel.size-Vector2(76,65)')
s=s.replace(' clear_menu();page=title.to_lower();',' clear_menu();GTControls.set_context(GTControls.Context.PAUSED if game.started else GTControls.Context.MENU);page=title.to_lower();')
s=s.replace('4.50*game.car.cfg.mass_kg/1520/maxf(.3,game.car.cfg.torque_scale)','game.car.cfg.performance_estimate().zero_100_s')
s=s.replace('button(col,"Controls",func():show_controls())','button(col,"키 설정 / Controls",func():show_controls())')
s=s.replace('button(col,"Drive                                  →"','button(col,"주행 시작 / Drive                      →"')
s=s.replace('button(col,"Garage"','button(col,"차고 / Garage"').replace('button(col,"Vehicle Setup"','button(col,"차량 설정 / Vehicle Setup"').replace('button(col,"Quit"','button(col,"종료 / Quit"')
s=s.replace('button(col,"Graphics"','button(col,"그래픽 / Graphics"')
s=s.replace('if self is GTV4Hud and onboarding_step>=0','if false') if False else s
s=s.replace('and not (self is GTV4Hud and onboarding_step>=0)','and not (self is GTV4Hud and get("onboarding_step")>=0)')
s=s.replace(' button(col,"Camera & Audio",func():show_camera())',' button(col,"Camera & Audio",func():show_camera())\n button(col,"운전 도움말 / Guide",func():call("show_guide"))')
s=s.replace(' toggle(col,"Mute audio",',' toggle(col,"멀미 감소 / Reduced motion",game.cam.reduced_motion,func(v):game.cam.reduced_motion=v)\n toggle(col,"선택 카메라 모두에 후방 미러 표시",game.mirror_all_cameras,func(v):game.mirror_all_cameras=v)\n toggle(col,"Mute audio",')
# Legacy controls implementation is replaced by derived registry UI.
f.write_text(s,encoding='utf8')
print('main and HUD integrated')
