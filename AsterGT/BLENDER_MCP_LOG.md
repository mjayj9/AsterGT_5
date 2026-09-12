# BlenderMCP 작업 기록
실제로 BlenderMCP get_scene_info / execute_blender_code를 호출해 수행했습니다. 구조·수치 기록이며 최종 렌더 품질 검사 결과가 아닙니다.

## 최초 연결
- Blender 5.2.1 LTS. 열린 파일 경로는 빈 문자열(아직 저장하지 않은 기본 장면).
- Scene, METRIC, scale_length 1.0, Collection.
- Cube(MESH, 12 triangles, material slot 1), Camera, Light.
- Cube bbox −1~+1m 각 축. 이 시점에는 차량이 없어 휠 중심/휠베이스/차량 bbox는 해당 없음.
- 기존 장면은 blender/v4/session_before.blend로 별도 보존하고 GT3_V4 장면을 만들었습니다.

## 차량 import 구조
원본을 덮어쓰지 않고 assets/porsche_992_gt3_r.glb를 import했습니다.
전체 목록: blender/v4/import_audit.json (오브젝트별 부모, 위치, bbox, triangle, material).
154 objects / 143 meshes / 475,382 triangles.
Blender bbox: X [−1.030159, 1.018905], Y [−2.426897, 2.340935], Z [−0.669998, 0.583460]m.
길이 약 4.767832m, 폭 약 2.049064m. 휠베이스 약 2.5166m.
Blender 전방 +Y, 상방 +Z / glTF-Godot 전방 −Z, 상방 +Y.
원점은 axle midpoint 근처, 노면보다 약 0.67m 위입니다.

## 실제 수행
1. 차축 안쪽과 오버행을 나눠 길이 4.619m, 휠베이스 2.507m에 맞게 교정. 바퀴 원형 형상을 별도 보존하고 전륜 0.340m/후륜 0.355m 반경 적용.
2. 좌우 휠·디스크·캘리퍼 피벗, Steering, Suspension/SteerAxis 기준점 정리. 하드포인트는 1,265kg·57,000N/m·0.45m 휴지 길이 기준으로 고정하여 설정 불러오기 순서에 의존하지 않게 했습니다.
3. UV 유지, 표면 normal 재계산, tangent export. 도장·카본·유리·타이어 PBR 스칼라 보정. 같은 재질 정의/텍스처/용도의 슬롯을 통합하고 같은 부모·시점 분류·재질 메시를 join.
4. cockpit/exterior 분류 및 중·원거리 LOD에서 내부 디테일 제거. 상세 모델은 조종석용으로 유지.
5. decimation LOD1/2/3, 각 LOD에 DamageFront/Rear/Left/Right morph. 원본과 각 단계의 편집 가능한 장면을 .blend에 저장.
6. 범퍼 앞/뒤·좌/우 측면·core·cabin의 6개 convex proxy를 만들고 Godot 좌표 vertex JSON으로 export. 시각 GLB에는 collider wire mesh를 넣지 않았습니다.
7. 별도 traffic body/cabin/roof, 타이어·휠 피벗·lamp 및 damage shape를 절차형으로 제작. 교통 GLB는 외부 모델/텍스처를 사용하지 않은 새 저폴리 형상입니다.
8. 네 개 Porsche GLB의 scene extras에 원저작자·출처·CC BY-NC-SA·변경 내역을 포함했습니다.

|LOD|삼각형|메시/재질 슬롯|
|---|---:|---:|
|Porsche LOD0|475382|98|
|Porsche LOD1|93903|52|
|Porsche LOD2|29176|52|
|Porsche LOD3|7963|52|
|Traffic LOD0|300|9|
|Traffic LOD1|156|9|

LOD0 실제 보정 bbox X [−1.030159, 1.018905], Y [−2.309500, 2.309500], Z [−0.670000, 0.583460]m.
휠 중심(Godot m):
LF (−0.841, −0.330, −1.2535), RF (+0.841, −0.330, −1.2535),
LR (−0.834, −0.315, +1.2535), RR (+0.834, −0.315, +1.2535).
mount y는 LF/RF 0.065572, LR/RR 0.080572m. 설정/physics rig는 assets/v4/porsche_rig.json에 있습니다.
LOD2/3 decimation은 외곽을 수 mm~약 13mm 이동시킬 수 있으며 collision proxy와 physics wheel dimensions는 변하지 않습니다.
전체 시점별 메시/triangle/material/UV/morph 및 reference 목록은 final_asset_inventory.json에 있습니다. material slot 감소는 구조 기록이며 실제 GPU draw-call 측정값은 아닙니다.

## 산출물
- blender/v4/porsche_gt3_v4.blend: 상세/LOD/compound collider 및 편집 가능한 Porsche 장면.
- blender/v4/traffic_v4.blend: 독립적인 교통 장면 두 개를 library-write로 저장.
- assets/v4/porsche_lod0.glb ~ porsche_lod3.glb, traffic_lod0.glb/traffic_lod1.glb.
- assets/v4/collision_proxies.json, porsche_rig.json.
- 원본 GLB와 기존 .blend는 그대로 유지했습니다.

## 실행 중 오류와 처리
연결 자체는 성공했습니다. 첫 geometry 단계 끝의 JSON 기록에서 Python 인코딩명 utf8-sig가 거부됐고, 다음 호출에서는 실행 namespace가 유지되지 않아 json 이름이 없다는 오류가 있었습니다. 변경된 Blender 장면을 유지한 채 새 호출에서 import와 측정값을 다시 선언하고 utf-8-sig로 기록을 완료했습니다. 동일 geometry 변환을 중복 적용하지 않았습니다.
이후 GLB export와 Godot import를 수행했습니다. 관련 JSON/소스는 저장되어 있습니다.

## 미구현·별도 QA
실제 soft-body/파편 분리, 새 UV atlas 베이킹, 원본 텍스처 전면 재제작, 실차 CAD 수준 하드포인트 측정은 하지 않았습니다. 하드포인트는 시뮬레이션 기준값입니다.
LOD 외관 손실, glass sorting/투명도, 카본·도장 노출, 조종석 시야, normal/tangent 최종 광학 품질, LOD pop 및 GPU draw call·프레임 시간은 별도 QA에서 검증해야 합니다. 최종 렌더 합격이나 모델 성능 합격을 선언하지 않습니다.
