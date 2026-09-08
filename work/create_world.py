from pathlib import Path
import math, random, wave, struct
from PIL import Image
p=Path('outputs/AsterGT')
def write(name,s):f=p/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(s.strip()+'\n',encoding='utf-8')
random.seed(26)
for typ in ['asphalt','ground','paint_normal']:
 im=Image.new('RGB',(256,256));px=im.load()
 for y in range(256):
  for x in range(256):
   n=random.random()
   if typ=='asphalt':v=int(99+n*30);px[x,y]=(v,v+1,v+2)
   elif typ=='ground':v=int(86+n*56);px[x,y]=(v,int(v*.98),int(v*.83))
   else:px[x,y]=(128+random.randint(-2,2),128+random.randint(-2,2),255)
 im.save(p/'assets'/f'{typ}.png')
for name,rpm in [('idle',850),('low',1800),('mid',3600),('high',6500),('wind',0),('tire',0),('rain',0),('impact',0),('shift',0),('horn',0)]:
 rate=22050;n=rate*2 if rpm or name in ['wind','tire','rain','horn'] else rate//3
 freq=round(rpm/60*4*2)/2
 samples=[];smooth=0
 for i in range(n):
  t=i/rate;noise=random.uniform(-1,1);smooth=smooth*.91+noise*.09
  if rpm:
   v=sum(math.sin(2*math.pi*freq*k*t+math.sin(2*math.pi*13*t)*.025)/(k**1.3) for k in range(1,9))*.28
   v+=math.sin(2*math.pi*(freq/2)*t)*.1
  elif name=='wind':v=smooth*.7
  elif name=='rain':v=noise*.12+smooth*.4
  elif name=='tire':v=noise*.22+math.sin(2*math.pi*1100*t+noise*.4)*.10
  elif name=='horn':v=(math.sin(2*math.pi*420*t)+math.sin(2*math.pi*510*t))*.2
  elif name=='impact':v=(smooth+math.sin(2*math.pi*65*t)*.7)*math.exp(-t*22)
  else:v=noise*math.exp(-t*75)*.7+math.sin(2*math.pi*80*t)*math.exp(-t*22)*.25
  samples.append(int(max(-.95,min(.95,v))*32767))
 with wave.open(str(p/'assets'/f'{name}.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(struct.pack('<'+'h'*n,*samples))
write('scripts/controls.gd',r'''
class_name GTControls
extends RefCounted
const BINDINGS={
 "throttle":[KEY_W,KEY_UP],"brake":[KEY_S,KEY_DOWN],"left":[KEY_A,KEY_LEFT],"right":[KEY_D,KEY_RIGHT],
 "handbrake":[KEY_SPACE],"clutch":[KEY_SHIFT],"shift_down":[KEY_Q],"shift_up":[KEY_E],"transmission":[KEY_M],
 "park":[KEY_1],"reverse":[KEY_2],"neutral":[KEY_3],"drive":[KEY_4],"ignition":[KEY_ENTER],"recover":[KEY_BACKSPACE],
 "abs":[KEY_F5],"tcs":[KEY_F6],"esc":[KEY_F7],"assist":[KEY_F8],"lights":[KEY_F],"highbeam":[KEY_G],
 "left_signal":[KEY_Z],"right_signal":[KEY_X],"hazards":[KEY_H],"horn":[KEY_B],"look_back":[KEY_V],
 "camera":[KEY_C],"weather":[KEY_T],"time":[KEY_Y],"help":[KEY_F1],"setup":[KEY_F2],"telemetry":[KEY_F3],"pause":[KEY_ESCAPE]
}
const LABELS={"throttle":"Accelerator","brake":"Foot brake","left":"Steer left","right":"Steer right","handbrake":"Handbrake","clutch":"Clutch","shift_down":"Downshift","shift_up":"Upshift","transmission":"Auto / manual","park":"Select P","reverse":"Select R","neutral":"Select N","drive":"Select D","ignition":"Ignition","recover":"Recover to road","abs":"Toggle ABS","tcs":"Toggle TCS","esc":"Toggle ESC","assist":"Auto clutch / rev match","lights":"Headlights","highbeam":"High beams","left_signal":"Left indicator","right_signal":"Right indicator","hazards":"Hazards","horn":"Horn","look_back":"Rear view (hold)","camera":"Cycle camera","weather":"Change weather","time":"Change time","help":"Help","setup":"Vehicle setup","telemetry":"Performance monitor","pause":"Pause / settings"}
static func initialize() -> void:
 for action in BINDINGS:
  if not InputMap.has_action(action):InputMap.add_action(action)
  InputMap.action_erase_events(action)
  for key in BINDINGS[action]:
   var ev=InputEventKey.new();ev.physical_keycode=key;InputMap.action_add_event(action,ev)
 var data=JSON.parse_string(FileAccess.get_file_as_string("user://controls.json")) if FileAccess.file_exists("user://controls.json") else null
 if data is Dictionary:
  for action in data:
   if BINDINGS.has(action) and data[action] is float:
    var key=int(data[action]);if key>0:rebind(action,key,false)
static func key_text(action: String) -> String:
 var names: Array[String]=[]
 for ev in InputMap.action_get_events(action):
  if ev is InputEventKey:names.append(OS.get_keycode_string(ev.physical_keycode))
 return " / ".join(names)
static func rebind(action: String,key: int,save: bool=true) -> String:
 for other in BINDINGS:
  if other==action:continue
  for ev in InputMap.action_get_events(other):
   if ev is InputEventKey and ev.physical_keycode==key:return "Already assigned: "+LABELS[other]
 InputMap.action_erase_events(action);var event=InputEventKey.new();event.physical_keycode=key;InputMap.action_add_event(action,event)
 if save:
  var d={}
  for a in BINDINGS:d[a]=InputMap.action_get_events(a)[0].physical_keycode
  var f=FileAccess.open("user://controls.json",FileAccess.WRITE);if f:f.store_string(JSON.stringify(d))
 return ""
''')
write('scripts/world.gd',r'''
class_name GTWorld
extends Node3D
var curve=Curve3D.new()
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
 var nodes=[Vector3(0,0,1000),Vector3(0,0,0),Vector3(0,0,-1800),Vector3(350,18,-2800),Vector3(1400,65,-3200),Vector3(2500,135,-2600),Vector3(2800,165,-1100),Vector3(2300,80,100),Vector3(1800,42,1150),Vector3(650,12,1800),Vector3(-600,18,1650),Vector3(-1800,65,850),Vector3(-2450,155,-500),Vector3(-2350,120,-1800),Vector3(-1500,50,-2450),Vector3(-900,25,-1450),Vector3(-780,20,300),Vector3(-650,12,1550)]
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
 road_material.texture_filter=BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
 ground_material=mat(Color("8e9671"),.96);ground_material.vertex_color_use_as_albedo=true
 ground_material.albedo_texture=load("res://assets/ground.png");ground_material.texture_filter=BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
func make_sky() -> void:
 world_env=WorldEnvironment.new();environment=Environment.new();world_env.environment=environment;add_child(world_env)
 environment.background_mode=Environment.BG_SKY
 var sky=Sky.new();sky_material=ProceduralSkyMaterial.new();sky.sky_material=sky_material;environment.sky=sky
 environment.ambient_light_source=Environment.AMBIENT_SOURCE_SKY;environment.ambient_light_energy=.55
 environment.reflected_light_source=Environment.REFLECTED_SOURCE_SKY
 environment.tonemap_mode=Environment.TONE_MAPPER_FILMIC
 environment.fog_enabled=true;environment.fog_density=.00055;environment.fog_height=100;environment.fog_height_density=.005
 sun=DirectionalLight3D.new();sun.rotation_degrees=Vector3(-32,-35,0);sun.light_energy=1.8;sun.shadow_enabled=true;sun.directional_shadow_max_distance=170;sun.directional_shadow_mode=DirectionalLight3D.SHADOW_PARALLEL_4_SPLITS;add_child(sun)
 update_weather()
func update_weather() -> void:
 var night=time_of_day==2
 var sunset=time_of_day==1
 sun.rotation_degrees.x=-14 if sunset else (-27 if not night else -35)
 sun.light_color=Color("ffba7c") if sunset else (Color("97b8de") if night else Color("fff0d8"))
 sun.light_energy=(1.55 if weather==0 else .85) if not night else .10
 sky_material.sky_top_color=Color("567f9a") if not night else Color("08101e")
 sky_material.sky_horizon_color=Color("c5d4d4") if not sunset else Color("d3a584")
 if night:sky_material.sky_horizon_color=Color("182b40")
 sky_material.ground_bottom_color=Color("5f695b") if not night else Color("0d131e")
 sky_material.ground_horizon_color=sky_material.sky_horizon_color
 sky_material.sky_curve=.18
 environment.ambient_light_energy=.5 if not night else .20
 environment.fog_light_color=sky_material.sky_horizon_color
 environment.fog_density=.00045 if weather==0 else (.0018 if weather==2 else .001)
 road_material.roughness=.27 if weather==2 else .88
 road_material.metallic=.1 if weather==2 else 0
 if player:player.wetness=1 if weather==2 else 0
func load_props() -> void:
 for i in range(3):
  var s=load("res://assets/tree_%d.glb"%i).instantiate()
  var children=s.find_children("*","MeshInstance3D",true,false)
  tree_meshes.append(children[0].mesh if children.size() else SphereMesh.new());s.free()
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
  for entry in [[a,Vector2(left/3,i*8/3.0)],[b,Vector2(right/3,i*8/3.0)],[c,Vector2(left/3,(i+1)*8/3.0)],[b,Vector2(right/3,i*8/3.0)],[d,Vector2(right/3,(i+1)*8/3.0)],[c,Vector2(left/3,(i+1)*8/3.0)]]:
   st.set_normal(Vector3.UP);st.set_uv(entry[1]);st.add_vertex(entry[0])
 var mesh=st.commit();var obj=add_mesh(parent,mesh,material)
 if collision:
  var body=StaticBody3D.new();body.set_meta("surface","asphalt");parent.add_child(body)
  var cs=CollisionShape3D.new();cs.shape=mesh.create_trimesh_shape();body.add_child(cs)
 return obj
func make_road() -> void:
 var shoulder=mat(Color("a6a69a"),.93)
 var stripe=mat(Color("e9e5cf"),.7)
 var guard=mat(Color("969f9f"),.48,.65)
 for begin in range(0,road_points.size()-1,32):
  var end=mini(begin+32,road_points.size()-1);var chunk=Node3D.new();add_child(chunk)
  chunks[begin]={"node":chunk,"center":road_points[(begin+end)/2]}
  ribbon(begin,end,-7.6,7.6,-.055,shoulder,chunk,true)
  ribbon(begin,end,-5.8,5.8,0,road_material,chunk,true)
  for side in [-1,1]:
   ribbon(begin,end,side*5.4-.065,side*5.4+.065,.013,stripe,chunk)
   ribbon(begin,end,side*7.2-.065,side*7.2+.065,.78,guard,chunk)
  for i in range(begin,end,2):ribbon(i,mini(i+1,end),-.08,.08,.015,stripe,chunk)
  for i in range(begin,end,4):
   var p=road_points[i];var right=direction(i*8.0).cross(Vector3.UP)
   for side in [-1,1]:box(chunk,p+right*side*7.2+Vector3.UP*.42,Vector3(.11,.85,.11),guard)
  # Solid rail segments close to the ribbon; collision remains active along entire network.
  for i in range(begin,end,2):
   var p=road_points[i];var q=road_points[mini(i+2,end)];var tangent=q-p
   for side in [-1,1]:
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
 for key in active_tiles:active_tiles[key].queue_free()
 active_tiles.clear();refresh_timer=0
func update_streaming(dt: float) -> void:
 if not player:return
 refresh_timer-=dt
 if refresh_timer>0:return
 refresh_timer=.35
 var center=Vector2i(floori(player.position.x/TILE),floori(player.position.z/TILE))
 var wanted={}
 for x in range(-2,3):
  for z in range(-2,3):wanted[center+Vector2i(x,z)]=true
 for key in active_tiles.keys():
  if not wanted.has(key):active_tiles[key].queue_free();active_tiles.erase(key)
 var made=0
 for key in wanted:
  if not active_tiles.has(key) and made<3:active_tiles[key]=make_tile(key);made+=1
 for key in chunks:chunks[key].node.visible=chunks[key].center.distance_squared_to(player.position)<render_distance*render_distance
 nearest_index=nearest(player.position).index
func make_tile(key: Vector2i) -> Node3D:
 var root3=Node3D.new();add_child(root3)
 var n=16;var step=TILE/n;var st=SurfaceTool.new();st.begin(Mesh.PRIMITIVE_TRIANGLES)
 for x in range(n):
  for z in range(n):
   for offset in [Vector2(0,0),Vector2(0,1),Vector2(1,0),Vector2(1,0),Vector2(0,1),Vector2(1,1)]:
    var xx=key.x*TILE+(x+offset.x)*step;var zz=key.y*TILE+(z+offset.y)*step
    var yy=terrain_y(xx,zz);st.set_uv(Vector2(xx,zz)/8)
    var tone=.82+.18*sin(xx*.01)*cos(zz*.008)
    st.set_color(Color(tone,tone,.87*tone));st.add_vertex(Vector3(xx,yy,zz))
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
''')
write('scripts/car_audio.gd',r'''
class_name GTAudio
extends Node
var car: GTCar
var players={}
var last_shift: float=0
var interior: bool=false
var muted: bool=false
var bus: int=-1
func _ready() -> void:
 bus=AudioServer.bus_count;AudioServer.add_bus();AudioServer.set_bus_name(bus,"EngineCabin")
 var lowpass=AudioEffectLowPassFilter.new();lowpass.cutoff_hz=18000;AudioServer.add_bus_effect(bus,lowpass)
 for name in ["idle","low","mid","high","wind","tire","rain","impact","shift","horn"]:
  var player=AudioStreamPlayer.new();player.stream=load("res://assets/"+name+".wav")
  if name in ["idle","low","mid","high","wind","tire","rain","horn"]:
   var stream=player.stream.duplicate();stream.loop_mode=AudioStreamWAV.LOOP_FORWARD;stream.loop_end=stream.data.size()/2;player.stream=stream
  player.bus="EngineCabin";player.volume_db=-80;add_child(player);players[name]=player
  if not name in ["impact","shift"]:player.play()
func _process(dt: float) -> void:
 if not car:return
 AudioServer.set_bus_mute(bus,muted or get_tree().paused)
 var lowpass=AudioServer.get_bus_effect(bus,0);lowpass.cutoff_hz=1800 if interior else 12000
 var anchors={"idle":850.0,"low":1800.0,"mid":3600.0,"high":6500.0}
 for name in anchors:
  var player=players[name];var ratio=maxf(car.rpm,300)/anchors[name]
  player.pitch_scale=clampf(ratio,.45,2.3)
  var weight=maxf(0,1-absf(log(ratio))/0.85)
  player.volume_db=linear_to_db(maxf(.0001,weight*(.17+.3*car.throttle)*(1 if car.engine_on else 0)))
 players.wind.volume_db=linear_to_db(maxf(.0001,pow(car.speed_kph/330,2)*.8))
 players.tire.volume_db=linear_to_db(maxf(.0001,clampf((car.max_slip-.16)*1.3,0,.7)*minf(car.speed_kph/35,1)))
 players.tire.pitch_scale=clampf(1+car.max_slip*.25,.8,1.8)
 players.rain.volume_db=-15 if car.wetness>.5 else -80
 players.horn.volume_db=-10 if Input.is_action_pressed("horn") and car.controls_enabled else -80
 if car.shift_timer>0 and last_shift<=0:players.shift.volume_db=-17;players.shift.play()
 last_shift=car.shift_timer
 if car.collision_energy>.2 and not players.impact.playing:players.impact.volume_db=linear_to_db(car.collision_energy*.7);players.impact.play()
''')
print('World, controls, materials and synthesized audio created')
