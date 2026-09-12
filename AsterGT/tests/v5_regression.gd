extends SceneTree
var failures: Array[String]=[]
var report: Dictionary={}
func _initialize() -> void:call_deferred("run")
func check(ok: bool,message: String) -> void:
 if not ok:failures.append(message);push_error(message)
func run() -> void:
 GTControls.initialize()
 var guide=JSON.parse_string(FileAccess.get_file_as_string("res://config/driving_help.json"))
 var ids=[]
 for topic in guide.topics:
  ids.append(topic.id)
  for lang in ["ko","en"]:
   var regex=RegEx.new();regex.compile("\\{([^}]+)\\}")
   for token in regex.search_all(topic["body_"+lang]):check(GTControls.registry.has(token.get_string(1)),"Invalid guide action: "+token.get_string(1))
 for id in ["park","reverse","neutral","drive","gear1","gear2","gear3","gear4","gear5","gear6","abs","tcs","esc"]:check(id in ids,"Missing topic "+id)
 var body=Node3D.new();root.add_child(body)
 body.transform=Transform3D(Basis(Vector3.UP,.7),Vector3(500,20,-300))
 var model=load("res://assets/v4/porsche_lod0.glb").instantiate();body.add_child(model)
 var visual=GTLocalDamageVisual.new()
 var target=Vector3(-.75,-.18,2.05)
 var closest=Vector3.ZERO;var best=INF;var selected: MeshInstance3D
 for mesh in model.find_children("*","MeshInstance3D",true,false):
  if not visual.exterior(mesh):continue
  var tr=body.global_transform.affine_inverse()*mesh.global_transform
  for surface in range(mesh.mesh.get_surface_count()):
   for v in mesh.mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]:
    var p=tr*v;var distance=p.distance_squared_to(target)
    if distance<best:best=distance;closest=p;selected=mesh
 report.contact_point=str(closest);report.selected_mesh=String(selected.name)
 check(not visual.add_hit(closest,Vector3.BACK,Vector3.RIGHT,60,8),"Micro contact created damage")
 check(visual.add_hit(closest,Vector3.BACK,Vector3.RIGHT,48000,8),"Meaningful rear impact ignored")
 var patch=visual.patches[0]
 check(patch.crack>0 and patch.chip>0 and patch.depth>0 and patch.scratch>0,"Four damage channels not present")
 var before={}
 for mesh in model.find_children("*","MeshInstance3D",true,false):
  if visual.exterior(mesh):before[mesh.get_instance_id()]=mesh.mesh
 var start=Time.get_ticks_usec();visual.apply(model);report.apply_ms=(Time.get_ticks_usec()-start)/1000.0
 var changed=0;var outside=0;var opposite=0;var max_displacement=0.0
 for mesh in model.find_children("*","MeshInstance3D",true,false):
  if not before.has(mesh.get_instance_id()):continue
  var tr=body.global_transform.affine_inverse()*mesh.global_transform
  var original: Mesh=before[mesh.get_instance_id()]
  for surface in range(original.get_surface_count()):
   var a=original.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX];var b=mesh.mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]
   check(a.size()==b.size(),"Topology changed")
   for i in range(a.size()):
    if a[i].distance_to(b[i])<.000001:continue
    changed+=1;max_displacement=maxf(max_displacement,(tr*a[i]).distance_to(tr*b[i]))
    if (tr*a[i]).distance_to(closest)>patch.radius+.0001:outside+=1
    if (tr*a[i]).x>.2:opposite+=1
 report.changed_vertices=changed;report.outside_radius=outside;report.opposite_side=opposite;report.max_displacement_m=max_displacement
 check(changed>0,"No actual mesh deformation")
 check(outside==0 and opposite==0,"Local impact spread beyond its radius / opposite bumper")
 check(max_displacement<=.2401,"Dent depth exceeded hard cap")
 visual.repair()
 for mesh in model.find_children("*","MeshInstance3D",true,false):
  if before.has(mesh.get_instance_id()):check(mesh.mesh==before[mesh.get_instance_id()] and mesh.material_overlay==null,"Repair did not restore exact resource")
 check(visual.patches.is_empty(),"Repair left patches")
 body.queue_free();await process_frame
 var game=load("res://scenes/main.tscn").instantiate();root.add_child(game)
 await process_frame;await process_frame
 game.automation_run=true
 game.start_drive("Free Drive")
 await process_frame;await process_frame
 check(game.hud.beginner_mode and game.hud.help_button.visible,"Beginner side help missing")
 check(game.hud.onboarding_step<0 and game.hud.toast_time==0,"Unrequested onboarding/hint")
 game.hud.help_button.pressed.emit();await process_frame
 check(paused and game.hud.page=="guide" and not game.car.controls_enabled,"Help did not pause drive")
 game.hud.set_beginner(false);game.resume();await process_frame;await process_frame
 check(not game.hud.help_button.visible and game.hud.onboarding_step<0,"Normal mode still shows help")
 var e=InputEventKey.new();e.pressed=true;e.keycode=KEY_F1;e.physical_keycode=KEY_F1
 game._unhandled_input(e);await process_frame
 check(game.hud.page=="guide" and paused,"F1 mapping failed")
 var old=GTControls.bindings.shift_up.duplicate(true)
 GTControls.bindings.shift_up=[GTControls.default_slot("J"),{}]
 check(game.hud.help_text("{shift_up}")=="J","Guide does not use current rebindings")
 GTControls.bindings.shift_up=old
 # Round-trip in the test-only APPDATA directory.
 game.automation_run=false;check(game.save_preferences(),"Preference write failed")
 game.hud.beginner_mode=true;game.load_preferences();game.automation_run=true
 check(not game.hud.beginner_mode,"Normal mode not persisted")
 report.topics=ids.size();report.failures=failures;report.status="PASS" if failures.is_empty() else "FAIL"
 var out=FileAccess.open("res://tests/v5-regression.json",FileAccess.WRITE);out.store_string(JSON.stringify(report,"  "));out.close()
 print("V5_REGRESSION ",JSON.stringify(report))
 await game.world.stop_streaming()
 game.queue_free();await process_frame
 quit(0 if failures.is_empty() else 1)
