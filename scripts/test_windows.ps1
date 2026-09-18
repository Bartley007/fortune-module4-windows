$ErrorActionPreference = "Stop"
$RootDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$VenvScripts = Join-Path $RootDir ".venv\Scripts"

Set-Location $RootDir

if (-not (Test-Path (Join-Path $VenvScripts "pytest.exe"))) {
    & (Join-Path $PSScriptRoot "bootstrap_windows.ps1")
}

& (Join-Path $VenvScripts "ruff.exe") check app alembic scripts tests
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& (Join-Path $VenvScripts "mypy.exe") app
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& (Join-Path $VenvScripts "pytest.exe") -q
exit $LASTEXITCODE
