> Pre-QA blocker correction 복제본. 새 실행 파일은 ../Windows-v4-pre-qa/AsterGT-v4-pre-qa.exe입니다. PRE_QA_BLOCKER_REPORT.md의 범위·결과를 먼저 참고하십시오. 아래 기존 v4 설명과 최종 QA 과제는 유지합니다.

# 별도 QA 실행 준비
상태: 구현 인계. 최종 QA·주행/충돌 테스트·홍보 영상은 이번 작업에서 수행하지 않았습니다.
기존 tests 및 상위 폴더의 과거 보고서는 v3에서 복제한 이력이며 v4 합격 증거가 아닙니다.

## 실행
Godot 4.6.3 / Windows x86_64 / Forward+ / 물리 120Hz 기준입니다.
소스: project.godot. 실행 파일: ../Windows-v4/AsterGT-v4.exe.
저장 위치는 %APPDATA%/AsterGT-v4이며 v3와 분리됩니다. 키 controls.json, 차량 vehicle.json, 보조/언어/그래픽 preferences.json, 카메라 cameras.json입니다.

PowerShell에서:
```powershell
& '.\AsterGT-v4.exe' -- --telemetry-logging
```
로그: %APPDATA%/AsterGT-v4/qa-v4/session-<timestamp>.jsonl.
기본 플레이에서는 로그를 쓰지 않습니다. 스키마 버전 4, player/traffic 10Hz, contact는 물리 접촉 이벤트, shift/recovery/transition/fixture는 사건별 기록입니다. tick 및 time_s, entity id로 양쪽 로그를 연결하십시오.

## 고속 조건
1. High Speed 주행 모드 및 성능 프로필. F4에서 실제 프로필 확인.
2. 자동 변속 보조 ON, 자동 클러치 ON, 레브매칭 ON. 기존 저장에서 수동 모드가 유지될 수 있으므로 명시적으로 확인.
3. 맑음·낮·교통 0·예열 타이어·손상 0. 설정에서 타이어 정비와 차체 수리.
4. 원본 직선 시작 위치 along=1180m. 무풍 모델, 평지 직선에서 actual speed_kph와 position/velocity로 측정.
5. 0–100 / 100–200 / 200–300 및 안정 최고속도, 실제 주행 거리, 타이어 슬립/온도를 기록.
목표는 0–300 약 30–35초, 안정 최고속도 315–325km/h입니다. 이 목표가 통과되었다는 자료는 없습니다. Authentic은 따로 측정하십시오.

## 입력/UX
초기 저장을 별도로 백업한 QA 사용자 폴더에서 첫 실행을 확인하십시오. 3단계 실습, skip/replay, F1 주제별 가이드, 모든 토글, primary/secondary, 좌우 Shift, Ctrl/Alt/Shift 조합, 중복 교체/교환/취소, 범주/전체 복구, IME, 포커스 이탈, 재시작·차고·모드 변경 유지, 실패/손상/저장 중 종료를 확인하십시오.
Shift 클러치+W 발진, Shift+Q/E 변속, 명시적 Shift+다른 키 바인딩 우선순위를 포함하십시오. F8/F9의 독립성을 각각 확인하십시오.
저장 실패는 AtomicReplace.exe 실행 실패/읽기 전용 경로도 포함하여 이전 파일과 메모리 바인딩 유지 여부를 확인하십시오.

## 충돌
spawn_qa_vehicle hook 또는 별도 QA 스크립트에서 정지·주행 차량을 배치하십시오. 1,200 / 1,580 / 2,050kg, 30 / 100 / 200 / 300km/h, 0 / 30 / 90도 접촉 조건을 교차 비교합니다.
양쪽 선운동량·각운동량/에너지(지면 마찰·중력·구동력의 외부 일을 별도 고려), 정지 상대의 이동/회전, 최소 회복 유지시간, lane snap 부재, CCD, road/curb 구분, 양쪽 손상/램프/출력저하를 기록하십시오.
접촉 로그의 normal_energy_estimate_j는 전체 시스템 보존 에너지와 구별하십시오.

## 시각·음향·성능
1920×1080, 1920×1200, 2560×1080 또는 3440×1440에서 온보딩·HUD·계기판·후방 미러 중첩을 확인하십시오. mirror는 기본 cockpit 전용이며 Camera & Audio에서 모든 카메라 표시를 선택할 수 있습니다.
후방 방향과 좌우 반전, cockpit 물리 미러 중복, LOD 전환과 손상 morph, 고속 look-ahead, 야간 반사판/표지판, 빗길 metallic=0, 흰 과노출/폴리곤·원거리 flicker·pop-in, 200→250→300km/h 풍절음·엔진·노면음 구분을 확인하십시오.
렌더 FPS/draw call, GPU/CPU, 음향 청취, 최종 사용자 플레이는 아직 검사하지 않았습니다.

## 이번 작업에서 허용 범위로 수행한 항목
work/v4/SMOKE_CHECK.json은 문법/import/export/최소 시작·정상 종료만 기록합니다. --v4-smoke는 시작 후 종료 정리를 호출하며 주행/충돌/온보딩 합격 테스트를 실행하지 않습니다.
