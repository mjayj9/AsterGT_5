import bpy, math, random, json
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'outputs'/'AsterGT'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
random.seed(47)
def coord(v):return (v[0],-v[2],v[1])
def mat(name,color,metal=0,rough=.5,emission=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough
 if emission:b.inputs['Emission Color'].default_value=(*color,1);b.inputs['Emission Strength'].default_value=emission
 return m
paint=mat('Paint | Aster Viridian',(.025,.235,.205),.72,.23)
carbon=mat('Carbon | satin graphite',(.018,.024,.027),.25,.4)
rubber=mat('Rubber | vulcanized',(.012,.014,.016),0,.87)
silver=mat('Alloy | machined titanium',(.48,.52,.54),.85,.22)
brake=mat('Brake | ceramic',(.16,.17,.17),.8,.55)
caliper=mat('Caliper | warm copper',(.7,.23,.045),.45,.3)
glass=mat('Glass | neutral smoked',(.07,.13,.16),.38,.12)
black=mat('Interior | ink leather',(.018,.024,.027),0,.82)
leather=mat('Interior | saddle',(.34,.14,.058),0,.64)
white=mat('Lamp | ice white',(.77,.93,1),.1,.18,3)
red=mat('Lamp | ruby red',(.7,.013,.019),.15,.2,2)
amber=mat('Lamp | amber',(.95,.28,.025),.05,.25,1)
def finish(obj,name,material,smooth=True,bevel=0):
 obj.name=name
 if material:obj.data.materials.append(material)
 if smooth and hasattr(obj.data,'polygons'):
  for p in obj.data.polygons:p.use_smooth=True
 if bevel:
  mod=obj.modifiers.new('Edge highlights','BEVEL');mod.width=bevel;mod.segments=3
  obj.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return obj
def cube(name,loc,scale,material,bevel=.02):
 bpy.ops.mesh.primitive_cube_add(size=1,location=coord(loc));o=bpy.context.object;o.scale=(scale[0],scale[2],scale[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 return finish(o,name,material,False,bevel)
def uv(name,loc,scale,material):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=coord(loc));o=bpy.context.object;o.scale=(scale[0],scale[2],scale[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,name,material)
def cyl(name,loc,radius,depth,material,axis='x',vertices=48):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=coord(loc));o=bpy.context.object
 if axis=='x':o.rotation_euler[1]=math.pi/2
 if axis=='z':o.rotation_euler[0]=math.pi/2
 return finish(o,name,material,True,.004)
def mesh(name,verts,faces,material):
 m=bpy.data.meshes.new(name);m.from_pydata([coord(v) for v in verts],[],faces);m.update();o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);finish(o,name,material,False);return o
def line(name,points,radius,material):
 curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.resolution_u=12;curve.bevel_depth=radius;curve.bevel_resolution=3
 sp=curve.splines.new('POLY');sp.points.add(len(points)-1)
 for p,v in zip(sp.points,points):p.co=(*coord(v),1)
 ob=bpy.data.objects.new(name,curve);bpy.context.collection.objects.link(ob);ob.data.materials.append(material);return ob
# Sculpted closed body shell with swept shoulders and true wheel apertures.
sections=[(-2.37,.67,-.03),(-2.30,.84,.08),(-2.14,.91,.19),(-1.75,.965,.28),(-1.39,.98,.33),(-.96,.95,.31),(-.45,.91,.29),(.3,.93,.30),(.9,.99,.34),(1.39,1.02,.38),(1.85,1.0,.32),(2.18,.95,.24),(2.32,.83,.18),(2.37,.72,.13)]
verts=[]
for z,w,t in sections:
 for x,y in [(0,t),(.68*w,t-.008),(.91*w,t-.03),(w,t-.10),(w*.99,-.13),(.90*w,-.28),(0,-.29),(-.90*w,-.28),(-.99*w,-.13),(-w,t-.10),(-.91*w,t-.03),(-.68*w,t-.008)]:verts.append((x,y,z))
faces=[];n=12
for j in range(len(sections)-1):
 for k in range(n):faces.append((j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k))
faces.extend([tuple(range(n-1,-1,-1)),tuple((len(sections)-1)*n+k for k in range(n))])
body=mesh('Body_Sculpted_GT',verts,faces,paint)
# Recalculate normals and subdivide, then boolean cut wheel wells.
bpy.context.view_layer.objects.active=body;body.select_set(True)
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT')
sub=body.modifiers.new('Coachwork surface','SUBSURF');sub.levels=2;bpy.ops.object.modifier_apply(modifier=sub.name)
for z in [-1.39,1.39]:
 cut=cyl('Arch cutter',(0,-.315,z),.417,2.8,None,vertices=64)
 bpy.context.view_layer.objects.active=body
 mod=body.modifiers.new('Sculpted wheel arch','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut
 bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
for poly in body.data.polygons:poly.use_smooth=True
# Cabin glass as well-defined separate surfaces.
mesh('Windshield',[(-.73,.33,-.96),(.73,.33,-.96),(.59,.93,-.28),(-.59,.93,-.28)],[(0,1,2,3)],glass)
mesh('RearGlass',[(-.6,.94,.57),(.6,.94,.57),(.80,.38,1.40),(-.80,.38,1.40)],[(0,3,2,1)],glass)
roof=mesh('Roof',[(-.60,.94,-.29),(.60,.94,-.29),(.62,.97,.32),(.60,.94,.59),(-.60,.94,.59),(-.62,.97,.32)],[(0,1,2,3,4,5)],paint)
sol=roof.modifiers.new('Roof thickness','SOLIDIFY');sol.thickness=.035
for side in [-1,1]:
 s=side
 mesh('SideWindow_'+str(s),[(s*.735,.34,-.90),(s*.606,.92,-.27),(s*.615,.94,.57),(s*.818,.38,1.33)],[(0,1,2,3)],glass)
 line('A_pillar_'+str(s),[(s*.735,.32,-.97),(s*.60,.94,-.29)],.027,paint)
 line('C_pillar_'+str(s),[(s*.60,.94,.58),(s*.81,.36,1.38)],.045,paint)
 line('WindowTrim_'+str(s),[(s*.74,.33,-.90),(s*.60,.93,-.28),(s*.61,.94,.58),(s*.82,.36,1.35),(s*.74,.33,-.90)],.013,carbon)
 line('B_pillar_'+str(s),[(s*.73,.35,.54),(s*.615,.935,.48)],.018,carbon)
 line('Door_seam_'+str(s),[(s*.948,.18,-.80),(s*.948,-.14,-.60),(s*.974,-.15,.70),(s*.971,.22,.88)],.006,carbon)
 cube('Flush_handle_'+str(s),(s*.977,.19,.63),(.016,.025,.15),carbon,.01)
 cube('Sill_'+str(s),(s*.946,-.25,0),(.1,.08,1.75),carbon,.02)
 uv('Mirror_'+str(s),(s*1.04,.44,-.68),(.15,.072,.14),paint)
 cube('MirrorGlass_'+str(s),(s*1.04,.44,-.57),(.23,.095,.013),silver,.016)
 line('Mirror_stalk_'+str(s),[(s*.74,.36,-.75),(s*.99,.43,-.67)],.027,carbon)
 # Front split LED signature and recessed grille.
 cube('HeadlampPocket_'+str(s),(s*.64,.095,-2.25),(.48,.14,.11),carbon,.055)
 line('Headlight_'+str(s),[(s*.44,.14,-2.307),(s*.68,.14,-2.30),(s*.86,.11,-2.24)],.018,white)
 line('FrontSignal_'+str(s),[(s*.60,.062,-2.31),(s*.83,.060,-2.26)],.01,amber)
 cube('Intake_'+str(s),(s*.61,-.12,-2.29),(.29,.13,.1),carbon,.04)
 for z in [-1.64,-1.52,-1.40]:cube('Fender_vent_'+str(s),(s*.68,.285,z),(.20,.017,.045),carbon,.015)
 cube('TailPocket_'+str(s),(s*.56,.12,2.28),(.61,.11,.10),carbon,.03)
 line('Taillight_'+str(s),[(s*.28,.16,2.335),(s*.62,.16,2.33),(s*.88,.10,2.25)],.017,red)
 line('RearSignal_'+str(s),[(s*.63,.075,2.337),(s*.84,.06,2.30)],.012,amber)
 cyl('Exhaust_'+str(s),(s*.67,-.20,2.39),.062,.17,silver,'z',32)
cube('Splitter',(0,-.285,-2.15),(1.84,.035,.48),carbon,.03)
cube('FrontGrille',(0,-.11,-2.365),(.60,.15,.06),carbon,.025)
for x in [i*.065 for i in range(-4,5)]:cube('GrilleBlade',(x,-.11,-2.408),(.009,.12,.012),silver,.001)
cube('RearDiffuser',(0,-.26,2.17),(1.75,.11,.50),carbon,.025)
for x in [-.6,-.3,0,.3,.6]:cube('DiffuserFin',(x,-.29,2.26),(.018,.13,.38),carbon,.008)
cube('Ducktail',(0,.295,2.12),(1.85,.07,.17),paint,.035)
# Original emblem: intersecting polished bars, no brand identifiers.
line('Aster_emblem',[(-.037,.206,-2.22),(0,.24,-2.20),(.037,.206,-2.22)],.008,silver)
# Interior remains present for cockpit camera.
cube('CabinFloor',(0,-.12,.28),(1.45,.09,2.20),black,.035)
cube('Dashboard',(0,.34,-.67),(1.40,.20,.36),black,.07)
cube('InstrumentPanel',(-.38,.45,-.52),(.45,.15,.035),carbon,.02)
cube('InstrumentDisplay',(-.38,.45,-.498),(.37,.10,.008),mat('Display | cyan',(.025,.45,.52),.2,.3,1),.008)
cube('CenterConsole',(0,.10,.26),(.24,.25,1.10),carbon,.03)
for side in [-1,1]:
 cube('SeatCushion_'+str(side),(side*.41,.04,.35),(.49,.16,.57),leather,.065)
 seat=cube('SeatBack_'+str(side),(side*.41,.30,.68),(.49,.55,.16),leather,.065);seat.rotation_euler[0]=-.14
 cube('Headrest_'+str(side),(side*.41,.65,.72),(.25,.19,.12),leather,.04)
# Steering ring in x/y plane, its rotation can be animated by game.
points=[(-.38+math.sin(t)*.18,.49+math.cos(t)*.18,-.33) for t in [i*math.tau/48 for i in range(49)]]
line('SteeringWheel',points,.018,black)
for a in [0,2.1,4.2]:line('SteeringSpoke',[(-.38,.49,-.33),(-.38+math.sin(a)*.16,.49+math.cos(a)*.16,-.33)],.017,silver)
# Select all car objects for export (no procedural wheel pivots baked into body).
bpy.ops.object.select_all(action='SELECT')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender'/'aster_gt.blend'))
bpy.ops.export_scene.gltf(filepath=str(ROOT/'assets'/'aster_gt.glb'),export_format='GLB',use_selection=True,export_apply=True)
# Wheel separately, local origin and local X axle, outward face toward +X in Godot.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
cyl('Tire',(0,0,0),.355,.265,rubber,'x',64)
# Sidewall rings / polished rim / barrel.
for x in [-.128,.128]:
 cyl('Sidewall',(x,0,0),.334,.012,rubber,'x',64)
 cyl('RimLip',(x,0,0),.264,.018,silver,'x',64)
 cyl('WheelWell',(x*1.1,0,0),.236,.016,carbon,'x',48)
cyl('BrakeDisc',(.115,0,0),.212,.026,brake,'x',64)
cube('BrakeCaliper',(.139,.00,.18),(.05,.14,.085),caliper,.012)
for n in range(10):
 a=n*math.tau/10
 line('ForgedSpoke_'+str(n),[(.158,math.cos(a)*.075,math.sin(a)*.075),(.153,math.cos(a+.13)*.243,math.sin(a+.13)*.243)],.022,silver)
cyl('Hub',(.174,0,0),.071,.032,silver,'x',32)
for n in range(5):
 a=n*math.tau/5;cyl('Lug',(.195,math.cos(a)*.044,math.sin(a)*.044),.010,.008,carbon,'x',12)
for n in range(40):
 a=n*math.tau/40
 # Tread grooves dark stripes across tire crown.
 line('Tread_'+str(n),[(-.105,math.cos(a)*.356,math.sin(a)*.356),(.105,math.cos(a+.06)*.356,math.sin(a+.06)*.356)],.0035,carbon)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender'/'wheel.blend'))
bpy.ops.export_scene.gltf(filepath=str(ROOT/'assets'/'wheel.glb'),export_format='GLB',use_selection=True,export_apply=True)
# Environment library: branch-grown broadleaf trees, cypress, roadside rocks, cafe.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bark=mat('Bark',(.19,.14,.09),0,.95)
leaf=[mat('Leaf_'+str(i),c,0,.94) for i,c in enumerate([(.12,.23,.085),(.20,.30,.11),(.28,.36,.15),(.11,.20,.13)])]
stone=mat('Limestone',(.46,.45,.37),0,.92)
for typ in range(3):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 if typ<2:
  height=7 if typ==0 else 10
  line('Trunk',[(0,0,0),(.06,height*.4,.03),(-.12,height*.7,.10)],.16 if typ==0 else .22,bark)
  for k in range(11):
   a=k*2.4;h=height*(.45+.045*k);reach=2.0 if typ==0 else 2.9
   x=math.sin(a)*reach*(.7+random.random()*.35);z=math.cos(a)*reach*(.7+random.random()*.35)
   line('Branch',[(0,h*.7,0),(x*.5,h-.3,z*.5),(x,h,z)],.055,bark)
   bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=coord((x,h+.1,z)));o=bpy.context.object;o.scale=(1.5+random.random()*.5,1.4+random.random()*.6,1.1+random.random()*.4);finish(o,'Canopy',leaf[k%4],True)
 else:
  line('Trunk',[(0,0,0),(0,8,0)],.10,bark)
  for k in range(9):
   y=2+k*.65;uv('CypressFoliage',(0,y,0),(.8*(1-k*.065),1.2,.8*(1-k*.065)),leaf[k%4])
 # Apply transforms and join into one mesh for MultiMesh instancing.
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.convert(target='MESH');bpy.context.view_layer.objects.active=bpy.context.selected_objects[0];bpy.ops.object.join();o=bpy.context.object;o.name='Tree'+str(typ)
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender'/('tree_'+str(typ)+'.blend')))
 bpy.ops.export_scene.gltf(filepath=str(ROOT/'assets'/('tree_'+str(typ)+'.glb')),export_format='GLB',use_selection=True,export_apply=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for k in range(5):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=coord((random.uniform(-1,1),random.uniform(.1,.6),random.uniform(-1,1))))
 o=bpy.context.object;o.scale=(random.uniform(.6,1.4),random.uniform(.6,1.4),random.uniform(.5,1.3));finish(o,'WeatheredRock',stone,False)
bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=bpy.context.selected_objects[0];bpy.ops.object.join();bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender'/'roadside_rocks.blend'))
bpy.ops.export_scene.gltf(filepath=str(ROOT/'assets'/'rocks.glb'),export_format='GLB',use_selection=True,export_apply=True)
print('ASTER_MODEL_BUILD_COMPLETE')
