param(
    [int]$Port = 8000,
    [string]$HostAddress = "0.0.0.0"
)

$ErrorActionPreference = "Stop"
$RootDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$VenvPython = Join-Path $RootDir ".venv\Scripts\python.exe"

Set-Location $RootDir

if (-not (Test-Path $VenvPython)) {
    & (Join-Path $PSScriptRoot "bootstrap_windows.ps1")
}

$env:PYTHONUTF8 = "1"
Write-Host "Starting Fortune Module 4 at http://127.0.0.1:$Port"
Write-Host "OpenAPI documentation: http://127.0.0.1:$Port/docs"

& $VenvPython -m uvicorn app.main:app --host $HostAddress --port $Port
