@echo off
setlocal
set PORT=%PORT%
if "%PORT%"=="" set PORT=8000
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start_windows.ps1" -Port %PORT%
endlocal
