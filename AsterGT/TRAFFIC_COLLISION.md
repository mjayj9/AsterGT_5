# v4 교통 충돌
구현 설명이며 충돌 최종 테스트 결과가 아닙니다.

## 구현
- Far: 충돌체 없는 Node3D, spline 추종, 0.20초 갱신, 156 triangle GLB, 그림자 비활성화.
- Near: GTTrafficBody/RigidBody3D. 활성 반경 max(220m, 상대속도*3초+30m), 해제는 최소 420m 및 활성 반경+120m의 hysteresis. 플레이어/AI가 동일 GodotPhysics3D 솔버를 사용합니다.
- 근거리 전환은 현재 transform·linear velocity·angular velocity를 전달합니다. Far와 Near를 동시에 충돌시키지 않습니다.
- 1,200kg compact / 1,580kg sedan / 2,050kg SUV, 차체 크기 기반 box inertia, 낮은 무게중심, 6개 compound convex 영역, CCD, 120Hz 물리.
- 근거리는 4륜 ray suspension·타이어 횡력·힘 기반 가감속으로 움직입니다. 매 프레임 transform/basis를 덮어쓰거나 delta/dt 속도로 플레이어를 미는 CharacterBody3D 코드는 제거했습니다.
- 접촉 후 최소 5초 Recovery. 최초 1초는 추진/제동 명령을 풀어 반응을 허용합니다. 이후 정차 제어, 2m/s 이하·0.35rad/s 이하·차체 직립 상태를 2초 유지해야 복귀를 판단합니다.
- 경로 복귀는 실제 위치에서 시작하는 힘 제어입니다. 원래 lane 또는 플레이어 앞쪽으로 snap하지 않습니다. 손상/회복 상태는 Far로 해제하지 않습니다.
- 바퀴 회전·전륜 조향·브레이크등·Recovery/Rejoin 비상등을 구현했습니다.

## 접촉·손상·로그
플레이어/AI 공통 GTContactDamage가 실제 collider id, 접촉점, 접촉 상대 속도, 법선, impulse(Ns), shape index, 질량을 기록합니다. 상대속도와 관성을 포함한 유효 접촉 질량으로 충격량 기반 normal energy를 추정합니다.
normal energy estimate = 0.5*(|impulse|/(1+e))² * inverse_effective_mass. 이는 telemetry 추정치이며 솔버 전후 전체 에너지 측정값은 아닙니다.
마찰/restitution/접촉점 회전 효과와 양쪽 운동량 교환은 엔진 솔버가 처리합니다. 로거 또는 손상 계산이 추가 반동을 주지 않습니다. 단순 프레임 속도차를 collision_energy로 사용하는 코드를 제거했습니다.
road/vehicle/barrier 접촉을 구분하고, 도로 하중 접촉을 차체 충돌 손상으로 누적하지 않습니다. contact impulse threshold와 0.25초 debounce를 사용합니다.
front/rear/left/right/body/lights/steering/power 상태를 양쪽에 적용합니다. 출력·조향 저하 및 조명 감쇠, Blender의 DamageFront/Rear/Left/Right shape를 사용합니다.

[Godot RigidBody3D](https://docs.godotengine.org/en/4.6/classes/class_rigidbody3d.html) 및 [PhysicsDirectBodyState3D 접촉 API](https://docs.godotengine.org/en/4.6/classes/class_physicsdirectbodystate3d.html)를 참고했습니다.

## 별도 QA hook
GTCar.telemetry(), GTTrafficBody.telemetry(), GTQA.record(), GTCar.shift_feedback.
GTTraffic.spawn_qa_vehicle(transform, mass_kg, velocity_mps, spin_rad_s, controller=false)는 지정한 동적 차량을 생성합니다. controller=false는 추진/경로추종을 끄며 충돌체를 고정하지 않습니다. 생성된 QA 차량은 Far 전환에서 제외됩니다. 이 hook은 이번 작업에서 실행하지 않았습니다.
로그 활성화는 QA_SETUP.md를 참고하십시오. 고정된 재현 조건은 config/qa_conditions.json에 기록했습니다.

## 기본 추월과 방향지시등
v3의 정방향 교통 기본 추월을 유지했습니다. 전방 느린 차량과 12–38m 간격이면 반대 차선의 Near/Far 차량과 플레이어를 경로 좌표로 확인합니다. 접근 여유가 있을 때 목표 차선을 초당 1.3m로 이동시키고 타이어 힘으로 따라갑니다. 6초 뒤 본선 앞 25m/뒤 48m가 비었을 때 복귀합니다. 이는 목표점 이동이며 차체 transform을 덮어쓰지 않습니다. 차선 변경 중 좌/우 방향지시등, Recovery/Rejoin 중 양쪽 비상등을 표시합니다. 추월 중에는 Far로 전환하지 않습니다. 안전 간격, 신호 주기와 목표 차선 변화율은 traffic_physics.json에 있습니다. 실제 안전성과 차선 복귀 성공률은 별도 QA 대상입니다.

## 미구현·별도 QA
soft-body, 파편 분리, 실제 충돌 하중에 따른 차체/충돌체 형상 영구변형은 미구현입니다. damage morph는 표현용이며 충돌 반응의 대체가 아닙니다. 관성/마찰/손상 임계값은 게임용 가정이며 실차 충돌시험 값이 아닙니다.
파손 AI의 견인·차량 제거/재스폰 및 고급 추월 계획은 미구현입니다. 회복이 불가능하면 동적 정차/잔해 상태로 남습니다. Far 차량은 저비용 갱신이므로 멀리서 업데이트 단계가 보일 수 있습니다.
정면·후면·측면·사선, 정지 차량, 질량 차이, AI-AI, 에너지 증가, 터널링·폭발 회전·지면 관통 및 접촉 법선/에너지 로거의 물리 의미 검증은 모두 별도 QA 대상입니다. CCD 설정이 이런 문제의 부재를 보증하지 않습니다.
