# ASTER GT Porsche 보완판 검증 보고서

기록 시각: 2026-09-09T00:10:20+09:00

최종 소스의 **97개 검사 조건이 통과**했습니다. 구성은 84개 엔진 검사, 두 연속 도로 시나리오의 10개 조건, 오디오 자산 3개 조건입니다. 같은 기본 검사를 30/60/120의 논리 렌더 FPS에서 반복한 수는 이 97개에 중복 합산하지 않았습니다. 별도로 원본·수정 GLB 바이너리 보존과 네 피벗 구조도 확인했습니다.

## 환경과 방법

- Windows x64 / NVIDIA GeForce RTX 5060 Laptop GPU / Vulkan Forward+.
- Godot 4.6.3 stable, GodotPhysics3D 고정 120Hz, GDScript. 소스 검사에는 .NET 에디터, 배포에는 일반 Windows release export template을 사용했습니다.
- 1,520kg, 약 492hp, 570Nm, RWD Street 게임 세팅. 실제 Porsche 992 GT3 R의 공인 성능이나 공학 시험 결과가 아닙니다.
- 물리 검사는 실제 GTCar와 평지·경사 충돌체를 실행합니다. 기본 제동 비교는 새 타이어·70°C를 기준으로 초기화하고 앞/뒤 바퀴의 실제 반경에 맞춰 초기 각속도를 설정했습니다.
- 입력 통합 검사는 실제 InputEventKey 경로를 사용합니다. 전체 도로 검사는 자동 운전기가 같은 GTCar에 throttle/brake/steering 입력을 전달합니다. 사람의 전 구간 키보드 완주 시험은 아닙니다.
- 네이티브 QA는 8개 PNG를 저장하고 화면을 검토했습니다. 오디오 수치와 실제 게임 녹화를 확인했으나 인간 청취 패널의 주관 평가를 수행하지 않았습니다.

## 검사 묶음

| 묶음 | 통과 | 원시 결과 |
|---|---:|---|
| 차량 기본 | 17 / 17 | [physics_results.json](../tests/physics_results.json) |
| 동역학 비교 | 17 / 17 | [dynamics_results.json](../tests/dynamics_results.json) |
| 입력·메뉴·환경 | 28 / 28 | [integration_results.json](../tests/integration_results.json) |
| Porsche·타이어·스톨·카메라 | 22 / 22 | [upgrade_results.json](../tests/upgrade_results.json) |
| 전체 도로 건조 | 5 / 5 | [continuous_route_results.json](../tests/continuous_route_results.json) |
| 전체 도로 우천 | 5 / 5 | [continuous_route_wet_results.json](../tests/continuous_route_wet_results.json) |
| 합성 오디오 자산 | 3 / 3 | [audio_asset_results.json](../tests/audio_asset_results.json) |

추가 자산 검증: [model_asset_results.json](../tests/model_asset_results.json). 원본과 수정 GLB의 BIN 청크가 byte-for-byte 동일하며 네 개 Wheel 피벗이 있습니다. 메시·이미지는 보존하고 장면 계층·변환·재질 JSON을 조정했습니다.

## 실제 차량 동역학

| 항목 | 측정 | 조건 |
|---|---:|---|
| 0–100km/h | 4.375초 | 정지 후 풀 스로틀, 입력 상승 필터 포함 |
| 출발 직전 속도 | 0.00002116km/h | 안정화 중 브레이크 유지 |
| 100–0km/h 거리 | 40.654m | 정확히 100km/h로 초기화한 새 제동 fixture |
| 100–0km/h 시간 | 2.892초 | 종료 기준 0.5km/h 미만 |
| 35초 가속 후 속도 | 297.08km/h | 평지 직진 |
| 95초 중 최고 관측 속도 | 320.52km/h | 큰 평지 시험장, 맵 최고속도 보장 아님 |
| 직진 횡방향 편향 | 0.000000m | 무조향·대칭 평지 |
| 8° 경사 P 유지 이동 | 0.000000m | 정지 후 4초 |
| 연결 구동계 RPM 최대 상대 편차 | 4.61% | 변속 구간 제외, RPM 보간 지연 포함 |

원본 차량의 좌우 후륜 축 위치가 미세하게 달라 초기 교체 시 직진 편향이 생겼습니다. 물리 마운트를 축별 좌우 평균으로 정렬하고 다시 시험한 결과 위의 0.0m를 얻었습니다. 차체 메시를 변형해 해결한 것이 아닙니다.

| 자동 변속 | 차속 km/h | 엔진 RPM |
|---|---:|---:|
| 1 → 2 | 63.29 | 6910 |
| 2 → 3 | 104.09 | 6900 |
| 3 → 4 | 150.27 | 6900 |
| 4 → 5 | 201.34 | 6900 |
| 5 → 6 | 251.69 | 6900 |

전진 6단을 모두 관측했습니다. Garage의 gear-limited maximum은 휠 반경·최대 RPM·기어비로 계산한 이론값이며 측정 최고속도와 다릅니다.

| 비교 | 보조 끔 | 보조 켬 |
|---|---:|---:|
| 젖은 노면 제동 거리 | 69.84m | 55.89m |
| 위 시험 평균 전륜 슬립 크기 | 0.948 | 0.182 |
| 1.6배 토크 출발 평균 후륜 슬립 | 3.077 | 0.420 |
| 위 시험 3초 후 속도 | 44.48km/h | 55.35km/h |
| 회전 외란의 요 누적량 | 2.587rad | 2.000rad |

ABS fixture는 약 100km/h에서 0.8km/h 미만까지, TCS는 고출력 출발 3초, ESC는 110km/h·낮은 후륜 그립·회전 외란 1.5초입니다. 서로 다른 조건을 같은 제동 수치로 혼합하지 않았습니다.

## 새 차량·타이어·스톨·카메라

- 네 독립 바퀴축, 구동 각속도에 따른 회전, 전륜 조향/후륜 무조향, 캘리퍼 회전 분리 통과.
- 타이어 시각 중심과 평지 접점의 오차: 0.00000255m. 이는 시험 평면에서 피벗과 반경의 정렬 수치이며 모든 차체 메시의 지면 관통 검사와 동일하지 않습니다.
- 타이어 70°C / 20°C 제동: **38.54m / 42.42m**. 별도 fixture의 100km/h·3단·0.8km/h 종료 조건으로, 위 기본 제동 시험과 초기화·종료 기준이 다릅니다.
- TCS를 끄고 1.8배 토크·젖은 노면에서 7.5초 슬립 시험: 최고 105.33°C, 최대 마모 1.814%. 정비 버튼의 온도·마모 초기화 통과.
- 완전 수동 6단 정지에서 스톨, 클러치 미분리 재시동 거절, 클러치 분리 재시동·아이들 복귀 통과.
- 다섯 카메라 모드에 범위 밖 위치와 NaN FOV를 넣은 제한 검사 통과. 0.16m 구체의 벽 여유, 보간 후 벽 관통 방지, 운전석 선스트립 숨김·복구 검사 통과.

카메라 범위 검사는 대표 경계 입력이며 허용 범위 내 모든 좌표·지도 지형 조합을 전수 조사한 것이 아닙니다.

## 26km 전체 도로 연속 주행

실제 도로 길이 **26.03761km**. 출발 배치 후 위치를 직접 설정하거나 복구하지 않고 조작 입력만으로 한 바퀴를 돌았습니다. 교통 차량은 없는 조건이며 도로·지형 스트리밍과 실제 차량 물리는 동작합니다. 속도 목표는 최대 약 97km/h이고 곡률에 따라 감속합니다.

| 조건 | 시뮬레이션 시간 | 차량 누적 거리 | 경로 진행량 | 순간이동 | 감지 충돌 | 최대 목표 차선 편차 |
|---|---:|---:|---:|---:|---:|---:|
| 맑은 낮 | 986.325 | 26.02711km | 26.04161km | 0 | 0 | 3.386m |
| 비 오는 밤 | 992.050 | 26.02932km | 26.04161km | 0 | 0 | 3.424m |

두 조건 모두 2개 미만의 바퀴만 접지한 시간이 연속으로 발생하지 않았습니다(기록된 longest_airborne_s=0). 커브를 자르는 경로 때문에 차량 누적 거리와 도로 중심선 길이는 조금 다릅니다. 최대 차선 편차가 약 3.4m이므로 **항상 목표 차선 중앙을 지켰다는 결과는 아닙니다**. 전체 맵의 연결·안정 접지·연속 이동을 확인한 시험이며 교통 상황 안전성·인간 운전 난이도·모든 튜닝의 완주를 보장하지 않습니다. 이전의 32개 위치 접지 시험도 32/32 통과했습니다.

## 렌더 간격 독립성

headless의 논리 렌더 delta를 `--fixed-fps 30/60/120`으로 바꾸고 물리는 120Hz로 유지했습니다. GPU 실제 프레임 제한 시험과는 구분합니다.

| 논리 렌더 FPS | 0–100초 | 100–0m | 검사 |
|---|---:|---:|---:|
| 30 | 4.375 | 40.654 | 17 / 17 |
| 60 | 4.375 | 40.654 | 17 / 17 |
| 120 | 4.375 | 40.654 | 17 / 17 |

## 최종 Windows 실행 파일 성능

새 모델·환경·오디오를 포함한 최종 일반 release EXE에서 프리셋마다 별도 프로세스를 순서대로 실행했습니다. 1920×1080, Free Drive 출발 직선, 맑은 낮, 추적 카메라, 45% 스로틀, 프리셋의 기본 교통·식생·미러를 사용했습니다. VSync/프레임 제한을 끄고 5초 워밍업 후 12초를 측정했습니다. 다른 GPU/물리 테스트는 동시에 실행하지 않았습니다.

평균 FPS는 프레임 수/총 시간, 최저는 가장 느린 단일 프레임의 역수, 1% low는 프레임 시간 99백분위수의 역수입니다. Ultra는 115% 렌더 스케일, 4x MSAA, SSR 96 steps, 교통 24대 목표를 사용합니다.

| 프리셋 | 평균 FPS | 최저 FPS | 1% low FPS | 표본 프레임 |
|---|---:|---:|---:|---:|
| Low | 604.5 | 235.6 | 433.1 | 7,255 |
| Medium | 487.2 | 85.8 | 358.7 | 5,851 |
| High | 231.0 | 105.2 | 186.6 | 2,773 |
| Ultra | 140.4 | 63.9 | 120.6 | 1,685 |

[네이티브 원시 결과](../tests/native/). Medium의 단일 최저치 85.8FPS처럼 일시적인 긴 프레임도 그대로 보고했습니다. 결과는 이 노트북의 짧은 구간이며 전체 지도·다른 GPU·발열 상태의 최소 FPS 보장이 아닙니다. 기본 플레이는 최대 120FPS 및 VSync를 켭니다.

## 화면·오디오·종료 로그

최종 EXE의 [차고](../tests/native/01_garage.png), [주행](../tests/native/02_driving.png), [범퍼](../tests/native/03_bumper.png), [후드](../tests/native/04_hood.png), [운전석](../tests/native/05_cockpit.png), [비 오는 밤](../tests/native/06_rain_night.png), [튜닝](../tests/native/07_setup.png), [그래픽](../tests/native/08_graphics.png)을 검토했습니다. 네이티브 QA와 네 번의 벤치마크는 모두 exit 0으로 종료했습니다.

별도 배포한 **AsterGT-Porsche-Preview.mp4**는 Godot MovieMaker로 기록한 실제 게임 장면입니다. 18.10초, 1280×720, 30FPS, H.264 영상과 48kHz stereo AAC 소리를 포함합니다. 차고 → 바퀴가 보이는 외부 주행 → 추적 → 운전석 → 제동 장면입니다. 이 영상은 전체 26km 주행 기록이나 실시간 성능 측정 영상이 아닙니다. 실제 게임 오디오의 피크는 -10.5dB, 평균은 -22.3dB였습니다. [오디오·영상 검사 로그](../tests/native/video_probe.log)를 함께 보관했습니다.

기존 7 Texture RID 경고는 [Godot #122498의 반사 아틀라스 정리 문제](https://github.com/godotengine/godot/issues/122498)와 일치했습니다. ReflectionProbe를 제거하고 하늘/SSR로 바꾼 후 [.NET Vulkan 에디터 로그](../tests/native/editor_final_qa.log)와 [최종 일반 EXE 로그](../tests/native/release_verified.log)에서 재발하지 않았습니다. 엔진 자체를 패치한 것이 아니라 해당 리소스 사용을 피한 수정입니다. release 빌드는 일부 디버그 경고를 생략할 수 있어 에디터 로그도 확인했습니다.

## 재현

프로젝트 폴더에서:

```powershell
python build_tools/run_tests.py --godot "C:/path/Godot.exe" --compare-frame-rates --full-route
python build_tools/generate_engine_audio.py
python build_tools/build_windows.py --godot "C:/path/Godot.exe"
```

네이티브 QA 출력 폴더를 먼저 만든 뒤:

```powershell
./AsterGT.exe -- --qa --qa-output=C:/Temp/AsterQA
./AsterGT.exe -- --benchmark=High --qa-output=C:/Temp/AsterQA
```

모델 변환 재현은 [모델 분석](MODEL_ANALYSIS.md)과 README의 `adapt_porsche.py --source` 명령을 참조하십시오. 전체 도로 원시 JSON에는 500m 간격 위치·속도·기어·RPM·접지 표본이 있습니다. headless 각 실행 로그는 [tests/logs](../tests/logs/)에 보존했습니다.

## 남아 있는 범위

실차 성능/타이어 시험 기반의 정밀 시뮬레이터, 실제 Porsche 엔진 녹음, 전 맵 실사급 환경 아트, 인간 키보드 전 구간 완주는 제공하지 않았습니다. 사용자가 주행 품질과 검증을 선택했으므로 보행자·도시 교차로·멀티플레이·손상 변형은 추가하지 않았습니다. 기존 AI의 모든 상황 무충돌도 검증하지 않았습니다.

## 검사 ID

### 차량 기본

| 검사 | 결과 |
|---|---|
| `automatic_downshift` | 통과 |
| `automatic_upshift` | 통과 |
| `brake_stable` | 통과 |
| `clutched_shift_accepts` | 통과 |
| `config_clamped` | 통과 |
| `config_roundtrip` | 통과 |
| `finite_state` | 통과 |
| `four_grounded` | 통과 |
| `manual_holds_second` | 통과 |
| `park_at_speed_refused` | 통과 |
| `park_holds` | 통과 |
| `park_stopped` | 통과 |
| `reverse_moves_backward` | 통과 |
| `reverse_selected` | 통과 |
| `standing_start` | 통과 |
| `straight_stable` | 통과 |
| `unclutched_shift_refused` | 통과 |

### 동역학 비교

| 검사 | 결과 |
|---|---|
| `ABS_reduces_wheel_lock` | 통과 |
| `ESC_reduces_yaw_disturbance` | 통과 |
| `GT_reaches_250kph` | 통과 |
| `TCS_reduces_launch_slip` | 통과 |
| `all_six_gears_used` | 통과 |
| `collision_does_not_tunnel` | 통과 |
| `collision_reduces_speed` | 통과 |
| `full_manual_low_rpm_lug` | 통과 |
| `handbrake_locks_rear` | 통과 |
| `high_speed_corner_stays_upright` | 통과 |
| `high_speed_steering_reduced` | 통과 |
| `neutral_disconnects_drive` | 통과 |
| `neutral_rolls_downhill` | 통과 |
| `park_holds_on_8_degree_slope` | 통과 |
| `rpm_matches_driven_wheels` | 통과 |
| `slope_four_wheel_contact` | 통과 |
| `uphill_launch` | 통과 |

### 입력·메뉴·환경

| 검사 | 결과 |
|---|---|
| `M_switches_to_manual` | 통과 |
| `all_five_cameras_cycle` | 통과 |
| `assist_keys_toggle` | 통과 |
| `automatic_shifts` | 통과 |
| `chase_camera_stops_before_wall` | 통과 |
| `checkpoint_timeout` | 통과 |
| `clutched_keyboard_shift_accepts` | 통과 |
| `duplicate_binding_refused` | 통과 |
| `garage_return_grounded` | 통과 |
| `graphics_presets_change_load` | 통과 |
| `keyboard_accelerates` | 통과 |
| `keyboard_recovery` | 통과 |
| `main_menu_has_six_actions` | 통과 |
| `malformed_settings_safe` | 통과 |
| `manual_no_uncommanded_shift` | 통과 |
| `ordered_checkpoint_finish` | 통과 |
| `pause_stops_physics` | 통과 |
| `paused_position_unchanged` | 통과 |
| `rain_night_keys` | 통과 |
| `rebind_works` | 통과 |
| `render_scale_applied` | 통과 |
| `resume_restores_controls` | 통과 |
| `road_at_least_15km` | 통과 |
| `road_collision_32_locations` | 통과 |
| `spawn_four_contacts` | 통과 |
| `throttle_is_filtered` | 통과 |
| `unclutched_keyboard_shift_refused` | 통과 |
| `vehicle_function_keys` | 통과 |

### Porsche·타이어·스톨·카메라

| 검사 | 결과 |
|---|---|
| `calipers_do_not_spin` | 통과 |
| `camera_limits_0` | 통과 |
| `camera_limits_1` | 통과 |
| `camera_limits_2` | 통과 |
| `camera_limits_3` | 통과 |
| `camera_limits_4` | 통과 |
| `clutched_restart_works` | 통과 |
| `cockpit_visor_visibility_restores` | 통과 |
| `cold_tires_change_braking` | 통과 |
| `four_separate_wheel_pivots` | 통과 |
| `front_wheels_steer` | 통과 |
| `full_manual_engine_stalls` | 통과 |
| `porsche_model_loaded` | 통과 |
| `restart_requires_clutch` | 통과 |
| `restarted_engine_idles` | 통과 |
| `slip_heats_tires` | 통과 |
| `slip_wears_tires` | 통과 |
| `smoothed_camera_cannot_cross_wall` | 통과 |
| `sphere_camera_wall_clearance` | 통과 |
| `tire_service_restores` | 통과 |
| `visual_tire_ground_alignment` | 통과 |
| `wheels_roll_from_angular_velocity` | 통과 |

### 전체 도로 건조

| 검사 | 결과 |
|---|---|
| `actual_distance_covers_loop` | 통과 |
| `finite_state` | 통과 |
| `full_26km_loop` | 통과 |
| `no_prolonged_airborne` | 통과 |
| `no_teleports` | 통과 |

### 전체 도로 우천

| 검사 | 결과 |
|---|---|
| `actual_distance_covers_loop` | 통과 |
| `finite_state` | 통과 |
| `full_26km_loop` | 통과 |
| `no_prolonged_airborne` | 통과 |
| `no_teleports` | 통과 |

### 합성 오디오 자산

| 검사 | 결과 |
|---|---|
| `no_clipping` | 통과 |
| `finite_rms` | 통과 |
| `all_12_engine_layers` | 통과 |
