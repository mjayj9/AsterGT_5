from pathlib import Path
p=Path('outputs/AsterGT/scripts/world.gd')
s=p.read_text(encoding='utf-8').replace('var nearest_index: int=0','''var nearest_index: int=0
var tile_thread: Thread
var pending_key: Vector2i
var pending_generation: int=0
var generation: int=0
var wanted_tiles={}
''')
s=s.replace('vegetation_density=value\n for key','vegetation_density=value\n generation+=1\n for key')
a=s.index('func update_streaming(');b=s.index('func make_tile(',a)
s=s[:a]+'''func update_streaming(dt: float) -> void:
 if not player:return
 if tile_thread and not tile_thread.is_alive():
  var built=tile_thread.wait_to_finish();tile_thread=null
  if is_instance_valid(built):
   if pending_generation==generation and wanted_tiles.has(pending_key) and not active_tiles.has(pending_key):
    add_child(built);active_tiles[pending_key]=built
   else:built.free()
 refresh_timer-=dt
 if refresh_timer<=0:
  refresh_timer=.35
  var center=Vector2i(floori(player.position.x/TILE),floori(player.position.z/TILE))
  wanted_tiles.clear()
  for x in range(-2,3):
   for z in range(-2,3):wanted_tiles[center+Vector2i(x,z)]=true
  for key in active_tiles.keys():
   if not wanted_tiles.has(key):active_tiles[key].queue_free();active_tiles.erase(key)
  for key in chunks:chunks[key].node.visible=chunks[key].center.distance_squared_to(player.position)<render_distance*render_distance
  nearest_index=nearest(player.position).index
 if tile_thread==null:
  var candidates=[]
  for key in wanted_tiles:
   if not active_tiles.has(key):candidates.append(key)
  candidates.sort_custom(func(a,b):return Vector2(a.x*TILE+TILE*.5,a.y*TILE+TILE*.5).distance_squared_to(Vector2(player.position.x,player.position.z))<Vector2(b.x*TILE+TILE*.5,b.y*TILE+TILE*.5).distance_squared_to(Vector2(player.position.x,player.position.z)))
  if not candidates.is_empty():
   pending_key=candidates[0];pending_generation=generation;tile_thread=Thread.new();tile_thread.start(make_tile.bind(pending_key))
func _exit_tree() -> void:
 if tile_thread:
  var built=tile_thread.wait_to_finish()
  if is_instance_valid(built):built.free()
  tile_thread=null
''' +s[b:]
s=s.replace('func make_tile(key: Vector2i) -> Node3D:\n var root3=Node3D.new();add_child(root3)','func make_tile(key: Vector2i) -> Node3D:\n var root3=Node3D.new()')
a=s.index(' var n=16;var step=TILE/n;');b=s.index(' st.generate_normals();var mesh=st.commit();',a)
s=s[:a]+''' var n=16;var step=TILE/n;var st=SurfaceTool.new();st.begin(Mesh.PRIMITIVE_TRIANGLES)
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
''' +s[b:]
p.write_text(s,encoding='utf-8')
p=Path('outputs/AsterGT/scripts/main.gd');s=p.read_text(encoding='utf-8').replace('fps_samples.append(1/maxf(dt,.0001))','fps_samples.append(dt)').replace('"average_fps":sum/fps_samples.size(),"minimum_fps":fps_samples.min()','"average_fps":fps_samples.size()/sum,"minimum_fps":1.0/fps_samples.max(),"one_percent_low_fps":1.0/fps_samples_sorted_p99()')
s+='''
func fps_samples_sorted_p99() -> float:
 var ordered=fps_samples.duplicate();ordered.sort()
 return ordered[mini(ordered.size()-1,int(ordered.size()*.99))]
''';p.write_text(s,encoding='utf-8')
