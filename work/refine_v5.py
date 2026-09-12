from pathlib import Path
p=Path(__file__).resolve().parents[1]/'outputs/AsterGT'
def update(path,fn):
 f=p/path;f.write_text(fn(f.read_text(encoding='utf-8')),encoding='utf-8')
update('tests/v5_regression.gd',lambda s:s.replace('game.world.shutdown_streaming()','await game.world.stop_streaming()'))
update('scripts/contact_damage.gd',lambda s:s.replace('  if visuals.add_hit(hit.point,hit.outward,hit.tangent,hit.energy,hit.tangent.length()):','  visuals.add_hit(hit.point,hit.outward,hit.tangent,hit.energy,hit.tangent.length())\n  if hit.energy>=900:'))
update('scripts/driving_ui.gd',lambda s:s.replace('+\"] · default \"+','+\"]\"+tr2(" · 기본값 "," · default ")+'))
# Translate existing menu surfaces consistently without touching internal identifiers.
translations={
'Graphics':'그래픽','Rendering controls are independent of vehicle performance.':'화면 품질 설정은 차량 성능과 별도로 적용됩니다.','Quality preset':'화면 품질','Low':'낮음','Medium':'중간','High':'높음','Ultra':'최고','Render scale':'렌더링 배율','Anti-aliasing':'계단 현상 완화','Off':'끄기','On':'켜기','Shadow quality':'그림자 품질','512 / hard':'512 · 선명','1024 / soft':'1024 · 부드럽게','2048 / soft':'2048 · 부드럽게','4096 / soft':'4096 · 부드럽게','Shadow distance · m':'그림자 거리 · m','Reflections':'반사','Sky':'하늘','Screen space':'화면 공간 반사','Screen space / high':'화면 공간 반사 · 높음','Vegetation density':'식생 밀도','Traffic count':'교통 차량 수','Particles':'입자 효과','Post-processing':'후처리','Rear-view mirror':'후방 미러','Frame limit':'초당 프레임 제한','Unlimited':'제한 없음','VSync':'수직 동기화','Fullscreen':'전체 화면','Window resolution':'창 해상도','Save settings':'설정 저장','Graphics preferences saved':'그래픽 설정을 저장했습니다.','Camera & audio':'카메라·소리','Camera':'카메라','Field of view':'시야각','Horizontal offset':'좌우 위치','Vertical offset':'높이','Forward / rear offset':'앞뒤 위치','Camera vibration':'카메라 흔들림','멀미 감소 / Reduced motion':'멀미 감소','Mute audio':'음소거','Speed in mph':'속도 단위: 마일/시','Save camera settings':'카메라 설정 저장','Camera saved':'카메라 설정을 저장했습니다.','Chase':'추적','Bumper':'범퍼','Hood':'후드','Cockpit':'조종석','Orbit':'자유 회전','PAINT FINISH':'차체 색상','Vehicle setup':'차량 설정','Take it for a drive                    →':'주행 시작  →','User-supplied 992 GT3 R model. Physics-driven wheels, brake discs, steering and suspension.':'992 GT3 R · 물리 기반 바퀴·브레이크·조향·서스펜션','Estimates vary with surface, gearing and driving aids.':'예상 성능은 노면·기어비·운전 보조에 따라 달라집니다.','POWER':'출력','TORQUE':'토크','MASS':'질량','DRIVE':'구동','CLEAR':'맑음','OVERCAST':'흐림','RAIN':'비','DAY':'낮','GOLDEN HOUR':'노을','NIGHT':'밤','THROTTLE':'가속','BRAKE':'브레이크','CLUTCH':'클러치','FREE DRIVE':'자유 주행','HIGH SPEED':'고속 주행','TIME TRIAL':'시간 기록','CHECKPOINTS':'체크포인트','Primary':'기본 키','Secondary':'보조 키','Throttle 0–1':'가속 0–1','Brake 0–1':'브레이크 0–1','Steering −1–1':'조향 −1–1',
}
# Called only on user-facing strings, never on action/profile IDs.
code='class_name GTLanguage\nextends RefCounted\nconst KOREAN='+__import__('json').dumps(translations,ensure_ascii=False,indent=1)+'\nstatic func text(value: String) -> String:\n if GTControls.language=="ko":return KOREAN.get(value,value)\n return value\n'
(p/'scripts/localization.gd').write_text(code,encoding='utf-8')
def hud(s):
 s=s.replace('draw_string(font,pos,text,','draw_string(font,pos,GTLanguage.text(text),')
 s=s.replace('l.text=text;','l.text=GTLanguage.text(text);').replace('b.text=text;','b.text=GTLanguage.text(text);').replace('b.text=title;','b.text=GTLanguage.text(title);').replace('o.add_item(str(item))','o.add_item(GTLanguage.text(str(item)))')
 s=s.replace('game.mode.to_upper()+','GTLanguage.text(game.mode.to_upper())+')
 s=s.replace('["CLEAR","OVERCAST","RAIN"][game.world.weather]+"  /  "+["DAY","GOLDEN HOUR","NIGHT"][game.world.time_of_day]','GTLanguage.text(["CLEAR","OVERCAST","RAIN"][game.world.weather])+"  /  "+GTLanguage.text(["DAY","GOLDEN HOUR","NIGHT"][game.world.time_of_day])')
 s=s.replace('GTCameraRig.NAMES[game.cam.mode]],','GTLanguage.text(GTCameraRig.NAMES[game.cam.mode])],')
 s=s.replace('"MODEL / MattDoesBlender     •     6-SPEED"','"모델: MattDoesBlender · 6단 순차식" if GTControls.language=="ko" else "Model: MattDoesBlender · 6-speed"')
 s=s.replace('txt("ROUTE  /  %0.1f KM"%(game.world.length/1000),','txt(("주행 경로 / %0.1f km" if GTControls.language=="ko" else "ROUTE / %0.1f km")%(game.world.length/1000),')
 # Wrap long menu headings and controls at small window sizes.
 s=s.replace('label(col,title,52,white)','var heading=label(col,title,40,white);heading.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART')
 return s
update('scripts/hud.gd',hud)
def perf(s):
 a=s.index('func show_performance()');b=s.index('func seconds(',a)
 return s[:a]+'''func show_performance() -> void:
 game.pause_game()
 var col=menu_base(tr2("성능·기어비","Performance and gearing"),true)
 var cfg=game.car.cfg;var estimate=cfg.performance_estimate()
 var profiles=["Authentic BoP","High Speed","Custom Sandbox"]
 var names=[tr2("실차 규정","Authentic BoP"),tr2("고속","High Speed"),tr2("자유 튜닝","Custom Sandbox")]
 label(col,names[maxi(0,profiles.find(cfg.profile))]+" · "+cfg.drive_layout,28,accent)
 small(col,"%.1f kW / %.1f PS · %d kg · %.1f kW/t"%[estimate.peak_kw,estimate.ps,cfg.mass_kg,estimate.peak_kw/cfg.mass_kg*1000])
 small(col,tr2("4194 cc · 수평대향 6기통 · 6단 순차식 · %.0f rpm","4194 cc · six-cylinder boxer · six-speed sequential · %.0f rpm")%cfg.max_rpm)
 for i in range(1,7):small(col,tr2("%d단: 회전 제한 속도 약 %.0f km/h · 기어비 %.3f","Gear %d: limiter speed about %.0f km/h · ratio %.3f")%[i,cfg.gear_speed(i),cfg.gear_ratios[i-1]])
 small(col,tr2("최종 감속비 %.3f · 윙 %.0f° · 항력 면적 %.3f m² · 다운포스 면적 %.3f m²\\n전방 공력 비율 %.0f%% · 전방 제동 비율 %.0f%% · 차동 제한 초기 토크 %.0f Nm\\nABS %.2f · TCS %.2f","Final drive %.3f · Wing %.0f° · CdA %.3f m² · ClA %.3f m²\\nFront aero %.0f%% · Front brake %.0f%% · Diff preload %.0f Nm\\nABS %.2f · TCS %.2f")%[cfg.final_drive,cfg.wing_angle_deg,cfg.effective_drag_area(),cfg.effective_lift_area(),cfg.aero_front_balance*100,cfg.brake_bias*100,cfg.diff_preload_nm,cfg.abs_strength,cfg.tcs_strength])
 small(col,tr2("기어비상 최고속도: %.1f km/h\\n항력 포함 예상 최고속도: %.1f km/h\\n0–100: %s · 100–200: %s · 200–300: %s","Gear-limited maximum: %.1f km/h\\nEstimated reachable speed: %.1f km/h\\n0–100: %s · 100–200: %s · 200–300: %s")%[estimate.gear_limited_kph,estimate.reachable_estimate_kph,seconds(estimate.zero_100_s),seconds(estimate["100_200_s"]),seconds(estimate["200_300_s"])])
 small(col,tr2("평지·건조·무풍·예열 타이어를 가정한 계산치입니다. 실측 기록과 다를 수 있으며, 설정에 따라 달라집니다.","Calculated for flat, dry, still-air conditions with warm tyres. Actual results vary with setup and driving."))
 var tires=[]
 for w in game.car.wheels:tires.append(tr2("%.0f°C / 마모 %.1f%%","%.0f°C / %.1f%% wear")%[w.temperature,w.wear*100])
 small(col,tr2("타이어 좌전 / 우전 / 좌후 / 우후: ","Tyres LF / RF / LR / RR: ")+" | ".join(tires))
 for i in range(profiles.size()):button(col,names[i],func():cfg.preset(profiles[i]);show_performance())
 button(col,tr2("상세 설정","Detailed setup"),show_setup);back(col)
''' + s[b:]
update('scripts/driving_ui.gd',perf)
print('v5 refinements applied')
