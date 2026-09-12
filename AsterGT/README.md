> Pre-QA blocker correction 복제본. 새 실행 파일은 ../Windows-v4-pre-qa/AsterGT-v4-pre-qa.exe입니다. PRE_QA_BLOCKER_REPORT.md의 범위·결과를 먼저 참고하십시오. 아래 기존 v4 설명과 최종 QA 과제는 유지합니다.

# ASTER GT3 v4 — 별도 QA 인계본

v3 전체 복사본에서 기존 프로젝트를 개선한 버전입니다. 최종 주행·충돌·사용성 테스트 및 최종 합격 판정, 새 시연 영상은 수행하지 않았습니다.

- 실행: [Windows v4](../Windows-v4/AsterGT-v4.exe)
- 소스: project.godot (Godot 4.6.3, Forward+, 120Hz physics)
- 저장: %APPDATA%/AsterGT-v4 — v3와 분리
- [키/온보딩](CONTROLS.md), [차량 물리](VEHICLE_PHYSICS.md), [교통 충돌](TRAFFIC_COLLISION.md)
- [BlenderMCP 기록](BLENDER_MCP_LOG.md), [변경·미구현 목록](CHANGELOG_V4.md), [별도 QA 조건](QA_SETUP.md)
- [차량 저작자·비영리·동일조건변경허락](licenses/PORSCHE_MODEL.md), [LICENSE](LICENSE)

High Speed는 300km/h 체험용 별도 공력/기어 프로필입니다. 0–300 30–35초와 최고속도 315–325km/h는 목표이며 실측 확인하지 않았습니다. F4 예상치는 1D 계산입니다.
Authentic는 6단 순차식/RWD이며 자동 변속 보조는 변속 요청만 대신합니다. F8 자동 클러치와 F9 레브매칭을 각각 선택할 수 있습니다.

전체 부모 폴더의 이전 Windows/GT3-v2/tests/영상/보고서는 v3에서 복제한 이력입니다. 이번 실행 파일은 **Windows-v4/AsterGT-v4.exe**입니다.

Windows 빌드:
```powershell
python build_tools/build_windows.py --godot "C:/Tools/Godot/4.6.3-dotnet/Godot_v4.6.3-stable_mono_win64/Godot_v4.6.3-stable_mono_win64_console.exe"
```
export preset은 전체 v4에 보존된 work/tools/windows_release_x86_64.exe(4.6.3)를 참조합니다. AtomicReplace.exe의 소스는 build_tools/atomic_replace.c이고 /MT로 빌드되어 별도 VC 런타임 배포가 필요하지 않습니다.
