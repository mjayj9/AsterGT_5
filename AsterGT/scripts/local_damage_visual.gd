class_name GTLocalDamageVisual
extends RefCounted
# Body-local, metre-sized patches. Original resources are never modified.
const MAX_PATCHES=16
const OVERLAY=preload("res://shaders/local_damage.gdshader")
var patches: Array[Dictionary]=[]
var revision: int=0
var roots: Dictionary={}
var meshes: Dictionary={}

func add_hit(point: Vector3,outward: Vector3,tangent: Vector3,energy: float,slide_speed: float) -> bool:
 if not point.is_finite() or not outward.is_finite() or energy<120 or outward.length_squared()<.5:return false
 var dent=clampf((energy-900.0)/55000.0,0,1)
 var scratch=clampf((slide_speed-1.2)/9.0,0,1)*clampf(energy/1800.0,0,1)
 var chip=clampf((energy-450.0)/17000.0,0,1)
 var plastic=absf(point.z)>1.65 and point.y<.25
 var crack=clampf((energy-12000.0)/45000.0,0,1) if plastic else 0.0
 if maxf(maxf(dent,scratch),maxf(chip,crack))<.025:return false
 var normal=outward.normalized()
 var axis=tangent-normal*tangent.dot(normal)
 if axis.length_squared()<.01:axis=normal.cross(Vector3.UP if absf(normal.y)<.9 else Vector3.RIGHT)
 var patch={"point":point,"normal":normal,"tangent":axis.normalized(),"radius":lerpf(.18,.55,sqrt(clampf(energy/65000.0,0,1))),"depth":dent*.16,"scratch":scratch,"chip":chip,"crack":crack,"plastic":plastic}
 # Repeated contact at the same point increases this patch; never a whole zone.
 for old in patches:
  if old.point.distance_to(point)<.16 and old.normal.dot(normal)>.75:
   var changed=false
   for key in ["radius","depth","scratch","chip","crack"]:
    if patch[key]>old[key]+.001:old[key]=patch[key];changed=true
   if changed:revision+=1
   return changed
 if patches.size()>=MAX_PATCHES:
  # Keep existing scars intact and bound shader/CPU work. Repairs clear the budget.
  return false
 patches.append(patch);revision+=1;return true

static func displacement(position: Vector3,normal: Vector3,patch: Dictionary) -> Vector3:
 var delta=position-patch.point
 if delta.length_squared()>=patch.radius*patch.radius or normal.dot(patch.normal)<.05:return Vector3.ZERO
 var falloff=1.0-delta.length_squared()/(patch.radius*patch.radius)
 return -patch.normal*patch.depth*falloff*falloff

func exterior(mesh: MeshInstance3D) -> bool:
 var tag=String(mesh.name).to_lower()
 return "carpaint" in tag or "body" in tag or "bumper" in tag or "fender" in tag or "hood" in tag or "door" in tag

func apply(root: Node3D) -> void:
 if not root or patches.is_empty() or not root.is_visible_in_tree():return
 if roots.get(root.get_instance_id(),-1)==revision:return
 var body=root.get_parent() as Node3D
 for mesh in root.find_children("*","MeshInstance3D",true,false):
  if not exterior(mesh) or not mesh.mesh:continue
  var id=mesh.get_instance_id()
  if not meshes.has(id):meshes[id]={"node":weakref(mesh),"original":mesh.mesh,"overlay":mesh.material_overlay}
  var original: Mesh=meshes[id].original
  var to_body=body.global_transform.affine_inverse()*mesh.global_transform
  var from_body=to_body.affine_inverse()
  var normal_to_body=to_body.basis.inverse().transposed()
  var rebuilt=ArrayMesh.new()
  var changed=false
  for surface in range(original.get_surface_count()):
   var arrays=original.surface_get_arrays(surface).duplicate(true)
   var vertices: PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
   var normals: PackedVector3Array=arrays[Mesh.ARRAY_NORMAL]
   for i in range(vertices.size()):
    var p=to_body*vertices[i]
    var n=(normal_to_body*normals[i]).normalized() if normals.size()==vertices.size() else Vector3.UP
    var offset=Vector3.ZERO
    var gradient=Vector3.ZERO
    for patch in patches:
     var d=displacement(p,n,patch)
     offset+=d
     if not d.is_zero_approx():
      var delta=p-patch.point
      var f=1.0-delta.length_squared()/pow(patch.radius,2)
      gradient+=4.0*patch.depth*f/(patch.radius*patch.radius)*(delta-n*delta.dot(n))
    if offset.length_squared()>0:
     changed=true;vertices[i]=from_body*(p+offset.limit_length(.24))
     if normals.size()==vertices.size():normals[i]=(to_body.basis.transposed()*(n-gradient).normalized()).normalized()
   arrays[Mesh.ARRAY_VERTEX]=vertices;arrays[Mesh.ARRAY_NORMAL]=normals
   rebuilt.add_surface_from_arrays(original.surface_get_primitive_type(surface),arrays,[],{},original.surface_get_format(surface))
   rebuilt.surface_set_material(surface,original.surface_get_material(surface))
  # Legacy whole-front/rear/side morphs are deliberately absent on replacement mesh.
  mesh.mesh=rebuilt if changed else original
  # The dummy headless renderer has no shader instances; geometry tests still run.
  if DisplayServer.get_name()=="headless":continue
  var material=ShaderMaterial.new();material.shader=OVERLAY
  material.set_shader_parameter("mesh_to_body",to_body)
  material.set_shader_parameter("patch_count",patches.size())
  var positions=PackedVector4Array();var directions=PackedVector4Array();var axes=PackedVector4Array();var channels=PackedVector4Array()
  for i in range(MAX_PATCHES):
   if i<patches.size():
    var p=patches[i]
    positions.append(Vector4(p.point.x,p.point.y,p.point.z,p.radius))
    directions.append(Vector4(p.normal.x,p.normal.y,p.normal.z,1 if p.plastic else 0))
    axes.append(Vector4(p.tangent.x,p.tangent.y,p.tangent.z,p.depth))
    channels.append(Vector4(p.scratch,p.chip,p.depth,p.crack))
   else:
    positions.append(Vector4.ZERO);directions.append(Vector4.ZERO);axes.append(Vector4.ZERO);channels.append(Vector4.ZERO)
  material.set_shader_parameter("hits",positions);material.set_shader_parameter("directions",directions)
  material.set_shader_parameter("axes",axes);material.set_shader_parameter("channels",channels)
  material.set_shader_parameter("composite_body","porsche" in String(root.name).to_lower())
  mesh.material_overlay=material
 roots[root.get_instance_id()]=revision

func repair() -> void:
 for entry in meshes.values():
  var mesh=entry.node.get_ref()
  if is_instance_valid(mesh):mesh.mesh=entry.original;mesh.material_overlay=entry.overlay
 meshes.clear();roots.clear();patches.clear();revision+=1
