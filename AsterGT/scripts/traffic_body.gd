class_name GTTrafficBody
extends RigidBody3D
var world: GTWorld
var manager: Node
var target_lane: float=2.8
var overtake_left: float=0
var signal_side: int=0
var spec: Dictionary
var tuning: Dictionary
var route_distance: float=0
var direction_sign: int=1
var lane: float=2.8
var cruise_mps: float=24
var controller_enabled: bool=true
var target_speed_mps: float=24
var mode: String="Dynamic"
var recovery_left: float=0
var stable_time: float=0
var time_s: float=0
var damage=GTContactDamage.new()
var visual: Node3D
var wheels: Array[Node3D]=[]
var brake_lamps: Array[GeometryInstance3D]=[]
var indicator_meshes: Array[MeshInstance3D]=[]
var light_material: StandardMaterial3D
var signal_material: StandardMaterial3D
var wheel_spin: float=0
var radius_m: float=.34
var brake_amount: float=0
var steer_angle: float=0
var ray_clock: float=0
var grounded: int=0
func _ready() -> void:
 target_lane=lane
 radius_m=tuning.wheel_radius_m*spec.size_m[1]/1.45
 mass=spec.mass_kg;continuous_cd=true;can_sleep=false;contact_monitor=true;max_contacts_reported=16
 collision_layer=4;collision_mask=1|2|4
 center_of_mass_mode=CENTER_OF_MASS_MODE_CUSTOM;center_of_mass=Vector3(0,-.18,0)
 var sz=Vector3(spec.size_m[0],spec.size_m[1],spec.size_m[2])
 inertia=Vector3(mass*(sz.y*sz.y+sz.z*sz.z)/12,mass*(sz.x*sz.x+sz.z*sz.z)/12,mass*(sz.x*sz.x+sz.y*sz.y)/12)
 linear_damp=0;linear_damp_mode=DAMP_MODE_REPLACE;angular_damp=.15;angular_damp_mode=DAMP_MODE_REPLACE
 var material=PhysicsMaterial.new();material.friction=tuning.friction;material.bounce=tuning.restitution;physics_material_override=material
 var proxies=JSON.parse_string(FileAccess.get_file_as_string("res://assets/v4/collision_proxies.json"))
 for entry in proxies.traffic:
  var cs=CollisionShape3D.new();cs.name=entry.name;var shape=ConvexPolygonShape3D.new();var points=PackedVector3Array()
  for v in entry.vertices:points.append(Vector3(v[0]*sz.x/1.87,v[1]*sz.y/1.45,v[2]*sz.z/4.42))
  shape.points=points;cs.shape=shape;add_child(cs)
 visual=load("res://assets/v4/traffic_lod0.glb").instantiate();visual.scale=Vector3(sz.x/1.87,sz.y/1.45,sz.z/4.42);add_child(visual)
 light_material=StandardMaterial3D.new();light_material.albedo_color=Color(.35,.008,.004);light_material.emission_enabled=true;light_material.emission=Color(1,.015,.003)
 signal_material=StandardMaterial3D.new();signal_material.albedo_color=Color(.55,.15,.005);signal_material.emission_enabled=true;signal_material.emission=Color(1,.3,.005)
 for mesh in visual.find_children("*TailLamp*","MeshInstance3D",true,false):mesh.material_override=light_material
 for tag in ["LF","RF","LR","RR"]:
  var node=visual.find_child("*Wheel_"+tag+"*",true,false) as Node3D
  if node:wheels.append(node)
 for side in [-1,1]:
  for z in [-sz.z*.501,sz.z*.501]:
   var light=MeshInstance3D.new();var box=BoxMesh.new();box.size=Vector3(.18,.09,.025);light.mesh=box;light.material_override=signal_material;light.position=Vector3(side*sz.x*.36,-.08,z);add_child(light);indicator_meshes.append(light)
func _integrate_forces(state: PhysicsDirectBodyState3D) -> void:
 var dt=state.step;time_s+=dt
 var basis=state.transform.basis;var front=-basis.z;var up=basis.y
 if damage.sample(self,state,time_s):
  recovery_left=tuning.recovery_min_s;stable_time=0;mode="Recovery";overtake_left=0;target_lane=direction_sign*tuning.lane_width_m*.5
 recovery_left=maxf(0,recovery_left-dt)
 if mode=="Recovery":
  var stable=state.linear_velocity.length()<tuning.stable_speed_mps and state.angular_velocity.length()<tuning.stable_spin_rad_s and up.dot(Vector3.UP)>.85
  stable_time=stable_time+dt if stable else 0
  if recovery_left<=0 and stable_time>tuning.stable_hold_s:
   # Resume from the actual position. No transform, basis or velocity reset.
   route_distance=world.nearest(state.transform.origin).along;mode="Rejoin"
 var speed=state.linear_velocity.dot(front)
 var nearest=world.nearest(state.transform.origin)
 route_distance=nearest.along
 overtake_left=maxf(0,overtake_left-dt)
 if mode=="Dynamic" and direction_sign>0 and target_lane<0 and overtake_left<=0 and manager.lane_clear(self,tuning.lane_width_m*.5,tuning.merge_front_m,tuning.merge_rear_m):
  target_lane=tuning.lane_width_m*.5
 lane=move_toward(lane,target_lane,tuning.lane_target_rate_mps*dt)
 var lane_tr=world.road_transform(route_distance,target_lane)
 var lateral_error=(lane_tr.origin-state.transform.origin).dot(basis.x)
 signal_side=int(signf(lateral_error)) if absf(lateral_error)>tuning.indicator_error_m else 0
 var ahead=maxf(tuning.path_lookahead_min_m,absf(speed)*tuning.follow_headway_s)
 var target=world.road_transform(route_distance+direction_sign*ahead,lane).origin
 var desired=state.transform.affine_inverse()*target
 steer_angle=clampf(atan2(-desired.x,maxf(.5,-desired.z)),-tuning.max_steer_rad,tuning.max_steer_rad)
 if mode=="Recovery":steer_angle=0
 if mode=="Rejoin" and nearest.distance<4:mode="Dynamic"
 ray_clock-=dt
 if ray_clock<=0:
  ray_clock=tuning.obstacle_poll_s
  var origin=state.transform.origin+front*spec.size_m[2]*.55
  var ray=PhysicsRayQueryParameters3D.create(origin,origin+front*(tuning.follow_gap_m+absf(speed)*tuning.follow_headway_s),2|4);ray.exclude=[get_rid()]
  var hit=state.get_space_state().intersect_ray(ray)
  target_speed_mps=cruise_mps*(1-damage.state.power)
  if not hit.is_empty():
   var gap=origin.distance_to(hit.position)
   target_speed_mps=minf(target_speed_mps,maxf(0,(gap-tuning.follow_gap_m)/tuning.follow_headway_s))
   if controller_enabled and mode=="Dynamic" and direction_sign>0 and target_lane>0 and signal_side==0 and overtake_left<=0 and gap>tuning.pass_gap_min_m and gap<tuning.pass_gap_max_m and target_speed_mps<cruise_mps-tuning.pass_speed_advantage_mps:
    var horizon=(cruise_mps+tuning.cruise_max_mps)*(tuning.pass_duration_s+tuning.pass_clearance_s)
    if manager.lane_clear(self,-tuning.lane_width_m*.5,horizon,tuning.merge_rear_m):
     target_lane=-tuning.lane_width_m*.5;overtake_left=tuning.pass_duration_s
 if mode=="Recovery":target_speed_mps=0
 if mode=="Rejoin":target_speed_mps=minf(target_speed_mps,tuning.rejoin_speed_mps)
 var accel=clampf((target_speed_mps-speed)*tuning.speed_controller_gain_per_s,-tuning.brake_accel_mps2,tuning.drive_accel_mps2)
 if mode=="Recovery" and recovery_left>tuning.recovery_min_s-tuning.coast_after_impact_s:accel=0
 if not controller_enabled:accel=0;steer_angle=0
 brake_amount=clampf(-accel/tuning.brake_accel_mps2,0,1)
 grounded=0
 for i in range(4):
  var rest=float(tuning.suspension_rest_m);var radius=radius_m
  var mount=Vector3((-1 if i%2==0 else 1)*spec.size_m[0]*.45,-.33*spec.size_m[1]/1.45+rest-mass*9.81/(4*tuning.spring_n_m),(-1 if i<2 else 1)*spec.size_m[2]*.302)
  var from=state.transform*mount
  var ray=PhysicsRayQueryParameters3D.create(from,from-up*(rest+tuning.suspension_travel_m+radius),1);ray.exclude=[get_rid()]
  var hit=state.get_space_state().intersect_ray(ray)
  if hit.is_empty():continue
  grounded+=1
  var offset: Vector3=hit.position-state.transform.origin
  var velocity=state.linear_velocity+state.angular_velocity.cross(offset-basis*center_of_mass)
  var length_m=from.distance_to(hit.position)-radius
  var load_n=clampf((rest-length_m)*tuning.spring_n_m-velocity.dot(up)*tuning.damper_ns_m,0,mass*9.81)
  state.apply_force(hit.normal*load_n,offset)
  var wheel_forward=front.rotated(up,steer_angle*(1-damage.state.steering) if i<2 else 0)
  wheel_forward=wheel_forward.slide(hit.normal).normalized()
  var right=wheel_forward.cross(hit.normal).normalized()
  var longitudinal=accel*mass*.25
  var lateral=-velocity.dot(right)*mass*.25*tuning.lateral_damping_per_s
  var forces=Vector2(longitudinal,lateral).limit_length(load_n*tuning.lateral_grip*(.67 if world.weather==2 else 1))
  var rolling=-signf(speed)*load_n*tuning.rolling_resistance*minf(absf(speed),1)
  state.apply_force(wheel_forward*(forces.x+rolling)+right*forces.y,offset)
  if wheels.size()>i:wheels[i].position.y=(mount.y-length_m)/visual.scale.y
 state.apply_central_force(-state.linear_velocity*state.linear_velocity.length()*.5*tuning.air_density*spec.drag_area)
func _process(dt: float) -> void:
 wheel_spin=fmod(wheel_spin+linear_velocity.dot(-global_basis.z)/radius_m*dt,TAU)
 for i in range(wheels.size()):wheels[i].rotation=Vector3(-wheel_spin,steer_angle if i<2 else 0,0)
 light_material.emission_energy_multiplier=(2.5 if brake_amount>.15 else .25)*(1-damage.state.lights)
 var hazards=mode in ["Recovery","Rejoin"]
 for light in indicator_meshes:light.visible=hazards or (signal_side!=0 and int(signf(light.position.x))==signal_side)
 signal_material.emission_energy_multiplier=2.5*(1-damage.state.lights) if fmod(time_s,tuning.signal_period_s)<tuning.signal_period_s*.5 else 0
 damage.apply_visuals(visual)
func telemetry() -> Dictionary:
 return {"time_s":time_s,"id":get_instance_id(),"mode":mode,"target_lane_m":target_lane,"indicator":signal_side,"mass_kg":mass,"position_m":[global_position.x,global_position.y,global_position.z],"velocity_mps":[linear_velocity.x,linear_velocity.y,linear_velocity.z],"angular_velocity_rad_s":[angular_velocity.x,angular_velocity.y,angular_velocity.z],"damage":damage.state,"grounded":grounded}
