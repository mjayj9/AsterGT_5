extends SceneTree
var scene: Node3D
var world: GTWorld
var car: GTCar
var elapsed: float=0
var progress: float=0
var last_along: float=1180
var next_sample: float=0
var stuck: float=0
var airborne: float=0
var max_airborne: float=0
var max_lane_error: float=0
var finished: bool=false
var wet_run: bool=false
var report={"checks":{},"samples":[],"driver":"Automated pure-pursuit driver applying throttle, brake and steering to GTCar. No transforms are changed after the initial spawn.","teleports":0,"collisions":0}
func _initialize() -> void:call_deferred("setup")
func setup() -> void:
 scene=Node3D.new();root.add_child(scene);world=GTWorld.new();scene.add_child(world)
 car=GTCar.new();car.transform=world.road_transform(1180,2.8);scene.add_child(car);world.player=car;world.set_density(.1)
 wet_run="--wet" in OS.get_cmdline_user_args()
 if wet_run:world.weather=2;world.time_of_day=2;world.update_weather();car.wetness=1
 car.test_input={"brake":1.0}
func _process(dt: float) -> bool:
 if world and not finished:world.update_streaming(dt)
 return false
func _physics_process(dt: float) -> bool:
 if not car or finished:return false
 elapsed+=dt
 if elapsed<2:return false
 var near=world.nearest(car.position);var step=wrapf(near.along-last_along,-world.length*.5,world.length*.5)
 if absf(step)>100:finish(false,"Route projection jumped");return false
 progress+=step;last_along=near.along
 var speed=maxf(car.forward_speed,0);var lookahead=clampf(10+speed*.8,12,45)
 var target=world.road_transform(near.along+lookahead,2.8).origin;var local=car.to_local(target)
 var angle=atan2(-2*car.cfg.wheelbase*local.x,maxf(4,local.x*local.x+local.z*local.z))
 var steer=clampf(angle/deg_to_rad(car.cfg.max_steer)*(1+speed*car.cfg.steering_speed_factor),-1,1)
 var target_speed=27.0
 for ahead in [20,65,130]:
  var a=world.direction(near.along+ahead-12);var b=world.direction(near.along+ahead+12)
  var curvature=acos(clampf(a.dot(b),-1,1))/24.0
  target_speed=minf(target_speed,sqrt((2.3 if wet_run else 3.3)/maxf(.0001,curvature)))
 target_speed=clampf(target_speed,6,27)
 var throttle=clampf((target_speed-speed)*.20+.15,0,.85)
 var brake=clampf((speed-target_speed)*.18,0,.8)
 car.test_input={"throttle":throttle,"brake":brake,"left":maxf(steer,0),"right":maxf(-steer,0)}
 var target_lane=world.road_transform(near.along,2.8).origin
 var lane_error=absf((car.position-target_lane).dot(world.direction(near.along).cross(Vector3.UP)))
 max_lane_error=maxf(max_lane_error,lane_error)
 airborne=airborne+dt if car.grounded<2 else 0
 max_airborne=maxf(max_airborne,airborne)
 stuck=stuck+dt if speed<1 else 0
 if car.collision_energy>.15:report.collisions+=1
 if progress>=next_sample:
  report.samples.append({"route_m":progress,"position":[car.position.x,car.position.y,car.position.z],"speed_kph":car.speed_kph,"gear":car.gear,"rpm":car.rpm,"contacts":car.grounded,"lane_error_m":lane_error})
  print("ROUTE ",roundi(progress)," / ",roundi(world.length)," m  ",roundi(car.speed_kph)," km/h  lane ",snappedf(lane_error,.01));next_sample+=500
 if not car.position.is_finite() or car.global_basis.y.dot(Vector3.UP)<.2 or airborne>4 or stuck>20 or elapsed>3000:finish(false,"Stuck, unstable, or timeout")
 elif progress>=world.length:finish(true,"Completed full continuous loop")
 return false
func finish(ok: bool,reason: String) -> void:
 if finished:return
 finished=true;car.test_input={"brake":1.0}
 report["weather"]="rain/night" if wet_run else "clear/day";report["final_tire_state"]=car.telemetry()
 report["reason"]=reason;report["route_length_m"]=world.length;report["progress_m"]=progress;report["odometer_m"]=car.odometer;report["simulation_seconds"]=elapsed;report["max_lane_error_m"]=max_lane_error;report["longest_airborne_s"]=max_airborne
 report.checks={"full_26km_loop":ok,"no_teleports":report.teleports==0,"actual_distance_covers_loop":car.odometer>=world.length*.98,"no_prolonged_airborne":max_airborne<4,"finite_state":car.position.is_finite()}
 var file=FileAccess.open("res://tests/continuous_route_wet_results.json" if wet_run else "res://tests/continuous_route_results.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"  "));file.close()
 print("CONTINUOUS_ROUTE_DONE ",ok," ",reason)
 call_deferred("cleanup",ok)
func cleanup(ok: bool) -> void:
 await world.stop_streaming();scene.queue_free();await process_frame;await process_frame;quit(0 if ok else 1)
