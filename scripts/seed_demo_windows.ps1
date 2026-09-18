$ErrorActionPreference = "Stop"
$RootDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$VenvPython = Join-Path $RootDir ".venv\Scripts\python.exe"

Set-Location $RootDir

if (-not (Test-Path $VenvPython)) {
    & (Join-Path $PSScriptRoot "bootstrap_windows.ps1")
}

$env:PYTHONUTF8 = "1"
& $VenvPython scripts\seed_demo.py
