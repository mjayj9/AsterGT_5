extends SceneTree
# Deterministic contact replay through the production GTContactDamage.sample().
# Native COM semantics are separately measured by native_com_probe.gd.
class ContactState extends PhysicsDirectBodyState3DExtension:
 var xf: Transform3D
 var com_local: Vector3
 var inv_mass: float
 var inv_tensor: Basis
 var point_world: Vector3
 var normal_world: Vector3
 var impulse_world: Vector3
 var velocity_a: Vector3
 var velocity_b: Vector3
 var collider: RigidBody3D
 func _get_transform() -> Transform3D:return xf
 func _get_center_of_mass() -> Vector3:return xf.basis*com_local
 func _get_center_of_mass_local() -> Vector3:return com_local
 func _get_step() -> float:return 1.0/120
 func _get_inverse_mass() -> float:return inv_mass
 func _get_inverse_inertia_tensor() -> Basis:return inv_tensor
 func _get_contact_count() -> int:return 1
 func _get_contact_collider_object(_i: int) -> Object:return collider
 func _get_contact_local_position(_i: int) -> Vector3:return point_world
 func _get_contact_local_normal(_i: int) -> Vector3:return normal_world
 func _get_contact_impulse(_i: int) -> Vector3:return impulse_world
 func _get_contact_local_velocity_at_position(_i: int) -> Vector3:return velocity_a
 func _get_contact_collider_velocity_at_position(_i: int) -> Vector3:return velocity_b
 func _get_contact_collider_id(_i: int) -> int:return collider.get_instance_id()
 func _get_contact_local_shape(_i: int) -> int:return 0
 func _get_contact_collider_shape(_i: int) -> int:return 0
func array3(v: Vector3) -> Array:return [v.x,v.y,v.z]
func relative_percent(a: float,b: float) -> float:return absf(a-b)/maxf(absf(a),.000000001)*100
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var cases=[]
 var owner=RigidBody3D.new();owner.mass=1265
 owner.physics_material_override=PhysicsMaterial.new();owner.physics_material_override.bounce=.05
 var offsets=[Vector3.ZERO,Vector3(4096,0,-2048)]
 for angle in [0.0,.625]:
  for magnitude in [1000.0,4000.0,8000.0]:
   var pair=[]
   for offset in offsets:
    var other=RigidBody3D.new();other.mass=1580;other.inertia=Vector3(1100,2700,1700);other.gravity_scale=0;other.can_sleep=false;other.collision_layer=0;other.collision_mask=0
    other.center_of_mass_mode=RigidBody3D.CENTER_OF_MASS_MODE_CUSTOM;other.center_of_mass=Vector3(-.125,-.25,.25)
    other.transform=Transform3D(Basis(Vector3.UP,-.25+angle),Vector3(8.5,8,4.5)+offset)
    var shape=CollisionShape3D.new();shape.shape=BoxShape3D.new();other.add_child(shape);root.add_child(other)
    var ps=ContactState.new();ps.xf=Transform3D(Basis(Vector3.UP,angle),Vector3(8,8,8)+offset);ps.com_local=Vector3(.125,-.125,.25);ps.inv_mass=1.0/owner.mass
    ps.inv_tensor=ps.xf.basis*Basis.from_scale(Vector3(1.0/510,1.0/1900,1.0/540))*ps.xf.basis.transposed()
    ps.point_world=ps.xf*Vector3(.75,-.125,-2.0);ps.normal_world=ps.xf.basis*Vector3(.25,0,1).normalized();ps.impulse_world=ps.normal_world*magnitude
    ps.velocity_a=Vector3(4,0,-25);ps.velocity_b=Vector3(0,0,3);ps.collider=other
    pair.append({"physics":ps,"other":other})
   cases.append({"angle_rad":angle,"impulse_ns":magnitude,"pair":pair})
 for i in range(4):await physics_frame
 var results=[];var failures=[];var max_energy_delta=0.0;var max_damage_delta=0.0;var max_expected_delta=0.0;var bad_formula_delta=0.0
 for case in cases:
  var samples=[]
  var reference=case.pair[0].physics
  # Translation-free lever arms, independent of the production world-COM expression.
  var r=reference.xf.basis*(Vector3(.75,-.125,-2)-reference.com_local)
  var other=case.pair[0].other
  var r2=Vector3(8,8,8)+reference.xf.basis*Vector3(.75,-.125,-2)-(Vector3(8.5,8,4.5)+other.global_basis*other.center_of_mass)
  var n=reference.impulse_world.normalized()
  var expected_inv=reference.inv_mass+n.dot((reference.inv_tensor*r.cross(n)).cross(r))+1.0/other.mass+n.dot((other.get_inverse_inertia_tensor()*r2.cross(n)).cross(r2))
  var expected_energy=.5*pow(reference.impulse_world.length()/(1+owner.physics_material_override.bounce),2)*expected_inv
  for fixture in case.pair:
   var ps=fixture.physics
   var damage=GTContactDamage.new();var impacted=damage.sample(owner,ps,1.0)
   var row=damage.last_contacts[0]
   var bad_r=ps.point_world-ps.center_of_mass
   var good_r=ps.point_world-ps.xf.origin-ps.center_of_mass
   var bad_extra=n.dot((ps.inv_tensor*bad_r.cross(n)).cross(bad_r))-n.dot((ps.inv_tensor*good_r.cross(n)).cross(good_r))
   var bad_energy=row.normal_energy_estimate_j+.5*pow(ps.impulse_world.length()/(1+owner.physics_material_override.bounce),2)*bad_extra
   samples.append({"origin_m":array3(ps.xf.origin),"point_world_m":array3(ps.point_world),"mass_kg":[owner.mass,fixture.other.mass],"velocity_a_mps":array3(ps.velocity_a),"velocity_b_mps":array3(ps.velocity_b),"normal_world":array3(ps.normal_world),"energy_j":row.normal_energy_estimate_j,"damage":damage.state.duplicate(true),"zone":row.zone,"impacted":impacted,"proposed_point_minus_offset_energy_j":bad_energy,"other_inverse_inertia":str(fixture.other.get_inverse_inertia_tensor())})
  var a=samples[0];var b=samples[1]
  var energy_delta=relative_percent(a.energy_j,b.energy_j);var damage_delta=0.0
  for zone in a.damage:damage_delta=maxf(damage_delta,relative_percent(a.damage[zone],b.damage[zone]))
  var expected_delta=maxf(relative_percent(expected_energy,a.energy_j),relative_percent(expected_energy,b.energy_j))
  max_energy_delta=maxf(max_energy_delta,energy_delta);max_damage_delta=maxf(max_damage_delta,damage_delta);max_expected_delta=maxf(max_expected_delta,expected_delta)
  bad_formula_delta=maxf(bad_formula_delta,relative_percent(a.proposed_point_minus_offset_energy_j,b.proposed_point_minus_offset_energy_j))
  var passed=energy_delta<=1 and damage_delta<=1 and expected_delta<=1 and a.zone==b.zone and a.impacted==b.impacted
  if not passed:failures.append({"angle":case.angle_rad,"impulse":case.impulse_ns})
  results.append({"angle_rad":case.angle_rad,"impulse_ns":case.impulse_ns,"expected_normal_energy_j":expected_energy,"energy_difference_percent":energy_delta,"damage_difference_percent":damage_delta,"expected_error_percent":expected_delta,"same_zone_and_impact_stage":a.zone==b.zone and a.impacted==b.impacted,"passed":passed,"samples":samples})
 var report={"scope":"Pre-QA blocker coordinate regression only; not final QA","engine":Engine.get_version_info().string,"backend":ProjectSettings.get_setting("physics/3d/physics_engine"),"method":"same contact replay through production sample; native COM probe stored separately","translation_m":array3(offsets[1]),"translation_length_m":offsets[1].length(),"case_count":results.size(),"max_energy_difference_percent":max_energy_delta,"max_damage_difference_percent":max_damage_delta,"max_expected_error_percent":max_expected_delta,"proposed_point_minus_offset_max_difference_percent":bad_formula_delta,"pass":failures.is_empty(),"results":results}
 var output="res://tests/preqa/contact_regression.json"
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
 var file=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify(report,"  "));file.close()
 print("PREQA_CONTACT_REGRESSION "+JSON.stringify({"pass":report.pass,"cases":results.size(),"max_energy_difference_percent":max_energy_delta,"max_damage_difference_percent":max_damage_delta,"max_expected_error_percent":max_expected_delta,"proposed_point_minus_offset_max_difference_percent":bad_formula_delta}))
 for case in cases:
  for fixture in case.pair:
   fixture.other.queue_free();fixture.physics.free()
 owner.free()
 await process_frame
 quit(0 if failures.is_empty() else 1)
