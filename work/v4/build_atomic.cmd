@echo off
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat" >nul
cl /nologo /O2 /MT /DUNICODE /D_UNICODE /Fe:"C:\Users\admin\Documents\Codex\2026-09-08\fable-5-1-vs-fable-at-4\outputs\AsterGT\runtime_tools\AtomicReplace.exe" /Fo:"C:\Users\admin\Documents\Codex\2026-09-08\fable-5-1-vs-fable-at-4\work\v4\atomic_replace.obj" "C:\Users\admin\Documents\Codex\2026-09-08\fable-5-1-vs-fable-at-4\outputs\AsterGT\build_tools\atomic_replace.c" /link /SUBSYSTEM:CONSOLE
