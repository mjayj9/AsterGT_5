from pathlib import Path
p=Path(r'C:/Users/admin/Documents/Codex/2026-09-08/fable-5-1-vs-fable-at-4/outputs/AsterGT')
f=p/'scripts/car.gd';s=f.read_text(encoding='utf-8-sig')
s=s.replace('var rpm: float=850','var rpm: float=1200')
s=s.replace('var dashboard: Label3D','''var dashboard: Label3D
var damage=GTContactDamage.new()
var manual_override: float=0
var clutch_engagement: float=0
var shift_status: String="READY"
var shift_cut: bool=false
var reengage_timer: float=0
var shaft_delta_rpm: float=0
var acceleration_local=Vector3.ZERO
var road_vibration: float=0
var last_suspension: float=0
var lod_visuals: Array[Node3D]=[]
var visual_timer: float=0
signal shift_feedback(event: Dictionary)
''')
s=s.replace('res://assets/porsche_rig.json','res://assets/v4/porsche_rig.json')
s=s.replace('res://assets/porsche_992_gt3_r.glb','res://assets/v4/porsche_lod0.glb')
a=s.index(' var shape=CollisionShape3D.new();var box=BoxShape3D.new()')
b=s.index(' for i in range(4):',a)
s=s[:a]+''' var proxies=JSON.parse_string(FileAccess.get_file_as_string("res://assets/v4/collision_proxies.json"))
 for proxy in proxies.player:
  var shape=CollisionShape3D.new();shape.name=proxy.name
  var convex=ConvexPolygonShape3D.new();var points=PackedVector3Array()
  for v in proxy.vertices:points.append(Vector3(v[0],v[1],v[2]))
  convex.points=points;shape.shape=convex;add_child(shape)
'''+s[b:]
s=s.replace('max_contacts_reported=8','max_contacts_reported=16').replace('mat.friction=0.3;mat.bounce=0.08','mat.friction=0.45;mat.bounce=0.05')
s=s.replace('  var radius=cfg.wheel_radius','  var radius=cfg.front_wheel_radius if i<2 else cfg.wheel_radius')
a=s.index('func set_selector(');b=s.index('func recover(',a)
s=s[:a]+'''func report_shift(kind: String,reason: String="") -> void:
 shift_status=reason if not reason.is_empty() else kind
 var row={"time_s":simulation_time,"kind":kind,"reason":reason,"gear":gear,"rpm":rpm,"auto_shift_assist":automatic,"auto_clutch":auto_clutch,"rev_match":rev_match}
 shift_feedback.emit(row);GTQA.record("shift",row)
 if not reason.is_empty():notice.emit(reason)
func set_selector(value: String) -> bool:
 if not value in ["P","R","N","D"]:return false
 if value==selector:return true
 if shift_timer>0:report_shift("rejected","변속 중입니다.");return false
 if not auto_clutch and clutch<.8:report_shift("rejected","클러치를 누르십시오: "+GTControls.key_text("clutch"));return false
 if value in ["P","R","D"]:
  if absf(forward_speed)>cfg.minimum_selector_speed_mps:report_shift("rejected","완전히 정차한 후 선택하십시오.");return false
  if brake<.3 and _input_value("brake")<.3:report_shift("rejected","브레이크를 누르십시오: "+GTControls.key_text("brake"));return false
  if value in ["R","D"] and selector not in ["N","P"]:report_shift("rejected","먼저 중립을 선택하십시오: "+GTControls.key_text("neutral"));return false
 selector=value;gear=1 if value=="D" else -1 if value=="R" else 0
 shift_timer=cfg.shift_time;report_shift("selector_success");return true
func toggle_transmission() -> void:
 automatic=not automatic
 notice.emit("자동 변속 보조 ON · 6단 순차식" if automatic else "순차 수동 · "+GTControls.key_text("shift_down")+" / "+GTControls.key_text("shift_up"))
func manual_shift(direction: int) -> bool:
 report_shift("request")
 if gear<1:report_shift("rejected","전진 셀렉터를 먼저 선택하십시오: "+GTControls.key_text("drive"));return false
 if shift_timer>0 or shift_cooldown>0:report_shift("rejected","변속이 끝날 때까지 기다리십시오.");return false
 if not auto_clutch and clutch<.8:report_shift("rejected","클러치를 누르십시오: "+GTControls.key_text("clutch"));return false
 var target=gear+direction
 if target<1 or target>6:report_shift("rejected","전진 기어 범위는 1–6단입니다. N/R은 별도 셀렉터를 사용합니다.");return false
 var predicted=absf(forward_speed)/cfg.wheel_radius*cfg.gear_ratios[target-1]*cfg.final_drive*60/TAU
 if predicted>cfg.max_rpm:report_shift("rejected","현재 속도에서 다운시프트하면 오버레브가 발생합니다.");return false
 manual_override=cfg.override_seconds if automatic else 0
 engage_shift(target);return true
func engage_shift(target: int) -> void:
 shaft_delta_rpm=rpm-absf(forward_speed)/cfg.wheel_radius*cfg.gear_ratios[target-1]*cfg.final_drive*60/TAU
 gear=target;shift_timer=cfg.shift_time;shift_cooldown=cfg.shift_cooldown_s;reengage_timer=cfg.shift_time*2
 report_shift("success","변속 성공 · "+str(gear)+"단")
'''+s[b:]
s=s.replace('Input.get_action_strength(action) if InputMap.has_action(action) else 0.0','GTControls.value(action)')
s=s.replace(' shift_timer=maxf(0,shift_timer-dt);shift_cooldown=maxf(0,shift_cooldown-dt)',' shift_timer=maxf(0,shift_timer-dt);shift_cooldown=maxf(0,shift_cooldown-dt);manual_override=maxf(0,manual_override-dt)\n shift_cut=shift_timer>0\n if not shift_cut:reengage_timer=maxf(0,reengage_timer-dt)')
s=s.replace('if automatic or auto_clutch:', 'if auto_clutch:')
s=s.replace('if not automatic and clutch>0.05:', 'if clutch>0.05:')
s=s.replace('cfg.idle_rpm if automatic or auto_clutch else 350','cfg.idle_rpm if auto_clutch else 350')
s=s.replace('(automatic or auto_clutch)','auto_clutch').replace('(automatic or rev_match)','rev_match').replace('not automatic and not auto_clutch','not auto_clutch')
s=s.replace('cfg.idle_rpm+throttle*1850','cfg.idle_rpm+throttle*cfg.launch_slip_rpm')
s=s.replace(' if shift_timer>0: target_rpm=', ' if shift_timer>0: target_rpm=')
s=s.replace(' var free_rpm=', ' clutch_engagement=engagement\n var free_rpm=')
a=s.index(' if automatic and selector=="D"');b=s.index(' var old_slip=',a)
s=s[:a]+''' if automatic and selector=="D" and manual_override<=0 and shift_timer==0 and shift_cooldown==0 and (auto_clutch or clutch>.8):
  var up_at=lerpf(4800,cfg.redline_rpm,throttle)
  if rpm>up_at and gear<6 and engagement>.9 and brake<.05 and throttle>.05:
   engage_shift(gear+1)
  elif gear>1:
   var lower_rpm=axle_rpm*cfg.gear_ratios[gear-2]/cfg.gear_ratios[gear-1]
   var down_at=5200 if throttle>.7 else 3800
   if (rpm<down_at or brake>.4 and rpm<5500) and lower_rpm<cfg.redline_rpm*.94:
    engage_shift(gear-1)
 ratio=get_ratio()
 var effective_throttle=throttle
'''+s[b:]
s=s.replace('var torque=cfg.torque_at(rpm)*effective_throttle','var torque=cfg.torque_at(rpm)*effective_throttle*(1-damage.state.power)')
s=s.replace(' var wheel_torque=torque*ratio*cfg.drivetrain_efficiency/maxi(1,drive_count)',''' if reengage_timer>0 and not shift_cut:
  var coupling=clampf(1-reengage_timer/(cfg.shift_time*2),0,1)
  torque=torque*coupling+clampf(shaft_delta_rpm*TAU/60*cfg.engine_inertia_kgm2/cfg.shift_time,-80,80)*coupling
  shaft_delta_rpm=move_toward(shaft_delta_rpm,0,12000*dt)
 var wheel_torque=torque*ratio*cfg.drivetrain_efficiency/maxi(1,drive_count)''')
s=s.replace('steering*deg_to_rad(cfg.max_steer)','steering*(1-damage.state.steering)*deg_to_rad(cfg.max_steer)')
s=s.replace('clampf((partner-w.omega)*cfg.diff_lock*30,-400,400)','clampf((partner-w.omega)*cfg.diff_lock*30,-cfg.diff_preload_nm,cfg.diff_preload_nm)')
s=s.replace('for sub in range(8):','for sub in range(cfg.tire_substeps):').replace('dt/8.0','dt/float(cfg.tire_substeps)').replace('fx_sum+=fx/8.0','fx_sum+=fx/float(cfg.tire_substeps)')
a=s.index(' state.apply_central_force(-v*v.length()');b=s.index(' var target_yaw=',a)
s=s[:a]+''' state.apply_central_force(-v*v.length()*0.5*cfg.air_density*cfg.effective_drag_area())
 if grounded>0:
  var aero=.5*cfg.air_density*cfg.effective_lift_area()*forward_speed*forward_speed
  state.apply_force(-up*aero*cfg.aero_front_balance,basis*Vector3(0,0,-cfg.wheelbase*.5))
  state.apply_force(-up*aero*(1-cfg.aero_front_balance),basis*Vector3(0,0,cfg.wheelbase*.5))
'''+s[b:]
a=s.index(' collision_energy=maxf(0,collision_energy-dt*4)');b=s.index('\nfunc toggle_ignition',a)
s=s[:a]+''' damage.sample(self,state,simulation_time);collision_energy=damage.impact
 acceleration_local=acceleration_local.lerp(basis.inverse()*(state.linear_velocity-last_velocity)/dt,1-exp(-10*dt))
 var suspension=0.0
 for w in wheels:suspension+=w.length*.25
 road_vibration=lerpf(road_vibration,clampf((suspension-last_suspension)/dt,-3,3),1-exp(-20*dt))
 last_suspension=suspension;last_velocity=state.linear_velocity
'''+s[b:]
s=s.replace('last_velocity=Vector3.ZERO\n  stall_timer','last_velocity=Vector3.ZERO;acceleration_local=Vector3.ZERO;road_vibration=0\n  stall_timer')
s=s.replace('"automatic":automatic,','"automatic":automatic,"auto_shift_assist":automatic,"auto_clutch":auto_clutch,"rev_match":rev_match,"shift_cut":shift_cut,"clutch_engagement":clutch_engagement,"manual_override_s":manual_override,"damage":damage.state.duplicate(),"contacts":damage.last_contacts.duplicate(true),"velocity_mps":[linear_velocity.x,linear_velocity.y,linear_velocity.z],"angular_velocity_rad_s":[angular_velocity.x,angular_velocity.y,angular_velocity.z],')
s=s.replace('func _process(_delta: float) -> void:', '''func _process(_delta: float) -> void:
 visual_timer+=_delta
 if visual_timer>.1:damage.apply_visuals(body_visual);visual_timer=0''')
s=s.replace('light_nodes[k].visible=headlights','light_nodes[k].visible=headlights and damage.state.lights<.8')
s=s.replace('spot_range=120 if highbeam else 65','spot_range=180 if highbeam else 105')
s=s.replace('material.albedo_color=Color(.68,.80,.85,.22)','material.metallic=0;material.albedo_color=Color(.68,.80,.85,.20)')
f.write_text(s,encoding='utf8')
print('car sequential controls, contact observation, aero and dimensions updated')
