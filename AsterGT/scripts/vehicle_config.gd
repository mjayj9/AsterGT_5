class_name VehicleConfig
extends Resource

@export var tire_simulation: bool = true
@export var tire_ambient_c: float = 20.0
@export var tire_optimal_c: float = 70.0
@export var tire_heat_capacity: float = 16000.0
@export var tire_cooling: float = 0.0012
@export var tire_wear_rate: float = 0.00000002
@export var stall_enabled: bool = true
@export var stall_rpm: float = 470.0
@export var stall_delay: float = 0.45
@export var center_of_mass: Vector3 = Vector3(0,-0.14,0.10)
@export var inertia_at_reference_mass: Vector3 = Vector3(510,1900,540)
@export var reference_mass: float = 1265.0
@export var steering_speed_factor: float = 0.072
@export var longitudinal_stiffness: float = 9.0
@export var lateral_stiffness: float = 7.0
@export var locked_grip_loss: float = 0.35
@export var drivetrain_efficiency: float = 0.92
@export var air_density: float = 1.225
@export var creep_throttle: float = 0.0
@export var parking_brake_torque: float = 6200.0
@export var esc_yaw_gain: float = 1900.0
@export var esc_max_torque: float = 2800.0
@export var mass_kg: float = 1265.0
@export var torque_scale: float = 1.0
@export var max_rpm: float = 9250.0
@export var idle_rpm: float = 1200.0
@export var redline_rpm: float = 9000.0
@export var gear_ratios: Array[float] = [2.85, 2.10, 1.65, 1.36, 1.16, 1.03]
@export var reverse_ratio: float = 3.10
@export var final_drive: float = 3.90
@export var drive_layout: String = "RWD"
@export var shift_time: float = 0.12
@export var engine_brake: float = 65.0
@export var wheel_radius: float = 0.355
@export var wheel_inertia: float = 3.0
@export var wheelbase: float = 2.507
@export var track: float = 1.72
@export var spring: float = 57000.0
@export var bump_damping: float = 4200.0
@export var rebound_damping: float = 4800.0
@export var ride_height: float = 0.45
@export var travel: float = 0.22
@export var grip_front: float = 1.40
@export var grip_rear: float = 1.42
@export var brake_torque: float = 8200.0
@export var brake_bias: float = 0.56
@export var max_steer: float = 32.0
@export var steer_rate: float = 2.2
@export var steer_return: float = 3.0
@export var throttle_rate: float = 2.6
@export var brake_rate: float = 5.0
@export var drag_area: float = 0.96
@export var rolling_resistance: float = 0.013
@export var downforce: float = 1.8
@export var abs_strength: float = 1.0
@export var tcs_strength: float = 0.9
@export var esc_strength: float = 0.7
@export var diff_lock: float = 0.32
@export var torque_curve: PackedVector2Array = PackedVector2Array([Vector2(1200,220),Vector2(2500,330),Vector2(4000,430),Vector2(5500,495),Vector2(6500,505),Vector2(7500,500),Vector2(8500,467),Vector2(9000,438),Vector2(9250,415)])

@export var profile: String="Authentic BoP"
@export var wing_angle_deg: float=12.0
@export var aero_front_balance: float=0.43
@export var diff_preload_nm: float=100.0
@export var front_wheel_radius: float=0.34
@export var override_seconds: float=5.0
@export var shift_cooldown_s: float=0.35
@export var minimum_selector_speed_mps: float=0.5
@export var launch_slip_rpm: float=3500.0
@export var clutch_engagement_rate: float=9.0
@export var tire_substeps: int=8
@export var wing_drag_per_degree: float=0.010
@export var aero_ride_reference_m: float=0.45
@export var engine_inertia_kgm2: float=0.22
@export var auto_clutch_full_speed_mps: float = 4.5
@export var auto_launch_engagement: float = 0.65
@export var rpm_response_per_s: float = 18.0
@export var upshift_min_rpm: float = 4800.0
@export var downshift_power_rpm: float = 5200.0
@export var downshift_cruise_rpm: float = 3800.0
@export var downshift_braking_rpm: float = 5500.0
@export var downshift_rpm_margin: float = 0.94
@export var shift_corner_accel_limit_mps2: float = 7.0
@export var limiter_cut_band_rpm: float = 80.0
@export var tcs_slip_target: float = 0.14
@export var tcs_gain: float = 1.8
@export var tcs_min_torque_fraction: float = 0.08
@export var abs_slip_target: float = 0.13
@export var abs_release_fraction: float = 0.88
@export var tire_max_omega_rad_s: float = 700.0
@export var tire_low_speed_mps: float = 3.0
const RANGES = {
 "wing_angle_deg":[0,20,1], "drag_area":[0.6,1.6,0.01], "aero_front_balance":[0.3,0.6,0.01], "diff_preload_nm":[0,250,5],
 "mass_kg":[900,2400,10], "torque_scale":[0.3,1.8,0.05], "max_rpm":[4500,10000,50],
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
 redline_rpm = max_rpm-250.0
 if not drive_layout in ["RWD","FWD","AWD"]: drive_layout="RWD"
 if gear_ratios.size()!=6: gear_ratios=[3.30,2.20,1.58,1.20,0.97,0.80]
 for i in range(6):
  if not is_finite(gear_ratios[i]): gear_ratios[i]=1.0
  gear_ratios[i]=clampf(gear_ratios[i],0.5,4.5)
func preset(label: String) -> void:
 var base=VehicleConfig.new()
 for item in base.get_property_list():
  if item.usage & PROPERTY_USAGE_STORAGE and item.name not in ["script","resource_path","resource_name","resource_local_to_scene"]:set(item.name,base.get(item.name))
 profile=label if label in ["Authentic BoP","High Speed","Custom Sandbox"] else "Custom Sandbox"
 gear_ratios=[2.85,2.10,1.65,1.36,1.16,1.03]
 if profile=="High Speed":
  final_drive=3.50;gear_ratios=[3.05,2.16,1.67,1.38,1.19,1.05]
  drag_area=0.805;wing_angle_deg=4;downforce=1.15
 if label=="Drift":grip_rear=.8;tcs_strength=0;esc_strength=0;max_steer=40
 sanitize()
func effective_drag_area() -> float:
 return drag_area+wing_angle_deg*wing_drag_per_degree+0.05*pow(downforce-1.15,2)+0.3*absf(ride_height-aero_ride_reference_m)+0.1*absf(aero_front_balance-.43)
func effective_lift_area() -> float:
 return downforce*(.75+wing_angle_deg*.025)*clampf(1+(aero_ride_reference_m-ride_height)*1.5,.7,1.2)
func peak_kw() -> float:
 var peak=0.0
 for point in torque_curve:peak=maxf(peak,torque_at(point.x)*point.x*TAU/60000.0)
 return peak
func gear_speed(g: int) -> float:return max_rpm/gear_ratios[g-1]/final_drive*TAU*wheel_radius/60*3.6
func performance_estimate() -> Dictionary:
 # A dry/flat/warm 1D engineering estimate, not measured gameplay or homologation data.
 var v=0.0;var elapsed=0.0;var g=1;var times=[-1.0,-1.0,-1.0];var cut=0.0
 var step=0.05
 while elapsed<180.0:
  var rev=maxf(launch_slip_rpm,v/wheel_radius*gear_ratios[g-1]*final_drive*60/TAU)
  if rev>redline_rpm and g<6:g+=1;cut=shift_time
  var force=torque_at(minf(rev,max_rpm))*gear_ratios[g-1]*final_drive*drivetrain_efficiency/wheel_radius
  force=minf(force,mass_kg*9.81*grip_rear*.68)
  if cut>0:force=0;cut-=step
  if rev>=max_rpm:force=0
  var resistance=.5*air_density*effective_drag_area()*v*v+rolling_resistance*mass_kg*9.81
  v=maxf(0,v+(force-resistance)/mass_kg*step);elapsed+=step
  for i in range(3):
   if times[i]<0 and v*3.6>=(i+1)*100:times[i]=elapsed
 return {"peak_kw":peak_kw(),"ps":peak_kw()/0.73549875,"gear_limited_kph":gear_speed(6),"reachable_estimate_kph":v*3.6,"zero_100_s":times[0],"100_200_s":times[1]-times[0] if times[1]>0 else -1,"200_300_s":times[2]-times[1] if times[2]>0 else -1,"zero_300_s":times[2],"conditions":"1D dry, flat, still air, warm tires; separate QA required"}
func save_settings(file: String="user://vehicle.json") -> Error:
 var d={"schema_version":4}
 for item in get_property_list():
  if item.usage & PROPERTY_USAGE_SCRIPT_VARIABLE:
   var v=get(item.name)
   if v is float or v is int or v is bool or v is String or v is Array:d[item.name]=v
 return GTSafeStore.save_json(file,d)
func load_settings(file: String="user://vehicle.json") -> bool:
 if not FileAccess.file_exists(file):return false
 var d=JSON.parse_string(FileAccess.get_file_as_string(file))
 if not d is Dictionary or d.get("schema_version")!=4:return false
 for key in RANGES:
  if d.get(key) is float or d.get(key) is int:set(key,float(d[key]))
 for key in ["tire_simulation","stall_enabled"]:
  if d.get(key) is bool:set(key,d[key])
 if d.get("profile") in ["Authentic BoP","High Speed","Custom Sandbox"]:profile=d.profile
 if d.get("drive_layout") is String:drive_layout=d.drive_layout
 if d.get("gear_ratios") is Array and d.gear_ratios.size()==6:
  for i in range(6):
   if d.gear_ratios[i] is float or d.gear_ratios[i] is int:gear_ratios[i]=float(d.gear_ratios[i])
 if profile!="Custom Sandbox" and (drive_layout!="RWD" or mass_kg<1250 or mass_kg>1265 or max_rpm!=9250 or torque_scale!=1.0):profile="Custom Sandbox"
 sanitize();return true
