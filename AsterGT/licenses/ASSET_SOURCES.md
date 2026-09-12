# 에셋 출처와 라이선스

| 구성 | 출처 | 고지 |
|---|---|---|
| 현재 플레이어 Porsche 992 GT3 R 및 원본 텍스처 | 사용자가 제공한 ZIP, 원저작자 MattDoesBlender | **CC BY-NC-SA 4.0**, [상세 출처·수정 고지](PORSCHE_MODEL.md). 비영리 조건 포함 |
| 기존 ASTER 차체·바퀴 | `blender/build_models.py`로 제작 | 이전 버전/대체용 자산으로 보존. 현재 플레이어는 Porsche |
| 수목·바위·지형·도로·건물 | 프로젝트 코드 및 Blender 생성 스크립트 | 외부 환경 팩 없음. 수목은 `blender/refine_environment.py`의 가지·잎 카드 모델로 보완 |
| 아스팔트·지면·normal·잎/침엽 텍스처 | `generate_audio_textures.py`, `generate_surface_details.py` | 절차형 생성, NumPy/Pillow 사용 |
| 엔진 12레이어·시동·스톨·변속 WAV | `generate_engine_audio.py` | 6기통 주기 합성. 실차 녹음 아님 |
| 바람·노면·타이어·비·경적·충돌 WAV | `generate_audio_textures.py` | 합성음, 외부 음원 라이브러리 없음 |
| ASTER 아이콘·UI | 프로젝트 코드 | 자동차에 포함된 실존 로고는 위 모델의 일부 |
| Godot Engine 4.6.3 | [Godot](https://github.com/godotengine/godot) | MIT, `GODOT_LICENSE.txt` |
| Godot 내장 글꼴·압축·렌더·오디오 구성요소 | 공식 release template | `GODOT_THIRD_PARTY.txt` |
| Blender 5.2.1 LTS, Python, NumPy, Pillow | 제작·검증 도구 | 게임 실행 파일에 도구 자체를 포함하지 않음 |
| 사용자 MP4·Reddit 게시물 | 분석 참고 | 기존 원본 영상은 게임에 포함하지 않음 |

Godot의 라이선스가 차량 에셋까지 MIT로 바꾸지는 않습니다. Windows 패키지에도 차량 고지와 Godot 고지를 동봉했습니다.
