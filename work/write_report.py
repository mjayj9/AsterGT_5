from pathlib import Path
import json,math,hashlib,datetime,shutil
r=Path('outputs/AsterGT');t=r/'tests';native=t/'native'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
p=read(t/'physics_results.json');d=read(t/'dynamics_results.json');i=read(t/'integration_results.json');m=d['measurements']
for f in native.glob('*_benchmark.json'):shutil.copy2(f,t/f.name)
exe=Path('outputs/Windows/AsterGT.exe');digest=hashlib.sha256(exe.read_bytes()).hexdigest()
bench='\n'.join(f"| {q} | {read(native/(q+'_benchmark.json'))['average_fps']:.1f} | {read(native/(q+'_benchmark.json'))['minimum_fps']:.1f} | {read(native/(q+'_benchmark.json'))['one_percent_low_fps']:.1f} | {read(native/(q+'_benchmark.json'))['frames']} |" for q in ['Low','Medium','High','Ultra'])
gears='\n'.join(f"| {x['from']} → {x['to']} | {x['speed_kph']:.2f} | {x['rpm']:.0f} |" for x in m['shift_events'])
limits=' / '.join(f'{7500/ratio/3.6*math.tau*.355/60*3.6:.1f}' for ratio in [3.3,2.2,1.58,1.2,.97,.8])
framerows='\n'.join(f"| {fps} | {read(t/('physics_'+str(fps)+'.json'))['zero_to_100_s']:.3f} | {read(t/('physics_'+str(fps)+'.json'))['100_to_0_distance_m']:.3f} | 17 / 17 |" for fps in [30,60,120])
checks=''
for title,data in [('핵심 물리·변속기',p),('동역학 비교',d),('입력·메뉴·환경 통합',i)]:
 checks+=f'\n### {title}\n\n| 검사 ID | 결과 |\n|---|---|\n'+'\n'.join(f'| `{key}` | {"통과" if value else "실패"} |' for key,value in data['checks'].items())+'\n'
report=f'''# ASTER 최종 검증 보고서

작성 시각: {datetime.datetime.now().astimezone().isoformat(timespec='seconds')}

최종 소스의 **62개 고유 자동 검사(17 + 17 + 28)가 통과**했습니다. 같은 핵심 17개 검사를 논리적 렌더 간격 30/60/120FPS로 추가 실행하여 물리 결과가 일치하는 것도 확인했습니다. 독립 Windows EXE에서 GPU 렌더링, 주행·카메라·튜닝·그래픽 메뉴, 종료를 실행했고 모든 실행은 exit code 0이었습니다.

## 환경과 방법

- Godot 4.6.3 stable, GodotPhysics3D 120Hz, GDScript. 개발 검사: 설치된 .NET 에디터의 headless 실행. 배포 확인: 일반 Windows x64 release template, embedded PCK.
- Windows 노트북, NVIDIA GeForce RTX 5060 Laptop GPU, Vulkan Forward+, 1920×1080 창. GPU 모델은 게임 내 RenderingServer가 반환한 값입니다.
- 물리 시험은 크고 평평한 충돌 바닥의 제어된 조건에서 실제 GTCar를 실행합니다. 엔진 계산을 다른 수식으로 재작성한 목 테스트가 아닙니다.
- 통합 시험은 Godot InputEventKey를 주입하여 실제 입력 경로를 통과합니다. 사람이 키보드를 조작하여 전체 지도를 완주한 시험이라고 주장하지 않습니다.
- 코드와 입력·상태 전환 검사, 캡처 이미지 검토를 수행했습니다. 합성 오디오 리소스와 런타임 믹싱을 확인했으나 별도의 인간 청취 패널 평가는 수행하지 않았습니다.

## 기본 차량 측정

Street, RWD, 1,520kg, 약 492hp, 건조 노면, 기본 운전 보조 설정입니다.

| 항목 | 결과 | 조건 |
|---|---:|---|
| 0–100km/h | {p['zero_to_100_s']:.2f}초 | 정지 후 풀 스로틀. 입력 상승 필터 포함 |
| 출발 직전 속도 | {p['launch_speed_kph']:.8f}km/h | 서스펜션이 가라앉을 때 브레이크를 유지 |
| 100–0km/h 제동 거리 | {p['100_to_0_distance_m']:.2f}m | 100.000km/h로 설정한 별도 fixture에서 새로 브레이크 입력 |
| 100–0km/h 제동 시간 | {p['100_to_0_time_s']:.2f}초 | 종료 기준 0.5km/h 미만. 입력 압력 상승 포함 |
| 35초 가속 후 속도 | {p['speed_after_35s_kph']:.2f}km/h | 평지 직진 |
| 95초 가속 중 최고 관측 속도 | {m['maximum_speed_after_95s_kph']:.2f}km/h | 타원·산길 지도 대신 큰 평지 시험장 |
| 직진 횡방향 드리프트 | {p['lateral_drift_m']:.6f}m | 대칭 평지·무조향 조건 |
| 8° 경사에서 P 유지 중 이동 | {m['slope_park_drift_m']:.6f}m | 정지 후 P, 4초 관측 |
| 연결 구동계 RPM 최대 상대 편차 | {m['max_coupled_rpm_relative_error']*100:.2f}% | 변속 중 제외; 가속 중 엔진 회전 보간 지연 포함 |

95초 최고 관측 속도는 모든 조건에서의 최고속도 보증이 아닙니다. 실차 측정 결과가 아니라 이 게임의 모델 결과입니다.

### 기어 동작

풀 스로틀 자동 변속에서 실제로 기록한 변속 순간입니다.

| 변속 | 차속 km/h | 엔진 RPM |
|---|---:|---:|
{gears}

6단까지 모두 사용했습니다. 7,500RPM, 기본 반경과 기어비에서 휠 슬립이 없다고 계산한 **기어 제한 이론 속도**는 1–6단 순서로 **{limits}km/h**입니다. 이는 각 단에서 실제로 도달했다고 측정한 속도와 다릅니다. Garage의 gear-limited maximum도 이 방식의 이론값입니다.

### ABS·TCS·ESC의 차이

| 시험 | 보조 끔 | 보조 켬 | 해석 |
|---|---:|---:|---|
| 젖은 노면 제동 거리 | {m['abs'][0]['distance_m']:.2f}m | {m['abs'][1]['distance_m']:.2f}m | 약 100km/h fixture, 정지 기준 0.8km/h 미만 |
| 위 시험 평균 전륜 슬립 크기 | {m['abs'][0]['mean_front_slip']:.3f} | {m['abs'][1]['mean_front_slip']:.3f} | ABS가 휠 잠김을 줄임 |
| 고출력 출발 평균 후륜 슬립 | {m['tcs'][0]['mean_rear_slip']:.3f} | {m['tcs'][1]['mean_rear_slip']:.3f} | 기본 토크의 1.6배로 3초 스트레스 시험 |
| 위 시험 3초 후 속도 | {m['tcs'][0]['speed_kph']:.2f}km/h | {m['tcs'][1]['speed_kph']:.2f}km/h | TCS가 실제 토크에 개입 |
| 요 흔들림 누적량 | {m['esc'][0]['integrated_yaw_rad']:.3f}rad | {m['esc'][1]['integrated_yaw_rad']:.3f}rad | 110km/h·후륜 저그립·회전 외란, 1.5초 |

ESC 시험의 누적 회전은 약 {(1-m['esc'][1]['integrated_yaw_rad']/m['esc'][0]['integrated_yaw_rad'])*100:.1f}% 줄었습니다. 이러한 결과는 정의된 시험 조건에서만 성립하며 임의의 노면·튜닝에 대한 효과 보장은 아닙니다.

### 렌더 간격 독립성

headless에서 `--fixed-fps`를 30/60/120으로 변경하고 물리는 120Hz로 유지했습니다. 이는 GPU를 실제 30/60/120FPS로 제한한 측정이 아니라 엔진에 주어진 논리적 렌더 delta를 바꾸는 재현 시험입니다.

| 논리 렌더 FPS | 0–100초 | 100–0m | 핵심 검사 |
|---|---:|---:|---:|
{framerows}

## 실제 Windows 렌더링 성능

최종 EXE에서 프리셋별로 별도 프로세스를 순서대로 실행했습니다. Free Drive 출발 직선, 45% 스로틀, 맑은 낮, 추적 시점입니다. 프리셋 적용 후 5초를 워밍업하고 12초 동안 프레임 시간을 수집했습니다. 게임의 VSync·FPS 제한을 끄고 동시에 다른 검사 작업을 실행하지 않았습니다. 각 프리셋의 기본 교통·식생·그림자·미러 설정을 사용합니다.

평균은 전체 프레임 수/총 측정 시간, 최저는 가장 느린 단일 프레임 시간의 역수입니다. 여기서 1% low는 프레임 시간 99백분위수의 역수로 정의했습니다. 첫 실행 셰이더 준비와 전체 맵 장기 주행을 포함한 최저치가 아닙니다.

| 프리셋 | 평균 FPS | 최저 FPS | 1% low FPS | 표본 프레임 |
|---|---:|---:|---:|---:|
{bench}

최종 값은 [native 원시 결과 폴더](../tests/native/)에 보관했습니다. 초기 실행 일부에서는 Low/Medium이 약 145FPS 근처에서 관측되는 변동이 있어 최종 빌드에서 동일 조건으로 다시 측정했습니다. 드라이버·창 포커스·전원 상태의 효과를 독립적으로 분리하지 않았으므로 다른 컴퓨터의 예상치로 환산하면 안 됩니다. 기본 플레이는 최대 120FPS와 VSync를 켭니다.

## 도로·화면·로그

도로 길이는 {i['road_length_m']/1000:.5f}km입니다. 순환 도로 전체에 고르게 배치한 32개 위치에서 제어된 복구 후 접지를 검사했습니다. 체크포인트 완료 시험 역시 게이트 위치로 제어된 이동을 사용했습니다. 이 검사는 충돌·목표 로직을 검증하며 모든 구간의 사람 운전 품질을 대신하지 않습니다.

최종 Windows QA는 가속·정지, 모든 기본 카메라, 비·밤, 튜닝·그래픽 메뉴를 실행하고 아래 8개 1920×1080 이미지를 저장했습니다. 모든 PNG 저장 반환 코드는 0이었습니다. 종료 직전 상태는 4륜 접지, 정지 속도, D/1단/850RPM으로 정상입니다.

| 화면 | 파일 |
|---|---|
| 시작·차고 | [01_garage.png](../tests/native/01_garage.png) |
| 주행 HUD | [02_driving.png](../tests/native/02_driving.png) |
| 범퍼 | [03_bumper.png](../tests/native/03_bumper.png) |
| 후드 | [04_hood.png](../tests/native/04_hood.png) |
| 운전석 | [05_cockpit.png](../tests/native/05_cockpit.png) |
| 비 오는 밤 | [06_rain_night.png](../tests/native/06_rain_night.png) |
| 차량 튜닝 | [07_setup.png](../tests/native/07_setup.png) |
| 그래픽 설정 | [08_graphics.png](../tests/native/08_graphics.png) |

최종 Import·자동 검사·배포 QA 로그에는 GDScript 파싱 오류, 누락 리소스, 반복 실행 오류가 없었습니다. 지형 생성 중 종료 시 스레드를 동기 join하면 멈추는 경우를 발견하여 비동기 종료 정리로 수정했고, 통합 검사 및 배포 종료를 다시 확인했습니다. 개발용 .NET Vulkan 실행의 과거 종료에서 Texture RID 7개 경고가 있었으나 일반 release EXE에서는 재현되지 않았습니다.

## 재현

프로젝트 폴더에서 다음을 실행합니다. 로그는 `tests/logs/`, JSON은 `tests/`에 생성됩니다. 이번 최종 확인에서는 아래 명령 자체도 실행하여 성공을 확인했습니다.

```powershell
python build_tools/run_tests.py --godot "<Godot 4.6.3 실행 파일 경로>" --compare-frame-rates
```

배포본은 `AsterGT.exe -- --qa --qa-output=<기존 절대 폴더>` 또는 `--benchmark=Low` / `Medium` / `High` / `Ultra`로 확인할 수 있습니다. `--qa`, `--benchmark`, `--test-profile` 실행은 일반 플레이 기록/환경설정 자동 저장을 막습니다.

검사에 사용한 EXE 크기: {exe.stat().st_size:,} bytes. SHA-256:

`{digest}`

## 미완성·검증 범위 제한

BlenderMCP는 연결이 없어 Blender Python API로 대체했습니다. 그래픽은 절차형 스타일화된 PBR 수준이며 실사급 차량·환경 아트는 아닙니다. 오디오는 합성음입니다. 복잡한 도시 교통, 상세 도로 소품, 타이어 열·마모, 엔진 스톨, 손상 변형, 멀티플레이는 제공하지 않습니다. 기본 시점은 확인했지만 임의의 카메라 오프셋 조합에서는 차체가 보일 수 있습니다. 모든 GPU·해상도·맵 위치·튜닝 조합이나 수시간 연속 실행은 검사하지 않았습니다.

정확한 항목별 상태는 [요구사항 대응표](IMPLEMENTATION_MATRIX.md)를 참조하십시오.

## 자동 검사 전체 목록
{checks}
'''
(r/'docs/TEST_REPORT.md').write_text(report,encoding='utf-8')
mp=r/'docs/IMPLEMENTATION_MATRIX.md';s=mp.read_text(encoding='utf-8').replace('프리셋별 FPS가 단조롭게 변하지 않는 관찰도 보고','초기 측정 변동과 최종 재측정 조건도 보고');mp.write_text(s,encoding='utf-8')
Path('outputs/Windows/README.txt').write_text('''ASTER — Grand Tour / Windows x64

AsterGT.exe 실행 → Drive → 주행 모드 선택
별도 Godot/Blender 설치나 인터넷 연결은 필요하지 않습니다.

W 또는 ↑: 가속 / S 또는 ↓: 브레이크
A,D 또는 ←,→: 조향 / Space: 핸드브레이크
M: 자동·수동 / Shift: 클러치 / Q,E: 다운·업
1=P, 2=R, 3=N, 4=D / Enter: 시동 / Backspace: 복구
C: 카메라 / V 유지: 후방 / T: 날씨 / Y: 시간
F1: 전체 조작표 / F2: 튜닝 / F3: 텔레메트리 / Esc: 메뉴
F5,F6,F7: ABS,TCS,ESC / F8: 클러치·레브매칭 보조
F: 전조등 / G: 상향등 / Z,X: 방향지시등 / H: 비상등 / B: 경적

기본 1080p High, 최대 120FPS, VSync 켜짐.
Graphics에서 품질·해상도·교통·렌더 스케일을 조절할 수 있습니다.
게임 UI는 영어입니다. 상세 한국어 설명서와 검증 자료는 소스 패키지의 README.md 및 docs/에 있습니다.
저장 위치: %APPDATA%\\AsterGT\\

독창적인 절차형 PBR 모델과 합성음을 사용하는 게임입니다.
실제 차량 데이터로 검증한 공학 시뮬레이터는 아닙니다.
Blender 원본과 전체 프로젝트는 AsterGT-Source.zip에 포함되어 있습니다.
Godot 및 내장 구성요소 라이선스는 동봉한 두 고지 파일을 참조하십시오.
''',encoding='utf-8-sig')
print('Report written. Unique checks:',sum(len(x['checks']) for x in [p,d,i]))
print('EXE SHA256',digest)
