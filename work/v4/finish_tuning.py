from pathlib import Path
import json,math,wave,array
p=Path(r'C:/Users/admin/Documents/Codex/2026-09-08/fable-5-1-vs-fable-at-4/outputs/AsterGT')
f=p/'scripts/vehicle_config.gd';s=f.read_text(encoding='utf8')
params={'auto_clutch_full_speed_mps':4.5,'auto_launch_engagement':.65,'rpm_response_per_s':18.0,'upshift_min_rpm':4800.0,'downshift_power_rpm':5200.0,'downshift_cruise_rpm':3800.0,'downshift_braking_rpm':5500.0,'downshift_rpm_margin':.94,'shift_corner_accel_limit_mps2':7.0,'limiter_cut_band_rpm':80.0,'tcs_slip_target':.14,'tcs_gain':1.8,'tcs_min_torque_fraction':.08,'abs_slip_target':.13,'abs_release_fraction':.88,'tire_max_omega_rad_s':700.0,'tire_low_speed_mps':3.0}
addition=''.join('@export var '+k+': float = '+repr(v)+'\n' for k,v in params.items())
s=s.replace('const RANGES = {',addition+'const RANGES = {')
f.write_text(s,encoding='utf8')
f=p/'scripts/car.gd';s=f.read_text(encoding='utf8')
for a,b in {'clutch),8*dt':'clutch),cfg.clutch_engagement_rate*dt','/4.5,throttle*.65':'/cfg.auto_clutch_full_speed_mps,throttle*cfg.auto_launch_engagement','1-exp(-18*dt)':'1-exp(-cfg.rpm_response_per_s*dt)','lerpf(4800,cfg.redline_rpm':'lerpf(cfg.upshift_min_rpm,cfg.redline_rpm','var down_at=5200 if throttle>.7 else 3800':'var down_at=cfg.downshift_power_rpm if throttle>.7 else cfg.downshift_cruise_rpm','rpm<5500':'rpm<cfg.downshift_braking_rpm','cfg.redline_rpm*.94':'cfg.redline_rpm*cfg.downshift_rpm_margin','rpm>=cfg.max_rpm-80':'rpm>=cfg.max_rpm-cfg.limiter_cut_band_rpm','old_slip>0.14':'old_slip>cfg.tcs_slip_target','(old_slip-0.14)*cfg.tcs_strength*1.8,0.08':'(old_slip-cfg.tcs_slip_target)*cfg.tcs_strength*cfg.tcs_gain,cfg.tcs_min_torque_fraction','slip*signf(vx)<-0.13':'slip*signf(vx)<-cfg.abs_slip_target','cfg.abs_strength*0.88':'cfg.abs_strength*cfg.abs_release_fraction','maxf(absf(vx),3.0)':'maxf(absf(vx),cfg.tire_low_speed_mps)','-700,700':'-cfg.tire_max_omega_rad_s,cfg.tire_max_omega_rad_s'}.items():s=s.replace(a,b)
s=s.replace('and brake<.05 and throttle>.05:', 'and brake<.05 and throttle>.05 and absf(acceleration_local.x)<cfg.shift_corner_accel_limit_mps2:')
s=s.replace(' if not engine_on: target_rpm=0',' if shift_cut:shaft_delta_rpm=rpm-axle_rpm\n if not engine_on: target_rpm=0')
f.write_text(s,encoding='utf8')
f=p/'config/traffic_physics.json';d=json.loads(f.read_text());d.update({'cruise_min_mps':19,'cruise_max_mps':29,'speed_controller_gain_per_s':1.2,'lateral_damping_per_s':4.0,'path_lookahead_min_m':8,'max_steer_rad':.45,'rejoin_speed_mps':6,'coast_after_impact_s':1,'obstacle_poll_s':.1});f.write_text(json.dumps(d,indent=2),encoding='utf8')
f=p/'scripts/traffic_body.gd';s=f.read_text(encoding='utf8')
for a,b in {'maxf(8,absf(speed)':'maxf(tuning.path_lookahead_min_m,absf(speed)','-.45,.45':'-tuning.max_steer_rad,tuning.max_steer_rad','ray_clock=.1':'ray_clock=tuning.obstacle_poll_s','minf(target_speed_mps,6)':'minf(target_speed_mps,tuning.rejoin_speed_mps)','(target_speed_mps-speed)*1.2':'(target_speed_mps-speed)*tuning.speed_controller_gain_per_s','recovery_min_s-1':'recovery_min_s-tuning.coast_after_impact_s','*mass*.25*4.0':'*mass*.25*tuning.lateral_damping_per_s'}.items():s=s.replace(a,b)
f.write_text(s,encoding='utf8')
f=p/'scripts/traffic.gd';s=f.read_text(encoding='utf8').replace('rng.randf_range(19,29)','rng.randf_range(tuning.cruise_min_mps,tuning.cruise_max_mps)');f.write_text(s,encoding='utf8')
# Buffeting is a separate low-frequency body signal, not speed lines or fake camera shake.
data=array.array('h',[round(5000*(math.sin(2*math.pi*41*i/48000)+.4*math.sin(2*math.pi*67*i/48000))*(.7+.3*math.sin(2*math.pi*3*i/48000))) for i in range(96000)])
with wave.open(str(p/'assets/v4/buffet.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(48000);w.writeframes(data.tobytes())
f=p/'scripts/car_audio.gd';s=f.read_text(encoding='utf8')
s=s.replace('var mix_load: float=0','var mix_load: float=0\nvar flow_bus: String\nvar buffet_bus: String\nvar flow_filter: AudioEffectLowPassFilter')
s=s.replace(' players["whine"]=make_player("res://assets/v4/whine.wav",true)',''' players["whine"]=make_player("res://assets/v4/whine.wav",true)
 flow_bus="AirTires_"+str(get_instance_id());var index=AudioServer.bus_count;AudioServer.add_bus();AudioServer.set_bus_name(index,flow_bus)
 flow_filter=AudioEffectLowPassFilter.new();AudioServer.add_bus_effect(index,flow_filter);players.wind.bus=flow_bus;players.roll.bus=flow_bus
 buffet_bus="BodyBuffet_"+str(get_instance_id());index=AudioServer.bus_count;AudioServer.add_bus();AudioServer.set_bus_name(index,buffet_bus)
 var body_filter=AudioEffectLowPassFilter.new();body_filter.cutoff_hz=180;AudioServer.add_bus_effect(index,body_filter)
 players["buffet"]=make_player("res://assets/v4/buffet.wav",true);players.buffet.bus=buffet_bus''')
s=s.replace(' AudioServer.set_bus_mute(bus,muted or get_tree().paused)',''' AudioServer.set_bus_mute(bus,muted or get_tree().paused)
 AudioServer.set_bus_mute(AudioServer.get_bus_index(flow_bus),muted or get_tree().paused)
 AudioServer.set_bus_mute(AudioServer.get_bus_index(buffet_bus),muted or get_tree().paused)
 flow_filter.cutoff_hz=lerpf(700,3200 if interior else 11000,clampf(car.speed_kph/340,0,1))
 gain(players.buffet,(absf(car.road_vibration)*.02+pow(car.speed_kph/340,3)*.06)*(.9 if interior else .3),dt)''')
s=s.replace(' var index=AudioServer.get_bus_index(bus_name)\n if index>=0:AudioServer.remove_bus(index)',''' for name in [bus_name,flow_bus,buffet_bus]:
  var index=AudioServer.get_bus_index(name)
  if index>=0:AudioServer.remove_bus(index)''')
f.write_text(s,encoding='utf8')
# Human-readable explanation lives with configurable values.
metadata={
'mass_kg':['kg','질량','관성과 가속·제동·충돌 운동량에 영향을 줍니다.'],
'torque_scale':['ratio','출력 배율 (Sandbox)','Custom에서만 출력 곡선을 배율 조정합니다.'],
'max_rpm':['rpm','엔진 제한 회전수','단수별 속도 한계 및 오버레브 거절 기준입니다.'],
'final_drive':['ratio','최종 감속비','크면 가속력이 증가하고 기어 한계 속도가 낮아집니다.'],
'brake_torque':['Nm','최대 제동 토크','네 바퀴 총 제동 토크입니다. 실제 힘은 타이어 마찰로 제한됩니다.'],
'brake_bias':['front ratio','브레이크 바이어스','전륜에 배분하는 제동 토크 비율입니다.'],
'max_steer':['deg','저속 최대 조향각','실제 고속 조향각은 속도에 따라 줄어듭니다.'],
'steer_rate':['1/s','조향 입력 속도','키 입력을 정규화 조향량으로 바꾸는 상승 속도입니다.'],
'steer_return':['1/s','조향 복귀 속도','키를 놓았을 때 중앙으로 돌아오는 속도입니다.'],
'spring':['N/m','스프링 강성','차륜당 서스펜션 강성입니다. 차고와 접지 하중에 영향을 줍니다.'],
'bump_damping':['Ns/m','압축 감쇠','서스펜션 압축 속도에 비례하는 저항입니다.'],
'rebound_damping':['Ns/m','리바운드 감쇠','서스펜션 팽창 속도에 비례하는 저항입니다.'],
'ride_height':['m','서스펜션 휴지 길이','실제 차고는 하중·스프링 압축으로 결정됩니다. 공력에도 영향을 줍니다.'],
'grip_front':['coefficient','전륜 마찰','전륜 마찰 원의 기본 계수입니다.'],
'grip_rear':['coefficient','후륜 마찰','후륜 마찰 원의 기본 계수입니다.'],
'downforce':['m²','기준 ClA','다운포스 면적 계수. 증가 시 항력도 증가합니다.'],
'abs_strength':['0–1','ABS 개입','바퀴 잠김 시 브레이크를 푸는 비율입니다.'],
'tcs_strength':['0–1','TCS 개입','구동 슬립이 클 때 엔진 토크를 줄이는 강도입니다.'],
'esc_strength':['0–1','ESC 개입','목표 요 회전율을 벗어났을 때 안정화 토크를 조절합니다.'],
'wing_angle_deg':['deg','윙 각도','각도 증가 시 ClA와 CdA가 함께 증가합니다.'],
'drag_area':['m²','기본 CdA','윙·차고·밸런스 효과가 추가되기 전 항력 면적입니다.'],
'aero_front_balance':['front ratio','전륜 다운포스 배분','전후 축별 다운포스 작용점을 결정하고 작은 항력 페널티가 있습니다.'],
'diff_preload_nm':['Nm','디퍼렌셜 프리로드','구동축 좌우 바퀴 사이 토크 전달 상한입니다.']}
(p/'config/setting_metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf8')
f=p/'scripts/driving_ui.gd';s=f.read_text(encoding='utf8').replace(' var base=VehicleConfig.new()',' var base=VehicleConfig.new()\n var metadata=JSON.parse_string(FileAccess.get_file_as_string("res://config/setting_metadata.json"))')
s=s.replace('  slider(col,key+" ["+units.get(key,"ratio")+"] · default "+str(base.get(key))','  if metadata.has(key):small(col,metadata[key][2] if GTControls.language=="ko" else key+" affects the physical simulation; see VEHICLE_PHYSICS.md.")\n  slider(col,(metadata[key][1] if GTControls.language=="ko" and metadata.has(key) else key)+" ["+units.get(key,"ratio")+"] · default "+str(base.get(key))')
f.write_text(s,encoding='utf8')
print('tuning parameters documented and split audio buses prepared')
