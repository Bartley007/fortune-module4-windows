#!/usr/bin/env bash
set -euo pipefail

MODEL="${MAC_QWEN_MODEL:-qwen3.8:27b-q8_0}"
OLLAMA_ADDR="${OLLAMA_ADDR:-127.0.0.1:11434}"
OLLAMA_CONTEXT_LENGTH_VALUE="${OLLAMA_CONTEXT_LENGTH:-8192}"
CHECK_ONLY=0

usage() {
  printf '%s\n' "Usage: scripts/setup_mac_qwen.sh [--model MODEL] [--host HOST:PORT] [--context N] [--check-only]"
}

while (($#)); do
  case "$1" in
    --model) MODEL="$2"; shift 2 ;;
    --host) OLLAMA_ADDR="$2"; shift 2 ;;
    --context) OLLAMA_CONTEXT_LENGTH_VALUE="$2"; shift 2 ;;
    --check-only) CHECK_ONLY=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'Unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ "$(uname -s)" != "Darwin" ]]; then
  printf 'setup_mac_qwen.sh must run on macOS.\n' >&2
  exit 1
fi

OLLAMA_BIN=""
if command -v ollama >/dev/null 2>&1; then
  OLLAMA_BIN="$(command -v ollama)"
else
  for candidate in /usr/local/bin/ollama /opt/homebrew/bin/ollama /Applications/Ollama.app/Contents/Resources/ollama; do
    if [[ -x "${candidate}" ]]; then
      OLLAMA_BIN="${candidate}"
      break
    fi
  done
fi

if [[ -z "${OLLAMA_BIN}" ]]; then
  printf 'Ollama is not installed. Install it first, then rerun this script.\n' >&2
  exit 1
fi

export OLLAMA_HOST="${OLLAMA_ADDR}"
export OLLAMA_CONTEXT_LENGTH="${OLLAMA_CONTEXT_LENGTH_VALUE}"

api_ready() {
  curl -fsS "http://${OLLAMA_ADDR}/v1/models" >/dev/null 2>&1
}

if ! api_ready; then
  if (( CHECK_ONLY )); then
    printf 'Ollama is not listening at %s.\n' "${OLLAMA_ADDR}" >&2
    exit 1
  fi
  printf 'Starting Ollama at %s with context %s...\n' "${OLLAMA_ADDR}" "${OLLAMA_CONTEXT_LENGTH_VALUE}"
  nohup caffeinate -d -i -m -s -u "${OLLAMA_BIN}" serve >"${HOME}/ollama.log" 2>&1 &
  for _ in $(seq 1 30); do
    api_ready && break
    sleep 1
  done
fi

if ! api_ready; then
  printf 'Ollama did not become ready. Inspect %s/ollama.log.\n' "${HOME}" >&2
  exit 1
fi

models_json="$(curl -fsS "http://${OLLAMA_ADDR}/v1/models")"
if ! grep -Fq "${MODEL}" <<<"${models_json}"; then
  if (( CHECK_ONLY )); then
    printf 'Model is not installed: %s\n' "${MODEL}" >&2
    exit 1
  fi
  OLLAMA_HOST="${OLLAMA_ADDR}" "${OLLAMA_BIN}" pull "${MODEL}"
fi

models_json="$(curl -fsS "http://${OLLAMA_ADDR}/v1/models")"
grep -Fq "${MODEL}" <<<"${models_json}"

printf 'Mac Ollama ready.\n'
printf '  Endpoint: http://%s/v1\n' "${OLLAMA_ADDR}"
printf '  Model: %s\n' "${MODEL}"