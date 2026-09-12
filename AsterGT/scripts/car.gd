class_name GTCar
extends RigidBody3D
signal notice(message: String)
var cfg = preload("res://config/street.tres").duplicate(true)
var throttle: float=0
var brake: float=0
var steering: float=0
var clutch: float=0
var handbrake: bool=false
var automatic: bool=true
var auto_clutch: bool=true
var rev_match: bool=true
var engine_on: bool=true
var selector: String="D"
var gear: int=1
var rpm: float=1200
var shift_timer: float=0
var shift_cooldown: float=0
var speed_kph: float=0
var forward_speed: float=0
var wetness: float=0
var abs_enabled: bool=true
var tcs_enabled: bool=true
var esc_enabled: bool=true
var abs_active: bool=false
var tcs_active: bool=false
var esc_active: bool=false
var grounded: int=0
var max_slip: float=0
var collision_energy: float=0
var odometer: float=0
var test_input: Dictionary={}
var controls_enabled: bool=true
var launch_hold: bool=false
var wheels: Array[Dictionary]=[]
var wheel_visuals: Array[Node3D]=[]
var body_visual: Node3D
var light_nodes: Dictionary={}
var headlights: bool=false
var highbeam: bool=false
var indicator: int=0
var hazards: bool=false
var simulation_time: float=0
var pending_reset: Transform3D
var reset_requested: bool=false
var last_velocity=Vector3.ZERO
var paint=Color("d4d7d8")
var stall_timer: float=0
var engine_load: float=0
var imported_model: bool=false
var vehicle_rig: Dictionary={}
var wheel_radii: Array[float]=[]
var chassis_base_y: float=0
var visual_lamps: Array[Dictionary]=[]
var steering_wheel: Node3D
var calipers: Array[Node3D]=[]
var dashboard: Label3D
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
var lod_wheels: Array=[]
var active_lod: int=0
var visual_timer: float=0
signal shift_feedback(event: Dictionary)


func _ready() -> void:
 if FileAccess.file_exists("res://assets/v4/porsche_rig.json"):
  vehicle_rig=JSON.parse_string(FileAccess.get_file_as_string("res://assets/v4/porsche_rig.json"))
  cfg.wheelbase=vehicle_rig.wheelbase
  cfg.wheel_radius=(vehicle_rig.radii.LR+vehicle_rig.radii.RR)*.5
 mass=cfg.mass_kg
 center_of_mass_mode=RigidBody3D.CENTER_OF_MASS_MODE_CUSTOM
 center_of_mass=cfg.center_of_mass
 inertia=cfg.inertia_at_reference_mass*cfg.mass_kg/cfg.reference_mass
 linear_damp=0; linear_damp_mode=RigidBody3D.DAMP_MODE_REPLACE; angular_damp=0.25; angular_damp_mode=RigidBody3D.DAMP_MODE_REPLACE
 continuous_cd=true;can_sleep=false
 contact_monitor=true;max_contacts_reported=16
 collision_layer=2;collision_mask=1|4
 var mat=PhysicsMaterial.new();mat.friction=0.45;mat.bounce=0.05;physics_material_override=mat
 var proxies=JSON.parse_string(FileAccess.get_file_as_string("res://assets/v4/collision_proxies.json"))
 for proxy in proxies.player:
  var shape=CollisionShape3D.new();shape.name=proxy.name
  var convex=ConvexPolygonShape3D.new();var points=PackedVector3Array()
  for v in proxy.vertices:points.append(Vector3(v[0],v[1],v[2]))
  convex.points=points;shape.shape=convex;add_child(shape)
 for i in range(4):
  var tag=["LF","RF","LR","RR"][i]
  var mount=Vector3((-1 if i%2==0 else 1)*cfg.track/2,0.05,(-1 if i<2 else 1)*cfg.wheelbase/2)
  var radius=cfg.front_wheel_radius if i<2 else cfg.wheel_radius
  if vehicle_rig.has("centers"):
   var pair=["LF","RF"] if i<2 else ["LR","RR"]
   var a=vehicle_rig.centers[pair[0]];var b=vehicle_rig.centers[pair[1]]
   mount=Vector3((-1 if i%2==0 else 1)*(absf(a[0])+absf(b[0]))*.5,(a[1]+b[1])*.5+cfg.ride_height-cfg.mass_kg*9.81/(4*cfg.spring),(a[2]+b[2])*.5)
   radius=(vehicle_rig.radii[pair[0]]+vehicle_rig.radii[pair[1]])*.5
  if vehicle_rig.has("mounts"):
   var fixed_mount=vehicle_rig.mounts[tag];mount=Vector3(fixed_mount[0],fixed_mount[1],fixed_mount[2])
  wheel_radii.append(radius)
  wheels.append({"mount":mount,"omega":0.0,"spin":0.0,"length":cfg.ride_height,"load":0.0,"slip":0.0,"angle":0.0,"ground":false,"surface":"asphalt","temperature":cfg.tire_optimal_c,"wear":0.0,"grip_factor":1.0})
 build_visuals()
 cache_details()
 cache_lod_lamps()

func build_visuals() -> void:
 if ResourceLoader.exists("res://assets/v4/porsche_lod0.glb"):
  imported_model=true
  body_visual=load("res://assets/v4/porsche_lod0.glb").instantiate();add_child(body_visual)
  for tag in ["LF","RF","LR","RR"]:
   var pivot=body_visual.find_child("Wheel_"+tag,true,false) as Node3D
   pivot.reparent(self,true);wheel_visuals.append(pivot)
   var caliper=body_visual.find_child("Caliper_"+tag,true,false) as Node3D
   caliper.reparent(self,true);calipers.append(caliper)
  for level in range(1,4):
   var lod=load("res://assets/v4/porsche_lod%d.glb"%level).instantiate();add_child(lod);lod.hide();lod_visuals.append(lod)
   var pivots=[]
   for tag in ["LF","RF","LR","RR"]:pivots.append(lod.find_child("*Wheel_"+tag+"*",true,false))
   lod_wheels.append(pivots)
  for side in [-1,1]:
   var lamp=SpotLight3D.new();lamp.position=Vector3(side*.72,-.23,-2.04);lamp.light_color=Color(.93,.97,1);lamp.spot_range=90;lamp.spot_angle=29;lamp.rotation_degrees.x=-3;lamp.light_energy=9;lamp.visible=false;add_child(lamp);light_nodes["head"+str(side)]=lamp
  return
 body_visual=Node3D.new();add_child(body_visual)
 if ResourceLoader.exists("res://assets/aster_gt.glb"):
  var model=load("res://assets/aster_gt.glb").instantiate();body_visual.add_child(model)
  for node in model.find_children("*","Node3D",true,false):
   if node.name.begins_with("Wheel_"): node.hide()
 else:
  var m=MeshInstance3D.new();var mesh=BoxMesh.new();mesh.size=Vector3(1.86,0.5,4.4);m.mesh=mesh
  var material=StandardMaterial3D.new();material.albedo_color=paint;material.metallic=0.75;material.roughness=0.27;m.material_override=material;body_visual.add_child(m)
 for i in range(4):
  var pivot=Node3D.new();pivot.position=wheels[i].mount-Vector3.UP*(cfg.ride_height-.085);add_child(pivot);wheel_visuals.append(pivot)
  if ResourceLoader.exists("res://assets/wheel.glb"):
   var model=load("res://assets/wheel.glb").instantiate();pivot.add_child(model)
   if i%2==0: model.rotation.y=PI
  else:
   var m=MeshInstance3D.new();var tire=CylinderMesh.new();tire.top_radius=cfg.wheel_radius;tire.bottom_radius=cfg.wheel_radius;tire.height=0.27;m.mesh=tire;m.rotation.z=PI/2
   var material=StandardMaterial3D.new();material.albedo_color=Color("151719");m.material_override=material;pivot.add_child(m)
 for side in [-1,1]:
  var lamp=SpotLight3D.new();lamp.position=Vector3(side*0.67,-0.15,-2.15);lamp.light_color=Color(0.86,0.94,1);lamp.spot_range=75;lamp.spot_angle=30;lamp.rotation_degrees.x=-4;lamp.light_energy=8;lamp.visible=false;add_child(lamp);light_nodes["head"+str(side)]=lamp

func report_shift(kind: String,reason: String="") -> void:
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
func recover(at: Transform3D) -> void:
 pending_reset=at;reset_requested=true
func _input_value(action: String) -> float:
 if action=="brake" and launch_hold:return 1.0
 if not controls_enabled: return 0.0
 return float(test_input.get(action,GTControls.value(action)))
func _integrate_forces(state: PhysicsDirectBodyState3D) -> void:
 var dt=state.step
 if reset_requested:
  state.transform=pending_reset;state.linear_velocity=Vector3.ZERO;state.angular_velocity=Vector3.ZERO
  for w in wheels: w.omega=0;w.slip=0
  throttle=0;brake=0;steering=0;rpm=cfg.idle_rpm;last_velocity=Vector3.ZERO;acceleration_local=Vector3.ZERO;road_vibration=0
  stall_timer=0
  reset_requested=false;return
 simulation_time+=dt
 if mass!=cfg.mass_kg:
  mass=cfg.mass_kg;inertia=cfg.inertia_at_reference_mass*cfg.mass_kg/cfg.reference_mass
 var basis=state.transform.basis
 var forward=-basis.z
 var up=basis.y
 forward_speed=state.linear_velocity.dot(forward)
 speed_kph=state.linear_velocity.length()*3.6
 odometer+=state.linear_velocity.length()*dt
 throttle=move_toward(throttle,_input_value("throttle"),cfg.throttle_rate*dt)
 brake=move_toward(brake,_input_value("brake"),cfg.brake_rate*dt)
 var steering_target=_input_value("left")-_input_value("right")
 steering=move_toward(steering,steering_target,(cfg.steer_return if absf(steering_target)<0.1 else cfg.steer_rate)*dt)
 clutch=move_toward(clutch,_input_value("clutch"),8*dt)
 handbrake=_input_value("handbrake")>0.5
 var steer_angle=steering*(1-damage.state.steering)*deg_to_rad(cfg.max_steer)/(1.0+absf(forward_speed)*cfg.steering_speed_factor)
 shift_timer=maxf(0,shift_timer-dt);shift_cooldown=maxf(0,shift_cooldown-dt);manual_override=maxf(0,manual_override-dt)
 shift_cut=shift_timer>0
 if not shift_cut:reengage_timer=maxf(0,reengage_timer-dt)
 var drive_omega=0.0;var drive_count=0
 for i in range(4):
  if is_driven(i):drive_omega+=wheels[i].omega;drive_count+=1
 drive_omega/=maxi(1,drive_count)
 var ratio=get_ratio()
 var axle_rpm=absf(drive_omega*ratio)*60.0/TAU
 var engagement=1.0-clutch
 if auto_clutch:
  engagement=clampf(maxf(absf(forward_speed)/cfg.auto_clutch_full_speed_mps,throttle*cfg.auto_launch_engagement),0.0,1.0)
  if clutch>0.05: engagement*=1.0-clutch
 if shift_timer>0 or gear==0: engagement=0
 clutch_engagement=engagement
 var free_rpm=cfg.idle_rpm+throttle*(cfg.max_rpm-cfg.idle_rpm)
 var coupled_rpm=maxf(cfg.idle_rpm if auto_clutch else 350,axle_rpm)
 var target_rpm=lerpf(free_rpm,coupled_rpm,engagement)
 if auto_clutch and gear!=0 and shift_timer<=0:
  target_rpm=lerpf(cfg.idle_rpm+throttle*cfg.launch_slip_rpm,coupled_rpm,engagement)
 if shift_timer>0: target_rpm=maxf(cfg.idle_rpm,axle_rpm if rev_match else rpm-900)
 if shift_cut:shaft_delta_rpm=rpm-axle_rpm
 if not engine_on: target_rpm=0
 rpm=clampf(lerpf(rpm,target_rpm,1-exp(-cfg.rpm_response_per_s*dt)),0,cfg.max_rpm)
 if cfg.stall_enabled and engine_on and not auto_clutch and gear!=0 and clutch<.35 and rpm<cfg.stall_rpm and shift_timer<=0:
  stall_timer+=dt
  if stall_timer>=cfg.stall_delay:engine_on=false;notice.emit("엔진 스톨: 클러치 "+GTControls.key_text("clutch")+" 후 시동 "+GTControls.key_text("ignition"))
 else:stall_timer=0
 if automatic and selector=="D" and manual_override<=0 and shift_timer==0 and shift_cooldown==0 and (auto_clutch or clutch>.8):
  var up_at=lerpf(cfg.upshift_min_rpm,cfg.redline_rpm,throttle)
  if rpm>up_at and gear<6 and (engagement>.9 if auto_clutch else clutch>.8) and brake<.05 and throttle>.05 and absf(acceleration_local.x)<cfg.shift_corner_accel_limit_mps2:
   engage_shift(gear+1)
  elif gear>1:
   var lower_rpm=axle_rpm*cfg.gear_ratios[gear-2]/cfg.gear_ratios[gear-1]
   var down_at=cfg.downshift_power_rpm if throttle>.7 else cfg.downshift_cruise_rpm
   if (rpm<down_at or brake>.4 and rpm<cfg.downshift_braking_rpm) and lower_rpm<cfg.redline_rpm*cfg.downshift_rpm_margin:
    engage_shift(gear-1)
 ratio=get_ratio()
 var effective_throttle=throttle
 var old_slip=0.0
 for i in range(4):
  if is_driven(i): old_slip=maxf(old_slip,wheels[i].slip)
 tcs_active=tcs_enabled and old_slip>cfg.tcs_slip_target and effective_throttle>0.1
 if tcs_active:effective_throttle*=clampf(1.0-(old_slip-cfg.tcs_slip_target)*cfg.tcs_strength*cfg.tcs_gain,cfg.tcs_min_torque_fraction,1.0)
 engine_load=effective_throttle if engine_on and shift_timer<=0 else 0.0
 var torque=cfg.torque_at(rpm)*effective_throttle*(1-damage.state.power)
 if not auto_clutch:torque*=clampf(rpm/cfg.idle_rpm,.3,1.0)
 if rpm>=cfg.max_rpm-cfg.limiter_cut_band_rpm: torque=0
 if shift_timer>0 or not engine_on: torque=0
 torque*=engagement
 if engine_on and gear!=0 and shift_timer<=0:torque-=cfg.engine_brake*(1-throttle)*engagement
 if reengage_timer>0 and not shift_cut:
  var coupling=clampf(1-reengage_timer/(cfg.shift_time*2),0,1)
  torque=torque*coupling+clampf(shaft_delta_rpm*TAU/60*cfg.engine_inertia_kgm2/cfg.shift_time,-80,80)*coupling
  shaft_delta_rpm=move_toward(shaft_delta_rpm,0,12000*dt)
 var wheel_torque=torque*ratio*cfg.drivetrain_efficiency/maxi(1,drive_count)
 if gear==0 or selector=="P":wheel_torque=0
 var space=state.get_space_state()
 grounded=0;max_slip=0;abs_active=false
 var omega_snapshot: Array[float]=[]
 for w in wheels:omega_snapshot.append(w.omega)
 for i in range(4):
  var w=wheels[i]
  var tire_radius=wheel_radii[i]
  if cfg.tire_simulation:
   var cooling=(cfg.tire_cooling+absf(forward_speed)*.00005)*(2.0 if wetness>.5 else 1.0)
   w.temperature=move_toward(w.temperature,cfg.tire_ambient_c,maxf(0,w.temperature-cfg.tire_ambient_c)*cooling*dt)
   var cold=clampf((cfg.tire_optimal_c-w.temperature)/60.0,0,1)
   var hot=clampf((w.temperature-cfg.tire_optimal_c-25.0)/70.0,0,1)
   w.grip_factor=(1.0-cold*.12-hot*.23)*(1.0-w.wear*.26)
  else:w.grip_factor=1.0
  var mount_world=state.transform*w.mount
  var ray=PhysicsRayQueryParameters3D.create(mount_world,mount_world-up*(cfg.ride_height+cfg.travel+tire_radius),1)
  ray.exclude=[get_rid()]
  var hit=space.intersect_ray(ray)
  w.ground=not hit.is_empty()
  var drive=wheel_torque if is_driven(i) else 0.0
  var partner=omega_snapshot[i^1]
  if is_driven(i): drive+=clampf((partner-w.omega)*cfg.diff_lock*30,-cfg.diff_preload_nm,cfg.diff_preload_nm)
  if w.ground:
   grounded+=1
   var normal: Vector3=hit.normal
   var point: Vector3=hit.position
   var offset=point-state.transform.origin
   var velocity=state.linear_velocity+state.angular_velocity.cross(offset-basis*center_of_mass)
   w.length=clampf(mount_world.distance_to(point)-tire_radius,cfg.ride_height-cfg.travel,cfg.ride_height+cfg.travel)
   var compression=cfg.ride_height-w.length
   var vertical=velocity.dot(up)
   var damping=cfg.bump_damping if vertical<0 else cfg.rebound_damping
   w.load=clampf(compression*cfg.spring-vertical*damping,0,cfg.mass_kg*9.81*1.4)
   state.apply_force(normal*w.load,offset)
   var tire_forward=forward.rotated(up,steer_angle if i<2 else 0)
   tire_forward=(tire_forward-normal*tire_forward.dot(normal)).normalized()
   var tire_right=tire_forward.cross(normal).normalized()
   var vx=velocity.dot(tire_forward);var vy=velocity.dot(tire_right)
   w.surface=str(hit.collider.get_meta("surface","asphalt"))
   var surface_grip=(0.68 if w.surface=="grass" else 1.0)*(1.0-maxf(wetness,1.0 if w.surface=="wet_asphalt" else 0.0)*0.33)
   var mu=(cfg.grip_front if i<2 else cfg.grip_rear)*surface_grip*w.grip_factor
   var capacity=maxf(1,w.load*mu)
   var brake_demand=brake*cfg.brake_torque*(cfg.brake_bias if i<2 else 1-cfg.brake_bias)*0.5
   if selector=="P" or handbrake and i>=2:brake_demand=maxf(brake_demand,cfg.parking_brake_torque)
   var lat_angle=atan2(vy,maxf(absf(vx),2.0));w.angle=lat_angle
   var fy=-tanh(lat_angle*cfg.lateral_stiffness)*(1.0-.18*smoothstep(.22,.75,absf(lat_angle)))*capacity
   if absf(vx)<2:fy=-clampf(vy*cfg.mass_kg*0.25/dt,-capacity,capacity)
   var fx_sum=0.0
   for sub in range(cfg.tire_substeps):
    var slip=(w.omega*tire_radius-vx)/maxf(absf(vx),cfg.tire_low_speed_mps)
    var available_brake=brake_demand
    if abs_enabled and cfg.abs_strength>0 and absf(vx)>3 and slip*signf(vx)<-cfg.abs_slip_target and not (handbrake and i>=2) and selector!="P":
     available_brake*=1-cfg.abs_strength*cfg.abs_release_fraction;abs_active=true
    var fx=tanh(slip*cfg.longitudinal_stiffness)*(1.0-cfg.locked_grip_loss*smoothstep(.18,.70,absf(slip)))*capacity
    var resultant=Vector2(fx,fy).length()
    if resultant>capacity:fx*=capacity/resultant
    var resisting=fx*tire_radius
    var omega_next=w.omega+(drive-resisting)*dt/float(cfg.tire_substeps)/cfg.wheel_inertia
    var bt=available_brake*dt/float(cfg.tire_substeps)/cfg.wheel_inertia
    w.omega=move_toward(omega_next,0,bt)
    w.omega=clampf(w.omega,-cfg.tire_max_omega_rad_s,cfg.tire_max_omega_rad_s)
    fx_sum+=fx/float(cfg.tire_substeps)
   w.slip=(w.omega*tire_radius-vx)/maxf(absf(vx),cfg.tire_low_speed_mps)
   max_slip=maxf(max_slip,absf(w.slip)+absf(lat_angle))
   if brake_demand>500 and absf(vx)<.30 and absf(drive)<500:
    fx_sum=clampf(-cfg.mass_kg*.25*(vx/dt+Vector3(0,-9.81,0).dot(tire_forward)),-capacity,capacity)
    w.omega=0
   var available_lat=sqrt(maxf(0,capacity*capacity-fx_sum*fx_sum))
   fy=clampf(fy,-available_lat,available_lat)
   var rolling=-signf(vx)*cfg.rolling_resistance*w.load*minf(absf(vx),1.0)*(2.5 if w.surface=="grass" else 1.0)
   state.apply_force(tire_forward*(fx_sum+rolling)+tire_right*fy,offset)
   if cfg.tire_simulation:
    var dissipated=absf(fx_sum*(w.omega*tire_radius-vx))+absf(fy*vy)
    w.temperature=clampf(w.temperature+(dissipated*.65+absf(rolling*vx))/cfg.tire_heat_capacity*dt,cfg.tire_ambient_c,180)
    w.wear=clampf(w.wear+dissipated*cfg.tire_wear_rate*dt,0,1)
  else:
   w.length=cfg.ride_height+cfg.travel;w.load=0;w.slip=0
   w.omega=clampf(w.omega+drive/cfg.wheel_inertia*dt,-cfg.tire_max_omega_rad_s,cfg.tire_max_omega_rad_s)
  w.spin=fmod(w.spin+w.omega*dt,TAU)
  wheel_visuals[i].position=w.mount-Vector3.UP*w.length
  wheel_visuals[i].rotation=Vector3(-w.spin,steer_angle if i<2 else 0,0)
  if calipers.size()>i:
   calipers[i].position=wheel_visuals[i].position
   calipers[i].rotation.y=steer_angle if i<2 else 0
 var v=state.linear_velocity
 state.apply_central_force(-v*v.length()*0.5*cfg.air_density*cfg.effective_drag_area())
 if grounded>0:
  var aero=.5*cfg.air_density*cfg.effective_lift_area()*forward_speed*forward_speed
  state.apply_force(-up*aero*cfg.aero_front_balance,basis*Vector3(0,0,-cfg.wheelbase*.5))
  state.apply_force(-up*aero*(1-cfg.aero_front_balance),basis*Vector3(0,0,cfg.wheelbase*.5))
 var target_yaw=forward_speed*tan(steer_angle)/cfg.wheelbase
 var yaw_limit=9.81*minf(cfg.grip_front,cfg.grip_rear)*(1-wetness*.33)/maxf(absf(forward_speed),1.0)
 target_yaw=clampf(target_yaw,-yaw_limit,yaw_limit)
 var yaw=state.angular_velocity.dot(up)
 esc_active=esc_enabled and cfg.esc_strength>0 and grounded>=3 and absf(forward_speed)>5 and absf(yaw-target_yaw)>0.18
 if esc_active: state.apply_torque(up*clampf((target_yaw-yaw)*cfg.esc_yaw_gain*cfg.esc_strength,-cfg.esc_max_torque,cfg.esc_max_torque))
 damage.sample(self,state,simulation_time);collision_energy=damage.impact
 acceleration_local=acceleration_local.lerp(basis.inverse()*(state.linear_velocity-last_velocity)/dt,1-exp(-10*dt))
 var suspension=0.0
 for w in wheels:suspension+=w.length*.25
 road_vibration=lerpf(road_vibration,clampf((suspension-last_suspension)/dt,-3,3),1-exp(-20*dt))
 last_suspension=suspension;last_velocity=state.linear_velocity

func toggle_ignition() -> bool:
 if engine_on:engine_on=false;return true
 if not auto_clutch and gear!=0 and clutch<.8:
  notice.emit("Restart: hold clutch or select neutral");return false
 engine_on=true;rpm=cfg.idle_rpm;stall_timer=0;notice.emit("Engine running");return true
func service_tires() -> void:
 for w in wheels:w.temperature=cfg.tire_optimal_c;w.wear=0.0;w.grip_factor=1.0
 notice.emit("Tires serviced and warmed")
func is_driven(i: int) -> bool:
 return cfg.drive_layout=="AWD" or cfg.drive_layout=="FWD" and i<2 or cfg.drive_layout=="RWD" and i>=2
func get_ratio() -> float:
 if gear>0:return cfg.gear_ratios[gear-1]*cfg.final_drive
 if gear<0:return -cfg.reverse_ratio*cfg.final_drive
 return 0
func telemetry() -> Dictionary:
 return {"speed_kph":speed_kph,"rpm":rpm,"gear":gear,"selector":selector,"automatic":automatic,"auto_shift_assist":automatic,"auto_clutch":auto_clutch,"rev_match":rev_match,"shift_cut":shift_cut,"clutch_engagement":clutch_engagement,"manual_override_s":manual_override,"damage":damage.state.duplicate(),"contacts":damage.last_contacts.duplicate(true),"velocity_mps":[linear_velocity.x,linear_velocity.y,linear_velocity.z],"angular_velocity_rad_s":[angular_velocity.x,angular_velocity.y,angular_velocity.z],"throttle":throttle,"brake":brake,"clutch":clutch,"steer":steering,"grounded":grounded,"abs":abs_active,"tcs":tcs_active,"esc":esc_active,"slip":max_slip,"position":[global_position.x,global_position.y,global_position.z],"engine_on":engine_on,"engine_load":engine_load,"tire_temperature":wheels.map(func(w):return w.temperature),"tire_wear":wheels.map(func(w):return w.wear)}
func _process(_delta: float) -> void:
 visual_timer+=_delta
 if visual_timer>.1:
  damage.apply_visuals(body_visual)
  for lod in lod_visuals:damage.apply_visuals(lod)
  visual_timer=0
 for level in range(lod_wheels.size()):
  if not lod_visuals[level].visible:continue
  for i in range(4):
   var pivot=lod_wheels[level][i]
   if pivot:pivot.position=wheel_visuals[i].position;pivot.rotation=wheel_visuals[i].rotation
 for k in light_nodes:
  light_nodes[k].visible=headlights and damage.state.lights<.8;light_nodes[k].spot_range=180 if highbeam else 105
  light_nodes[k].light_energy=14 if highbeam else 8
 if steering_wheel:steering_wheel.rotation.z=steering*.75
 if dashboard:dashboard.modulate=Color("ff643d") if rpm>cfg.redline_rpm else Color("d8f7ec")
 if dashboard:dashboard.text="%03d km/h   %s\n%04d rpm"%[roundi(speed_kph),"N" if gear==0 else "R" if gear<0 else str(gear),roundi(rpm)]
 for item in visual_lamps:
  var intensity=.04
  if item.kind=="head":intensity=2.0 if headlights else .6
  if item.kind=="tail":intensity=4.0 if brake>.08 else (.7 if headlights else .16)
  if item.kind=="signal":intensity=2.2 if fmod(simulation_time,1)<.5 and (hazards or indicator==item.side) else .02
  item.material.emission_energy_multiplier=intensity*(1-damage.state.lights)
func cache_details() -> void:
 if imported_model:
  steering_wheel=body_visual.find_child("Steering",true,false)
  dashboard=Label3D.new();dashboard.font_size=22;dashboard.pixel_size=.00067;dashboard.position=Vector3(-.306,.105,-.523);dashboard.modulate=Color("d8f7ec");dashboard.outline_size=3;body_visual.add_child(dashboard)
  for node in body_visual.find_children("*","MeshInstance3D",true,false):
   if "PHISICS_DASH" in str(node.name):node.hide()
   for surface in range(node.mesh.get_surface_count()):
    var original=node.mesh.surface_get_material(surface)
    if not original is StandardMaterial3D:continue
    var material=original.duplicate();var name_lower=original.resource_name.to_lower()
    if "window" in name_lower or "windshield" in name_lower:
     material.metallic=0;material.albedo_color=Color(.68,.80,.85,.20);material.roughness=.08;material.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA_DEPTH_PRE_PASS
    var kind=""
    if "ext_emissive_light_front" in name_lower:kind="head";material.emission=Color(.9,.96,1)
    if "ext_emissive_light_rear" in name_lower:kind="tail";material.emission=Color(1,.035,.015)
    if kind!="":
     material.emission_enabled=true;visual_lamps.append({"material":material,"kind":kind,"side":0})
    node.set_surface_override_material(surface,material)
  return
 var model=body_visual
 dashboard=Label3D.new();dashboard.font_size=28;dashboard.pixel_size=.0012;dashboard.position=Vector3(-.38,.255,-.475);dashboard.modulate=Color("a8e0c5");dashboard.outline_size=2;body_visual.add_child(dashboard)
 steering_wheel=Node3D.new();body_visual.add_child(steering_wheel);steering_wheel.position=Vector3(-.38,.29,-.33)
 for node in model.find_children("*","MeshInstance3D",true,false):
  if node.name.begins_with("InstrumentDisplay"):
   var display_mat=StandardMaterial3D.new();display_mat.albedo_color=Color("062830");display_mat.emission_enabled=true;display_mat.emission=Color("05202a");display_mat.emission_energy_multiplier=.3;node.material_override=display_mat
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



func update_lod(distance_m: float,cockpit: bool) -> void:
 if lod_visuals.size()!=3:return
 var wanted=0 if cockpit or distance_m<6 else 1 if distance_m<25 else 2 if distance_m<75 else 3
 active_lod=wanted;body_visual.visible=wanted==0
 for wheel in wheel_visuals:wheel.visible=wanted==0
 for caliper in calipers:caliper.visible=wanted==0
 for i in range(3):lod_visuals[i].visible=wanted==i+1

func cache_lod_lamps() -> void:
 for model in lod_visuals:
  for mesh in model.find_children("*","MeshInstance3D",true,false):
   for surface in range(mesh.mesh.get_surface_count()):
    var old=mesh.mesh.surface_get_material(surface)
    if not old is StandardMaterial3D:continue
    var kind="head" if "emissive_light_front" in old.resource_name.to_lower() else "tail" if "emissive_light_rear" in old.resource_name.to_lower() else ""
    if kind.is_empty():continue
    var material=old.duplicate();material.emission_enabled=true
    material.emission=Color(.9,.96,1) if kind=="head" else Color(1,.035,.015)
    mesh.set_surface_override_material(surface,material);visual_lamps.append({"material":material,"kind":kind,"side":0})
 # Explicit inexpensive direction lamps for all camera LODs.
 for side in [-1,1]:
  for z in [-2.22,2.22]:
   var node=MeshInstance3D.new();var shape=BoxMesh.new();shape.size=Vector3(.13,.06,.02);node.mesh=shape;node.position=Vector3(side*.78,-.23,z)
   var material=StandardMaterial3D.new();material.albedo_color=Color(.5,.15,.01);material.emission_enabled=true;material.emission=Color(1,.3,.01);node.material_override=material
   add_child(node);visual_lamps.append({"material":material,"kind":"signal","side":side})
