from pathlib import Path
import json
p=Path(r'C:/Users/admin/Documents/Codex/2026-09-08/fable-5-1-vs-fable-at-4/outputs/AsterGT')
t=p/'scripts/traffic_body.gd'
s=t.read_text(encoding='utf-8-sig')
s=s.replace('var world: GTWorld','var world: GTWorld\nvar manager: Node\nvar target_lane: float=2.8\nvar overtake_left: float=0\nvar signal_side: int=0')
s=s.replace(' radius_m=tuning.wheel_radius_m',' target_lane=lane\n radius_m=tuning.wheel_radius_m',1)
s=s.replace('recovery_left=tuning.recovery_min_s;stable_time=0;mode="Recovery"','recovery_left=tuning.recovery_min_s;stable_time=0;mode="Recovery";overtake_left=0;target_lane=direction_sign*tuning.lane_width_m*.5')
s=s.replace(' var ahead=maxf(',''' overtake_left=maxf(0,overtake_left-dt)
 if mode=="Dynamic" and direction_sign>0 and target_lane<0 and overtake_left<=0 and manager.lane_clear(self,tuning.lane_width_m*.5,tuning.merge_front_m,tuning.merge_rear_m):
  target_lane=tuning.lane_width_m*.5
 lane=move_toward(lane,target_lane,tuning.lane_target_rate_mps*dt)
 var lane_tr=world.road_transform(route_distance,target_lane)
 var lateral_error=(lane_tr.origin-state.transform.origin).dot(basis.x)
 signal_side=int(signf(lateral_error)) if absf(lateral_error)>tuning.indicator_error_m else 0
 var ahead=maxf(''',1)
old='  if not hit.is_empty():target_speed_mps=minf(target_speed_mps,maxf(0,(origin.distance_to(hit.position)-tuning.follow_gap_m)/tuning.follow_headway_s))'
new='''  if not hit.is_empty():
   var gap=origin.distance_to(hit.position)
   target_speed_mps=minf(target_speed_mps,maxf(0,(gap-tuning.follow_gap_m)/tuning.follow_headway_s))
   if controller_enabled and mode=="Dynamic" and direction_sign>0 and target_lane>0 and signal_side==0 and overtake_left<=0 and gap>tuning.pass_gap_min_m and gap<tuning.pass_gap_max_m and target_speed_mps<cruise_mps-tuning.pass_speed_advantage_mps:
    var horizon=(cruise_mps+tuning.cruise_max_mps)*(tuning.pass_duration_s+tuning.pass_clearance_s)
    if manager.lane_clear(self,-tuning.lane_width_m*.5,horizon,tuning.merge_rear_m):
     target_lane=-tuning.lane_width_m*.5;overtake_left=tuning.pass_duration_s
'''
assert old in s;s=s.replace(old,new.rstrip())
s=s.replace(' signal_material.emission_energy_multiplier=2.5 if mode in ["Recovery","Rejoin"] and fmod(time_s,1)<.5 else 0',''' var hazards=mode in ["Recovery","Rejoin"]
 for light in indicator_meshes:light.visible=hazards or (signal_side!=0 and int(signf(light.position.x))==signal_side)
 signal_material.emission_energy_multiplier=2.5*(1-damage.state.lights) if fmod(time_s,tuning.signal_period_s)<tuning.signal_period_s*.5 else 0''')
s=s.replace('"mode":mode,"mass_kg"','"mode":mode,"target_lane_m":target_lane,"indicator":signal_side,"mass_kg"')
t.write_text(s,encoding='utf8')
t=p/'scripts/traffic.gd';s=t.read_text(encoding='utf-8-sig')
s=s.replace('body.world=world;body.tuning=tuning','body.world=world;body.manager=self;body.tuning=tuning')
s=s.replace('body.mode=="Dynamic" and body.damage.state.body', 'body.mode=="Dynamic" and absf(body.lane-body.direction_sign*tuning.lane_width_m*.5)<.1 and body.signal_side==0 and body.damage.state.body')
s+='''
func lane_clear(subject: GTTrafficBody,wanted_lane: float,ahead_m: float,behind_m: float) -> bool:
 var candidates: Array[Node3D]=[car]
 for item in cars:
  if item.body!=subject:candidates.append(item.body)
 for other in candidates:
  var nearest=world.nearest(other.global_position)
  var along_delta=fposmod(nearest.along-subject.route_distance+world.length*.5,world.length)-world.length*.5
  if along_delta < -behind_m or along_delta > ahead_m:continue
  var frame=world.road_transform(nearest.along,0)
  var actual_lane=(other.global_position-frame.origin).dot(frame.basis.x)
  if absf(actual_lane-wanted_lane)<tuning.clearance_lateral_m:return false
  if other is GTTrafficBody and absf(other.target_lane-wanted_lane)<tuning.clearance_lateral_m:return false
 return true
'''
t.write_text(s,encoding='utf8')
t=p/'config/traffic_physics.json';d=json.loads(t.read_text());d.update({'lane_target_rate_mps':1.3,'pass_gap_min_m':12,'pass_gap_max_m':38,'pass_duration_s':6,'pass_clearance_s':5,'pass_speed_advantage_mps':2,'merge_front_m':25,'merge_rear_m':48,'clearance_lateral_m':2.5,'indicator_error_m':.6,'signal_period_s':1})
t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
t=p/'TRAFFIC_COLLISION.md';s=t.read_text(encoding='utf8')
s=s.replace('## 미구현·별도 QA','''## 기본 추월과 방향지시등
v3의 정방향 교통 기본 추월을 유지했습니다. 전방 느린 차량과 12–38m 간격이면 반대 차선의 Near/Far 차량과 플레이어를 경로 좌표로 확인합니다. 접근 여유가 있을 때 목표 차선을 초당 1.3m로 이동시키고 타이어 힘으로 따라갑니다. 6초 뒤 본선 앞 25m/뒤 48m가 비었을 때 복귀합니다. 이는 목표점 이동이며 차체 transform을 덮어쓰지 않습니다. 차선 변경 중 좌/우 방향지시등, Recovery/Rejoin 중 양쪽 비상등을 표시합니다. 추월 중에는 Far로 전환하지 않습니다. 안전 간격, 신호 주기와 목표 차선 변화율은 traffic_physics.json에 있습니다. 실제 안전성과 차선 복귀 성공률은 별도 QA 대상입니다.

## 미구현·별도 QA''')
t.write_text(s,encoding='utf8')
