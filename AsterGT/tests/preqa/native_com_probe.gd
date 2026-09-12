extends SceneTree
class ProbeBody extends RigidBody3D:
 var captured: Dictionary={}
 func _integrate_forces(state: PhysicsDirectBodyState3D) -> void:
  captured={"origin":v(state.transform.origin),"com":v(state.center_of_mass),"com_local":v(state.center_of_mass_local),"world_com_from_local":v(state.transform*state.center_of_mass_local)}
 func v(x: Vector3) -> Array:return [x.x,x.y,x.z]
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var bodies=[]
 for offset in [Vector3.ZERO,Vector3(4096,0,-2048)]:
  var body=ProbeBody.new();body.gravity_scale=0;body.mass=1265;body.center_of_mass_mode=RigidBody3D.CENTER_OF_MASS_MODE_CUSTOM;body.center_of_mass=Vector3(.25,-.125,.5)
  body.transform=Transform3D(Basis(Vector3.UP,.5),offset)
  var cs=CollisionShape3D.new();var shape=BoxShape3D.new();shape.size=Vector3(2,1,4);cs.shape=shape;body.add_child(cs);root.add_child(body);bodies.append(body)
 for i in range(4):await physics_frame
 var rows=[]
 for body in bodies:rows.append(body.captured);body.queue_free()
 print("PREQA_NATIVE_COM "+JSON.stringify(rows))
 var file=FileAccess.open("res://tests/preqa/native_com_probe.json",FileAccess.WRITE);file.store_string(JSON.stringify(rows,"  "));file.close()
 await process_frame
 quit(0)
