param(
    [string]$PythonVersion = "3.12"
)

$ErrorActionPreference = "Stop"
$RootDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$VenvDir = Join-Path $RootDir ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$EnvFile = Join-Path $RootDir ".env"
$EnvExample = Join-Path $RootDir "windows.env.example"

Set-Location $RootDir

if (-not (Get-Command py -ErrorAction SilentlyContinue) -and -not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python is not installed. Install 64-bit Python $PythonVersion and enable the Python launcher or PATH."
}

if (-not (Test-Path $VenvPython)) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py "-$PythonVersion" -m venv $VenvDir
    } else {
        & python -m venv $VenvDir
    }
}

& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -e ".[dev]"

if (-not (Test-Path $EnvFile)) {
    Copy-Item $EnvExample $EnvFile
    Write-Host "Created .env from windows.env.example"
}

Write-Host "Windows environment is ready."
Write-Host "Virtual environment: $VenvDir"
