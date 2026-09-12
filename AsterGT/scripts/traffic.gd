class_name GTTraffic
extends Node3D
var world: GTWorld
var car: GTCar
var cars: Array[Dictionary]=[]
var density: int=12
var enabled: bool=true
var clock: float=0
var rng=RandomNumberGenerator.new()
var tuning: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://config/traffic_physics.json"))
var asset: PackedScene=preload("res://assets/v4/traffic_lod1.glb")
func _ready() -> void:rng.seed=1240
func set_density(count: int) -> void:
 density=clampi(count,0,36)
 for item in cars:item.body.queue_free()
 cars.clear()
 for i in range(density):
  var direction_sign=1 if i%3!=0 else -1
  var along=world.nearest(car.position).along+rng.randf_range(150,850)*(1 if i%2==0 else -1)
  var spec=tuning.classes[i%tuning.classes.size()]
  var tr=world.road_transform(along,2.8*direction_sign)
  if direction_sign<0:tr.basis=tr.basis.rotated(tr.basis.y,PI)
  var body=make_far(spec);body.transform=tr
  var speed=rng.randf_range(tuning.cruise_min_mps,tuning.cruise_max_mps)
  cars.append({"body":body,"d":along,"dir":direction_sign,"speed":speed,"lane":2.8*direction_sign,"spec":spec,"velocity":-tr.basis.z*speed,"spin":Vector3.ZERO,"far_clock":0.0})
func make_far(spec: Dictionary) -> Node3D:
 var body=Node3D.new();add_child(body)
 var visual=asset.instantiate();visual.scale=Vector3(spec.size_m[0]/1.87,spec.size_m[1]/1.45,spec.size_m[2]/4.42);body.add_child(visual)
 for mesh in visual.find_children("*","MeshInstance3D",true,false):mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
 return body
func promote(item: Dictionary) -> void:
 var old: Node3D=item.body;var tr=old.global_transform
 var body=GTTrafficBody.new();body.world=world;body.manager=self;body.tuning=tuning;body.spec=item.spec;body.route_distance=item.d;body.direction_sign=item.dir;body.lane=item.lane;body.cruise_mps=item.speed;body.transform=tr
 add_child(body);body.linear_velocity=item.velocity;body.angular_velocity=item.spin
 item.body=body;old.queue_free()
 GTQA.record("traffic_transition",{"mode":"Dynamic","id":body.get_instance_id(),"velocity_mps":[body.linear_velocity.x,body.linear_velocity.y,body.linear_velocity.z]})
func demote(item: Dictionary) -> void:
 var old: GTTrafficBody=item.body
 item.velocity=old.linear_velocity;item.spin=old.angular_velocity;item.d=world.nearest(old.position).along;item.speed=maxf(0,old.linear_velocity.dot(-old.global_basis.z))
 var body=make_far(item.spec);body.global_transform=old.global_transform
 item.body=body;item.far_clock=0.0;old.queue_free()
func _physics_process(dt: float) -> void:
 if not enabled or not car:return
 clock+=dt
 for item in cars:
  var body: Node3D=item.body
  var distance=body.global_position.distance_to(car.global_position)
  var relative=(car.linear_velocity-item.velocity).length()
  var activation=maxf(tuning.near_min_m,relative*tuning.activation_horizon_s+30)
  if body is GTTrafficBody:
   item.velocity=body.linear_velocity;item.spin=body.angular_velocity
   # Hysteresis and recovery lock. Off-road/damaged traffic stays physical.
   if not item.get("qa_pinned",false) and distance>maxf(tuning.far_release_m,activation+120) and body.mode=="Dynamic" and absf(body.lane-body.direction_sign*tuning.lane_width_m*.5)<.1 and body.signal_side==0 and body.damage.state.body<.01 and body.grounded>=3 and body.angular_velocity.length()<.15:
    demote(item)
  elif distance<activation:promote(item)
  else:
   item.far_clock+=dt
   if item.far_clock<tuning.far_update_s:continue
   var elapsed: float=item.far_clock;item.far_clock=0
   item.d=fposmod(item.d+item.speed*elapsed*item.dir,world.length)
   var tr=world.road_transform(item.d,item.lane)
   if item.dir<0:tr.basis=tr.basis.rotated(tr.basis.y,PI)
   var previous_yaw=body.rotation.y
   body.global_transform=tr
   item.velocity=-tr.basis.z*item.speed
   item.spin=Vector3(0,angle_difference(previous_yaw,body.rotation.y)/elapsed,0)

func spawn_qa_vehicle(at: Transform3D,mass_kg: float,velocity_mps: Vector3=Vector3.ZERO,spin_rad_s: Vector3=Vector3.ZERO,controller: bool=false) -> GTTrafficBody:
 var body=GTTrafficBody.new();body.world=world;body.manager=self;body.tuning=tuning;body.spec=tuning.classes[1].duplicate(true)
 body.spec.mass_kg=clampf(mass_kg,800,8000);body.transform=at;body.controller_enabled=controller;body.cruise_mps=0
 body.route_distance=world.nearest(at.origin).along;add_child(body);body.linear_velocity=velocity_mps;body.angular_velocity=spin_rad_s
 cars.append({"body":body,"d":body.route_distance,"dir":1,"speed":0,"lane":2.8,"spec":body.spec,"velocity":velocity_mps,"spin":spin_rad_s,"far_clock":0.0,"qa_pinned":true})
 GTQA.record("qa_fixture",{"id":body.get_instance_id(),"mass_kg":body.mass,"controller":controller})
 return body

func lane_clear(subject: GTTrafficBody,wanted_lane: float,ahead_m: float,behind_m: float) -> bool:
 var candidates: Array[Node3D]=[car]
 for item in cars:
  if item.body!=subject:candidates.append(item.body)
 for other in candidates:
  var nearest=world.nearest(other.global_position)
  var along_delta=fposmod(nearest.along-subject.route_distance+world.length*.5,world.length)-world.length*.5
  if along_delta < -behind_m or along_delta > ahead_m:continue
  var frame=world.road_transform(nearest.along,0)
  var actual_lane=(other.global_position-frame.origin).dot(frame.basis.x)
  if absf(actual_lane-wanted_lane)<tuning.clearance_lateral_m:return false
  if other is GTTrafficBody and absf(other.target_lane-wanted_lane)<tuning.clearance_lateral_m:return false
 return true
