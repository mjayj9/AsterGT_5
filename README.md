# ASTER GT — v5

Godot 4.6.3로 만든 Windows용 3D GT 드라이빙 게임의 **v5 (도움말 시스템 · 국소 손상 모델)** 소스입니다.

> **버전 계보** · [AsterGT_3](https://github.com/mjayj9/AsterGT_3) → [AsterGT_4](https://github.com/mjayj9/AsterGT_4) → **v5**

---

## 프로젝트 소개

**ASTER — Grand Tour**는 키보드로 직접 운전하는 Windows용 3D GT 드라이빙 게임입니다.
Porsche 992 GT3 R 모델, 26.04 km 순환 도로, 4개 주행 모드, 자동·수동 6단 변속기,
차량 튜닝, 날씨·시간 변경을 제공합니다.

엔진은 **Godot 4.6.3** (Vulkan Forward+, 120 Hz 물리)이며 전체 게임 로직은 GDScript입니다.

---

## v5에서 한 일

Pre-QA 후보를 보존한 채 별도 작업 사본에서 두 가지 기능을 구현했습니다.
전체 결과는 [`reports/V5_BUILD_REPORT.md`](reports/V5_BUILD_REPORT.md)에 있습니다.

### 1. 도움말 · 현지화 시스템

- 여섯 분류 **24개 목적별 도움말 항목**. P/R/N/D와 전진 1~6단을 각각 설명
- 초보 모드는 작은 도움 버튼만 노출, 일반 모드는 자동 안내를 숨김
- <kbd>F1</kbd>은 두 모드에서 동일한 도움말을 열고 주행을 일시정지
- 변속기 설명이 실제 정차·브레이크·클러치·오버레브 검사와 현재 키 바인딩을 반영
- 각 단의 회전 제한 속도를 현재 차량 설정에서 계산
- 홈·일시정지·도움말·성능 화면 한국어/영어 전환 (`scripts/localization.gd`)

### 2. 국소 손상 모델

부위 전체 블렌드셰이프를 제거하고 **충돌점 기반 정점 변형**으로 교체했습니다.

| 항목 | 값 |
|---|---|
| 손상 반경 | 최대 0.55 m |
| 단일 충격 깊이 | 최대 0.16 m |
| 중첩 변위 | 최대 0.24 m |
| 차량당 독립 손상 지점 | 최대 16개 |

- 긁힘은 접선 방향·속도, 칠 까짐·찌그러짐·범퍼 크랙은 충격 에너지로 분리
- **원본 메시를 수정하지 않고** 외장 메시 사본의 정점만 변형. 반대편 표면에는 미적용
- 수리 시 원본 메시·재질 덮개를 정확히 복원하고 출력/조향 저하를 초기화
- 표면 자국은 `shaders/local_damage.gdshader`로 표현

게임용 근사 모델이며 부품 분리·파편 시뮬레이션이나 재료 파괴 해석은 포함하지 않습니다.

### 검증 결과

| 검사 | 결과 |
|---|---|
| 왼쪽 뒤 충격 국소성 | 정점 2,963개 변형, 반경 밖 0개, 반대편 0개, 최대 0.137 m |
| 원형 복구 | 원본 메시 리소스·덮개 복원, 손상 지점 전체 제거 |
| 30 km/h 후방 추돌 / 대각선 | 양쪽 손상·회복, 오류 없음 |
| 100 km/h 대각선 · AI 대 AI 정면 | 양쪽 손상·회복, 오류 없음 |
| 배포 EXE headless / Vulkan | 두 경로 모두 종료 코드 0 |
| 기존 Pre-QA 후보 보존 | 5,060개 파일 변경 0 |

---

## 저장소 구성

```
AsterGT/              Godot 4.6.3 프로젝트
├── scripts/          GDScript 로직 — 차량 물리, 손상, 현지화, HUD, 교통, QA 로깅
├── shaders/          local_damage.gdshader — 긁힘·칠 까짐·크랙 표면 표현
├── scenes/           main.tscn — 시작 씬
├── config/           키 바인딩·도움말·경험 설정·교통 물리 JSON
├── assets/           GLB 메시, 텍스처, 오디오 (v4 LOD 세트 포함)
├── blender/          .blend 원본 및 모델 생성 스크립트
├── build_tools/      Windows 패키징·에셋 생성·테스트 러너
├── runtime_tools/    AtomicReplace.exe — 무중단 파일 교체
├── tests/            물리·동역학·통합·Pre-QA·v5 회귀 스위트와 캡처
├── docs/             모델 분석·물리 문서·검증 보고서
└── licenses/         차량 에셋 및 Godot 제3자 고지

work/                 제작·검증에 사용한 파이썬 스크립트, 로그, Pre-QA 산출물
reports/              버전별 인계 보고서 (v4 · Pre-QA · v5)
```

---

## 실행 방법

Godot **4.6.3** 에디터에서 `AsterGT/project.godot`을 Import 한 뒤 <kbd>F5</kbd>로 실행합니다.
시작 씬은 `AsterGT/scenes/main.tscn`입니다.

```bash
# Windows 빌드
python AsterGT/build_tools/build_windows.py --godot <Godot_v4.6.3_콘솔_실행파일_경로>
```

`.godot/` 임포트 캐시는 저장소에 포함하지 않았습니다. 최초 Import 시 자동으로 재생성됩니다.
Blender 설치 없이도 실행됩니다 — 실행용 GLB가 `AsterGT/assets/`에 포함되어 있습니다.

### 기본 조작

| 키 | 기능 |
|---|---|
| <kbd>W</kbd> / <kbd>S</kbd> | 가속 / 제동 |
| <kbd>A</kbd> / <kbd>D</kbd> | 좌 / 우 조향 |
| <kbd>Space</kbd> | 핸드브레이크 |
| <kbd>Q</kbd> / <kbd>E</kbd> | 기어 다운 / 업 |
| <kbd>M</kbd> | 자동 / 수동 변속 전환 |
| <kbd>Enter</kbd> | 시동 On / Off |
| <kbd>C</kbd> | 카메라 전환 |
| <kbd>T</kbd> / <kbd>Y</kbd> | 날씨 / 시간대 순환 |
| <kbd>F1</kbd> | 도움말 |
| <kbd>Esc</kbd> | 일시정지·설정 |

전체 키 배치는 `AsterGT/README.md`를 참고하십시오.

---

## 라이선스

- 프로젝트 코드: `AsterGT/LICENSE`
- **차량 에셋: MattDoesBlender / CC BY-NC-SA 4.0** — 비영리·동일조건변경허락 조건이 적용됩니다.
  전체 고지는 [`AsterGT/licenses/PORSCHE_MODEL.md`](AsterGT/licenses/PORSCHE_MODEL.md)를 확인하십시오.
- Godot 엔진 및 제3자 고지: `AsterGT/licenses/`

---

## 참고

- 저장소에는 **소스와 에셋**만 포함했습니다. 빌드 산출물(`Windows-v5/` 실행 파일,
  `.zip` 패키지, 시연 영상 `.mp4`), Godot export template 및 내려받은 도구,
  중간 모델링 산출물(`gt3_v2`, `porsche_upgrade`)은 용량 문제로 제외했습니다.
- 커밋 날짜는 원본 파일의 실제 수정 시각을 사용해 작업 순서를 반영했습니다.
- v5는 기존 Pre-QA 후보에 대한 **GO 판정을 의미하지 않습니다.**
