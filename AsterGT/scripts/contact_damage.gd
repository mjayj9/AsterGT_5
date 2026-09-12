class_name GTContactDamage
extends RefCounted
var state: Dictionary={"front":0.0,"rear":0.0,"left":0.0,"right":0.0,"body":0.0,"lights":0.0,"steering":0.0,"power":0.0}
var recent: Dictionary={}
var last_contacts: Array=[]
var settings: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://config/experience.json"))
var impact: float=0
var visuals=GTLocalDamageVisual.new()
func sample(owner: RigidBody3D,physics: PhysicsDirectBodyState3D,time_s: float) -> bool:
 last_contacts.clear();impact=move_toward(impact,0,physics.step*4)
 var impacted=false
 var candidates: Dictionary={}
 for i in range(physics.get_contact_count()):
  var other=physics.get_contact_collider_object(i)
  var point=physics.get_contact_local_position(i)
  var raw_normal=physics.get_contact_local_normal(i)
  var impulse=physics.get_contact_impulse(i)
  var normal=impulse.normalized() if impulse.length()>0.001 else raw_normal.normalized()
  var relative=physics.get_contact_local_velocity_at_position(i)-physics.get_contact_collider_velocity_at_position(i)
  # GodotPhysics3D center_of_mass is a world-axis OFFSET from the body origin.
  # Contact points are world positions. Keep both lever-arm endpoints in world space.
  var world_center_of_mass=physics.transform.origin+physics.center_of_mass
  var r=point-world_center_of_mass
  var inverse_mass=physics.inverse_mass+normal.dot((physics.inverse_inertia_tensor*(r.cross(normal))).cross(r))
  if other is RigidBody3D:
   # RigidBody3D.center_of_mass is body-local (both vehicle classes use CUSTOM).
   var other_world_center_of_mass=other.global_transform*other.center_of_mass
   var r2=point-other_world_center_of_mass
   inverse_mass+=1.0/other.mass+normal.dot((other.get_inverse_inertia_tensor()*(r2.cross(normal))).cross(r2))
  # Impulse-derived incident normal energy estimate; solver owns ALL response impulses.
  var e=owner.physics_material_override.bounce if owner.physics_material_override else 0.0
  var energy=.5*pow(impulse.length()/(1+e),2)*maxf(0,inverse_mass)
  var source="solver_impulse"
  # First-tick Godot contacts may expose zero impulse. Estimate incoming normal
  # energy only for damage; never add a second physics response impulse.
  var closing=maxf(0,-relative.dot(raw_normal.normalized()))
  if impulse.length()<.001 and closing>1.0 and inverse_mass>0:
   energy=.5*closing*closing/inverse_mass;source="incoming_speed_estimate"
  var kind="vehicle" if other is RigidBody3D else ("road" if other and other.has_meta("surface") else "barrier")
  var id=physics.get_contact_collider_id(i)
  var local=physics.transform.affine_inverse()*point
  var zone="front" if local.z< -1 else "rear" if local.z>1 else "left" if local.x<0 else "right"
  var row={"time_s":time_s,"tick":Engine.get_physics_frames(),"self_id":owner.get_instance_id(),"other_id":id,"kind":kind,"zone":zone,"point_world_m":[point.x,point.y,point.z],"normal_world":[normal.x,normal.y,normal.z],"engine_contact_normal":[raw_normal.x,raw_normal.y,raw_normal.z],"relative_contact_velocity_mps":[relative.x,relative.y,relative.z],"impulse_ns":[impulse.x,impulse.y,impulse.z],"energy_source":source,"normal_energy_estimate_j":energy,"self_mass_kg":owner.mass,"other_mass_kg":other.mass if other is RigidBody3D else 0,"self_shape":physics.get_contact_local_shape(i),"other_shape":physics.get_contact_collider_shape(i)}
  last_contacts.append(row)
  if kind!="road" and energy>=120:
   row["point_local_m"]=[local.x,local.y,local.z]
   if not candidates.has(id) or energy>candidates[id].energy:
    var outward=-(physics.transform.basis.inverse()*raw_normal).normalized()
    var tangent=physics.transform.basis.inverse()*(relative-raw_normal*relative.dot(raw_normal))
    candidates[id]={"energy":energy,"point":local,"outward":outward,"tangent":tangent,"row":row,"zone":zone}
 for id in candidates:
  var hit=candidates[id]
  var prior=recent.get(id,{"time":-100.0,"point":Vector3.INF})
  if time_s-prior.time<settings.contact_damage_cooldown_s:continue
  recent[id]={"time":time_s,"point":hit.point}
  GTQA.record("contact",hit.row)
  visuals.add_hit(hit.point,hit.outward,hit.tangent,hit.energy,hit.tangent.length())
  if hit.energy>=900:
   var severity=clampf(hit.energy/settings.damage_energy_j,0,1)
   state[hit.zone]=clampf(state[hit.zone]+severity*.35,0,1)
   state.body=clampf(state.body+severity*.15,0,1)
   state.lights=maxf(state.front,state.rear)
   state.steering=maxf(state.left,state.right)*.35
   state.power=maxf(state.front,state.rear)*.35
   impact=maxf(impact,severity);impacted=impacted or severity>.015
 return impacted
func apply_visuals(root: Node3D) -> void:
 visuals.apply(root)
func repair() -> void:
 visuals.repair();recent.clear();last_contacts.clear();impact=0
 for key in state:state[key]=0.0
