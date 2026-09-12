# CHANGELOG v4

## Pre-QA blocker correction — 2026-09-12
기존 v3/v4를 보존한 별도 pre-qa 복제본에서 수행했으며 최종 QA가 아닙니다.
- 실제 GodotPhysics3D center_of_mass는 전역축 오프셋. 제안된 기존 COM 결함은 재현되지 않아 원점 차감을 제거하지 않고 양쪽 world COM을 명시했습니다.
- 재현된 P1: 플레이어/교통의 로컬 위치 텔레메트리를 전역 위치로 통일. 이동 QA 배치 오차 4,579.467285m → 0m.
- 4,579m 이동·동일 입력 6조건 회귀: 에너지·손상 차이 최대 0.001464860%, 부위·충격 판정 동일.
- import/export/최소 시작·종료, native 최초/기존 교체 저장 확인. 새 exe SHA-256: f531155b603527d45c200fe85ae866ec16f37cfae377e2461410f5b2824edd76.
- 튜닝·기능 추가 없음. 종합 주행·충돌·렌더 QA는 미수행. PRE_QA_BLOCKER_REPORT.md 참조.

기준: fable-5-1-vs-fable-at-3 전체를 fable-5-1-vs-fable-at-4로 복제한 뒤 outputs/AsterGT를 수정했습니다.
이전 테스트·영상·보고서는 이력으로 남아 있으며 v4 결과가 아닙니다.

## 변경 파일
|영역|파일|
|---|---|
|입력|scripts/controls.gd, safe_store.gd, config/control_actions.json|
|키 UI/안내|scripts/driving_ui.gd, hud.gd, main.gd|
|차량|scripts/car.gd, vehicle_config.gd, config/street.tres, setting_metadata.json|
|교통/접촉|scripts/traffic.gd, traffic_body.gd, contact_damage.gd, config/traffic_physics.json|
|카메라/월드/소리|scripts/camera_rig.gd, world.gd, car_audio.gd, config/experience.json, assets/v4/*.wav|
|Blender 제작|blender/v4/*.blend, *_audit.json, final_asset_inventory.json, assets/v4/*.glb, collision_proxies.json, porsche_rig.json|
|저장/빌드|runtime_tools/AtomicReplace.exe, build_tools/atomic_replace.c, build_windows.py, project.godot, export_presets.cfg|
|별도 QA|scripts/qa_logging.gd, config/qa_conditions.json, QA_SETUP.md|
|인계/고지|CONTROLS.md, VEHICLE_PHYSICS.md, TRAFFIC_COLLISION.md, BLENDER_MCP_LOG.md, CHANGELOG_V4.md, LICENSE, README.md, licenses/PORSCHE_MODEL.md|

## 구현
두 슬롯 재설정과 modifier, 충돌 선택 UI, 손상 설정 복구와 Windows 원자적 교체, 한국어 기본 온보딩/가이드, 자동 변속 보조·클러치·레브매칭 독립 및 저장, 6단/RWD 기준과 별도 Sandbox, 실제 속도 기반 물리·공력 프로필·예상치, 속도별 카메라/오디오, 동적 near traffic와 양쪽 손상, Blender 실제 교정/LOD/collider 및 로그, cockpit 기본 미러/좌우 반전, 젖은 노면 metallic=0, 도로 reference/streaming 개선.
기존 약 26km 월드, 날씨/시간, 카메라, 차고, 그래픽, 저장, 주행 모드, Windows export를 확장했습니다. 전체 재작성 방식은 사용하지 않았습니다.

## 수행 범위
work/v4/SMOKE_CHECK.json에 import/export/최소 시작·정상 종료, 종료 코드, 오류 목록, 실행 파일 SHA-256을 기록합니다. 문법·import·빌드 가능한지 확인하는 smoke 범위를 넘는 테스트를 실행하지 않았습니다.
최초 --quit-after 2 실행은 시작 후 terrain worker 종료에서 지연되어 해당 smoke 프로세스만 종료했습니다. --v4-smoke는 기존 정상 종료 정리를 통해 worker를 기다린 뒤 종료합니다.

## 미구현/미검증
- 게임패드 실제 입력 및 기존 모든 메뉴의 완전한 이중 언어화는 미구현입니다.
- 실차 토크/공력/타이어 측정 데이터 피팅, soft-body crash, 파편, 고급 AI 추월·견인은 미구현입니다.
- 아직 레거시 수학/렌더/레이아웃의 모든 수치 리터럴을 완전히 데이터화하지는 않았습니다. 주요 입력/차량/AI/카메라 튜닝은 레지스트리·Resource·JSON으로 분리했습니다.
- High Speed 목표 성능, 질량·각도별 충돌 안정성, input corruption/persistence 실기, 원거리 pop/flicker/흰 폴리곤, ultrawide 배치, 시각·음향·렌더 성능은 미검증입니다.
- 계기판/미러 및 responsive 배치 변경은 구현되어 있으나 화면별 최종 렌더 검사를 수행하지 않았습니다.
- 과거 테스트 스크립트에는 v3 파라미터/API 가정이 남아 있습니다. 별도 QA에서는 새 schema와 프로필을 사용해야 합니다.

READY_FOR_SEPARATE_QA는 구현·빌드 산출물을 별도 QA에 인계할 수 있다는 상태이며 최종 합격 의미가 아닙니다.
