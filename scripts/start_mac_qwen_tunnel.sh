#!/usr/bin/env bash
set -euo pipefail

LOCAL_PORT="${MAC_QWEN_LOCAL_PORT:-11434}"
REMOTE_PORT="${MAC_QWEN_REMOTE_PORT:-11434}"
MODEL="${MAC_QWEN_MODEL:-qwen3.8:27b-q8_0}"
SSH_TARGET="${MAC_QWEN_SSH_TARGET:-}"
BACKGROUND=0
CHECK_ONLY=0

usage() {
  printf '%s\n' "Required: MAC_QWEN_SSH_TARGET=user@host"
  printf '%s\n' "Usage: scripts/start_mac_qwen_tunnel.sh [--background|--check-only]"
}

while (($#)); do
  case "$1" in
    --background) BACKGROUND=1; shift ;;
    --check-only) CHECK_ONLY=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'Unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "${SSH_TARGET}" ]]; then
  printf 'MAC_QWEN_SSH_TARGET is required.\n' >&2
  exit 2
fi

local_ready() {
  curl -fsS "http://127.0.0.1:${LOCAL_PORT}/v1/models" 2>/dev/null | grep -Fq "${MODEL}"
}

if local_ready; then
  printf 'Remote Qwen tunnel is ready on 127.0.0.1:%s.\n' "${LOCAL_PORT}"
  exit 0
fi

if (( CHECK_ONLY )); then
  remote_json="$(ssh -o BatchMode=yes -o ConnectTimeout=10 "${SSH_TARGET}" "curl -fsS http://127.0.0.1:${REMOTE_PORT}/v1/models")"
  grep -Fq "${MODEL}" <<<"${remote_json}"
  printf 'Mac Ollama is reachable and the model is available.\n'
  exit 0
fi

if command -v lsof >/dev/null 2>&1 && lsof -nP -iTCP:"${LOCAL_PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
  printf 'Local port %s is already in use but does not expose %s.\n' "${LOCAL_PORT}" "${MODEL}" >&2
  exit 1
fi

ssh_args=(-o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -N -L "${LOCAL_PORT}:127.0.0.1:${REMOTE_PORT}" "${SSH_TARGET}")

if (( BACKGROUND )); then
  nohup ssh "${ssh_args[@]}" >"${TMPDIR:-/tmp}/module4-remote-qwen-tunnel.log" 2>&1 &
  for _ in $(seq 1 30); do
    local_ready && exit 0
    sleep 1
  done
  printf 'Tunnel did not become ready.\n' >&2
  exit 1
fi

exec ssh "${ssh_args[@]}"