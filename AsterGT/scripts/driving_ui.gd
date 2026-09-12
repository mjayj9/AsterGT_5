class_name GTV4Hud
extends GTHud
var slot_index: int=0
var pending_key: Dictionary={}
var conflict_info: Dictionary={}
var capture_label: Label
var modal: Window
var capture_panel: Control
var mouse_menu: Button
var diagnostic: Label
var diagnostic_holds: Dictionary={}
var diagnostic_bars: Array[ProgressBar]=[]
var binding_buttons: Array[Dictionary]=[]
var category: String="주행"
var guide_category: String="주행"
var onboarding: PanelContainer
var onboarding_step: int=-1
var onboarding_done: bool=false
var practiced={"throttle":false,"brake":false,"steering":false,"camera":false}
var first_minutes: float=0
var tip_clock: float=0
var onb_text: Label
var guide_keys: Array[String]=[]
var onb_start_camera: int=0
var beginner_mode: bool=true
var help_button: Button
var help_category: String="start"
var help_topic: String=""
var help_data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://config/driving_help.json"))
func _ready() -> void:
 super._ready()
 mouse_menu=Button.new();mouse_menu.text="메뉴";mouse_menu.focus_mode=Control.FOCUS_NONE;add_child(mouse_menu)
 mouse_menu.anchor_left=1;mouse_menu.anchor_right=1;mouse_menu.offset_left=-150;mouse_menu.offset_right=-40;mouse_menu.offset_top=138;mouse_menu.offset_bottom=183
 mouse_menu.pressed.connect(func():game.pause_game();show_pause())
 help_button=Button.new();add_child(help_button);help_button.focus_mode=Control.FOCUS_NONE
 help_button.anchor_left=1;help_button.anchor_right=1;help_button.offset_left=-160;help_button.offset_right=-40;help_button.offset_top=196;help_button.offset_bottom=242
 help_button.add_theme_font_size_override("font_size",20)
 help_button.pressed.connect(show_guide)
func tr2(ko: String,en: String) -> String:return ko if GTControls.language=="ko" else en
func _process(dt: float) -> void:
 super._process(dt)
 mouse_menu.visible=game.started and page=="";mouse_menu.text=tr2("메뉴","Menu")
 help_button.visible=beginner_mode and game.started and page=="" and onboarding_step<0
 help_button.text=tr2("? 도움","? Help")
 for row in binding_buttons:
  if is_instance_valid(row.button):row.button.text=(tr2("기본 키 · ","Primary · ") if row.slot==0 else tr2("보조 키 · ","Secondary · "))+GTControls.slot_text(GTControls.bindings[row.action][row.slot])
 if is_instance_valid(diagnostic):
  diagnostic.text=tr2("인식된 입력: ","Recognized input: ")+GTControls.last_event+" → "+GTControls.text_for(GTControls.last_action)+"\n"+tr2("컨텍스트: ","Context: ")+GTControls.Context.keys()[GTControls.context]+" | 실제 T %.2f / B %.2f / S %.2f"%[game.car.throttle,game.car.brake,game.car.steering]
  var values=[1.0 if diagnostic_holds.has("throttle") else 0.0,1.0 if diagnostic_holds.has("brake") else 0.0,(1.0 if diagnostic_holds.has("right") else 0.0)-(1.0 if diagnostic_holds.has("left") else 0.0)]
  for i in range(diagnostic_bars.size()):diagnostic_bars[i].value=values[i]
 if not game.started or game.get_tree().paused:return
 first_minutes+=dt;tip_clock+=dt
 if onboarding_step>=0:
  if game.car.throttle>.15 and GTControls.value("throttle")>.5 and game.car.speed_kph>1:practiced.throttle=true
  if game.car.brake>.2 and GTControls.value("brake")>.5:practiced.brake=true
  if absf(game.car.steering)>.15 and (GTControls.value("left")>.5 or GTControls.value("right")>.5) and game.car.speed_kph>1:practiced.steering=true
  if game.cam.mode!=onb_start_camera:practiced.camera=true
  update_onboarding()
  if onboarding_step==0 and not practiced.values().has(false):onboarding_step=1;rebuild_onboarding()
func clear_menu() -> void:
 binding_buttons.clear();diagnostic_bars.clear();diagnostic_holds.clear();diagnostic=null
 super.clear_menu()
func show_controls() -> void:
 var col=menu_base(tr2("키 설정 · 입력 진단","Controls · diagnostics"),true);page="controls"
 option(col,tr2("언어","Language"),["한국어","English"],0 if GTControls.language=="ko" else 1,func(i):GTControls.language="ko" if i==0 else "en";show_controls();game.save_preferences())
 var cats=["주행","변속","차량","보조장치","환경","메뉴"]
 option(col,tr2("카테고리","Category"),cats,cats.find(category),func(i):category=cats[i];show_controls())
 small(col,tr2("기본 키 / 보조 키 슬롯을 선택하십시오. Esc 취소 · Backspace 비우기. Shift/Ctrl/Alt 조합을 지원합니다. 범주 초기화는 다른 범주의 충돌 슬롯도 비웁니다.","Choose a Primary / Secondary slot. Esc cancels; Backspace clears. Modifier chords supported. Category reset clears conflicting slots elsewhere."))
 for a in GTControls.registry:
  if GTControls.registry[a].category!=category:continue
  label(col,GTControls.text_for(a),24,accent);small(col,GTControls.text_for(a,"description"))
  var row=HBoxContainer.new();col.add_child(row)
  for index in range(2):
   var b=button(row,GTControls.slot_text(GTControls.bindings[a][index]),func():begin_capture(a,index))
   b.size_flags_horizontal=Control.SIZE_EXPAND_FILL;b.tooltip_text="Primary" if index==0 else "Secondary"
   binding_buttons.append({"button":b,"action":a,"slot":index})
 label(col,tr2("입력 진단 (이 화면에서는 차량 조작 차단)","Input diagnosis (driving is blocked here)"),23,accent)
 diagnostic=label(col,"—",18);diagnostic.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
 for i in range(3):
  small(col,["Throttle 0–1","Brake 0–1","Steering −1–1"][i])
  var bar=ProgressBar.new();bar.min_value=-1 if i==2 else 0;bar.max_value=1;bar.show_percentage=false;bar.custom_minimum_size.y=18;col.add_child(bar);diagnostic_bars.append(bar)
 button(col,tr2("이 카테고리 기본값 복구","Restore category defaults"),func():confirm_reset(category))
 button(col,tr2("전체 기본값 복구…","Restore all defaults…"),func():confirm_reset(""))
 button(col,tr2("운전 도움말","Driving guide"),show_guide)
 back(col)
func confirm_reset(cat: String) -> void:
 var dialog=ConfirmationDialog.new();add_child(dialog);modal=dialog
 dialog.dialog_text=tr2("키 설정을 기본값으로 복구하시겠습니까? 다른 범주의 충돌 슬롯은 비워집니다.","Restore defaults? Conflicting slots in other categories will be cleared.")
 dialog.confirmed.connect(func():var err=GTControls.reset_defaults(cat);notify(tr2("복구했습니다.","Defaults restored.") if err==OK else error_string(err));dialog.queue_free();modal=null;show_controls())
 dialog.canceled.connect(func():dialog.queue_free();modal=null)
 dialog.popup_centered()
func begin_capture(a: String,index: int) -> void:
 if DisplayServer.get_name()!="headless":DisplayServer.window_set_ime_active(false)
 rebind_action=a;slot_index=index;pending_key={};GTControls.set_context(GTControls.Context.REBIND_CAPTURE)
 capture_panel=ColorRect.new();capture_panel.color=Color(0,0,0,.75);capture_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT);add_child(capture_panel)
 var panel=PanelContainer.new();capture_panel.add_child(panel);panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER);panel.offset_left=-340;panel.offset_right=340;panel.offset_top=-160;panel.offset_bottom=160
 var col=VBoxContainer.new();panel.add_child(col)
 label(col,tr2("키 입력 대기","Waiting for a key"),32,accent)
 label(col,GTControls.text_for(a)+" · "+(tr2("기본 키","Primary") if index==0 else tr2("보조 키","Secondary")),28)
 small(col,tr2("Esc: 취소 · Backspace: 비우기","Esc: Cancel · Backspace: Clear"))
 small(col,"Ctrl / Alt / Shift + Key")
 button(col,tr2("취소","Cancel"),cancel_capture)

func cancel_capture() -> void:
 if DisplayServer.get_name()!="headless":DisplayServer.window_set_ime_active(true)
 rebind_action="";pending_key={};conflict_info={}
 if is_instance_valid(capture_panel):capture_panel.queue_free()
 capture_panel=null
 if is_instance_valid(modal):modal.queue_free()
 modal=null;GTControls.set_context(GTControls.Context.PAUSED if game.started else GTControls.Context.MENU)
func capture_event(event: InputEvent) -> bool:
 if rebind_action.is_empty():return false
 if not event is InputEventKey:return true
 if not conflict_info.is_empty():return false
 if event.echo:return true
 if event.pressed and event.physical_keycode==KEY_ESCAPE:cancel_capture();return true
 if event.pressed and event.physical_keycode==KEY_BACKSPACE:commit_binding({});return true
 if event.physical_keycode==0 or event.keycode==0 or event.unicode>127:
  notify(tr2("IME 조합 또는 지원하지 않는 입력입니다. 영문 키보드 상태에서 입력하십시오.","IME composition or unsupported input. Switch to direct keyboard input."));return true
 if event.physical_keycode in [KEY_SHIFT,KEY_CTRL,KEY_ALT,KEY_META]:
  if event.pressed:pending_key=GTControls.event_slot(event)
  elif not pending_key.is_empty():commit_binding(pending_key)
  return true
 if event.pressed:commit_binding(GTControls.event_slot(event))
 return true
func commit_binding(s: Dictionary) -> void:
 if not GTControls.valid_slot(s):notify(tr2("유효하지 않은 키입니다.","Invalid key."));return
 pending_key=s;conflict_info=GTControls.conflict(rebind_action,slot_index,s)
 if conflict_info.is_empty():finish_binding("cancel");return
 if is_instance_valid(modal):modal.queue_free()
 var dialog=ConfirmationDialog.new();modal=dialog;add_child(dialog)
 dialog.title=tr2("중복 키","Key conflict")
 dialog.dialog_text=GTControls.slot_text(s)+" → "+GTControls.text_for(conflict_info.action)+"\n"+tr2("기존 키를 비우고 교체하거나 두 슬롯을 서로 바꿀 수 있습니다.","Replace the existing slot or swap the two slots.")
 dialog.ok_button_text=tr2("교체","Replace")
 dialog.add_button(tr2("서로 바꾸기","Swap"),true,"swap")
 dialog.confirmed.connect(func():finish_binding("replace"))
 dialog.custom_action.connect(func(_a):finish_binding("swap"))
 dialog.canceled.connect(cancel_capture);dialog.popup_centered(Vector2i(700,230))
func finish_binding(policy: String) -> void:
 var err=GTControls.assign(rebind_action,slot_index,pending_key,policy)
 notify(tr2("키 설정 저장 완료","Bindings saved") if err==OK else tr2("저장 실패, 이전 설정 유지: ","Save failed; previous bindings retained: ")+error_string(err))
 cancel_capture();show_controls()
func diagnose(event: InputEventKey) -> void:
 var a=GTControls.recognize(event,true)
 if event.pressed and not a.is_empty():diagnostic_holds[a]=event.physical_keycode
 if not event.pressed:
  for key in diagnostic_holds.keys():
   if diagnostic_holds[key]==event.physical_keycode:diagnostic_holds.erase(key)
func dismiss_practice() -> void:
 onboarding_step=-1
 if is_instance_valid(onboarding):onboarding.queue_free()
 onboarding=null
func set_beginner(value: bool) -> void:
 beginner_mode=value;dismiss_practice();toast_time=0;game.save_preferences()
func mode_choice(col: Node) -> void:
 option(col,tr2("도움 표시","Help display"),[tr2("초보 모드","Beginner mode"),tr2("일반 모드","Normal mode")],0 if beginner_mode else 1,func(i):set_beginner(i==0))
 small(col,tr2("초보: 옆의 작은 도움 버튼 · 일반: 안내 숨김, ","Beginner: small side help button · Normal: hidden, press ")+GTControls.key_text("help")+tr2("로 열기"," to open"))
func help_text(text: String) -> String:
 for action in GTControls.registry:
  text=text.replace("{"+action+"}",GTControls.key_text(action))
 return text
func show_guide() -> void:
 game.pause_game();dismiss_practice()
 var col=menu_base(tr2("무엇을 하고 싶나요?","What would you like to do?"),true);page="guide"
 small(col,tr2("도움말을 읽는 동안 주행은 멈춥니다. 원하는 항목을 고르세요.","Driving is paused while you read. Choose a task below."))
 var row=HBoxContainer.new();col.add_child(row)
 button(row,tr2("닫고 주행 계속","Close and resume") if game.started else tr2("홈으로","Home"),func():game.resume() if game.started else show_home())
 button(row,tr2("키 설정","Keys"),show_controls)
 var categories=help_data.categories
 var keys: Array=categories.keys();var names=[]
 for key in keys:names.append(categories[key][GTControls.language])
 option(col,tr2("분류","Category"),names,maxi(0,keys.find(help_category)),func(i):help_category=keys[i];help_topic="";show_guide())
 if help_topic.is_empty():
  for topic in help_data.topics:
   if topic.category==help_category:
    button(col,topic["title_"+GTControls.language]+"  →",func():help_topic=topic.id;show_guide())
 else:
  for topic in help_data.topics:
   if topic.id!=help_topic:continue
   button(col,tr2("← 항목 목록","← All tasks"),func():help_topic="";show_guide())
   label(col,topic["title_"+GTControls.language],30,accent)
   small(col,help_text(topic["body_"+GTControls.language]))
   if topic.has("gear"):
    small(col,tr2("현재 설정에서 %d단의 회전 제한 속도: 약 %.0f km/h. 권장 변속 속도가 아니라 계산상 한계입니다.","Gear %d reaches the limiter at about %.0f km/h with this setup. This is a calculated ceiling, not a shift recommendation.")%[int(topic.gear),game.car.cfg.gear_speed(int(topic.gear))])
   var action=topic.get("open","")
   if action=="setup":button(col,tr2("차량 설정 열기","Open vehicle setup"),show_setup)
   if action=="performance":button(col,tr2("성능·기어비 보기","Open performance and gearing"),show_performance)
   if action=="camera":button(col,tr2("카메라 설정 열기","Open camera settings"),show_camera)
   if action=="repair":button(col,tr2("차량 손상 복구","Repair vehicle damage"),repair_body)
 small(col,tr2("현재 차량: ","Current car: ")+game.car.selector+tr2(" / %d단 / "," / gear %d / ")%game.car.gear+tr2("자동 변속 ","Shift assist ")+on_off(game.car.automatic)+tr2(" · 자동 클러치 "," · Auto clutch ")+on_off(game.car.auto_clutch))
 mode_choice(col)
func on_off(value: bool) -> String:return tr2("켜짐","On") if value else tr2("꺼짐","Off")
func repair_body() -> void:
 game.car.damage.repair();notify(tr2("긁힘·칠 까짐·찌그러짐·크랙을 복구했습니다.","Scuffs, chips, dents and cracks repaired."))
func show_home() -> void:
 var col=menu_base(tr2("주행을 시작하세요","Take the wheel"));page="home"
 option(col,tr2("언어","Language"),["한국어","English"],0 if GTControls.language=="ko" else 1,func(i):GTControls.language="ko" if i==0 else "en";game.save_preferences();show_home())
 mode_choice(col)
 button(col,tr2("주행 시작  →","Start driving  →"),show_drive)
 button(col,tr2("운전 도움말","Driving help"),show_guide)
 button(col,tr2("차고","Garage"),show_garage)
 button(col,tr2("차량 설정","Vehicle setup"),show_setup)
 button(col,tr2("그래픽","Graphics"),show_graphics)
 button(col,tr2("키 설정","Controls"),show_controls)
 button(col,tr2("종료","Quit"),func():game.finish())
func show_pause() -> void:
 var col=menu_base(tr2("일시정지","Paused"));page="pause"
 button(col,tr2("주행 계속  →","Resume driving  →"),func():game.resume())
 mode_choice(col)
 button(col,tr2("운전 도움말","Driving help"),show_guide)
 button(col,tr2("차량 손상 복구","Repair vehicle damage"),repair_body)
 button(col,tr2("차량 설정","Vehicle setup"),show_setup)
 button(col,tr2("카메라·소리","Camera and audio"),show_camera)
 button(col,tr2("그래픽","Graphics"),show_graphics)
 button(col,tr2("키 설정","Controls"),show_controls)
 button(col,tr2("주행 종류 변경","Choose another drive"),show_drive)
 button(col,tr2("차고로 돌아가기","Return to garage"),func():game.to_garage())
 button(col,tr2("종료","Quit"),func():game.finish())
func show_drive() -> void:
 var col=menu_base(tr2("어디서 달릴까요?","Choose your drive"))
 var modes=["Free Drive","High Speed","Time Trial","Checkpoints"]
 var titles=[tr2("자유 주행","Free drive"),tr2("고속 주행","High speed"),tr2("시간 기록","Time trial"),tr2("체크포인트","Checkpoints")]
 var descriptions=[tr2("교통 차량과 함께 시간 제한 없이 달립니다.","Explore with traffic and no time limit."),tr2("평탄한 고속 구간에서 가속과 최고속도를 측정합니다.","Measure acceleration and top speed on a flat highway."),tr2("3 km 구간의 통과 지점을 순서대로 달립니다.","Follow the ordered gates on a 3 km route."),tr2("제한 시간 안에 여섯 지점을 통과합니다.","Pass six consecutive checkpoints before time runs out.")]
 for i in range(modes.size()):
  button(col,titles[i]+"  →",func():game.start_drive(modes[i]));small(col,descriptions[i])
 back(col)
func back(col: Node) -> void:
 button(col,tr2("← 이전 메뉴","← Back"),func():show_pause() if game.started else show_home())
func start_onboarding() -> void:
 onboarding_step=0;practiced={"throttle":false,"brake":false,"steering":false,"camera":false};onb_start_camera=game.cam.mode
 GTControls.set_context(GTControls.Context.ONBOARDING);rebuild_onboarding()
func rebuild_onboarding() -> void:
 if is_instance_valid(onboarding):onboarding.queue_free()
 onboarding=PanelContainer.new();add_child(onboarding)
 onboarding.set_anchors_and_offsets_preset(Control.PRESET_TOP_LEFT);onboarding.position=Vector2(30,190);onboarding.custom_minimum_size=Vector2(550,0)
 var style=StyleBoxFlat.new();style.bg_color=pane;style.content_margin_left=20;style.content_margin_right=20;style.content_margin_top=15;style.content_margin_bottom=15;onboarding.add_theme_stylebox_override("panel",style)
 var col=VBoxContainer.new();onboarding.add_child(col)
 label(col,tr2("주행 실습","Driving practice")+"  %d / 3"%(onboarding_step+1),26,accent)
 guide_keys.assign([["throttle","brake","left","right","handbrake","camera","look_back","recover"],["transmission","shift_down","shift_up","clutch","neutral","reverse","drive","park"],["ignition","setup","performance","abs","tcs","esc","assist","rev_match","lights","highbeam","left_signal","right_signal","hazards","horn","weather","time","help","pause"]][onboarding_step])
 onb_text=label(col,"",17);onb_text.custom_minimum_size.x=520;onb_text.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
 if onboarding_step>0:button(col,tr2("다음","Next") if onboarding_step<2 else tr2("완료","Finish"),func():onboarding_step+=1;finish_onboarding() if onboarding_step>2 else rebuild_onboarding())
 button(col,tr2("건너뛰기 · 도움말에서 다시 보기","Skip · replay from Guide"),finish_onboarding)
 option(col,"Language",["한국어","English"],0 if GTControls.language=="ko" else 1,func(i):GTControls.language="ko" if i==0 else "en";rebuild_onboarding())
 update_onboarding()
func update_onboarding() -> void:
 if not is_instance_valid(onb_text):return
 var lines: Array[String]=[]
 for a in guide_keys:lines.append(GTControls.key_text(a)+" · "+GTControls.text_for(a))
 if onboarding_step==0:
  lines.append(tr2("실제로 조작하면 자동으로 다음 단계로 넘어갑니다.","Perform the actions to advance automatically."))
  lines.append("가속 %s  제동 %s  조향 %s  카메라 %s"%[mark(practiced.throttle),mark(practiced.brake),mark(practiced.steering),mark(practiced.camera)])
 elif onboarding_step==1:
  lines.append(tr2("R/D: 정차 → 브레이크 → N → R 또는 D.\n자동 클러치·레브매칭은 각각 선택합니다.","R/D: stop → brake → N → R or D.\nAuto clutch and rev matching are separate settings."))
  lines.append(("자동 변속 보조" if game.car.automatic else "순차 수동")+" | "+game.car.selector+" | "+str(game.car.gear)+" | 클러치 보조 "+str(game.car.auto_clutch))
 else:lines.append(tr2("설정은 일시정지 후 적용됩니다. 자세한 사용 조건은 운전 도움말에서 볼 수 있습니다.","Setup changes apply while paused. The Guide explains when each control is available."))
 onb_text.text="\n".join(lines)
func mark(value: bool) -> String:return "✓" if value else "□"
func finish_onboarding() -> void:
 onboarding_step=-1;onboarding_done=true
 if is_instance_valid(onboarding):onboarding.queue_free()
 onboarding=null;GTControls.set_context(GTControls.Context.DRIVING);game.save_preferences()
func show_setup() -> void:
 game.pause_game()
 var col=menu_base(tr2("차량 설정","Vehicle setup"),true)
 small(col,tr2("현재 값 · 기본값 · 단위가 표시됩니다. 성능 변경은 일시정지 중에만 적용됩니다.","Current values, defaults and units. Performance changes apply while paused."))
 var profiles=["Authentic BoP","High Speed","Custom Sandbox"]
 option(col,tr2("성능 모드","Performance profile"),[tr2("실차 규정","Authentic BoP"),tr2("고속","High Speed"),tr2("자유 튜닝","Custom Sandbox")],maxi(0,profiles.find(game.car.cfg.profile)),func(i):game.car.cfg.preset(profiles[i]);show_setup())
 button(col,tr2("성능 / 기어 / 예상치 보기","Performance / gearing / estimates"),show_performance)
 toggle(col,tr2("자동 변속 보조 (6단 순차식)","Auto Shift Assist (6-speed sequential)"),game.car.automatic,func(v):game.car.automatic=v)
 toggle(col,tr2("자동 클러치","Auto clutch"),game.car.auto_clutch,func(v):game.car.auto_clutch=v)
 toggle(col,tr2("레브매칭","Rev matching"),game.car.rev_match,func(v):game.car.rev_match=v)
 if game.car.cfg.profile=="Custom Sandbox":
  option(col,tr2("구동 방식","Custom drive layout"),["RWD","FWD","AWD"],["RWD","FWD","AWD"].find(game.car.cfg.drive_layout),func(i):game.car.cfg.drive_layout=["RWD","FWD","AWD"][i])
 var units={"mass_kg":"kg","max_rpm":"rpm","brake_torque":"Nm","brake_bias":"0–1","spring":"N/m","bump_damping":"Ns/m","rebound_damping":"Ns/m","ride_height":"m","wing_angle_deg":"deg","drag_area":"m²","diff_preload_nm":"Nm","downforce":"ClA m²","aero_front_balance":"0–1","steer_rate":"1/s","steer_return":"1/s","max_steer":"deg"}
 if game.car.cfg.profile!="Custom Sandbox":slider(col,tr2("규정 차량 질량 · kg (기본값 1265)","BoP mass · kg (default 1265)"),game.car.cfg.mass_kg,1250,1265,5,func(v):game.car.cfg.mass_kg=v)
 var base=VehicleConfig.new()
 var metadata=JSON.parse_string(FileAccess.get_file_as_string("res://config/setting_metadata.json"))
 for key in VehicleConfig.RANGES:
  if game.car.cfg.profile!="Custom Sandbox" and key in ["mass_kg","torque_scale","max_rpm","grip_front","grip_rear"]:continue
  var limits=VehicleConfig.RANGES[key]
  if metadata.has(key):small(col,metadata[key][2] if GTControls.language=="ko" else key+" affects the physical simulation; see VEHICLE_PHYSICS.md.")
  slider(col,(metadata[key][1] if GTControls.language=="ko" and metadata.has(key) else key)+" ["+units.get(key,tr2("비율","ratio"))+"]"+tr2(" · 기본값 "," · default ")+str(base.get(key)),game.car.cfg.get(key),limits[0],limits[1],limits[2],func(v):game.car.cfg.set(key,v);game.car.cfg.sanitize())
 if game.car.cfg.profile=="Custom Sandbox":
  for i in range(6):slider(col,tr2("%d단 · 기어비","Gear %d · ratio")%(i+1),game.car.cfg.gear_ratios[i],.5,4.5,.01,func(v):game.car.cfg.gear_ratios[i]=v)
 small(col,tr2("윙·다운포스·차고·공력 밸런스는 항력과 다운포스 양쪽에 영향을 줍니다. ABS/TCS는 0–1 개입 강도입니다.","Wing, lift, ride height and aero balance affect both drag and downforce. ABS/TCS use normalized intervention levels."))
 toggle(col,tr2("타이어 온도 / 마모","Tire temperature / wear"),game.car.cfg.tire_simulation,func(v):game.car.cfg.tire_simulation=v)
 toggle(col,tr2("엔진 스톨","Engine stalling"),game.car.cfg.stall_enabled,func(v):game.car.cfg.stall_enabled=v)
 button(col,tr2("타이어 예열 / 정비","Warm / service tires"),func():game.car.service_tires())
 button(col,tr2("차체 수리","Repair body"),repair_body)
 button(col,tr2("설정 저장","Save settings"),func():game.save_preferences())
 back(col)
func show_performance() -> void:
 game.pause_game()
 var col=menu_base(tr2("성능·기어비","Performance and gearing"),true)
 var cfg=game.car.cfg;var estimate=cfg.performance_estimate()
 var profiles=["Authentic BoP","High Speed","Custom Sandbox"]
 var names=[tr2("실차 규정","Authentic BoP"),tr2("고속","High Speed"),tr2("자유 튜닝","Custom Sandbox")]
 label(col,names[maxi(0,profiles.find(cfg.profile))]+" · "+cfg.drive_layout,28,accent)
 small(col,"%.1f kW / %.1f PS · %d kg · %.1f kW/t"%[estimate.peak_kw,estimate.ps,cfg.mass_kg,estimate.peak_kw/cfg.mass_kg*1000])
 small(col,tr2("4194 cc · 수평대향 6기통 · 6단 순차식 · %.0f rpm","4194 cc · six-cylinder boxer · six-speed sequential · %.0f rpm")%cfg.max_rpm)
 for i in range(1,7):small(col,tr2("%d단: 회전 제한 속도 약 %.0f km/h · 기어비 %.3f","Gear %d: limiter speed about %.0f km/h · ratio %.3f")%[i,cfg.gear_speed(i),cfg.gear_ratios[i-1]])
 small(col,tr2("최종 감속비 %.3f · 윙 %.0f° · 항력 면적 %.3f m² · 다운포스 면적 %.3f m²\n전방 공력 비율 %.0f%% · 전방 제동 비율 %.0f%% · 차동 제한 초기 토크 %.0f Nm\nABS %.2f · TCS %.2f","Final drive %.3f · Wing %.0f° · CdA %.3f m² · ClA %.3f m²\nFront aero %.0f%% · Front brake %.0f%% · Diff preload %.0f Nm\nABS %.2f · TCS %.2f")%[cfg.final_drive,cfg.wing_angle_deg,cfg.effective_drag_area(),cfg.effective_lift_area(),cfg.aero_front_balance*100,cfg.brake_bias*100,cfg.diff_preload_nm,cfg.abs_strength,cfg.tcs_strength])
 small(col,tr2("기어비상 최고속도: %.1f km/h\n항력 포함 예상 최고속도: %.1f km/h\n0–100: %s · 100–200: %s · 200–300: %s","Gear-limited maximum: %.1f km/h\nEstimated reachable speed: %.1f km/h\n0–100: %s · 100–200: %s · 200–300: %s")%[estimate.gear_limited_kph,estimate.reachable_estimate_kph,seconds(estimate.zero_100_s),seconds(estimate["100_200_s"]),seconds(estimate["200_300_s"])])
 small(col,tr2("평지·건조·무풍·예열 타이어를 가정한 계산치입니다. 실측 기록과 다를 수 있으며, 설정에 따라 달라집니다.","Calculated for flat, dry, still-air conditions with warm tyres. Actual results vary with setup and driving."))
 var tires=[]
 for w in game.car.wheels:tires.append(tr2("%.0f°C / 마모 %.1f%%","%.0f°C / %.1f%% wear")%[w.temperature,w.wear*100])
 small(col,tr2("타이어 좌전 / 우전 / 좌후 / 우후: ","Tyres LF / RF / LR / RR: ")+" | ".join(tires))
 for i in range(profiles.size()):button(col,names[i],func():cfg.preset(profiles[i]);show_performance())
 button(col,tr2("상세 설정","Detailed setup"),show_setup);back(col)
func seconds(v: float) -> String:return "%.1f s"%v if v>=0 else tr2("도달하지 않음","Not reached")
