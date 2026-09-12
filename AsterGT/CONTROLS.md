# v4 입력·온보딩
이 문서는 구현 설명입니다. 기능별 실기 검증 및 최종 합격 판정은 수행하지 않았습니다.

## 구현
- 단일 정의: `config/control_actions.json`. id, 한국어/영어 이름·설명, 카테고리, 컨텍스트, hold/axis/toggle, 기본 두 슬롯, modifier 지원, 재설정 여부, 게임패드 확장 메타데이터.
- 현재 두 슬롯은 `GTControls.bindings`와 schema_version 4의 `user://controls.json`에 저장합니다.
- REBIND_CAPTURE → modal → MENU/PAUSED → DRIVING 순서입니다. ONBOARDING은 실습 주행을 허용하며 PHOTO_ORBIT은 카메라 조작 컨텍스트입니다.
- 캡처 중 차량 이벤트를 소비하고, key echo로 토글하지 않습니다. 컨텍스트 전환·포커스 이탈 때 hold 상태를 비웁니다. hold 값은 게임 전용 상태를 사용하므로 UI에 소비된 키가 InputMap을 통해 차량에 새지 않습니다.
- Primary/Secondary, modifier 및 좌우 modifier 위치 저장. 명시적인 modifier 조합이 우선이며 독립 hold modifier(기본 클러치 Shift)와 W/Q/E 동시 조작을 허용합니다.
- Esc 취소, Backspace 슬롯 비우기, 중복 키 교체/서로 바꾸기/취소, 범주·전체 초기화 확인. 범주 복구 시 다른 범주의 충돌 슬롯을 비우며 UI에서 안내합니다.
- 0·알 수 없는 코드·지원하지 않는 키·조합 Unicode 입력 거부. 캡처 동안 IME 텍스트 조합을 비활성화하고 종료 시 활성화합니다.
- 입력 진단에 인식된 키/액션/컨텍스트, raw throttle/brake/steering 막대, 차량의 실제 정규화 값을 표시합니다. 메뉴에서는 실제 차량이 일시정지되어 있습니다.
- 한국어 기본 3단계 안내, 영어 선택, 건너뛰기/재실행. 첫 단계는 실제 키 입력과 차량 가속·조향·제동·카메라 변경을 관측해 자동 진행합니다. 2/3단계는 사용자가 다음/완료로 진행합니다.
- 첫 300초 시동 꺼짐, 중립, 수동 클러치, 고속 상황 도움말. F1은 주행/변속/차량/보조/문제 해결 주제별 가이드입니다.
- 모든 바인딩을 비워도 화면 우측 마우스 메뉴 버튼으로 설정에 돌아갈 수 있습니다.
- 변속 보조·자동 클러치·레브매칭·ABS/TCS/ESC·언어·온보딩 완료를 저장하며 start_drive에서 automatic=true를 강제하지 않습니다.

## 저장 방식
`GTSafeStore`가 같은 폴더에 .tmp를 쓰고 flush합니다. Windows에서는 배포에 포함된 `runtime_tools/AtomicReplace.exe`를 처음 저장할 때 user://runtime-tools에 추출합니다. 이 네이티브 도구는 FlushFileBuffers 후 ReplaceFileW(기존 파일) 또는 MoveFileExW(새 파일)를 사용하며, 기존 파일을 먼저 삭제하는 fallback은 없습니다. 실패하면 메모리 바인딩도 이전 상태를 유지하고 UI에 오류를 표시합니다.
손상 문서는 `controls.json.corrupt-<시간>.bak`으로 옮기고 기본값을 사용합니다. 백업 실패 시 원본을 보존합니다. 이 Windows 동작은 [Godot 4.6의 remove-then-move 구현](https://github.com/godotengine/godot/blob/4.6/drivers/windows/dir_access_windows.cpp)을 그대로 사용하지 않도록 작성했습니다.

## 기본 키
아래 표는 레지스트리에서 생성한 별도 참고입니다. 실행 화면은 현재 바인딩을 사용합니다.

|기능|Primary|Secondary|
|---|---|---|
|가속|W|Up|
|브레이크|S|Down|
|좌 조향|A|Left|
|우 조향|D|Right|
|핸드브레이크|Space|—|
|카메라 변경|C|—|
|후방 보기|V|—|
|안전 복구|Backspace|—|
|자동 변속 보조 / 순차 수동|M|—|
|다운시프트|Q|—|
|업시프트|E|—|
|수동 클러치|Shift|—|
|정차 잠금 P|1|—|
|후진 R|2|—|
|중립 N|3|—|
|전진 D / 1단|4|—|
|시동|Enter|—|
|전조등|F|—|
|상향등|G|—|
|좌 방향지시등|Z|—|
|우 방향지시등|X|—|
|비상등|H|—|
|경적|B|—|
|ABS|F5|—|
|TCS|F6|—|
|ESC|F7|—|
|자동 클러치|F8|—|
|레브매칭|F9|—|
|날씨|T|—|
|시간대|Y|—|
|운전 도움말|F1|—|
|차량 설정|F2|—|
|텔레메트리|F3|—|
|성능 / 엔진 맵|F4|—|
|일시정지|Escape|—|

## 미구현·별도 QA
실제 게임패드 입력은 미구현이며 확장 메타데이터만 있습니다. 기존 메뉴 전체의 완전한 한/영 번역은 미완료입니다. Windows IME 종류, 키보드 레이아웃, modifier 조합, 포커스 이동, 손상 파일과 저장 실패·중단 복구, 재시작 유지, 16:9/16:10/21:9 실기 검증은 별도 QA에서 수행해야 합니다.
