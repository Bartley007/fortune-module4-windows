param(
    [string]$PythonVersion = "3.12",
    [string]$TorchIndexUrl = "https://download.pytorch.org/whl/cu128"
)

$ErrorActionPreference = "Stop"
$RootDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$VenvPython = Join-Path $RootDir ".venv\Scripts\python.exe"

Set-Location $RootDir

if (-not (Test-Path $VenvPython)) {
    & (Join-Path $PSScriptRoot "bootstrap_windows.ps1") -PythonVersion $PythonVersion
}

Write-Host "Installing CUDA-enabled PyTorch from $TorchIndexUrl"
& $VenvPython -m pip install --upgrade torch --index-url $TorchIndexUrl
& $VenvPython -m pip install -e ".[ml]"

Write-Host "GPU Python dependencies are ready."
Write-Host "Set EMBEDDING_PROVIDER=sentence-transformers in .env to use BGE embeddings on CUDA."
