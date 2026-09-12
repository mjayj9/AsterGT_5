class_name GTCameraRig
extends Node3D
var car: GTCar
var reduced_motion: bool=false
var experience: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://config/experience.json"))
var camera: Camera3D
var mode: int=0
const DEFAULT_OFFSETS=[Vector3(0,1.8,7.3),Vector3(0,-.27,-2.49),Vector3(0,.33,-1.14),Vector3(-.306,.22,.12),Vector3(5,1.8,6)]
const MIN_OFFSETS=[Vector3(-3,.8,3.4),Vector3(-.4,-.38,-2.7),Vector3(-.35,.29,-1.4),Vector3(-.40,.17,-.05),Vector3(3,1,4)]
const MAX_OFFSETS=[Vector3(3,4,11),Vector3(.4,-.14,-2.42),Vector3(.35,.55,-.9),Vector3(-.23,.27,.22),Vector3(7,3,8)]
var offsets: Array[Vector3]=[Vector3(0,1.8,7.3),Vector3(0,-.27,-2.49),Vector3(0,.33,-1.14),Vector3(-.306,.22,.12),Vector3(5,1.8,6)]
var fovs: Array[float]=[65,78,74,78,57]
var shake_strength: float=.10
var orbit_yaw: float=.55
var orbit_pitch: float=.20
var orbit_distance: float=7
var menu_preview: bool=true
var smoothed_yaw: float=0
var first: bool=true
var collision_radius: float=.16
var collision_count: int=0
var probe=SphereShape3D.new()
const NAMES=["CHASE","BUMPER","HOOD","COCKPIT","ORBIT"]
func _ready() -> void:
 camera=Camera3D.new();camera.near=.055;camera.far=9000;add_child(camera);camera.make_current();probe.radius=collision_radius
 load_settings()
func cycle() -> void:
 mode=(mode+1)%5;first=true;update_visibility()
func update_visibility() -> void:
 if not car or not car.body_visual:return
 if car.imported_model:
  for node in car.body_visual.find_children("*","MeshInstance3D",true,false):
   if "MIRROR" in str(node.name):node.visible=not (mode==3 and not menu_preview)
   if "INT_BANNER" in str(node.name) or "EXT_Banner" in str(node.name):node.visible=not (mode==3 and not menu_preview)
  return
 for node in car.body_visual.find_children("*","MeshInstance3D",true,false):
  if "Windshield" in node.name or "Roof" in node.name or "SideWindow" in node.name or "RearGlass" in node.name:node.visible=not (mode==3 and not menu_preview)
func sanitize() -> void:
 mode=clampi(mode,0,4)
 shake_strength=clampf(shake_strength if is_finite(shake_strength) else .1,0,1)
 for i in range(5):
  fovs[i]=clampf(fovs[i] if is_finite(fovs[i]) else 70,40,105)
  for axis in range(3):offsets[i][axis]=clampf(offsets[i][axis] if is_finite(offsets[i][axis]) else DEFAULT_OFFSETS[i][axis],MIN_OFFSETS[i][axis],MAX_OFFSETS[i][axis])
func safe_position(origin: Vector3,target: Vector3) -> Vector3:
 var delta=target-origin
 if delta.length()<.001:return target
 var q=PhysicsShapeQueryParameters3D.new();q.shape=probe;q.transform=Transform3D(Basis.IDENTITY,origin);q.motion=delta;q.collision_mask=1|4;q.exclude=[car.get_rid()];q.margin=.02
 var space=car.get_world_3d().direct_space_state
 var hit=space.cast_motion(q)
 if hit.size()>0 and hit[0]<1.0:
  collision_count+=1
  return origin+delta*maxf(0,hit[0]-.025/delta.length())
 return target
func _unhandled_input(event: InputEvent) -> void:
 if mode!=4 or menu_preview or not GTControls.driving():return
 if event is InputEventMouseMotion and Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT):
  orbit_yaw-=event.relative.x*.006;orbit_pitch=clampf(orbit_pitch+event.relative.y*.003,.04,.95)
 if event is InputEventMouseButton and event.pressed:
  if event.button_index==MOUSE_BUTTON_WHEEL_UP:orbit_distance=maxf(3.4,orbit_distance-.5)
  if event.button_index==MOUSE_BUTTON_WHEEL_DOWN:orbit_distance=minf(15,orbit_distance+.5)
func update(dt: float) -> void:
 if not car:return
 sanitize()
 var tr=car.global_transform;var target: Vector3;var look: Vector3
 var anchor=tr.origin+Vector3.UP*.4
 if menu_preview:
  target=tr.origin-tr.basis.z*5.4+tr.basis.x*5.5+Vector3.UP*1.8
  look=tr.origin-(tr.origin-target).normalized().cross(Vector3.UP)*2.25+Vector3.UP*.06
  camera.fov=47
 else:
  smoothed_yaw=lerp_angle(smoothed_yaw,car.rotation.y,1-exp(-7*dt)) if not first else car.rotation.y
  var b=Basis(Vector3.UP,smoothed_yaw);var rear=GTControls.value("look_back")>.5
  if mode==0:
   target=tr.origin+b*(Vector3(0,1.65,-6.8) if rear else offsets[0])
   look=tr.origin+b*Vector3(0,.4,3 if rear else -3)
  elif mode==4:
   target=tr.origin+b*Vector3(sin(orbit_yaw)*orbit_distance,1.0+sin(orbit_pitch)*orbit_distance,cos(orbit_yaw)*orbit_distance)+b*(offsets[4]-DEFAULT_OFFSETS[4]);look=tr.origin+Vector3.UP*.06
   if rear:target=tr.origin+b*Vector3(0,1.65,-6.8);look=tr.origin+b*Vector3(0,.4,3)
  else:
   target=tr*offsets[mode];look=target+(-tr.basis.z if not rear else tr.basis.z)*50+Vector3.UP*.05
   anchor=tr*Vector3(-.306,.22,.12) if mode==3 else tr.origin+Vector3.UP*.2
  var effects=0.0 if reduced_motion else shake_strength
  target+=tr.basis*Vector3(-car.acceleration_local.x,0,-car.acceleration_local.z)*experience.camera_displacement_m_per_mps2*effects
  target.y+=car.road_vibration*experience.camera_road_effect_m*effects
  camera.fov=lerpf(camera.fov,fovs[mode]+speed_fov(mode,car.speed_kph)*(0.3 if reduced_motion else 1.0),1-exp(-4*dt))
 target=safe_position(anchor,target)
 var proposed=target if first or mode in [1,2,3] else camera.global_position.lerp(target,1-exp(-10*dt))
 # Resolve the final smoothed position, so damping cannot leave the camera behind a wall.
 camera.global_position=safe_position(anchor,proposed)
 camera.look_at(look,Vector3.UP)
 if not menu_preview and not reduced_motion:
  var limit=float(experience.max_acceleration_effect_mps2)
  camera.rotate_object_local(Vector3.RIGHT,-clampf(car.acceleration_local.z,-limit,limit)*experience.camera_accel_pitch_rad_per_mps2*shake_strength)
  camera.rotate_object_local(Vector3.BACK,clampf(car.acceleration_local.x,-limit,limit)*experience.camera_lateral_roll_rad_per_mps2*shake_strength)
 car.update_lod(camera.global_position.distance_to(car.global_position),mode==3 and not menu_preview)
 first=false
func speed_fov(camera_index: int,speed: float) -> float:
 var knots=experience.fov_speed_knots_kph
 var values=experience.fov_add_degrees[camera_index]
 for i in range(knots.size()-1):
  if speed<=knots[i+1]:return lerpf(values[i],values[i+1],clampf((speed-knots[i])/(knots[i+1]-knots[i]),0,1))
 return values[-1]
func save_settings() -> Error:
 sanitize()
 var d={"version":4,"reduced_motion":reduced_motion,"shake":shake_strength,"fovs":fovs,"offsets":[]}
 for v in offsets:d.offsets.append([v.x,v.y,v.z])
 return GTSafeStore.save_json("user://cameras.json",d)
func load_settings() -> void:
 if not FileAccess.file_exists("user://cameras.json"):return
 var d=JSON.parse_string(FileAccess.get_file_as_string("user://cameras.json"))
 if not d is Dictionary:return
 if d.get("reduced_motion") is bool:reduced_motion=d.reduced_motion
 if d.get("shake") is float:shake_strength=d.shake
 if d.get("fovs") is Array and d.fovs.size()==5:
  for i in range(5):
   if d.fovs[i] is float:fovs[i]=d.fovs[i]
 if d.get("version",0)>=2 and d.get("offsets") is Array and d.offsets.size()==5:
  for i in range(5):
   if d.offsets[i] is Array and d.offsets[i].size()==3:
    var a=d.offsets[i]
    if a[0] is float and a[1] is float and a[2] is float:offsets[i]=Vector3(a[0],a[1],a[2])
 sanitize()
