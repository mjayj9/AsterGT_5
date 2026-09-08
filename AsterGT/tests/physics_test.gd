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
 car.test_input={"throttle":0.0,"brake":1.0}
func _physics_process(dt: float) -> bool:
 frame+=1;elapsed+=dt
 if frame%120==0 and metrics.samples.size()<120:metrics.samples.append(car.telemetry())
 match phase:
  "settle":
   if elapsed>2:
    metrics.checks["four_grounded"]=car.grounded==4
    metrics["static_height_m"]=car.position.y
    metrics["launch_speed_kph"]=car.speed_kph
    metrics.checks["standing_start"]=car.speed_kph<.05
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
    phase="brake_setup";car.test_input={"brake":1.0};car.recover(Transform3D(Basis.IDENTITY,Vector3(0,.8,0)));elapsed=0
  "brake_setup":
   if elapsed>1.5:
    car.service_tires();car.linear_velocity=Vector3(0,0,-100.0/3.6)
    for i in range(4):car.wheels[i].omega=100.0/3.6/car.wheel_radii[i]
    car.gear=3;car.rpm=100.0/3.6/car.cfg.wheel_radius*car.get_ratio()*60/TAU
    car.brake=0;car.throttle=0;car.test_input={"brake":1.0}
    brake_start_z=car.position.z;phase="brake";elapsed=0
    metrics["brake_start_speed_kph"]=100.0
  "brake":
   if elapsed>.05 and car.speed_kph<0.5:
    metrics.checks["automatic_downshift"]=car.gear<3
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
