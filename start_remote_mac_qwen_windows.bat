
@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start_mac_qwen_tunnel_windows.ps1" %*
endlocal
