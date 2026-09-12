# Pre-QA blocker correction
지정된 P0/P1 감사와 좌표 회귀·빌드 게이트 기록입니다. 최종 QA나 최종 합격 판정이 아닙니다. 주행감·성능·충돌 강도 튜닝, 새 기능·메뉴·차량·그래픽 효과를 추가하지 않았습니다.

## 원본 보존
기존 v4 전체를 fable-5-1-vs-fable-at-4-pre-qa에 복제했습니다. 기존 v3 4,223개와 기존 v4 5,010개 파일 전체의 SHA-256·이름·크기가 수정 전후 동일합니다. work/preqa/ORIGINALS_PRESERVED.json 및 originals_before.json에 근거가 있습니다.
복제된 Windows-v4 패키지·DELIVERY_V4.json·과거 보고서는 이전 이력입니다. 이번 산출물은 Windows-v4-pre-qa 및 PRE_QA_DELIVERY.json입니다.

## 접촉 좌표계 — 제안된 결함은 현재 엔진에서 재현되지 않음
실제 파일은 scripts/contact_damage.gd입니다. scripts/v4/contact_damage.gd는 없습니다.
project.godot:25는 GodotPhysics3D를 지정하며 사용 엔진은 4.6.3입니다.

get_contact_local_position()은 전역 접촉점입니다. PhysicsDirectBodyState3D.center_of_mass는 전역축으로 표현한 **차체 원점 기준 오프셋**이므로, point - physics.center_of_mass만 계산하면 잘못됩니다. [Godot 4.6 API](https://docs.godotengine.org/en/4.6/classes/class_physicsdirectbodystate3d.html#class-physicsdirectbodystate3d-property-center-of-mass), [4.6.3 엔진 구현](https://github.com/godotengine/godot/blob/4.6.3-stable/modules/godot_physics_3d/godot_body_direct_state_3d.cpp).

실제 RigidBody3D._integrate_forces의 origin을 (0,0,0)에서 (4096,0,-2048)m로 옮겨도 center_of_mass는 두 위치에서 (0.4591084123,-0.125,0.3189348876)m로 같았습니다. tests/preqa/native_com_probe.json에 원시값이 있습니다.

기존 자기 차량 수식은 정상입니다. 요청에 따라 양쪽의 전역 질량중심을 명시한 동치식으로 정리했으며, 이를 기존 P1 물리 오류 수정이라고 주장하지 않습니다.

변경 전:
~~~gdscript
var r = point - physics.transform.origin - physics.center_of_mass
var r2 = point - other.global_position - other.global_basis * other.center_of_mass
~~~
변경 후:
~~~gdscript
var world_center_of_mass = physics.transform.origin + physics.center_of_mass
var r = point - world_center_of_mass
var other_world_center_of_mass = other.global_transform * other.center_of_mass
var r2 = point - other_world_center_of_mass
~~~
RigidBody3D.center_of_mass는 body-local이며 현재 양쪽 차량은 CUSTOM 모드입니다. 질량·관성·충격량·반발계수·에너지/손상 임계값은 그대로입니다. 덧셈 순서에 따른 float 반올림 차이만 존재합니다.

## 재현된 P1: 텔레메트리의 좌표 혼합
scripts/car.gd:387의 position과 scripts/traffic_body.gd:139의 position_m은 부모 기준 로컬 위치였지만 속도·접촉점은 전역 좌표였습니다. 부모가 identity인 현재 main에서는 차이가 가려집니다. QA 배치의 부모를 (4096,0,-2048)m 옮기면 양쪽 위치 로그가 실제 전역 위치와 4,579.467285m 어긋납니다.
두 필드 값만 [position.x,position.y,position.z]에서 [global_position.x,global_position.y,global_position.z]로 변경했습니다. schema·필드명·차량 움직임은 그대로입니다. 수정 후 원점·이동 배치 모두 오차 0m입니다.
telemetry_regression.gd는 실제 production telemetry()를 호출합니다. 테스트 subclass는 무관한 렌더·주행 초기화만 생략합니다. 변경 전 실패와 변경 후 성공 JSON을 모두 보존했습니다.

## 위치 불변성 회귀
원점 부근 (8,8,8)m와 여기에 (4096,0,-2048)m를 더한 배치를 비교했습니다. 위치 간 거리 4,579.467285m.
질량 1,265/1,580kg, 속도 (4,0,-25)/(0,0,3)m/s를 고정하고 각도 0/0.625rad와 충격량 1,000/4,000/8,000Ns의 6조건을 재생했습니다. 각 위치 쌍의 접촉 법선·질량·관성·속도·충격량·자세는 동일하고 위치만 바뀝니다.
실제 GTContactDamage.sample()을 호출하는 결정적 접촉 계산 회귀입니다. solver로 차량을 들이받는 종합 충돌 QA가 아닙니다. 기준 에너지는 이동량 없는 로컬 레버암으로 독립 계산했습니다.
손상은 실제 연속 zone/body/lights/steering/power 값 전체, 부위와 impacted 판정을 비교했습니다. 게임에 없는 별도 손상 단계 시스템을 가정하지 않았습니다.

|각도 rad|충격량 Ns|기준 에너지 J|원점 부근 J|이동 위치 J|에너지 차이|손상 차이|부위·충격 판정|
|---:|---:|---:|---:|---:|---:|---:|---|
| 0.000 | 1000 | 970.207130 | 970.207123 | 970.212047 | 0.00050744% | 0.00050744% | 동일 |
| 0.000 | 4000 | 15523.314083 | 15523.313975 | 15523.392747 | 0.00050744% | 0.00050744% | 동일 |
| 0.000 | 8000 | 62093.256334 | 62093.255901 | 62093.570988 | 0.00050744% | 0.00000000% | 동일 |
| 0.625 | 1000 | 1374.991268 | 1374.991261 | 1374.971120 | 0.00146486% | 0.00146486% | 동일 |
| 0.625 | 4000 | 21999.860292 | 21999.860184 | 21999.537916 | 0.00146486% | 0.00146486% | 동일 |
| 0.625 | 8000 | 87999.441167 | 87999.440734 | 87998.151665 | 0.00146486% | 0.00000000% | 동일 |

변경 전 최대 에너지·손상 차이 0.00000767948% / 0.00000767948%.
변경 후 최대 에너지·손상 차이 0.001464860% / 0.001464860%.
독립 기준 에너지와의 최대 차이 0.001465352%. 6조건 모두 1% 이내이며 부위·충격 판정이 같습니다.
제안된 point - physics.center_of_mass 단순 치환의 비교 계산은 최대 7309097.80%의 위치 차이를 냅니다.

## 지정된 정적 감사
|항목|근거와 판단|
|---|---|
|실제 main/HUD/입력|project.godot:6 → scenes/main.tscn → main.gd. main.gd:48 GTControls.initialize(), :54 GTV4Hud.new(). 변경 없음.|
|레거시 입력 중복|hud.gd:256 _input()은 pass. main.gd:121 capture 우선, :127 modal 차단 후 registry recognize. 차량 hold는 GTControls.value(). 중복 주행 입력 경로 발견되지 않음.|
|최초 저장·기존 교체|GTSafeStore가 같은 디렉터리 .tmp를 flush 후 helper 호출. helper는 FlushFileBuffers 뒤 최초 MoveFileExW(WRITE_THROUGH), 기존 ReplaceFileW. 삭제 후 rename fallback 없음. controls는 저장 성공 후 메모리 적용.|
|교통 승격·강등|traffic.gd:33–34 같은 spec.mass_kg·velocity/spin 전달. :39 전체 선속도·각속도 벡터 보관. traffic_body.gd:36–40 spec 질량·관성 설정. 현재 main의 identity 부모 구조에서 전환 순간 상태 소실 근거 없음.|
|나머지 좌표|양쪽 바퀴 접촉 속도는 world offset - basis × body-local COM. acceleration_local은 basis.inverse()로 변환. contact/velocity는 world. 두 위치 로그의 local만 수정.|

생산 native helper를 별도 임시 테스트 디렉터리에서 실행해 첫 생성·기존 교체 각각 종료 0, 내용 일치, tmp 소멸을 확인했습니다. 원자성은 API와 코드 경로를 검토한 결과이며 전원 차단 내구성 합격을 뜻하지 않습니다. 원래 사용자 설정 파일은 테스트 대상으로 사용하지 않았습니다.
Far의 전환 이후 spline 갱신은 기존 설계이며 동역학 보존을 새로 보장하도록 바꾸지 않았습니다.

## 수정 파일과 이유
- scripts/contact_damage.gd:18–26 — 전역 질량중심 명시와 오프셋 API 주석. 정상 수학 유지.
- scripts/car.gd:387, scripts/traffic_body.gd:139 — 재현된 QA 위치 로그 P1만 수정.
- export_presets.cfg — 별도 출력 경로만 변경.
- tests/preqa/*.gd 및 JSON — native API/접촉/텔레메트리 좌표 회귀 증거.
- work/preqa/*.py, runtime_changes.patch 및 JSON/log — 재현·보존·빌드 기록.
- CHANGELOG_V4.md, PRE_QA_BLOCKER_REPORT.md, README.md, QA_SETUP.md, README_PRE_QA.md — 이번 범위·인계 기록.
런타임 실질 diff는 work/preqa/runtime_changes.patch입니다. config·GLB·Blender·오디오 파일은 해시가 동일합니다.

## 빌드 게이트
headless import, 좌표 회귀 2종, Windows export, 새 실행 파일 최소 시작·정상 종료 모두 종료 0, 스크립트 오류 0. ASTER_READY를 확인했습니다.
실행 파일: C:\Users\admin\Documents\Codex\2026-09-08\fable-5-1-vs-fable-at-4-pre-qa\outputs\Windows-v4-pre-qa\AsterGT-v4-pre-qa.exe
크기: 198,878,520 bytes.
SHA-256: f531155b603527d45c200fe85ae866ec16f37cfae377e2461410f5b2824edd76
기계 판독 기록: work/preqa/PRE_QA_GATE.json.
재현: Python으로 work/preqa/run_gate.py 실행. 종합 QA나 주행 성능 테스트를 호출하지 않습니다.

## 의도적으로 수정하지 않고 QA로 넘긴 항목
- 최고속도·가속력·기어비·타이어 그립·공력·질량·충돌 강도·손상 계수.
- 전체 UI/IME/재바인딩 실기와 시각·음향·렌더 성능.
- 실제 충돌의 solver 에너지 보존, CCD·관통·회복, 접촉 에너지 모델의 실차 적합성.
- Far/Near 장시간 운용, 비 identity 경로 관리자 변환 지원, 자동 COM인 외부 차량 등 현재 main과 다른 확장 구조.
- 전원 차단·동시 저장·손상 설정 복구의 종합 내구성 시험.
현재 P0/P1 근거가 없는 영역은 추측성 리팩터링하지 않았습니다.

READY_FOR_PRE_QA_GATE: YES — 제한된 사전 게이트 기준 충족. 최종 QA 합격이 아닙니다.
