from pathlib import Path
p=Path(r'C:/Users/admin/Documents/Codex/2026-09-08/fable-5-1-vs-fable-at-4/outputs/AsterGT')
f=p/'scripts/driving_ui.gd';s=f.read_text(encoding='utf8').replace('var modal: Window','var modal: Window\nvar capture_panel: Control')
a=s.index(' var dialog=AcceptDialog.new()');b=s.index('\nfunc cancel_capture',a)
s=s[:a]+''' capture_panel=ColorRect.new();capture_panel.color=Color(0,0,0,.75);capture_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT);add_child(capture_panel)
 var panel=PanelContainer.new();capture_panel.add_child(panel);panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER);panel.offset_left=-340;panel.offset_right=340;panel.offset_top=-160;panel.offset_bottom=160
 var col=VBoxContainer.new();panel.add_child(col)
 label(col,tr2("키 입력 대기","Waiting for a key"),32,accent)
 label(col,GTControls.text_for(a)+" · "+("Primary" if index==0 else "Secondary"),28)
 small(col,"Esc: 취소 / Cancel · Backspace: 비우기 / Clear")
 small(col,"Ctrl / Alt / Shift + Key")
 button(col,tr2("취소","Cancel"),cancel_capture)
'''+s[b:]
s=s.replace(' rebind_action="";pending_key={};conflict_info={}',' rebind_action="";pending_key={};conflict_info={}\n if is_instance_valid(capture_panel):capture_panel.queue_free()\n capture_panel=null')
s=s.replace('수동 클러치 OFF는 자동 클러치 사용을 뜻합니다.','자동 클러치·레브매칭은 각각 선택합니다.')
f.write_text(s,encoding='utf8')
f=p/'scripts/car.gd';s=f.read_text(encoding='utf8')
s=s.replace('engagement=clampf(absf(forward_speed)/4.5,0.0,1.0)','engagement=clampf(maxf(absf(forward_speed)/4.5,throttle*.65),0.0,1.0)')
s=s.replace(' if not auto_clutch:torque*=1-clutch',' torque*=engagement')
s=s.replace('and engagement>.9 and brake<.05','and (engagement>.9 if auto_clutch else clutch>.8) and brake<.05')
s=s.replace('notice.emit("Engine stalled — hold clutch and press ENTER")','notice.emit("엔진 스톨: 클러치 "+GTControls.key_text("clutch")+" 후 시동 "+GTControls.key_text("ignition"))')
# LOD1 at typical chase distance; cockpit always keeps LOD0 and dashboard.
s=s.replace('var lod_visuals: Array[Node3D]=[]','var lod_visuals: Array[Node3D]=[]\nvar lod_wheels: Array=[]\nvar active_lod: int=0')
s=s.replace('  for side in [-1,1]:\n   var lamp=SpotLight3D.new();lamp.position=Vector3(side*.72', '''  for level in range(1,4):
   var lod=load("res://assets/v4/porsche_lod%d.glb"%level).instantiate();add_child(lod);lod.hide();lod_visuals.append(lod)
   var pivots=[]
   for tag in ["LF","RF","LR","RR"]:pivots.append(lod.find_child("*Wheel_"+tag+"*",true,false))
   lod_wheels.append(pivots)
  for side in [-1,1]:
   var lamp=SpotLight3D.new();lamp.position=Vector3(side*.72''')
s=s.replace(' if visual_timer>.1:damage.apply_visuals(body_visual);visual_timer=0',''' if visual_timer>.1:
  damage.apply_visuals(body_visual)
  for lod in lod_visuals:damage.apply_visuals(lod)
  visual_timer=0
 for level in range(lod_wheels.size()):
  if not lod_visuals[level].visible:continue
  for i in range(4):
   var pivot=lod_wheels[level][i]
   if pivot:pivot.position=wheel_visuals[i].position;pivot.rotation=wheel_visuals[i].rotation''')
s+='''\nfunc update_lod(distance_m: float,cockpit: bool) -> void:
 if lod_visuals.size()!=3:return
 var wanted=0 if cockpit or distance_m<6 else 1 if distance_m<25 else 2 if distance_m<75 else 3
 active_lod=wanted;body_visual.visible=wanted==0
 for wheel in wheel_visuals:wheel.visible=wanted==0
 for caliper in calipers:caliper.visible=wanted==0
 for i in range(3):lod_visuals[i].visible=wanted==i+1
'''
f.write_text(s,encoding='utf8')
f=p/'scripts/camera_rig.gd';s=f.read_text(encoding='utf8').replace(' first=false',' car.update_lod(camera.global_position.distance_to(car.global_position),mode==3 and not menu_preview)\n first=false');f.write_text(s,encoding='utf8')
print('capture isolation, clutch coupling and runtime LOD connected')
