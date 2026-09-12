from pathlib import Path
import json,wave,array,math
p=Path(r'C:/Users/admin/Documents/Codex/2026-09-08/fable-5-1-vs-fable-at-4/outputs/AsterGT')
f=p/'scripts/camera_rig.gd';s=f.read_text(encoding='utf-8-sig')
s=s.replace('var car: GTCar','var car: GTCar\nvar reduced_motion: bool=false\nvar experience: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://config/experience.json"))')
s=s.replace(' if mode!=4 or menu_preview:return',' if mode!=4 or menu_preview or not GTControls.driving():return')
s=s.replace('Input.is_action_pressed("look_back")','GTControls.value("look_back")>.5')
a=s.index('  var shake=sin(');b=s.index(' target=safe_position',a)
s=s[:a]+'''  var effects=0.0 if reduced_motion else shake_strength
  target+=tr.basis*Vector3(-car.acceleration_local.x,0,-car.acceleration_local.z)*experience.camera_displacement_m_per_mps2*effects
  target.y+=car.road_vibration*experience.camera_road_effect_m*effects
  camera.fov=lerpf(camera.fov,fovs[mode]+speed_fov(mode,car.speed_kph)*(0.3 if reduced_motion else 1.0),1-exp(-4*dt))
'''+s[b:]
s=s.replace(' camera.look_at(look,Vector3.UP);first=false',''' camera.look_at(look,Vector3.UP)
 if not menu_preview and not reduced_motion:
  var limit=float(experience.max_acceleration_effect_mps2)
  camera.rotate_object_local(Vector3.RIGHT,-clampf(car.acceleration_local.z,-limit,limit)*experience.camera_accel_pitch_rad_per_mps2*shake_strength)
  camera.rotate_object_local(Vector3.BACK,clampf(car.acceleration_local.x,-limit,limit)*experience.camera_lateral_roll_rad_per_mps2*shake_strength)
 first=false''')
s=s.replace('func save_settings() -> void:','''func speed_fov(camera_index: int,speed: float) -> float:
 var knots=experience.fov_speed_knots_kph
 var values=experience.fov_add_degrees[camera_index]
 for i in range(knots.size()-1):
  if speed<=knots[i+1]:return lerpf(values[i],values[i+1],clampf((speed-knots[i])/(knots[i+1]-knots[i]),0,1))
 return values[-1]
func save_settings() -> Error:''')
s=s.replace('"version":2,"shake":','"version":4,"reduced_motion":reduced_motion,"shake":')
s=s.replace(' var f=FileAccess.open("user://cameras.json",FileAccess.WRITE)\n if f:f.store_string(JSON.stringify(d))',' return GTSafeStore.save_json("user://cameras.json",d)')
s=s.replace(' if d.get("shake") is float:',' if d.get("reduced_motion") is bool:reduced_motion=d.reduced_motion\n if d.get("shake") is float:')
s=s.replace('   if "INT_BANNER" in str(node.name)', '   if "MIRROR" in str(node.name):node.visible=not (mode==3 and not menu_preview)\n   if "INT_BANNER" in str(node.name)')
f.write_text(s,encoding='utf8')
# Derive a new 9250-RPM anchor from the existing generated sample; no recording claim.
for load in ['on','off']:
 src=p/'assets/audio'/('engine_7500_'+load+'.wav');dst=p/'assets/v4'/('engine_9250_'+load+'.wav')
 with wave.open(str(src),'rb') as r:rate=r.getframerate();channels=r.getnchannels();data=array.array('h',r.readframes(r.getnframes()))
 frames=len(data)//channels;ratio=9250/7500;out=array.array('h')
 for i in range(int(frames/ratio)):
  at=i*ratio;j=int(at);t=at-j
  for ch in range(channels):out.append(round(data[j*channels+ch]*(1-t)+data[((j+1)%frames)*channels+ch]*t))
 with wave.open(str(dst),'wb') as w:w.setnchannels(channels);w.setsampwidth(2);w.setframerate(rate);w.writeframes(out.tobytes())
out=array.array('h',[round(8000*(math.sin(2*math.pi*320*i/48000)+.23*math.sin(2*math.pi*640*i/48000))) for i in range(48000)])
with wave.open(str(p/'assets/v4/whine.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(48000);w.writeframes(out.tobytes())
f=p/'scripts/car_audio.gd';s=f.read_text(encoding='utf-8-sig')
s=s.replace('for rpm in [850,1800,3000,4500,6000,7500]:','for rpm in [850,1800,3000,4500,6000,7500,9250]:')
s=s.replace('var player=make_player("res://assets/audio/engine_%d_%s.wav"%[rpm,state],true)','var player=make_player(("res://assets/v4/" if rpm==9250 else "res://assets/audio/")+"engine_%d_%s.wav"%[rpm,state],true)')
s=s.replace('func make_player(path:', ' players["whine"]=make_player("res://assets/v4/whine.wav",true)\nfunc make_player(path:')
s=s.replace('gain(players.wind,pow(car.speed_kph/330,2)*.48,dt)','gain(players.wind,pow(car.speed_kph/330,2.7)*(.42 if interior else .64),dt)\n players.wind.pitch_scale=lerpf(.55,1.8,clampf(car.speed_kph/340,0,1))\n players.whine.pitch_scale=clampf(car.rpm/4500,.35,2.3)\n gain(players.whine,(.025+.075*car.engine_load)*minf(car.speed_kph/80,1)*(0.2 if car.shift_cut else 1),dt)')
s=s.replace('players.roll.pitch_scale=.7 if car.wheels[0].surface=="grass" else 1.6','players.roll.pitch_scale=(.7 if car.wheels[0].surface=="grass" else 1.0)*lerpf(.65,1.85,clampf(car.speed_kph/340,0,1))')
s=s.replace('Input.is_action_pressed("horn")','GTControls.value("horn")>.5')
s=s.replace(' var stream=source.duplicate()',' if not source:return player\n var stream=source.duplicate()')
s=s.replace(' if car.shift_timer>0 and last_shift<=0:', ' if car.shift_timer<=0 and last_shift>0:players.shift.volume_db=-15;players.shift.play()\n if car.shift_timer>0 and last_shift<=0:')
f.write_text(s,encoding='utf8')
f=p/'scripts/world.gd';s=f.read_text(encoding='utf-8-sig')
s=s.replace('var curve=Curve3D.new()','var curve=Curve3D.new()\nvar experience: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://config/experience.json"))\nvar lookahead_m: float=0\nvar stream_focus=Vector3.ZERO')
s=s.replace('road_material.metallic=.1 if weather==2 else 0','road_material.metallic=0\n road_material.normal_scale=.20 if weather==2 else .45')
s=s.replace('wet.metallic=.12','wet.metallic=0')
s=s.replace('ribbon(begin,end,-7.6,7.6,-.055,shoulder,chunk,true)','ribbon(begin,end,-7.6,-5.8,-.025,shoulder,chunk,true)\n  ribbon(begin,end,5.8,7.6,-.025,shoulder,chunk,true)')
s=s.replace('  # Solid rail segments','  add_reference_markers(chunk,begin,end)\n  # Solid rail segments')
s=s.replace('environment.ambient_light_energy=.5 if not night else .20','environment.ambient_light_energy=.5 if not night else .28\n environment.tonemap_exposure=1.05 if night else .92')
s=s.replace('  var center=Vector2i(floori(player.position.x/TILE),floori(player.position.z/TILE))','''  lookahead_m=player.linear_velocity.length()*experience.stream_lookahead_s+experience.stream_margin_m
  stream_focus=player.position+player.linear_velocity.normalized()*lookahead_m*.5
  var center=Vector2i(floori(player.position.x/TILE),floori(player.position.z/TILE))''')
s=s.replace('  for key in active_tiles.keys():','''  for step in range(1,int(ceil(lookahead_m/TILE))+1):
   var ahead=player.position+player.linear_velocity.normalized()*TILE*step
   var ahead_key=Vector2i(floori(ahead.x/TILE),floori(ahead.z/TILE))
   for x in range(-1,2):
    for z in range(-1,2):wanted_tiles[ahead_key+Vector2i(x,z)]=true
  for key in active_tiles.keys():''')
s=s.replace('<render_distance*render_distance','<pow(maxf(render_distance,lookahead_m+TILE),2)')
s=s.replace('distance_squared_to(Vector2(player.position.x,player.position.z))','distance_squared_to(Vector2(stream_focus.x,stream_focus.z))')
s+='''\nfunc add_reference_markers(chunk: Node3D,begin: int,end: int) -> void:
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
'''
f.write_text(s,encoding='utf8')
# Export presets retain original assets but ship v4 alongside a separate binary name.
f=p/'export_presets.cfg';s=f.read_text(encoding='utf-8-sig').replace('include_filter="assets/*.json"','include_filter="assets/*.json,assets/v4/*.json,config/*.json"').replace('export_path="../Windows/AsterGT.exe"','export_path="../Windows-v4/AsterGT-v4.exe"')
s=s.replace('custom_template/release=""','custom_template/release="../../work/tools/windows_release_x86_64.exe"')
f.write_text(s,encoding='utf8')
f=p/'scripts/hud.gd';s=f.read_text(encoding='utf8').replace('game.cam.save_settings();game.save_preferences();notify("Camera preferences saved")','var err=game.cam.save_settings();game.save_preferences();notify("Camera saved" if err==OK else "저장 실패: "+error_string(err))');f.write_text(s,encoding='utf8')
print('camera/world/audio/export changes applied')
