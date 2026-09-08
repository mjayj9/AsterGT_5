extends SceneTree
var scene: Node3D
var car: GTCar
var camera: GTCameraRig
var result={"checks":{},"measurements":{}}
func _initialize() -> void:call_deferred("run")
func frames(n: int) -> void:
 for i in range(n):await physics_frame
func check(name: String,ok: bool) -> void:result.checks[name]=ok;print("CHECK ",name," ",ok)
func reset(speed: float=0) -> void:
 car.automatic=true;car.auto_clutch=true;car.selector="D";car.gear=1;car.engine_on=true;car.cfg.preset("Street");car.service_tires();car.test_input={"brake":1.0};car.recover(Transform3D(Basis.IDENTITY,Vector3(0,.8,0)));await frames(150)
 car.linear_velocity=Vector3(0,0,-speed/3.6)
 for i in range(4):car.wheels[i].omega=speed/3.6/car.wheel_radii[i]
 car.test_input={};await frames(2)
func run() -> void:
 GTControls.initialize();scene=Node3D.new();root.add_child(scene)
 var floor=StaticBody3D.new();scene.add_child(floor);var col=CollisionShape3D.new();var shape=BoxShape3D.new();shape.size=Vector3(5000,1,5000);col.shape=shape;col.position.y=-.5;floor.add_child(col)
 car=GTCar.new();car.position.y=.8;scene.add_child(car);camera=GTCameraRig.new();camera.car=car;scene.add_child(camera)
 await reset()
 check("porsche_model_loaded",car.imported_model and car.body_visual.find_child("Body",true,false)!=null)
 check("four_separate_wheel_pivots",car.wheel_visuals.size()==4 and car.calipers.size()==4)
 var contact_error=0.0
 for i in range(4):contact_error=maxf(contact_error,absf(car.wheel_visuals[i].global_position.y-car.wheel_radii[i]))
 result.measurements["wheel_ground_error_m"]=contact_error
 check("visual_tire_ground_alignment",contact_error<.018)
 car.test_input={"throttle":.8};await frames(360)
 check("wheels_roll_from_angular_velocity",absf(car.wheels[2].omega)>20 and absf(car.wheel_visuals[2].rotation.x)>0.05)
 car.test_input={"left":.5,"throttle":.25};await frames(40)
 check("front_wheels_steer",absf(car.wheel_visuals[0].rotation.y)>.02 and absf(car.wheel_visuals[2].rotation.y)<.001)
 check("calipers_do_not_spin",absf(car.calipers[0].rotation.x)<.001 and absf(car.calipers[0].rotation.y-car.wheel_visuals[0].rotation.y)<.001)
 var brakes=[]
 for cold in [false,true]:
  await reset(100);car.gear=3
  for w in car.wheels:w.temperature=20.0 if cold else 70.0
  var origin=car.position;car.test_input={"brake":1.0};var ticks=0
  while car.speed_kph>.8 and ticks<1200:await frames(1);ticks+=1
  brakes.append(origin.distance_to(car.position))
 result.measurements["warm_cold_brake_distance_m"]=brakes
 check("cold_tires_change_braking",brakes[1]>brakes[0]+1)
 await reset();car.tcs_enabled=false;car.cfg.torque_scale=1.8;car.wetness=1;car.test_input={"throttle":1.0};await frames(900)
 var heat=0.0;var wear=0.0
 for w in car.wheels:heat=maxf(heat,w.temperature);wear=maxf(wear,w.wear)
 result.measurements["slip_tire_peak_c"]=heat;result.measurements["slip_tire_wear"]=wear
 check("slip_heats_tires",heat>72)
 check("slip_wears_tires",wear>.0005)
 car.service_tires();check("tire_service_restores",car.wheels[2].wear==0 and car.wheels[2].temperature==car.cfg.tire_optimal_c)
 await reset();car.automatic=false;car.selector="M";car.gear=6;car.auto_clutch=false;car.test_input={};await frames(240)
 check("full_manual_engine_stalls",not car.engine_on)
 check("restart_requires_clutch",not car.toggle_ignition())
 car.test_input={"clutch":1.0};await frames(60);check("clutched_restart_works",car.toggle_ignition());await frames(60)
 check("restarted_engine_idles",car.engine_on and car.rpm>700)
 await reset();camera.menu_preview=false
 for mode in range(5):
  camera.mode=mode;camera.offsets[mode]=Vector3(100,-100,-100);camera.fovs[mode]=NAN;camera.sanitize()
  check("camera_limits_%d"%mode,camera.offsets[mode].x<=GTCameraRig.MAX_OFFSETS[mode].x and camera.offsets[mode].y>=GTCameraRig.MIN_OFFSETS[mode].y and is_finite(camera.fovs[mode]))
  camera.offsets[mode]=GTCameraRig.DEFAULT_OFFSETS[mode]
 camera.mode=3;camera.update_visibility()
 var banner=car.body_visual.find_child("INT_BANNER_INT_BANNER_0",true,false)
 var hidden=not banner.visible
 camera.mode=0;camera.update_visibility()
 check("cockpit_visor_visibility_restores",hidden and banner.visible)
 var wall=StaticBody3D.new();wall.position=Vector3(0,2,4);scene.add_child(wall);var wc=CollisionShape3D.new();var ws=BoxShape3D.new();ws.size=Vector3(12,5,.2);wc.shape=ws;wall.add_child(wc);await frames(4)
 var hit=camera.safe_position(Vector3(0,1.4,0),Vector3(0,1.4,9))
 check("sphere_camera_wall_clearance",hit.z<3.76)
 camera.mode=0;camera.first=false;camera.camera.global_position=Vector3(0,1.8,8);camera.update(.016)
 check("smoothed_camera_cannot_cross_wall",camera.camera.global_position.z<3.76)
 var f=FileAccess.open("res://tests/upgrade_results.json",FileAccess.WRITE);f.store_string(JSON.stringify(result,"  "));f.close()
 var ok=true
 for v in result.checks.values():if not v:ok=false
 print("UPGRADE_DONE ",ok);scene.queue_free();await process_frame;await process_frame;quit(0 if ok else 1)
