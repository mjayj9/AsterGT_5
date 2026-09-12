from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'outputs/AsterGT'
def edit(path,old,new):
 p=P/path;s=p.read_text(encoding='utf-8');assert old in s,(path,old[:100]);p.write_text(s.replace(old,new),encoding='utf-8')
edit('project.godot','GT3 v4','GT3 v5')
edit('project.godot','AsterGT-v4','AsterGT-v5')
edit('export_presets.cfg','../Windows-v4-pre-qa/AsterGT-v4-pre-qa.exe','../Windows-v5/AsterGT-v5.exe')
edit('scripts/contact_damage.gd','var impact: float=0','var impact: float=0\nvar visuals=GTLocalDamageVisual.new()')
edit('scripts/contact_damage.gd',' var impacted=false',' var impacted=false\n var candidates: Dictionary={}')
edit('scripts/contact_damage.gd','  var kind="vehicle"','  var source="solver_impulse"\n  # First-tick Godot contacts may expose zero impulse. Estimate incoming normal\n  # energy only for damage; never add a second physics response impulse.\n  var closing=maxf(0,-relative.dot(raw_normal.normalized()))\n  if impulse.length()<.001 and closing>1.0 and inverse_mass>0:\n   energy=.5*closing*closing/inverse_mass;source="incoming_speed_estimate"\n  var kind="vehicle"')
edit('scripts/contact_damage.gd','"normal_energy_estimate_j":energy','"energy_source":source,"normal_energy_estimate_j":energy')
p=P/'scripts/contact_damage.gd';s=p.read_text(encoding='utf-8');s=s[:s.index('  if impulse.length()>settings.contact_min_impulse_ns:')]+'''  if kind!="road" and energy>=120:
   row["point_local_m"]=[local.x,local.y,local.z]
   if not candidates.has(id) or energy>candidates[id].energy:
    var outward=-(physics.transform.basis.inverse()*raw_normal).normalized()
    var tangent=physics.transform.basis.inverse()*(relative-raw_normal*relative.dot(raw_normal))
    candidates[id]={"energy":energy,"point":local,"outward":outward,"tangent":tangent,"row":row,"zone":zone}
 for id in candidates:
  var hit=candidates[id]
  var prior=recent.get(id,{"time":-100.0,"point":Vector3.INF})
  if time_s-prior.time<settings.contact_damage_cooldown_s:continue
  recent[id]={"time":time_s,"point":hit.point}
  GTQA.record("contact",hit.row)
  if visuals.add_hit(hit.point,hit.outward,hit.tangent,hit.energy,hit.tangent.length()):
   var severity=clampf(hit.energy/settings.damage_energy_j,0,1)
   state[hit.zone]=clampf(state[hit.zone]+severity*.35,0,1)
   state.body=clampf(state.body+severity*.15,0,1)
   state.lights=maxf(state.front,state.rear)
   state.steering=maxf(state.left,state.right)*.35
   state.power=maxf(state.front,state.rear)*.35
   impact=maxf(impact,severity);impacted=impacted or severity>.015
 return impacted
func apply_visuals(root: Node3D) -> void:
 visuals.apply(root)
func repair() -> void:
 visuals.repair();recent.clear();last_contacts.clear();impact=0
 for key in state:state[key]=0.0
''';p.write_text(s,encoding='utf-8')
edit('scripts/driving_ui.gd','game.car.damage=GTContactDamage.new()','game.car.damage.repair()')
edit('scripts/main.gd',' if not hud.onboarding_done:hud.start_onboarding()\n else:hud.notify("가속 "+GTControls.key_text("throttle")+" · 도움말 "+GTControls.key_text("help"))',' # Help is opt-in: beginner side button, or F1 in either mode.\n hud.dismiss_practice()')
edit('scripts/main.gd','"onboarding_done":hud.onboarding_done','"beginner_mode":hud.beginner_mode,"onboarding_done":hud.onboarding_done')
edit('scripts/main.gd',' if d.get("onboarding_done") is bool:',' if d.get("beginner_mode") is bool:hud.beginner_mode=d.beginner_mode\n if d.get("onboarding_done") is bool:')
edit('scripts/hud.gd','  txt(GTControls.key_text("camera")+" 카메라  "+GTControls.key_text("help")+" 도움말  "+GTControls.key_text("pause")+" 메뉴",Vector2(42,1060),16,dim)','  # Driving hints live in the requested help panel, not over the road.')
edit('scripts/driving_ui.gd','var onb_start_camera: int=0','var onb_start_camera: int=0\nvar beginner_mode: bool=true\nvar help_button: Button\nvar help_category: String="start"\nvar help_topic: String=""\nvar help_data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://config/driving_help.json"))')
edit('scripts/driving_ui.gd',' mouse_menu.pressed.connect(func():game.pause_game();show_pause())',' mouse_menu.pressed.connect(func():game.pause_game();show_pause())\n help_button=Button.new();add_child(help_button);help_button.focus_mode=Control.FOCUS_NONE\n help_button.anchor_left=1;help_button.anchor_right=1;help_button.offset_left=-160;help_button.offset_right=-40;help_button.offset_top=196;help_button.offset_bottom=242\n help_button.add_theme_font_size_override("font_size",20)\n help_button.pressed.connect(show_guide)')
edit('scripts/driving_ui.gd',' mouse_menu.visible=game.started and page=="";mouse_menu.text=tr2("메뉴","Menu")',' mouse_menu.visible=game.started and page=="";mouse_menu.text=tr2("메뉴","Menu")\n help_button.visible=beginner_mode and game.started and page=="" and onboarding_step<0\n help_button.text=tr2("? 도움","? Help")')
edit('scripts/driving_ui.gd','("Primary · " if row.slot==0 else "Secondary · ")','(tr2("기본 키 · ","Primary · ") if row.slot==0 else tr2("보조 키 · ","Secondary · "))')
p=P/'scripts/driving_ui.gd';s=p.read_text(encoding='utf-8');a=s.index(' if first_minutes<300');b=s.index('func clear_menu()',a);s=s[:a]+s[b:];a=s.index('func show_guide()');b=s.index('func start_onboarding()',a)
s=s[:a]+'''func dismiss_practice() -> void:
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
''' + s[b:]
s=s.replace('var profiles=["Authentic BoP","High Speed","Custom Sandbox"]','var profiles=["Authentic BoP","High Speed","Custom Sandbox"]')
s=s.replace('profiles,maxi(0,profiles.find(game.car.cfg.profile))','[tr2("실차 규정","Authentic BoP"),tr2("고속","High Speed"),tr2("자유 튜닝","Custom Sandbox")],maxi(0,profiles.find(game.car.cfg.profile))')
s=s.replace('" · default "','tr2(" · 기본값 "," · default ")').replace('"ratio")','tr2("비율","ratio"))')
s=s.replace('"front 0–1"','"0–1"')
s=s.replace('"BoP mass · kg (default 1265)"','tr2("규정 차량 질량 · kg (기본값 1265)","BoP mass · kg (default 1265)")')
s=s.replace('"Gear "+str(i+1)+" · ratio"','tr2("%d단 · 기어비","Gear %d · ratio")%(i+1)')
s=s.replace('"Custom drive layout"','tr2("구동 방식","Custom drive layout")')
s=s.replace('func():game.car.damage.repair();notify(tr2("수리했습니다.","Repaired."))','repair_body')
s=s.replace('Choose a Primary / Secondary slot.','Choose a Primary / Secondary slot.').replace('Primary / Secondary 슬롯을 선택하십시오.','기본 키 / 보조 키 슬롯을 선택하십시오.')
s=s.replace('("Primary" if index==0 else "Secondary")','(tr2("기본 키","Primary") if index==0 else tr2("보조 키","Secondary"))')
s=s.replace('small(col,"Esc: 취소 / Cancel · Backspace: 비우기 / Clear")','small(col,tr2("Esc: 취소 · Backspace: 비우기","Esc: Cancel · Backspace: Clear"))')
p.write_text(s,encoding='utf-8')
print('v5 source modifications applied')
