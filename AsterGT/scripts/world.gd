class_name GTWorld
extends Node3D
var curve=Curve3D.new()
var experience: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://config/experience.json"))
var lookahead_m: float=0
var stream_focus=Vector3.ZERO
var road_points=PackedVector3Array()
var length: float=0
var road_grid={}
var chunks={}
var active_tiles={}
var road_material: StandardMaterial3D
var ground_material: StandardMaterial3D
var tree_meshes: Array[Mesh]=[]
var rock_mesh: Mesh
var vegetation_density: float=1.0
var render_distance: float=950
var scenery_clock: float=0
var nearest_index: int=0
var tile_thread: Thread
var streaming_stopping: bool=false
var pending_key: Vector2i
var pending_generation: int=0
var generation: int=0
var wanted_tiles={}

var player: GTCar
var environment: Environment
var sun: DirectionalLight3D
var world_env: WorldEnvironment
var weather: int=0
var time_of_day: int=0
var refresh_timer: float=0
var sky_material: ProceduralSkyMaterial
const TILE=256.0
const ROAD_WIDTH=11.6
const ZONES=["VALLE VERDE","PASSO ALTO","VIADOTTO","RIVIERA","BOSCO NORD"]
func _ready() -> void:
 make_route();make_materials();make_sky();load_props();make_road();make_landmarks();make_horizon()
 print("ROAD_LENGTH_M=",length)
func make_route() -> void:
 var nodes=[Vector3(0,0,1000),Vector3(0,0,0),Vector3(0,0,-1800),Vector3(0,0,-3500),Vector3(350,18,-4200),Vector3(1400,65,-4400),Vector3(2500,135,-3600),Vector3(2800,165,-1100),Vector3(2300,80,100),Vector3(1800,42,1150),Vector3(650,12,1800),Vector3(-600,18,1650),Vector3(-1800,65,850),Vector3(-2450,155,-500),Vector3(-2350,120,-1800),Vector3(-1500,50,-2450),Vector3(-900,25,-1450),Vector3(-780,20,300),Vector3(-650,12,1550)]
 for i in range(nodes.size()+1):
  var at=i%nodes.size();var tangent=(nodes[(at+1)%nodes.size()]-nodes[posmod(at-1,nodes.size())])/6
  curve.add_point(nodes[at],-tangent,tangent)
 curve.bake_interval=8
 length=curve.get_baked_length()
 var count=int(ceil(length/8))
 for i in range(count+1):
  var point=curve.sample_baked(minf(i*8.0,length),true);road_points.append(point)
  var key=Vector2i(floori(point.x/128),floori(point.z/128))
  if not road_grid.has(key):road_grid[key]=[]
  road_grid[key].append(i)
func sample(distance: float) -> Vector3:return curve.sample_baked(fposmod(distance,length),true)
func direction(distance: float) -> Vector3:return (sample(distance+2)-sample(distance-2)).normalized()
func road_transform(distance: float,lane: float=2.8) -> Transform3D:
 var dir=direction(distance);var right=dir.cross(Vector3.UP).normalized()
 return Transform3D(Basis.looking_at(dir,Vector3.UP),sample(distance)+right*lane+Vector3.UP*.80)
func nearest(pos: Vector3,wide: bool=false) -> Dictionary:
 var key=Vector2i(floori(pos.x/128),floori(pos.z/128));var best=INF;var idx=0
 for x in range(-1,2):
  for z in range(-1,2):
   for i in road_grid.get(key+Vector2i(x,z),[]):
    var d=Vector2(pos.x-road_points[i].x,pos.z-road_points[i].z).length_squared()
    if d<best:best=d;idx=i
 if best==INF or wide:
  for i in range(0,road_points.size(),4):
   var d=Vector2(pos.x-road_points[i].x,pos.z-road_points[i].z).length_squared()
   if d<best:best=d;idx=i
 var a=road_points[idx];var b=road_points[min(idx+1,road_points.size()-1)]
 var ax=Vector2(a.x,a.z);var bx=Vector2(b.x,b.z);var q=Vector2(pos.x,pos.z)
 var t=clampf((q-ax).dot(bx-ax)/maxf((bx-ax).length_squared(),0.001),0,1)
 var point=a.lerp(b,t)
 return {"point":point,"index":idx,"distance":q.distance_to(Vector2(point.x,point.z)),"along":fposmod(idx*8.0+t*8,length)}
func terrain_y(x: float,z: float) -> float:
 var near=nearest(Vector3(x,0,z));var d=near.distance;var h=near.point.y
 var away=smoothstep(15,110,d)
 var undulate=sin(x*.005)*cos(z*.006)*22+sin(x*.012+z*.006)*8
 var elev=h-.3+away*(undulate+maxf(0,d-100)*.12)
 if near.along>7500 and near.along<7900:elev-=smoothstep(7500,7560,near.along)*(1-smoothstep(7840,7900,near.along))*22
 return elev
func mat(color: Color,rough: float=.7,metal: float=0) -> StandardMaterial3D:
 var m=StandardMaterial3D.new();m.albedo_color=color;m.roughness=rough;m.metallic=metal;return m
func make_materials() -> void:
 road_material=mat(Color("444a4e"),.88)
 road_material.albedo_texture=load("res://assets/asphalt.png");road_material.uv1_scale=Vector3(1,1,1)
 road_material.normal_enabled=true;road_material.normal_texture=load("res://assets/asphalt_normal.png");road_material.normal_scale=.45
 road_material.texture_filter=BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
 ground_material=mat(Color("acb3a1"),.96);ground_material.vertex_color_use_as_albedo=true
 ground_material.normal_enabled=true;ground_material.normal_texture=load("res://assets/ground_normal.png");ground_material.normal_scale=.7
 ground_material.albedo_texture=load("res://assets/ground.png");ground_material.texture_filter=BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
func make_sky() -> void:
 world_env=WorldEnvironment.new();environment=Environment.new();world_env.environment=environment;add_child(world_env)
 environment.background_mode=Environment.BG_SKY
 var sky=Sky.new();sky_material=ProceduralSkyMaterial.new();sky.sky_material=sky_material;environment.sky=sky
 environment.ambient_light_source=Environment.AMBIENT_SOURCE_SKY;environment.ambient_light_energy=.55
 environment.reflected_light_source=Environment.REFLECTION_SOURCE_SKY
 environment.tonemap_mode=Environment.TONE_MAPPER_FILMIC
 environment.fog_enabled=true;environment.fog_sky_affect=.12;environment.fog_density=.00055;environment.fog_height=0;environment.fog_height_density=0
 sun=DirectionalLight3D.new();sun.rotation_degrees=Vector3(-32,-35,0);sun.light_energy=1.8;sun.shadow_enabled=true;sun.directional_shadow_max_distance=170;sun.directional_shadow_mode=DirectionalLight3D.SHADOW_PARALLEL_4_SPLITS;add_child(sun)
 update_weather()
func update_weather() -> void:
 var night=time_of_day==2
 var sunset=time_of_day==1
 sun.rotation_degrees.x=-14 if sunset else (-27 if not night else -35)
 sun.light_color=Color("ffba7c") if sunset else (Color("97b8de") if night else Color("fff0d8"))
 sun.light_energy=(1.55 if weather==0 else .85) if not night else .10
 sky_material.sky_top_color=Color("416d8d") if not night else Color("08101e")
 sky_material.sky_horizon_color=Color("c5d4d4") if not sunset else Color("d3a584")
 if night:sky_material.sky_horizon_color=Color("182b40")
 sky_material.ground_bottom_color=Color("5f695b") if not night else Color("0d131e")
 sky_material.ground_horizon_color=sky_material.sky_horizon_color
 sky_material.sky_curve=.40
 environment.ambient_light_energy=.5 if not night else .28
 environment.tonemap_exposure=1.05 if night else .92
 environment.fog_light_color=sky_material.sky_horizon_color
 environment.fog_density=.00045 if weather==0 else (.0018 if weather==2 else .001)
 road_material.roughness=.27 if weather==2 else .88
 road_material.metallic=0
 road_material.normal_scale=.20 if weather==2 else .45
 if player:player.wetness=1 if weather==2 else 0
func load_props() -> void:
 for i in range(3):
  var s=load("res://assets/tree_%d.glb"%i).instantiate()
  var children=s.find_children("*","MeshInstance3D",true,false)
  var mesh=children[0].mesh if children.size() else SphereMesh.new()
  for surface in range(mesh.get_surface_count()):
   var original=mesh.surface_get_material(surface)
   if original is StandardMaterial3D and "Leaves" in original.resource_name:
    var leaf=original.duplicate();leaf.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR;leaf.alpha_scissor_threshold=.45;leaf.cull_mode=BaseMaterial3D.CULL_DISABLED;leaf.roughness=.85;mesh.surface_set_material(surface,leaf)
  tree_meshes.append(mesh);s.free()
 var rocks=load("res://assets/rocks.glb").instantiate();rock_mesh=rocks.find_children("*","MeshInstance3D",true,false)[0].mesh;rocks.free()
func add_mesh(parent: Node3D,mesh: Mesh,material: Material=null,pos: Vector3=Vector3.ZERO) -> MeshInstance3D:
 var obj=MeshInstance3D.new();obj.mesh=mesh;obj.position=pos
 if material:obj.material_override=material
 parent.add_child(obj);return obj
func box(parent: Node3D,pos: Vector3,size3: Vector3,material: Material,collision: bool=false) -> MeshInstance3D:
 var mesh=BoxMesh.new();mesh.size=size3;var obj=add_mesh(parent,mesh,material,pos)
 if collision:
  var body=StaticBody3D.new();body.position=pos;parent.add_child(body);var c=CollisionShape3D.new();var sh=BoxShape3D.new();sh.size=size3;c.shape=sh;body.add_child(c)
 return obj
func ribbon(begin: int,end: int,left: float,right: float,height: float,material: Material,parent: Node3D,collision: bool=false) -> MeshInstance3D:
 var st=SurfaceTool.new();st.begin(Mesh.PRIMITIVE_TRIANGLES)
 for i in range(begin,mini(end,road_points.size()-1)):
  var p=road_points[i];var q=road_points[i+1];var r=(q-p).normalized().cross(Vector3.UP).normalized()
  var a=p+r*left+Vector3.UP*height;var b=p+r*right+Vector3.UP*height;var c=q+r*left+Vector3.UP*height;var d=q+r*right+Vector3.UP*height
  for entry in [[a,Vector2(left/3,i*8/3.0)],[c,Vector2(left/3,(i+1)*8/3.0)],[b,Vector2(right/3,i*8/3.0)],[b,Vector2(right/3,i*8/3.0)],[c,Vector2(left/3,(i+1)*8/3.0)],[d,Vector2(right/3,(i+1)*8/3.0)]]:
   st.set_normal(Vector3.UP);st.set_uv(entry[1]);st.add_vertex(entry[0])
 var mesh=st.commit();var obj=add_mesh(parent,mesh,material)
 if collision:
  var body=StaticBody3D.new();body.set_meta("surface","wet_asphalt" if begin*8>13000 and begin*8<13400 else "asphalt");parent.add_child(body)
  var cs=CollisionShape3D.new();cs.shape=mesh.create_trimesh_shape();body.add_child(cs)
 return obj
func make_road() -> void:
 var wet=road_material.duplicate();wet.roughness=.25;wet.metallic=0
 var shoulder=mat(Color("a6a69a"),.93)
 var stripe=mat(Color("e9e5cf"),.7)
 var guard=mat(Color("969f9f"),.48,.65)
 for begin in range(0,road_points.size()-1,32):
  var end=mini(begin+32,road_points.size()-1);var chunk=Node3D.new();add_child(chunk)
  chunks[begin]={"node":chunk,"center":road_points[(begin+end)/2]}
  ribbon(begin,end,-7.6,-5.8,-.025,shoulder,chunk,true)
  ribbon(begin,end,5.8,7.6,-.025,shoulder,chunk,true)
  ribbon(begin,end,-5.8,5.8,0,wet if begin*8>13000 and begin*8<13400 else road_material,chunk,true)
  for side in [-1,1]:
   ribbon(begin,end,side*5.4-.065,side*5.4+.065,.013,stripe,chunk)
   if side==1 and begin<166 and end>156:
    if begin<156:ribbon(begin,156,7.2-.065,7.2+.065,.78,guard,chunk)
    if end>166:ribbon(166,end,7.2-.065,7.2+.065,.78,guard,chunk)
   else:ribbon(begin,end,side*7.2-.065,side*7.2+.065,.78,guard,chunk)
  for i in range(begin,end,2):ribbon(i,mini(i+1,end),-.08,.08,.015,stripe,chunk)
  for i in range(begin,end,4):
   var p=road_points[i];var right=direction(i*8.0).cross(Vector3.UP)
   for side in [-1,1]:
    if side==1 and i>=156 and i<=166:continue
    box(chunk,p+right*side*7.2+Vector3.UP*.42,Vector3(.11,.85,.11),guard)
  add_reference_markers(chunk,begin,end)
  # Solid rail segments close to the ribbon; collision remains active along entire network.
  for i in range(begin,end,2):
   var p=road_points[i];var q=road_points[mini(i+2,end)];var tangent=q-p
   for side in [-1,1]:
    if side==1 and i>=156 and i<=166:continue
    var right=tangent.normalized().cross(Vector3.UP);var body=StaticBody3D.new();chunk.add_child(body)
    body.position=(p+q)*.5+right*side*7.35+Vector3.UP*.48;body.basis=Basis.looking_at(tangent.normalized(),Vector3.UP)
    var cs=CollisionShape3D.new();var shape=BoxShape3D.new();shape.size=Vector3(.2,.8,tangent.length()+.1);cs.shape=shape;body.add_child(cs)
 for d in range(300,int(length),700):make_sign(float(d))
func make_sign(distance: float) -> void:
 var tr=road_transform(distance,9);var root3=Node3D.new();root3.transform=tr;root3.position.y-=.8;add_child(root3)
 var dark=mat(Color("203b37"));var grey=mat(Color("919a98"),.4,.6)
 box(root3,Vector3(0,1.8,0),Vector3(.11,3.6,.11),grey)
 box(root3,Vector3(0,3.3,0),Vector3(3.3,1.3,.09),dark)
 var label=Label3D.new();label.text=ZONES[int(distance/length*5)%5]+"\n"+str(int(distance/1000))+" km   /   ASTER ROUTE";label.font_size=44;label.pixel_size=.008;label.position=Vector3(0,3.3,.07);label.modulate=Color("e7eee4");root3.add_child(label)
func make_landmarks() -> void:
 var concrete=mat(Color("b7b3a2"),.9);var charcoal=mat(Color("313d3e"),.7);var windows=mat(Color("29474e"),.18,.55);var copper=mat(Color("c48251"),.4,.5)
 # Road house on the flat start straight, outside guardrail.
 var village=Node3D.new();village.position=Vector3(37,0,-280);add_child(village)
 box(village,Vector3(0,-.10,0),Vector3(42,.2,60),road_material,true)
 box(village,Vector3(-24,-.10,0),Vector3(18,.2,18),road_material,true)
 box(village,Vector3(0,2.6,-9),Vector3(22,5.2,10),concrete,true)
 box(village,Vector3(0,2.3,-3.94),Vector3(20,3.4,.1),windows)
 box(village,Vector3(0,5.4,-8),Vector3(24,.42,15),charcoal)
 for x in [-10,-6,-2,2,6,10]:box(village,Vector3(x,2.2,-3.8),Vector3(.12,4.4,.16),charcoal)
 var sign=Label3D.new();sign.text="ASTER  /  ROAD HOUSE";sign.font_size=72;sign.pixel_size=.013;sign.position=Vector3(0,4.7,-3.75);sign.modulate=Color("f4d8b0");village.add_child(sign)
 for x in [-8,8]:
  box(village,Vector3(x,2,12),Vector3(.30,4,.30),copper,true)
 box(village,Vector3(0,4.15,12),Vector3(21,.3,9),charcoal)
 for x in [-6,0,6]:box(village,Vector3(x,.9,12),Vector3(.9,1.8,.65),concrete,true)
 for k in range(8):box(village,Vector3(-16+k*4,.017,22),Vector3(.10,.02,5.5),mat(Color("e3dfca")))
 # Additional compact villages make later zones identifiable.
 for d in [4400,11900,15400]:
  var tr=road_transform(d,28)
  for k in range(5):
   var h=4+(k%3)*2;var q=tr.origin+tr.basis.x*k*16;q.y=terrain_y(q.x,q.z)
   box(self,q+Vector3.UP*h*.5,Vector3(9,h,10),concrete,true)
   box(self,q+Vector3.UP*(h+.1),Vector3(10,.35,11),charcoal)
 # Viaduct with piers and deck, road remains physical.
 for d in range(7500,7900,40):
  var p=sample(d);box(self,p-Vector3.UP*12,Vector3(2.6,23,3.2),concrete,true)
  var deck=box(self,p-Vector3.UP*.40,Vector3(15,.5,41),concrete)
  deck.basis=Basis.looking_at(direction(d),Vector3.UP)
 # Short covered gallery: exposed steel ribs and a solid roof.
 for d in range(5300,5520,10):
  var tr=road_transform(d,0);var parent3=Node3D.new();parent3.transform=tr;parent3.position.y-=.8;add_child(parent3)
  for side in [-1,1]:box(parent3,Vector3(side*6.8,3.3,0),Vector3(.45,6.6,.55),concrete,true)
  box(parent3,Vector3(0,6.5,0),Vector3(14,.55,10.1),concrete,true)
  var lamp=box(parent3,Vector3(0,6.12,0),Vector3(.18,.03,2),mat(Color("e4c989")))
func make_horizon() -> void:
 var st=SurfaceTool.new();st.begin(Mesh.PRIMITIVE_TRIANGLES)
 for i in range(96):
  var a=i*TAU/96;var b=(i+1)*TAU/96
  var va=Vector3(cos(a)*7700,600+sin(a*7)*230+cos(a*13)*180,sin(a)*7700)
  var vb=Vector3(cos(b)*7700,600+sin(b*7)*230+cos(b*13)*180,sin(b)*7700)
  for v in [va,vb,Vector3(vb.x,-60,vb.z),va,Vector3(vb.x,-60,vb.z),Vector3(va.x,-60,va.z)]:st.add_vertex(v)
 st.generate_normals();add_mesh(self,st.commit(),mat(Color("718080"),1))
func set_density(value: float) -> void:
 vegetation_density=value
 generation+=1
 for key in active_tiles:active_tiles[key].queue_free()
 active_tiles.clear();refresh_timer=0
func update_streaming(dt: float) -> void:
 if streaming_stopping or not player:return
 if tile_thread and not tile_thread.is_alive():
  var built=tile_thread.wait_to_finish();tile_thread=null
  if is_instance_valid(built):
   if pending_generation==generation and wanted_tiles.has(pending_key) and not active_tiles.has(pending_key):
    add_child(built);active_tiles[pending_key]=built
   else:built.free()
 refresh_timer-=dt
 if refresh_timer<=0:
  refresh_timer=.35
  lookahead_m=player.linear_velocity.length()*experience.stream_lookahead_s+experience.stream_margin_m
  stream_focus=player.position+player.linear_velocity.normalized()*lookahead_m*.5
  var center=Vector2i(floori(player.position.x/TILE),floori(player.position.z/TILE))
  wanted_tiles.clear()
  for x in range(-2,3):
   for z in range(-2,3):wanted_tiles[center+Vector2i(x,z)]=true
  for step in range(1,int(ceil(lookahead_m/TILE))+1):
   var ahead=player.position+player.linear_velocity.normalized()*TILE*step
   var ahead_key=Vector2i(floori(ahead.x/TILE),floori(ahead.z/TILE))
   for x in range(-1,2):
    for z in range(-1,2):wanted_tiles[ahead_key+Vector2i(x,z)]=true
  for key in active_tiles.keys():
   if not wanted_tiles.has(key):active_tiles[key].queue_free();active_tiles.erase(key)
  for key in chunks:chunks[key].node.visible=chunks[key].center.distance_squared_to(player.position)<pow(maxf(render_distance,lookahead_m+TILE),2)
  nearest_index=nearest(player.position).index
 if tile_thread==null:
  var candidates=[]
  for key in wanted_tiles:
   if not active_tiles.has(key):candidates.append(key)
  candidates.sort_custom(func(a,b):return Vector2(a.x*TILE+TILE*.5,a.y*TILE+TILE*.5).distance_squared_to(Vector2(stream_focus.x,stream_focus.z))<Vector2(b.x*TILE+TILE*.5,b.y*TILE+TILE*.5).distance_squared_to(Vector2(stream_focus.x,stream_focus.z)))
  if not candidates.is_empty():
   pending_key=candidates[0];pending_generation=generation;tile_thread=Thread.new();tile_thread.start(make_tile.bind(pending_key))
func stop_streaming() -> void:
 streaming_stopping=true
 # Let RenderingServer requests from the worker complete before joining it.
 while tile_thread and tile_thread.is_alive():await get_tree().process_frame
 if tile_thread:
  var built=tile_thread.wait_to_finish();tile_thread=null
  if is_instance_valid(built):built.free()
func _exit_tree() -> void:
 if tile_thread:
  var built=tile_thread.wait_to_finish()
  if is_instance_valid(built):built.free()
  tile_thread=null
func make_tile(key: Vector2i) -> Node3D:
 var root3=Node3D.new()
 var n=16;var step=TILE/n;var st=SurfaceTool.new();st.begin(Mesh.PRIMITIVE_TRIANGLES)
 var grid=[]
 for x in range(n+1):
  for z in range(n+1):
   var xx=key.x*TILE+x*step;var zz=key.y*TILE+z*step
   grid.append(Vector3(xx,terrain_y(xx,zz),zz))
 for x in range(n):
  for z in range(n):
   for offset in [Vector2i(0,0),Vector2i(1,0),Vector2i(0,1),Vector2i(1,0),Vector2i(1,1),Vector2i(0,1)]:
    var v=grid[(x+offset.x)*(n+1)+z+offset.y]
    st.set_uv(Vector2(v.x,v.z)/8)
    var tone=.82+.18*sin(v.x*.01)*cos(v.z*.008)
    st.set_color(Color(tone,tone,.87*tone));st.add_vertex(v)
 st.generate_normals();var mesh=st.commit();add_mesh(root3,mesh,ground_material)
 var body=StaticBody3D.new();body.set_meta("surface","grass");root3.add_child(body)
 var cs=CollisionShape3D.new();cs.shape=mesh.create_trimesh_shape();body.add_child(cs)
 var rng=RandomNumberGenerator.new();rng.seed=hash(key)
 var transforms: Array[Array]=[[],[],[]];var rocks=[]
 for i in range(int(90*vegetation_density)):
  var x=key.x*TILE+rng.randf_range(0,TILE);var z=key.y*TILE+rng.randf_range(0,TILE)
  var near=nearest(Vector3(x,0,z))
  if near.distance<15 or absf(x-37)<30 and absf(z+280)<40:continue
  var pos=Vector3(x,terrain_y(x,z),z);var scale3=Vector3.ONE*rng.randf_range(.6,1.5)
  var b=Basis(Vector3.UP,rng.randf()*TAU).scaled(scale3)
  transforms[i%3].append(Transform3D(b,pos))
  if i%9==0:rocks.append(Transform3D(b,pos+Vector3(5,0,0)))
 for i in range(3):make_instances(root3,tree_meshes[i],transforms[i],550)
 make_instances(root3,rock_mesh,rocks,420)
 return root3
func make_instances(parent: Node3D,mesh: Mesh,transforms: Array,distance: float) -> void:
 if transforms.is_empty():return
 var multi=MultiMesh.new();multi.transform_format=MultiMesh.TRANSFORM_3D;multi.mesh=mesh;multi.instance_count=transforms.size()
 for i in range(transforms.size()):multi.set_instance_transform(i,transforms[i])
 var m=MultiMeshInstance3D.new();m.multimesh=multi;m.visibility_range_end=distance;m.visibility_range_end_margin=70;parent.add_child(m)


func add_reference_markers(chunk: Node3D,begin: int,end: int) -> void:
 var reflector=mat(Color("e8dec0"),.35,0);reflector.emission_enabled=true;reflector.emission=Color(.1,.085,.05);reflector.emission_energy_multiplier=.5
 var post=BoxMesh.new();post.size=Vector3(.10,.82,.12);post.material=mat(Color("8d9493"),.5,.5)
 var lens=BoxMesh.new();lens.size=Vector3(.12,.09,.035);lens.material=reflector
 var pole=BoxMesh.new();pole.size=Vector3(.2,8,.2);pole.material=mat(Color("786f62"),.9)
 var posts=[];var lenses=[];var poles=[]
 for i in range(begin,end):
  var tr=road_transform(i*8,0);var right=tr.basis.x
  for side in [-1,1]:
   var base=road_points[i]+right*side*7.1
   posts.append(Transform3D(tr.basis,base+Vector3.UP*.42))
   if i%2==0:lenses.append(Transform3D(tr.basis,base+Vector3.UP*.82))
  if i%10==0:poles.append(Transform3D(tr.basis,road_points[i]+right*12+Vector3.UP*4))
 make_instances(chunk,post,posts,1400);make_instances(chunk,lens,lenses,1400);make_instances(chunk,pole,poles,2000)
