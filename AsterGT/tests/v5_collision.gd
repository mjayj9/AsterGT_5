extends SceneTree
# v5 development regression fixture. Production v5 classes. No InputEvent
# injection, direct damage/impulse assignment, freezing, or post-release resets.
var fixture_root: Node3D
var route: GTWorld
var manager: GTTraffic
var player_reference: GTCar
var a: RigidBody3D
var b: RigidBody3D
var collector: GTQA
var output: FileAccess
var condition: String = "C1"
var repetition: int = 1
var output_path: String = ""
var elapsed: float = 0
var released: bool = false
var first_contact_s: float = -1
var sample_index: int = 0
var intended_a_kph: float
var intended_b_kph: float
var fixture_start_tick: int
var initial_a_kph: float = -1

func _initialize() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--condition="): condition = arg.trim_prefix("--condition=")
  if arg.begins_with("--initial-a-kph="): initial_a_kph = float(arg.trim_prefix("--initial-a-kph="))
  if arg.begins_with("--repeat="): repetition = int(arg.trim_prefix("--repeat="))
  if arg.begins_with("--output="): output_path = arg.trim_prefix("--output=")
 call_deferred("setup_fixture")

func vec(v: Vector3) -> Array:
 return [v.x,v.y,v.z]

func write_row(kind: String, data: Dictionary) -> void:
 output.store_line(JSON.stringify({"schema_version":1,"kind":kind,"fixture":condition,"repeat":repetition,"fixture_time_s":elapsed,"global_tick":Engine.get_physics_frames(),"data":data}))

func setup_fixture() -> void:
 output = FileAccess.open(output_path,FileAccess.WRITE)
 if not output: printerr("HARNESS_OUTPUT_FAIL"); quit(21); return
 GTControls.initialize()
 # Route queries use the production curve. Rendering/streaming is irrelevant to
 # this wide, flat asphalt solver fixture; production _integrate_forces is intact.
 route=GTWorld.new(); route.make_route()
 fixture_root=Node3D.new(); root.add_child(fixture_root)
 var floor_body=StaticBody3D.new(); floor_body.name="QA_Asphalt"; floor_body.collision_layer=1; floor_body.collision_mask=2|4; floor_body.set_meta("surface","asphalt")
 var shape=CollisionShape3D.new(); var box=BoxShape3D.new(); box.size=Vector3(2000,1,2000); shape.shape=box; floor_body.add_child(shape)
 floor_body.position=Vector3(0,-.5,-500); fixture_root.add_child(floor_body)
 collector=GTQA.new(); collector.enabled=true; GTQA.instance=collector
 player_reference=GTCar.new(); player_reference.controls_enabled=false; player_reference.launch_hold=false; player_reference.engine_on=false; player_reference.selector="N"; player_reference.gear=0
 player_reference.transform=Transform3D(Basis.IDENTITY,Vector3(150,.67,-200)); fixture_root.add_child(player_reference)
 manager=GTTraffic.new(); manager.world=route; manager.car=player_reference; fixture_root.add_child(manager)
 var impact=Vector3(0,.67,-200)
 var target_basis=Basis.IDENTITY
 var mass_a=1265.0; var mass_b=1200.0
 intended_a_kph=30; intended_b_kph=0
 match condition:
  "D1": intended_a_kph=30; mass_b=1200; target_basis=Basis(Vector3.UP,deg_to_rad(30))
  "C2": intended_a_kph=100; mass_b=1580
  "C3": intended_a_kph=100; mass_b=2050; target_basis=Basis(Vector3.UP,deg_to_rad(30))
  "C4": intended_a_kph=50; intended_b_kph=50; mass_a=1200; mass_b=1580; target_basis=Basis(Vector3.UP,PI)
  "C5": intended_a_kph=300; target_basis=Basis(Vector3.UP,deg_to_rad(30))
  "C6": intended_a_kph=110; mass_a=1200; mass_b=1580; target_basis=Basis(Vector3.UP,PI*.5)
 # 1.25 s nominal approach, plus vehicle half-lengths. Speeds at first contact
 # are measured; nominal values are never substituted for actual coasting speed.
 var duration=1.25
 var pos_a=impact+Vector3(0,0,intended_a_kph/3.6*duration+2.5)
 var pos_b=impact+Vector3(.55 if condition in ["D1","C3","C5"] else 0,0,-intended_b_kph/3.6*duration-2.5)
 if condition in ["C4","C6"]:
  a=manager.spawn_qa_vehicle(Transform3D(Basis.IDENTITY,pos_a),mass_a,Vector3.ZERO,Vector3.ZERO,false)
 else:
  a=player_reference; a.global_transform=Transform3D(Basis.IDENTITY,pos_a)
 b=manager.spawn_qa_vehicle(Transform3D(target_basis,pos_b),mass_b,Vector3.ZERO,Vector3.ZERO,false)
 write_row("fixture_setup",{"engine":Engine.get_version_info().string,"physics_hz":Engine.physics_ticks_per_second,"ground":"QA flat asphalt, y=0, wide plane","production_physics_unmodified":true,"a_id":a.get_instance_id(),"b_id":b.get_instance_id(),"a_mass_kg":a.mass,"b_mass_kg":b.mass,"a_nominal_kph":intended_a_kph,"b_nominal_kph":intended_b_kph,"target_heading_deg":rad_to_deg(target_basis.get_euler().y),"target_lateral_offset_m":pos_b.x,"controller_a":false,"controller_b":false,"traffic_shape_note":"Production spawn_qa_vehicle uses Sedan geometry for every requested mass","initialization":"1 s gravity/suspension settle, then one-time velocity and wheel angular speed initialization; free evolution thereafter"})
 # Let both actual bodies settle under gravity and their own suspensions.
 for n in range(120): await physics_frame
 a.linear_velocity=Vector3(0,0,-(initial_a_kph if initial_a_kph>0 else intended_a_kph)/3.6)
 b.linear_velocity=Vector3(0,0,intended_b_kph/3.6)
 if a is GTCar:
  for i in range(a.wheels.size()): a.wheels[i].omega=((initial_a_kph if initial_a_kph>0 else intended_a_kph)/3.6)/a.wheel_radii[i]
 elapsed=0; released=true; fixture_start_tick=Engine.get_physics_frames()
 write_row("release",{"a":body_state(a),"b":body_state(b)})
 for n in range(1440):
  await physics_frame
  elapsed=float(Engine.get_physics_frames()-fixture_start_tick)/Engine.physics_ticks_per_second
  sample_index+=1
  var standard=collector.queue.duplicate(true); collector.queue.clear()
  for row in standard:
   write_row("production_"+row.kind,row.data)
   if row.kind=="contact" and int(row.data.self_id) in [a.get_instance_id(),b.get_instance_id()] and int(row.data.other_id) in [a.get_instance_id(),b.get_instance_id()] and first_contact_s<0:
    first_contact_s=elapsed
  write_row("state",{"a":body_state(a),"b":body_state(b)})
  if sample_index%120==0: output.flush()
  if first_contact_s>=0 and elapsed-first_contact_s>=6: break
 write_row("fixture_end",{"first_contact_s":first_contact_s,"post_contact_s":elapsed-first_contact_s if first_contact_s>=0 else 0,"samples":sample_index,"a":body_state(a),"b":body_state(b)})
 output.flush(); output.close()
 print("COLLISION_GATE_COMPLETE ",condition," repeat=",repetition," contact=",first_contact_s)
 GTQA.instance=null; collector.free(); fixture_root.free(); route.free(); quit(0)

func body_state(body) -> Dictionary:
 var d=body.telemetry().duplicate(true)
 d["local_damage_patches"]=body.damage.visuals.patches.duplicate(true)
 d["id"]=body.get_instance_id(); d["mass_kg"]=body.mass
 d["position_world_m"]=vec(body.global_position)
 d["basis_world"]=[vec(body.global_basis.x),vec(body.global_basis.y),vec(body.global_basis.z)]
 d["center_of_mass_world_m"]=vec(body.global_transform*body.center_of_mass)
 d["inertia_local_kgm2"]=vec(body.inertia)
 d["freeze"]=body.freeze; d["sleeping"]=body.sleeping; d["continuous_cd"]=body.continuous_cd
 d["collision_layer"]=body.collision_layer; d["collision_mask"]=body.collision_mask
 d["reported_contacts"]=body.damage.last_contacts.duplicate(true)
 if body is GTTrafficBody:
  d["controller_enabled"]=body.controller_enabled; d["recovery_left_s"]=body.recovery_left; d["stable_time_s"]=body.stable_time; d["steer_angle_rad"]=body.steer_angle; d["brake_amount"]=body.brake_amount
 return d


