from pathlib import Path
import re,json
p=Path(r'C:/Users/admin/Documents/Codex/2026-09-08/fable-5-1-vs-fable-at-4/outputs/AsterGT')
f=p/'scripts/vehicle_config.gd';s=f.read_text(encoding='utf-8-sig')
repl={'reference_mass: float = 1520.0':'reference_mass: float = 1265.0','mass_kg: float = 1520.0':'mass_kg: float = 1265.0','max_rpm: float = 7500.0':'max_rpm: float = 9250.0','idle_rpm: float = 850.0':'idle_rpm: float = 1200.0','redline_rpm: float = 7200.0':'redline_rpm: float = 9000.0','creep_throttle: float = 0.10':'creep_throttle: float = 0.0','wheelbase: float = 2.78':'wheelbase: float = 2.507','shift_time: float = 0.22':'shift_time: float = 0.12','drag_area: float = 0.69':'drag_area: float = 0.96','downforce: float = 0.8':'downforce: float = 1.8','spring: float = 44000.0':'spring: float = 57000.0','final_drive: float = 3.60':'final_drive: float = 3.90','[3.30, 2.20, 1.58, 1.20, 0.97, 0.80]':'[2.85, 2.10, 1.65, 1.36, 1.16, 1.03]','Vector3(0,-0.12,0.05)':'Vector3(0,-0.14,0.10)','Vector3(640,2350,650)':'Vector3(510,1900,540)','"max_rpm":[4500,8500,100]':'"max_rpm":[4500,10000,50]','brake_bias: float = 0.64':'brake_bias: float = 0.56','grip_front: float = 1.20':'grip_front: float = 1.40','grip_rear: float = 1.22':'grip_rear: float = 1.42'}
for a,b in repl.items():s=s.replace(a,b)
s=re.sub(r'@export var torque_curve:.*', '@export var torque_curve: PackedVector2Array = PackedVector2Array([Vector2(1200,220),Vector2(2500,330),Vector2(4000,430),Vector2(5500,495),Vector2(6500,505),Vector2(7500,500),Vector2(8500,467),Vector2(9000,438),Vector2(9250,415)])',s)
s=s.replace('const RANGES = {','''@export var profile: String="Authentic BoP"
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
const RANGES = {
 "wing_angle_deg":[0,20,1], "drag_area":[0.6,1.6,0.01], "aero_front_balance":[0.3,0.6,0.01], "diff_preload_nm":[0,250,5],''')
s=s[:s.index('func preset(')]+'''func preset(label: String) -> void:
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
'''
s=s.replace('redline_rpm = max_rpm-300.0','redline_rpm = max_rpm-250.0')
f.write_text(s,encoding='utf8')
(p/'config/street.tres').write_text('[gd_resource type="Resource" script_class="VehicleConfig" load_steps=2 format=3]\n[ext_resource type="Script" path="res://scripts/vehicle_config.gd" id="1"]\n[resource]\nscript = ExtResource("1")\n',encoding='utf8')
f=p/'project.godot';s=f.read_text(encoding='utf-8-sig').replace('config/custom_user_dir_name="AsterGT"','config/custom_user_dir_name="AsterGT-v4"').replace('ASTER — Grand Tour','ASTER — GT3 v4');f.write_text(s,encoding='utf8')
print('vehicle configuration and v4 save namespace written')
