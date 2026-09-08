extends SceneTree
var car: GTCar
var scene: Node3D
var results={"checks":{},"measurements":{}}
func _initialize() -> void:call_deferred("run")
func frames(n: int) -> void:
 for i in range(n):await physics_frame
func reset(speed: float=0) -> void:
 car.cfg.preset("Street");car.service_tires();car.automatic=true;car.selector="D";car.gear=1;car.engine_on=true;car.auto_clutch=true;car.abs_enabled=true;car.tcs_enabled=true;car.esc_enabled=true;car.wetness=0
 car.test_input={"brake":1.0};car.recover(Transform3D(Basis.IDENTITY,Vector3(0,.8,0)));await frames(120)
 car.linear_velocity=Vector3(0,0,-speed/3.6)
 for i in range(4):car.wheels[i].omega=speed/3.6/car.wheel_radii[i]
 car.test_input={}
 await frames(2)
func check(name: String,value: bool) -> void:results.checks[name]=value;print("CHECK ",name," ",value)
func run() -> void:
 scene=Node3D.new();root.add_child(scene)
 var floor=StaticBody3D.new();scene.add_child(floor);var c=CollisionShape3D.new();var shape=BoxShape3D.new();shape.size=Vector3(10000,1,50000);c.shape=shape;c.position.y=-.5;floor.add_child(c)
 car=GTCar.new();car.position=Vector3(0,.8,0);scene.add_child(car);await frames(120)
 # TCS comparison with deliberately excessive launch torque.
 var tcs=[]
 for enabled in [false,true]:
  await reset();car.cfg.torque_scale=1.6;car.tcs_enabled=enabled;car.test_input={"throttle":1.0}
  var slip_sum=0.0;var active=0
  for i in range(360):
   await frames(1);slip_sum+=(absf(car.wheels[2].slip)+absf(car.wheels[3].slip))*.5
   if car.tcs_active:active+=1
  tcs.append({"enabled":enabled,"mean_rear_slip":slip_sum/360,"speed_kph":car.speed_kph,"active_ticks":active})
 results.measurements["tcs"]=tcs
 check("TCS_reduces_launch_slip",tcs[1].mean_rear_slip<tcs[0].mean_rear_slip*.75 and tcs[1].active_ticks>0)
 var abs_results=[]
 for enabled in [false,true]:
  await reset(100);car.abs_enabled=enabled;car.wetness=1;car.gear=3;car.test_input={"brake":1.0}
  var slip=0.0;var active=0;var ticks=0;var origin=car.position
  while car.speed_kph>.8 and ticks<1200:
   await frames(1);ticks+=1;slip+=absf(car.wheels[0].slip)
   if car.abs_active:active+=1
  abs_results.append({"enabled":enabled,"mean_front_slip":slip/maxi(1,ticks),"distance_m":origin.distance_to(car.position),"active_ticks":active})
 results.measurements["abs"]=abs_results
 check("ABS_reduces_wheel_lock",abs_results[1].mean_front_slip<abs_results[0].mean_front_slip*.75 and abs_results[1].active_ticks>0)
 var esc=[]
 for enabled in [false,true]:
  await reset(110);car.esc_enabled=enabled;car.cfg.grip_rear=.7;car.gear=3;car.angular_velocity=Vector3(0,1.1,0)
  var instability=0.0;var active=0
  for i in range(180):
   await frames(1);instability+=absf(car.angular_velocity.y)/120
   if car.esc_active:active+=1
  esc.append({"enabled":enabled,"integrated_yaw_rad":instability,"active_ticks":active})
 results.measurements["esc"]=esc
 check("ESC_reduces_yaw_disturbance",esc[1].integrated_yaw_rad<esc[0].integrated_yaw_rad and esc[1].active_ticks>0)
 await reset(80);car.test_input={"handbrake":1.0};await frames(45)
 check("handbrake_locks_rear",absf(car.wheels[2].omega)<1 and absf(car.wheels[3].omega)<1)
 await reset(110);car.gear=4;car.test_input={"left":1.0};await frames(50)
 check("high_speed_steering_reduced",absf(car.wheel_visuals[0].rotation.y)<.23 and absf(car.steering)>.8)
 await frames(180)
 check("high_speed_corner_stays_upright",car.global_basis.y.dot(Vector3.UP)>.8 and absf(car.angular_velocity.y)<1.2)
 await reset();car.test_input={"throttle":1.0};var maxspeed=0.0;var maxrpmerror=0.0;var shift_events=[];var lastgear=1
 for i in range(120*95):
  await frames(1);maxspeed=maxf(maxspeed,car.speed_kph)
  if car.gear!=lastgear:shift_events.append({"from":lastgear,"to":car.gear,"speed_kph":car.speed_kph,"rpm":car.rpm});lastgear=car.gear
  if car.shift_timer==0 and car.shift_cooldown<.1 and car.speed_kph>40:
   var target=(car.wheels[2].omega+car.wheels[3].omega)*.5*car.get_ratio()*60/TAU
   maxrpmerror=maxf(maxrpmerror,absf(car.rpm-target)/maxf(target,850))
 results.measurements["maximum_speed_after_95s_kph"]=maxspeed;results.measurements["shift_events"]=shift_events;results.measurements["max_coupled_rpm_relative_error"]=maxrpmerror
 check("rpm_matches_driven_wheels",maxrpmerror<.06)
 check("all_six_gears_used",car.gear==6)
 check("GT_reaches_250kph",maxspeed>250)
 # Neutral must coast, not drive under throttle.
 await reset();car.set_selector("N");car.test_input={"throttle":1.0};await frames(240)
 check("neutral_disconnects_drive",car.speed_kph<.2 and car.rpm>6500)
 await reset();car.automatic=false;car.selector="M";car.gear=6;car.auto_clutch=false;car.test_input={};await frames(100)
 check("full_manual_low_rpm_lug",car.rpm<car.cfg.idle_rpm)
 # Inclined surface: neutral rollback, parking lock, uphill launch.
 var hill=StaticBody3D.new();hill.position=Vector3(1000,0,0);hill.rotation.x=deg_to_rad(8);scene.add_child(hill)
 var hill_shape=BoxShape3D.new();hill_shape.size=Vector3(30,1,100);var hill_col=CollisionShape3D.new();hill_col.shape=hill_shape;hill.add_child(hill_col)
 await reset();car.recover(Transform3D(Basis(Vector3.RIGHT,deg_to_rad(8)),Vector3(1000,4.7,-25)));car.test_input={"brake":1.0};await frames(240)
 check("slope_four_wheel_contact",car.grounded==4)
 car.set_selector("N");car.test_input={};await frames(240)
 check("neutral_rolls_downhill",car.forward_speed<-.5)
 car.test_input={"brake":1.0};await frames(240);var parked=car.set_selector("P");var hill_origin=car.position;car.test_input={};await frames(480)
 results.measurements["slope_park_drift_m"]=car.position.distance_to(hill_origin)
 check("park_holds_on_8_degree_slope",parked and car.position.distance_to(hill_origin)<.15)
 car.set_selector("D");car.test_input={"throttle":.9};await frames(240)
 check("uphill_launch",car.forward_speed>1.0)
 # Rigid collision and continuous collision detection at 100 km/h.
 await reset(100)
 var wall=StaticBody3D.new();wall.position=Vector3(0,2,-30);scene.add_child(wall)
 var wall_shape=BoxShape3D.new();wall_shape.size=Vector3(20,4,.5);var wall_col=CollisionShape3D.new();wall_col.shape=wall_shape;wall.add_child(wall_col)
 await frames(240)
 check("collision_does_not_tunnel",car.position.z> -31 and car.position.is_finite())
 check("collision_reduces_speed",car.speed_kph<50)
 # Engine-side changes must not depend on graphics frame rate; separate core runs cover 30/60/120 render ticks.
 var f=FileAccess.open("res://tests/dynamics_results.json",FileAccess.WRITE);f.store_string(JSON.stringify(results,"  "));f.close()
 var ok=true
 for value in results.checks.values():if not value:ok=false
 print(JSON.stringify(results));scene.queue_free();await process_frame;quit(0 if ok else 1)
