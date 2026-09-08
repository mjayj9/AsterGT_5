import bpy,math,random
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];random.seed(992)
def material(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*color,1);n.inputs['Roughness'].default_value=.87;return m
def branch(a,b,r1,r2,mat):
 delta=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cone_add(vertices=7,radius1=r1,radius2=r2,depth=delta.length,location=(Vector(a)+Vector(b))*.5);o=bpy.context.object;o.rotation_euler=delta.to_track_quat('Z','Y').to_euler();o.data.materials.append(mat)
def cards(center,size,mat):
 for k in range(3):
  angle=k*math.pi/3+random.random();u=Vector((math.cos(angle),math.sin(angle),random.uniform(-.3,.3)))*size;v=Vector((random.uniform(-.3,.3),random.uniform(-.3,.3),1))*size*.75;c=Vector(center)
  mesh=bpy.data.meshes.new('Foliage');mesh.from_pydata([c-u-v,c+u-v,c+u+v,c-u+v],[],[(0,1,2,3)]);mesh.uv_layers.new()
  for loop,uv in zip(mesh.uv_layers.active.data,[(0,0),(1,0),(1,1),(0,1)]):loop.uv=uv
  obj=bpy.data.objects.new('Foliage',mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(mat)
for typ in range(3):
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bark=material('Bark',(0.19,.15,.105) if typ!=1 else (.45,.43,.36));leaf=material('Leaves',(1,1,1));nodes=leaf.node_tree.nodes;tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'assets'/('needle_cluster.png' if typ==2 else 'leaf_cluster.png')));tex.image.pack();bs=nodes.get('Principled BSDF');leaf.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);leaf.node_tree.links.new(tex.outputs['Alpha'],bs.inputs['Alpha']);leaf.surface_render_method='DITHERED';leaf.use_backface_culling=False
 height=[9,12,11][typ];branch((0,0,0),(.15,.07,height),.27,.035,bark)
 for j in range(44 if typ!=2 else 65):
  f=j/(44 if typ!=2 else 65);z=height*(.35+.58*f);angle=j*2.399+random.uniform(-.3,.3)
  length=(2.9*math.sin(f*math.pi*.8)+.6) if typ==0 else (1.6*(1-f)+.4 if typ==1 else 3.5*(1-f)+.35)
  a=Vector((.1,0,z));b=a+Vector((math.cos(angle)*length*.56,math.sin(angle)*length*.56,.15 if typ==2 else .45));c=a+Vector((math.cos(angle)*length,math.sin(angle)*length,.2 if typ==2 else .8))
  branch(a,b,.065*(1-f)+.02,.025,bark);branch(b,c,.03,.009,bark)
  cards(c,random.uniform(.65,1.10) if typ==0 else random.uniform(.48,.78),leaf)
  if j%2==0:cards(b,.65,leaf)
 bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=next(o for o in bpy.context.scene.objects if o.type=='MESH');bpy.ops.object.join();o=bpy.context.object;o.name=['Oak','Aspen','Pine'][typ];bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender'/f'tree_{typ}.blend'))
 bpy.ops.export_scene.gltf(filepath=str(ROOT/'assets'/f'tree_{typ}.glb'),export_format='GLB',export_animations=False)
# Save the actual minimally adapted Porsche rig, with original embedded textures packed.
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets/porsche_992_gt3_r.glb'));bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/porsche_992_gt3_r_rigged.blend'))
print('DETAILED_FOLIAGE_AND_PORSCHE_SAVED')
