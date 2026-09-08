from pathlib import Path
p=Path('outputs/AsterGT')
f=p/'scripts/car.gd';s=f.read_text(encoding='utf-8').replace('var calipers: Array[Node3D]=[]','var calipers: Array[Node3D]=[]\nvar dashboard: Label3D')
s=s.replace('var fx=tanh(slip*9.0)*capacity','var fx=tanh(slip*9.0)*(1.0-.35*smoothstep(.18,.70,absf(slip)))*capacity')
s=s.replace('var fy=-tanh(lat_angle*7.0)*capacity','var fy=-tanh(lat_angle*7.0)*(1.0-.18*smoothstep(.22,.75,absf(lat_angle)))*capacity')
s=s.replace('var available_lat=sqrt(maxf(0,capacity*capacity-fx_sum*fx_sum))','''if brake_demand>500 and absf(vx)<.30 and absf(drive)<500:
    fx_sum=clampf(-cfg.mass_kg*.25*(vx/dt+Vector3(0,-9.81,0).dot(tire_forward)),-capacity,capacity)
    w.omega=0
   var available_lat=sqrt(maxf(0,capacity*capacity-fx_sum*fx_sum))''')
s=s.replace('*(1.0-wetness*0.33)','*(1.0-maxf(wetness,1.0 if w.surface=="wet_asphalt" else 0.0)*0.33)')
s=s.replace('if steering_wheel:steering_wheel.rotation.z=steering*.75','''if steering_wheel:steering_wheel.rotation.z=steering*.75
 if dashboard:dashboard.text="%03d km/h   %s\\n%04d rpm"%[roundi(speed_kph),"N" if gear==0 else "R" if gear<0 else str(gear),roundi(rpm)]''')
s=s.replace('var model=body_visual\n steering_wheel','''var model=body_visual
 dashboard=Label3D.new();dashboard.font_size=28;dashboard.pixel_size=.0012;dashboard.position=Vector3(-.38,.455,-.475);dashboard.modulate=Color("a8e0c5");dashboard.outline_size=2;body_visual.add_child(dashboard)
 steering_wheel''')
s=s.replace('if node.name.begins_with("Steering"):', '''if node.name.begins_with("InstrumentDisplay"):
   var display_mat=StandardMaterial3D.new();display_mat.albedo_color=Color("062830");display_mat.emission_enabled=true;display_mat.emission=Color("05202a");display_mat.emission_energy_multiplier=.3;node.material_override=display_mat
  if node.name.begins_with("Steering"):''')
f.write_text(s,encoding='utf-8')
f=p/'scripts/world.gd';s=f.read_text(encoding='utf-8')
s=s.replace('var shoulder=mat(Color("a6a69a"),.93)','var wet=road_material.duplicate();wet.roughness=.25;wet.metallic=.12\n var shoulder=mat(Color("a6a69a"),.93)')
s=s.replace('ribbon(begin,end,-5.8,5.8,0,road_material,chunk,true)','ribbon(begin,end,-5.8,5.8,0,wet if begin*8>13000 and begin*8<13400 else road_material,chunk,true)')
s=s.replace('body.set_meta("surface","asphalt");parent.add_child(body)','body.set_meta("surface","wet_asphalt" if begin*8>13000 and begin*8<13400 else "asphalt");parent.add_child(body)')
s=s.replace('ribbon(begin,end,side*7.2-.065,side*7.2+.065,.78,guard,chunk)','''if side==1 and begin<166 and end>156:
    if begin<156:ribbon(begin,156,7.2-.065,7.2+.065,.78,guard,chunk)
    if end>166:ribbon(166,end,7.2-.065,7.2+.065,.78,guard,chunk)
   else:ribbon(begin,end,side*7.2-.065,side*7.2+.065,.78,guard,chunk)''')
s=s.replace('for side in [-1,1]:box(chunk,p+right*side*7.2+Vector3.UP*.42,Vector3(.11,.85,.11),guard)','''for side in [-1,1]:
    if side==1 and i>=156 and i<=166:continue
    box(chunk,p+right*side*7.2+Vector3.UP*.42,Vector3(.11,.85,.11),guard)''')
s=s.replace('var right=tangent.normalized().cross(Vector3.UP);var body=StaticBody3D.new();chunk.add_child(body)','if side==1 and i>=156 and i<=166:continue\n    var right=tangent.normalized().cross(Vector3.UP);var body=StaticBody3D.new();chunk.add_child(body)')
s=s.replace('box(village,Vector3(0,-.10,0),Vector3(42,.2,60),road_material,true)','box(village,Vector3(0,-.10,0),Vector3(42,.2,60),road_material,true)\n box(village,Vector3(-24,-.10,0),Vector3(18,.2,18),road_material,true)')
f.write_text(s,encoding='utf-8')
f=p/'scripts/car_audio.gd';s=f.read_text(encoding='utf-8').replace('"wind","tire"','"wind","roll","tire"')
s=s.replace('players.tire.volume_db=','players.roll.volume_db=linear_to_db(maxf(.0001,car.speed_kph/330*.2*(2.0 if car.wheels[0].surface=="grass" else 1.0)))\n players.roll.pitch_scale=.7 if car.wheels[0].surface=="grass" else 1.6\n players.tire.volume_db=')
f.write_text(s,encoding='utf-8')
import shutil
shutil.copy(p/'assets/wind.wav',p/'assets/roll.wav')
# Reliable wall-clock frame times, independent of engine delta smoothing.
f=p/'scripts/main.gd';s=f.read_text(encoding='utf-8').replace('var fps_samples: Array[float]=[]','var fps_samples: Array[float]=[]\nvar benchmark_last_us: int=0')
s=s.replace('if qa_stage==1 and runtime>5:fps_samples.append(dt)','''var now=Time.get_ticks_usec()
  if qa_stage==1 and runtime>5 and benchmark_last_us>0:fps_samples.append((now-benchmark_last_us)/1000000.0)
  benchmark_last_us=now''');f.write_text(s,encoding='utf-8')
