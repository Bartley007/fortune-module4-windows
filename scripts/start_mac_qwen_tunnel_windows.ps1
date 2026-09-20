param(
    [string]$SshTarget = $env:MAC_QWEN_SSH_TARGET,
    [string]$MacHost = $env:MAC_QWEN_HOST,
    [string]$MacUser = $env:MAC_QWEN_USER,
    [int]$LocalPort = 11434,
    [int]$RemotePort = 11434,
    [string]$Model = $(if ($env:MAC_QWEN_MODEL) { $env:MAC_QWEN_MODEL } else { "qwen3.8:27b-q8_0" }),
    [switch]$CheckOnly,
    [switch]$Foreground
)

$ErrorActionPreference = "Stop"

if (-not $SshTarget) {
    if ($MacHost -and $MacUser) {
        $SshTarget = "$MacUser@$MacHost"
    } elseif ($MacHost) {
        $SshTarget = $MacHost
    }
}

function Test-LocalModel {
    try {
        $body = Invoke-RestMethod -Uri "http://127.0.0.1:$LocalPort/v1/models" -TimeoutSec 3
        return [bool]($body.data | Where-Object { $_.id -eq $Model })
    } catch {
        return $false
    }
}

if (Test-LocalModel) {
    Write-Host "Remote Qwen tunnel is ready on 127.0.0.1:$LocalPort."
    exit 0
}

if (-not $SshTarget) {
    throw "Set MAC_QWEN_SSH_TARGET or pass -SshTarget."
}

if ($CheckOnly) {
    $remoteJson = ssh -o BatchMode=yes -o ConnectTimeout=10 $SshTarget "curl -fsS http://127.0.0.1:$RemotePort/v1/models"
    if ($LASTEXITCODE -ne 0) {
        throw "SSH target is not reachable or Mac Ollama is not running."
    }
    if ($remoteJson -notmatch [regex]::Escape($Model)) {
        throw "Mac Ollama is reachable but model '$Model' was not found."
    }
    Write-Host "Mac Ollama is reachable and model '$Model' is available."
    exit 0
}

$listener = Get-NetTCPConnection -LocalPort $LocalPort -State Listen -ErrorAction SilentlyContinue
if ($listener) {
    throw "Local port $LocalPort is already in use but does not expose model '$Model'."
}

$sshArgs = @(
    "-o", "BatchMode=yes",
    "-o", "ConnectTimeout=10",
    "-o", "ServerAliveInterval=30",
    "-o", "ServerAliveCountMax=3",
    "-N",
    "-L", "${LocalPort}:127.0.0.1:${RemotePort}",
    $SshTarget
)

if ($Foreground) {
    & ssh @sshArgs
    exit $LASTEXITCODE
}

$process = Start-Process -FilePath "ssh" -ArgumentList $sshArgs -WindowStyle Hidden -PassThru
for ($index = 0; $index -lt 30; $index++) {
    Start-Sleep -Seconds 1
    if (Test-LocalModel) {
        Write-Host "Remote Qwen tunnel ready on 127.0.0.1:$LocalPort (ssh pid $($process.Id))."
        exit 0
    }
}

throw "Tunnel did not become ready. Check SSH connectivity and Mac Ollama."