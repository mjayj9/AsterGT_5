from pathlib import Path
p=Path(__file__).resolve().parents[1]/'outputs'/'AsterGT'
def write(name,s):
    f=p/name; f.parent.mkdir(parents=True,exist_ok=True); f.write_text(s.strip()+'\n',encoding='utf-8')
write('project.godot',r'''
config_version=5
[application]
config/name="ASTER — Grand Tour"
run/main_scene="res://scenes/main.tscn"
config/features=PackedStringArray("4.6", "GL Compatibility")
[display]
window/size/viewport_width=1920
window/size/viewport_height=1080
window/size/window_width_override=1440
window/size/window_height_override=810
window/stretch/mode="canvas_items"
[rendering]
renderer/rendering_method="gl_compatibility"
renderer/rendering_method.mobile="gl_compatibility"
textures/default_filters/use_nearest_mipmap_filter=false
textures/default_filters/anisotropic_filtering_level=3
anti_aliasing/quality/msaa_3d=1
environment/defaults/default_clear_color=Color(0.42,0.6,0.7,1)
[physics]
common/physics_ticks_per_second=120
common/max_physics_steps_per_frame=16
3d/physics_engine="GodotPhysics3D"
[debug]
gdscript/warnings/untyped_declaration=0
''')
write('scripts/vehicle_config.gd',r'''
class_name VehicleConfig
extends Resource

@export var mass_kg: float = 1520.0
@export var torque_scale: float = 1.0
@export var max_rpm: float = 7500.0
@export var idle_rpm: float = 850.0
@export var redline_rpm: float = 7200.0
@export var gear_ratios: Array[float] = [3.30, 2.20, 1.58, 1.20, 0.97, 0.80]
@export var reverse_ratio: float = 3.10
@export var final_drive: float = 3.60
@export var drive_layout: String = "RWD"
@export var shift_time: float = 0.22
@export var engine_brake: float = 65.0
@export var wheel_radius: float = 0.355
@export var wheel_inertia: float = 3.0
@export var wheelbase: float = 2.78
@export var track: float = 1.72
@export var spring: float = 44000.0
@export var bump_damping: float = 4200.0
@export var rebound_damping: float = 4800.0
@export var ride_height: float = 0.45
@export var travel: float = 0.22
@export var grip_front: float = 1.20
@export var grip_rear: float = 1.22
@export var brake_torque: float = 8200.0
@export var brake_bias: float = 0.64
@export var max_steer: float = 32.0
@export var steer_rate: float = 2.2
@export var steer_return: float = 3.0
@export var throttle_rate: float = 2.6
@export var brake_rate: float = 5.0
@export var drag_area: float = 0.69
@export var rolling_resistance: float = 0.013
@export var downforce: float = 0.8
@export var abs_strength: float = 1.0
@export var tcs_strength: float = 0.9
@export var esc_strength: float = 0.7
@export var diff_lock: float = 0.32
@export var torque_curve: PackedVector2Array = PackedVector2Array([Vector2(850,240),Vector2(1800,380),Vector2(3000,510),Vector2(4500,565),Vector2(5800,570),Vector2(6500,540),Vector2(7200,470),Vector2(7500,410)])

const RANGES = {
 "mass_kg":[900,2400,10], "torque_scale":[0.3,1.8,0.05], "max_rpm":[4500,8500,100],
 "final_drive":[2.4,4.8,0.05], "brake_torque":[3500,14000,100], "brake_bias":[0.45,0.8,0.01],
 "max_steer":[15,42,1], "steer_rate":[0.5,5,0.1], "steer_return":[0.8,6,0.1],
 "spring":[25000,80000,1000], "bump_damping":[1500,7500,100], "rebound_damping":[1800,8500,100],
 "ride_height":[0.34,0.55,0.01], "grip_front":[0.6,1.65,0.02], "grip_rear":[0.5,1.65,0.02],
 "downforce":[0,2.5,0.1], "abs_strength":[0,1,0.05], "tcs_strength":[0,1,0.05], "esc_strength":[0,1,0.05]
}
func torque_at(rpm: float) -> float:
 for i in range(torque_curve.size()-1):
  if rpm <= torque_curve[i+1].x:
   var t = clampf((rpm-torque_curve[i].x)/(torque_curve[i+1].x-torque_curve[i].x),0,1)
   return lerpf(torque_curve[i].y,torque_curve[i+1].y,t)*torque_scale
 return torque_curve[-1].y*torque_scale
func sanitize() -> void:
 for key in RANGES:
  var value = float(get(key))
  if not is_finite(value): value = float(RANGES[key][0])
  set(key,clampf(value,RANGES[key][0],RANGES[key][1]))
 redline_rpm = max_rpm-300.0
 if not drive_layout in ["RWD","FWD","AWD"]: drive_layout="RWD"
 if gear_ratios.size()!=6: gear_ratios=[3.30,2.20,1.58,1.20,0.97,0.80]
 for i in range(6):
  if not is_finite(gear_ratios[i]): gear_ratios[i]=1.0
  gear_ratios[i]=clampf(gear_ratios[i],0.5,4.5)
func preset(label: String) -> void:
 var base = VehicleConfig.new()
 for key in RANGES: set(key,base.get(key))
 gear_ratios=base.gear_ratios.duplicate(); drive_layout="RWD"
 match label:
  "GT": grip_front=1.38;grip_rear=1.40;spring=57000;downforce=1.8;ride_height=0.37
  "Drift": grip_rear=0.75;grip_front=1.25;tcs_strength=0;esc_strength=0;max_steer=40
  "Wet": drive_layout="AWD";torque_scale=0.82;grip_front=1.28;grip_rear=1.3;esc_strength=1;tcs_strength=1
  "Eco": torque_scale=0.60;final_drive=3.1;downforce=0.3
 sanitize()
func save_settings(file: String="user://vehicle.json") -> void:
 var d={}
 for key in RANGES: d[key]=get(key)
 d["gear_ratios"]=gear_ratios;d["drive_layout"]=drive_layout
 var f=FileAccess.open(file,FileAccess.WRITE)
 if f: f.store_string(JSON.stringify(d,"  "))
func load_settings(file: String="user://vehicle.json") -> bool:
 if not FileAccess.file_exists(file): return false
 var data=JSON.parse_string(FileAccess.get_file_as_string(file))
 if not data is Dictionary: return false
 for key in RANGES:
  if data.has(key) and (data[key] is float or data[key] is int): set(key,float(data[key]))
 if data.get("drive_layout") is String: drive_layout=data.drive_layout
 if data.get("gear_ratios") is Array and data.gear_ratios.size()==6:
  for i in range(6):
   if data.gear_ratios[i] is float or data.gear_ratios[i] is int: gear_ratios[i]=float(data.gear_ratios[i])
 sanitize()
 return true
''')
write('scripts/car.gd',r'''
class_name GTCar
extends RigidBody3D
signal notice(message: String)
var cfg = VehicleConfig.new()
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
var rpm: float=850
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
var paint=Color("216d67")
var chassis_base_y: float=0

func _ready() -> void:
 mass=cfg.mass_kg
 center_of_mass_mode=RigidBody3D.CENTER_OF_MASS_MODE_CUSTOM
 center_of_mass=Vector3(0,-0.12,0.05)
 inertia=Vector3(640,2350,650)
 linear_damp=0; angular_damp=0.25
 continuous_cd=true;can_sleep=false
 contact_monitor=true;max_contacts_reported=8
 collision_layer=2;collision_mask=1|4
 var mat=PhysicsMaterial.new();mat.friction=0.3;mat.bounce=0.08;physics_material_override=mat
 var shape=CollisionShape3D.new();var box=BoxShape3D.new();box.size=Vector3(1.84,0.48,4.2)
 shape.shape=box;shape.position.y=0.04;add_child(shape)
 for i in range(4):
  wheels.append({"mount":Vector3((-1 if i%2==0 else 1)*cfg.track/2,0.05,(-1 if i<2 else 1)*cfg.wheelbase/2),"omega":0.0,"spin":0.0,"length":cfg.ride_height,"load":0.0,"slip":0.0,"angle":0.0,"ground":false,"surface":"asphalt"})
 build_visuals()

func build_visuals() -> void:
 body_visual=Node3D.new();add_child(body_visual)
 if ResourceLoader.exists("res://assets/aster_gt.glb"):
  var model=load("res://assets/aster_gt.glb").instantiate();body_visual.add_child(model)
  for node in model.find_children("*","Node3D",true,false):
   if node.name.begins_with("Wheel_"): node.hide()
 else:
  var m=MeshInstance3D.new();var mesh=BoxMesh.new();mesh.size=Vector3(1.86,0.5,4.4);m.mesh=mesh
  var material=StandardMaterial3D.new();material.albedo_color=paint;material.metallic=0.75;material.roughness=0.27;m.material_override=material;body_visual.add_child(m)
 for i in range(4):
  var pivot=Node3D.new();add_child(pivot);wheel_visuals.append(pivot)
  if ResourceLoader.exists("res://assets/wheel.glb"):
   var model=load("res://assets/wheel.glb").instantiate();pivot.add_child(model)
   if i%2==0: model.rotation.y=PI
  else:
   var m=MeshInstance3D.new();var tire=CylinderMesh.new();tire.top_radius=cfg.wheel_radius;tire.bottom_radius=cfg.wheel_radius;tire.height=0.27;m.mesh=tire;m.rotation.z=PI/2
   var material=StandardMaterial3D.new();material.albedo_color=Color("151719");m.material_override=material;pivot.add_child(m)
 for side in [-1,1]:
  var lamp=SpotLight3D.new();lamp.position=Vector3(side*0.67,0.05,-2.15);lamp.light_color=Color(0.86,0.94,1);lamp.spot_range=75;lamp.spot_angle=24;lamp.light_energy=3;lamp.visible=false;add_child(lamp);light_nodes["head"+str(side)]=lamp

func set_selector(value: String) -> bool:
 if value in ["P","R"] and absf(forward_speed)>0.7:
  notice.emit("Stop before selecting "+value); return false
 selector=value
 if value=="D": gear=1
 elif value=="R": gear=-1
 else: gear=0
 shift_timer=cfg.shift_time
 return true
func toggle_transmission() -> void:
 automatic=not automatic
 if automatic:
  selector="R" if gear<0 else "D"
  gear=maxi(1,gear) if selector=="D" else -1
 else:
  selector="M"
 notice.emit("Automatic transmission" if automatic else "Manual transmission")
func manual_shift(direction: int) -> bool:
 if automatic: return false
 if not auto_clutch and clutch<0.8:
  notice.emit("Hold LEFT SHIFT to disengage clutch");return false
 var target=clampi(gear+direction,-1,6)
 if target==gear: return false
 if target<0 and absf(forward_speed)>0.7:
  notice.emit("Stop before selecting reverse");return false
 if target>0 and absf(forward_speed)/cfg.wheel_radius*cfg.gear_ratios[target-1]*cfg.final_drive*60/TAU>cfg.max_rpm:
  notice.emit("Downshift refused: engine overspeed");return false
 gear=target;shift_timer=cfg.shift_time
 return true
func recover(at: Transform3D) -> void:
 pending_reset=at;reset_requested=true
func _input_value(action: String) -> float:
 if not controls_enabled: return 0.0
 return float(test_input.get(action,Input.get_action_strength(action) if InputMap.has_action(action) else 0.0))
func _integrate_forces(state: PhysicsDirectBodyState3D) -> void:
 var dt=state.step
 if reset_requested:
  state.transform=pending_reset;state.linear_velocity=Vector3.ZERO;state.angular_velocity=Vector3.ZERO
  for w in wheels: w.omega=0;w.slip=0
  throttle=0;brake=0;steering=0;rpm=cfg.idle_rpm;last_velocity=Vector3.ZERO
  reset_requested=false;return
 simulation_time+=dt
 mass=cfg.mass_kg
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
 var steer_angle=steering*deg_to_rad(cfg.max_steer)/(1.0+absf(forward_speed)*0.072)
 shift_timer=maxf(0,shift_timer-dt);shift_cooldown=maxf(0,shift_cooldown-dt)
 var drive_omega=0.0;var drive_count=0
 for i in range(4):
  if is_driven(i):drive_omega+=wheels[i].omega;drive_count+=1
 drive_omega/=maxi(1,drive_count)
 var ratio=get_ratio()
 var axle_rpm=absf(drive_omega*ratio)*60.0/TAU
 var engagement=1.0-clutch
 if automatic or auto_clutch:
  engagement=clampf(absf(forward_speed)/4.5,0.0,1.0)
  if not automatic and clutch>0.05: engagement*=1.0-clutch
 if shift_timer>0 or gear==0: engagement=0
 var free_rpm=cfg.idle_rpm+throttle*(cfg.max_rpm-cfg.idle_rpm)
 var coupled_rpm=maxf(cfg.idle_rpm,axle_rpm)
 var target_rpm=lerpf(free_rpm,coupled_rpm,engagement)
 if (automatic or auto_clutch) and gear!=0 and shift_timer<=0:
  target_rpm=lerpf(cfg.idle_rpm+throttle*1850,coupled_rpm,engagement)
 if shift_timer>0: target_rpm=maxf(cfg.idle_rpm,rpm-4500*dt)
 if not engine_on: target_rpm=0
 rpm=clampf(lerpf(rpm,target_rpm,1-exp(-18*dt)),0,cfg.max_rpm)
 if automatic and selector=="D" and shift_timer==0 and shift_cooldown==0:
  var up_at=lerpf(2600,cfg.redline_rpm-300,throttle)
  if rpm>up_at and gear<6 and engagement>0.9: gear+=1;shift_timer=cfg.shift_time;shift_cooldown=0.75
  elif gear>1:
   var lower_rpm=axle_rpm*cfg.gear_ratios[gear-2]/cfg.gear_ratios[gear-1]
   if rpm<1700 or (throttle>0.88 and rpm<3600 and lower_rpm<cfg.redline_rpm*0.78): gear-=1;shift_timer=cfg.shift_time;shift_cooldown=0.85
 ratio=get_ratio()
 var effective_throttle=throttle
 if automatic and selector in ["D","R"] and brake<0.05 and absf(forward_speed)<2.0: effective_throttle=maxf(throttle,0.10)
 var old_slip=0.0
 for i in range(4):
  if is_driven(i): old_slip=maxf(old_slip,wheels[i].slip)
 tcs_active=tcs_enabled and old_slip>0.14 and effective_throttle>0.1
 if tcs_active:effective_throttle*=clampf(1.0-(old_slip-0.14)*cfg.tcs_strength*1.8,0.08,1.0)
 var torque=cfg.torque_at(rpm)*effective_throttle
 if rpm>=cfg.max_rpm-80: torque=0
 if shift_timer>0 or not engine_on: torque=0
 if not automatic and not auto_clutch:torque*=1-clutch
 if engine_on and gear!=0 and shift_timer<=0:torque-=cfg.engine_brake*(1-throttle)*engagement
 var wheel_torque=torque*ratio*0.92/maxi(1,drive_count)
 if gear==0 or selector=="P":wheel_torque=0
 var space=state.get_space_state()
 grounded=0;max_slip=0;abs_active=false
 for i in range(4):
  var w=wheels[i]
  var mount_world=state.transform*w.mount
  var ray=PhysicsRayQueryParameters3D.create(mount_world,mount_world-up*(cfg.ride_height+cfg.travel+cfg.wheel_radius),1)
  ray.exclude=[get_rid()]
  var hit=space.intersect_ray(ray)
  w.ground=not hit.is_empty()
  var drive=wheel_torque if is_driven(i) else 0.0
  var partner=wheels[i^1].omega
  if is_driven(i): drive+=clampf((partner-w.omega)*cfg.diff_lock*30,-400,400)
  if w.ground:
   grounded+=1
   var normal: Vector3=hit.normal
   var point: Vector3=hit.position
   var offset=point-state.transform.origin
   var velocity=state.linear_velocity+state.angular_velocity.cross(offset-basis*center_of_mass)
   w.length=clampf(mount_world.distance_to(point)-cfg.wheel_radius,cfg.ride_height-cfg.travel,cfg.ride_height+cfg.travel)
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
   var surface_grip=(0.68 if w.surface=="grass" else 1.0)*(1.0-wetness*0.33)
   var mu=(cfg.grip_front if i<2 else cfg.grip_rear)*surface_grip
   var capacity=maxf(1,w.load*mu)
   var brake_demand=brake*cfg.brake_torque*(cfg.brake_bias if i<2 else 1-cfg.brake_bias)*0.5
   if selector=="P" or handbrake and i>=2:brake_demand=maxf(brake_demand,6200)
   var lat_angle=atan2(vy,maxf(absf(vx),2.0));w.angle=lat_angle
   var fy=-tanh(lat_angle*7.0)*capacity
   if absf(vx)<2:fy=-clampf(vy*cfg.mass_kg*0.25/dt,-capacity,capacity)
   var fx_sum=0.0
   for sub in range(8):
    var slip=(w.omega*cfg.wheel_radius-vx)/maxf(absf(vx),3.0)
    var available_brake=brake_demand
    if abs_enabled and cfg.abs_strength>0 and absf(vx)>3 and slip*signf(vx)<-0.13 and not (handbrake and i>=2) and selector!="P":
     available_brake*=1-cfg.abs_strength*0.88;abs_active=true
    var fx=tanh(slip*9.0)*capacity
    var resultant=Vector2(fx,fy).length()
    if resultant>capacity:fx*=capacity/resultant
    var resisting=fx*cfg.wheel_radius
    var omega_next=w.omega+(drive-resisting)*dt/8.0/cfg.wheel_inertia
    var bt=available_brake*dt/8.0/cfg.wheel_inertia
    w.omega=move_toward(omega_next,0,bt)
    w.omega=clampf(w.omega,-700,700)
    fx_sum+=fx/8.0
   w.slip=(w.omega*cfg.wheel_radius-vx)/maxf(absf(vx),3.0)
   max_slip=maxf(max_slip,absf(w.slip)+absf(lat_angle))
   var available_lat=sqrt(maxf(0,capacity*capacity-fx_sum*fx_sum))
   fy=clampf(fy,-available_lat,available_lat)
   var rolling=-signf(vx)*cfg.rolling_resistance*w.load*minf(absf(vx),1.0)*(2.5 if w.surface=="grass" else 1.0)
   state.apply_force(tire_forward*(fx_sum+rolling)+tire_right*fy,offset)
  else:
   w.length=cfg.ride_height+cfg.travel;w.load=0;w.slip=0
   w.omega=clampf(w.omega+drive/cfg.wheel_inertia*dt,-700,700)
  w.spin=fmod(w.spin+w.omega*dt,TAU)
  wheel_visuals[i].position=w.mount-Vector3.UP*w.length
  wheel_visuals[i].rotation=Vector3(-w.spin,steer_angle if i<2 else 0,0)
 var v=state.linear_velocity
 state.apply_central_force(-v*v.length()*0.5*1.225*cfg.drag_area)
 if grounded>0: state.apply_central_force(-up*cfg.downforce*forward_speed*forward_speed*0.5)
 var target_yaw=forward_speed*tan(steer_angle)/cfg.wheelbase
 var yaw=state.angular_velocity.dot(up)
 esc_active=esc_enabled and cfg.esc_strength>0 and grounded>=3 and absf(forward_speed)>5 and absf(yaw-target_yaw)>0.18
 if esc_active: state.apply_torque(up*clampf((target_yaw-yaw)*1900*cfg.esc_strength,-2800,2800))
 collision_energy=maxf(0,collision_energy-dt*4)
 if state.get_contact_count()>0:
  var impact=(state.linear_velocity-last_velocity).length()
  if impact>1.5: collision_energy=minf(1,impact/12)
 last_velocity=state.linear_velocity

func is_driven(i: int) -> bool:
 return cfg.drive_layout=="AWD" or cfg.drive_layout=="FWD" and i<2 or cfg.drive_layout=="RWD" and i>=2
func get_ratio() -> float:
 if gear>0:return cfg.gear_ratios[gear-1]*cfg.final_drive
 if gear<0:return -cfg.reverse_ratio*cfg.final_drive
 return 0
func telemetry() -> Dictionary:
 return {"speed_kph":speed_kph,"rpm":rpm,"gear":gear,"selector":selector,"automatic":automatic,"throttle":throttle,"brake":brake,"clutch":clutch,"steer":steering,"grounded":grounded,"abs":abs_active,"tcs":tcs_active,"esc":esc_active,"slip":max_slip,"position":[position.x,position.y,position.z]}
func _process(_delta: float) -> void:
 for k in light_nodes: light_nodes[k].visible=headlights;light_nodes[k].spot_range=120 if highbeam else 65
''')
write('tests/physics_test.gd',r'''
extends SceneTree
var car: GTCar
var frame=0
var phase="settle"
var elapsed: float=0
var metrics={"engine":"Godot 4.6.3", "physics_hz":120,"checks":{},"samples":[]}
var start_z: float
var brake_start_z: float
var accel_time: float=-1
var reached_100: bool=false
var gears_seen={}
func _initialize() -> void:
 var root3=Node3D.new();root.add_child(root3)
 var floor=StaticBody3D.new();root3.add_child(floor)
 var cs=CollisionShape3D.new();var shape=BoxShape3D.new();shape.size=Vector3(10000,1,50000);cs.shape=shape;cs.position.y=-0.5;floor.add_child(cs)
 car=GTCar.new();car.position=Vector3(0,0.8,0);root3.add_child(car)
 car.test_input={"throttle":0.0,"brake":0.0}
func _physics_process(dt: float) -> bool:
 frame+=1;elapsed+=dt
 if frame%120==0 and metrics.samples.size()<120:metrics.samples.append(car.telemetry())
 match phase:
  "settle":
   if elapsed>2:
    metrics.checks["four_grounded"]=car.grounded==4
    metrics["static_height_m"]=car.position.y
    phase="accel";elapsed=0;start_z=car.position.z;car.test_input={"throttle":1.0}
  "accel":
   gears_seen[str(car.gear)]=true
   if car.speed_kph>=100 and not reached_100: metrics["zero_to_100_s"]=elapsed;reached_100=true
   if elapsed>35:
    metrics["speed_after_35s_kph"]=car.speed_kph
    metrics["lateral_drift_m"]=absf(car.position.x)
    metrics["gears_seen"]=gears_seen.keys()
    metrics.checks["automatic_upshift"]=gears_seen.size()>=4
    metrics.checks["straight_stable"]=absf(car.position.x)<2
    phase="decelerate";car.test_input={"throttle":0.0,"brake":1.0};elapsed=0
  "decelerate":
   if car.speed_kph<=100:
    brake_start_z=car.position.z;phase="brake";elapsed=0
  "brake":
   if car.speed_kph<0.5:
    metrics["100_to_0_distance_m"]=absf(car.position.z-brake_start_z)
    metrics["100_to_0_time_s"]=elapsed
    metrics.checks["brake_stable"]=car.global_basis.y.dot(Vector3.UP)>0.95
    metrics.checks["park_stopped"]=car.set_selector("P")
    phase="park";elapsed=0;car.test_input={"throttle":1.0}
  "park":
   if elapsed>1:
    metrics.checks["park_holds"]=car.speed_kph<1
    metrics.checks["reverse_selected"]=car.set_selector("R")
    phase="reverse";elapsed=0;car.test_input={"throttle":0.5}
  "reverse":
   if elapsed>3:
    metrics.checks["reverse_moves_backward"]=car.forward_speed< -1
    metrics.checks["park_at_speed_refused"]=not car.set_selector("P")
    car.test_input={"brake":1.0};phase="manual_setup";elapsed=0
  "manual_setup":
   if car.speed_kph<0.5:
    car.set_selector("D");car.toggle_transmission();car.auto_clutch=false
    metrics.checks["unclutched_shift_refused"]=not car.manual_shift(1)
    car.test_input={"clutch":1.0};phase="manual_shift";elapsed=0
  "manual_shift":
   if elapsed>0.3:
    metrics.checks["clutched_shift_accepts"]=car.manual_shift(1)
    car.auto_clutch=true;car.test_input={"throttle":1.0};phase="manual_hold";elapsed=0
  "manual_hold":
   if elapsed>8:
    metrics.checks["manual_holds_second"]=car.gear==2
    metrics.checks["finite_state"]=car.position.is_finite() and is_finite(car.rpm)
    var cfg=VehicleConfig.new();cfg.torque_scale=99;cfg.mass_kg=-20;cfg.sanitize()
    metrics.checks["config_clamped"]=cfg.torque_scale==1.8 and cfg.mass_kg==900
    cfg.save_settings("user://test_config.json");var c2=VehicleConfig.new();c2.load_settings("user://test_config.json")
    metrics.checks["config_roundtrip"]=is_equal_approx(c2.torque_scale,cfg.torque_scale)
    var file=FileAccess.open("res://tests/physics_results.json",FileAccess.WRITE);file.store_string(JSON.stringify(metrics,"  "))
    print(JSON.stringify(metrics))
    var ok=true
    for v in metrics.checks.values():if not v:ok=false
    quit(0 if ok else 1)
 if frame>120*100:print("TIMEOUT ",phase," ",car.telemetry());quit(2)
 return false
''')
write('scenes/main.tscn',r'''
[gd_scene load_steps=2 format=3]
[ext_resource type="Script" path="res://scripts/main.gd" id="1"]
[node name="AsterGrandTour" type="Node3D"]
script=ExtResource("1")
''')
write('scripts/main.gd',r'''
extends Node3D
func _ready() -> void:
 pass
''')
print('Core physics project written to',p)
