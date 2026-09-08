from pathlib import Path
r=Path('outputs/AsterGT')
p=r/'README.md';s=p.read_text(encoding='utf-8');s=s.replace('Graphics에는 카메라별 위치·FOV, 흔들림, 속도 단위, 음소거 항목도 있습니다.','Esc의 Camera & Audio 또는 Controls 하단의 Camera & audio에서 카메라별 위치·FOV, 흔들림, 속도 단위, 음소거를 설정합니다.');p.write_text(s,encoding='utf-8')
(r/'build_tools/run_tests.py').write_text('''"""Run the supplied Godot vehicle tests and retain logs/results."""
from pathlib import Path
import argparse, json, shutil, subprocess
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--godot', default=shutil.which('godot') or shutil.which('godot4'))
p.add_argument('--compare-frame-rates', action='store_true')
a = p.parse_args()
if not a.godot:
    p.error('Pass --godot with a Godot 4.6.3 executable path.')
logs = ROOT / 'tests' / 'logs'
logs.mkdir(exist_ok=True)
def run(name, args):
    with (logs / (name + '.log')).open('w', encoding='utf-8') as out:
        result = subprocess.run([a.godot, '--headless', '--path', str(ROOT), *args],
                                stdout=out, stderr=subprocess.STDOUT, timeout=600)
    if result.returncode:
        raise SystemExit(f'{name} failed ({result.returncode}); see {logs}')
def check(name):
    data = json.loads((ROOT / 'tests' / (name + '_results.json')).read_text(encoding='utf-8-sig'))
    failed = [key for key, passed in data['checks'].items() if not passed]
    print(f"{name}: {len(data['checks']) - len(failed)} / {len(data['checks'])} passed", flush=True)
    if failed:
        raise SystemExit('Failed: ' + ', '.join(failed))
    return data
run('import', ['--editor', '--import', '--quit'])
for name in ['physics', 'dynamics', 'integration']:
    run(name, ['--fixed-fps', '60', '--script', f'res://tests/{name}_test.gd', '--', '--test-profile'])
    check(name)
if a.compare_frame_rates:
    values = []
    for fps in [30, 60, 120]:
        run(f'physics_{fps}', ['--fixed-fps', str(fps), '--script', 'res://tests/physics_test.gd', '--', '--test-profile'])
        result = check('physics')
        shutil.copy2(ROOT / 'tests/physics_results.json', ROOT / f'tests/physics_{fps}.json')
        values.append([result['zero_to_100_s'], result['100_to_0_distance_m']])
    for i in range(2):
        assert max(v[i] for v in values) - min(v[i] for v in values) < 0.01
    print('30 / 60 / 120 render step comparison passed')
print('All tests passed. Logs:', logs)
''',encoding='utf-8')
(r/'docs/IMPLEMENTATION_MATRIX.md').write_text('''# 요구사항·기존 영상 대응표

상태는 코드의 존재뿐 아니라 실제 확인 수준을 구분합니다. 영상 내부 구현은 알 수 없으므로 영상에 보이지 않은 기능의 부재를 단정하지 않습니다.

| 요구 / 영상에서의 관찰 | 이번 구현 | 확인 / 남은 제한 |
|---|---|---|
| 기존 프로젝트 보존 | 현재 작업 폴더에 기존 프로젝트가 없어 새 Godot 프로젝트 생성 | 사용자 MP4 원본은 변경하지 않음 |
| 영상 전체 분석 | 30.10초 전 구간 디코딩, 00–29초 프레임별 검토와 타임스탬프 표 | VIDEO_REVIEW.md. 원본이 854×290이므로 접지·FPS 단정은 피함 |
| 실제 키보드 운전 | RigidBody3D + 네 개 레이 서스펜션, 고정 120Hz | 가속·수동 조작·도로 이탈 가능. 플레이어 PathFollow 없음 |
| 차체 접지·비율 불명확 | 차체 높이·이중 충돌체·분리 휠 축 정렬, 독립 서스펜션 | 출발·차고 복귀 4륜 접지. 전체 도로 32위치 검사; 모든 지형 모서리 보장은 아님 |
| 물리적 그립·미끄러짐 | 휠 회전 동역학, 슬립 비율·각, 마찰 원, 하중 이동, 저항·다운포스 | ABS·TCS·ESC on/off 수치 비교. 실차 데이터 기반 정밀 시뮬레이터는 아님 |
| 급격한 키보드 입력 | 스로틀·제동·조향 보간, 고속 조향 축소 | InputEventKey 파이프라인 검사, 고속 코너 안정성 검사 |
| 영상에서 3단 유지 | 자동 6단 변속·히스테리시스·킥다운·P/R/N/D, 수동 클러치·보조 | 모든 전진 기어 관찰, 업/다운시프트·변속 거부·P/R/N 검사 |
| RPM·속도·휠 표시 일관성 | 강체 속도, 구동륜 기어비 기반 엔진 RPM, 동일 텔레메트리 HUD/오디오 | 연결 상태 RPM 관계 검사. 변속·슬립·클러치 분리 시 차속 환산과 차이 발생 |
| 성능 파라미터 조절 | 리소스, 게임 내 20개 주요 파라미터·6단 비율·구동 방식, 5프리셋 | 저장/로드/범위 제한 검사. 고급 물리 값은 리소스 편집만 지원 |
| 그래픽 설정 | 4프리셋과 개별 스케일·AA·그림자·반사·식생·교통·파티클·후처리·미러 등 | 실제 뷰포트 설정 검사 및 Windows GPU 측정. 프리셋별 FPS가 단조롭게 변하지 않는 관찰도 보고 |
| BlenderMCP 모델링 | 설치된 Blender 5.2.1을 Python API로 실행, 실제 .blend 및 GLB | **부분 충족: BlenderMCP 연결이 없어 해당 MCP는 사용하지 못함** |
| 독창적인 고성능 GT | 신규 차체, 휠·디스크·캘리퍼, 실내·계기·스티어링, 등화·유리·PBR | 스타일화된 절차형 모델. 실사 수준의 디테일·재질 완성도에는 한계 |
| 15km 이상 지도 | 26.04km 연속 순환 도로, 긴 직선·계곡·산길·휴게소·소규모 건물·교량·갤러리 | 거리와 32개 위치 접지 검사. 도시 교차로망·주차 미션·건물 내부는 없음 |
| 단순한 지형·식생 반복 | 3종 수목, 바위, 지형·원경 산, 차선·갓길·가드레일·표지판 | 실제 Blender 수목, MultiMesh·LOD. 배수로/전신주를 포함한 풍부한 세부 소품은 미구현 |
| 날씨·시간 | 낮·해질녘·밤, 맑음·흐림·비, 젖은 도로·강수·안개·등화 | 비·밤 실제 캡처 및 상태 변경 입력 검사. 동적 웅덩이/수막 시뮬레이션은 없음 |
| 교통·상호작용 확인 어려움 | 도로 AI, 교통량 설정, 앞차 감속·추월·반대 차선 확인, 충돌 | 간단한 양방향 교통. 복잡한 상황의 무충돌·도시 행동은 보장하지 않음 |
| 후드·하이라이트가 도로 가림 | 다섯 기본 카메라, 후방 보기, 노출·재질 조절, 위치·FOV·흔들림 설정 | 기본 시점 캡처와 추적 카메라 벽 검사. 극단적인 사용자 오프셋은 관통 가능 |
| 작고 대비 낮은 HUD | 어두운 반투명 패널, 큰 속도계·RPM·기어, 입력·보조·등화·미니맵 | 낮·비오는 밤 캡처. UI는 영어, 한국어 설명서는 별도 제공 |
| 회전 모델에서 끝나는 데모 우려 | 여섯 시작 메뉴, Garage 색상·세팅·추정치, 실제 Drive 연결 | 메뉴와 주행 전환 검사. Garage 최고속도는 기어 제한 이론치 |
| 오디오 스트림 없음 | RPM/부하 엔진 레이어, 슬립·노면·바람·충돌·비·경적·실내 필터 | 합성 WAV와 교체 방법 제공. 실제 엔진 녹음 수준의 음색은 아님 |
| 주행 목표 확인 어려움 | Free Drive / High Speed / Time Trial / Checkpoints, 기록 저장 | 게이트 순서·완료·시간 초과 로직 검사. 시험은 제어된 위치 이동도 사용 |
| 실시간 성능 | 지형 작업 스레드, 타일 유지·삭제, 도로 거리 제한, 식생 인스턴싱·LOD, 교통 풀 | 원시 프레임 시간 기반 측정. 단일 노트북 짧은 구간이고 전 맵 최소 FPS 보증은 아님 |
| 독립 실행·최종 자료 | Windows release EXE, 전체 Godot 프로젝트, export preset, .blend, README, 테스트 JSON·화면 | 네이티브 실행·정상 종료·로그 확인. 다른 OS export는 미제공 |

선택 사항인 엔진 시동 꺼짐, 손상 변형, 멀티플레이, 교통 회피 점수 모드, 세팅별 전체 랩 비교는 구현하지 않았습니다. 핵심 요구의 실행 가능한 게임은 제공하지만 위의 부분 충족 항목을 완성품 수준으로 과장하지 않습니다.
''',encoding='utf-8')
print('Wrote test runner and implementation matrix')
