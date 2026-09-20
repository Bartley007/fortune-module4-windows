$ErrorActionPreference = "Stop"
$RootDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Python = Join-Path $RootDir ".venv\Scripts\python.exe"
Set-Location $RootDir
if (-not (Test-Path $Python)) {
    throw "Virtual environment not found. Run setup_windows.bat first."
}
& $Python scripts\verify_end_to_end.py
exit $LASTEXITCODE