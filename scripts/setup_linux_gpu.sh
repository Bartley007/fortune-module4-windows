#!/usr/bin/env bash
set -euo pipefail

if [[ "$(uname -s)" != "Linux" ]]; then
  printf 'This script is intended for Linux. Use setup_mac_qwen.sh on macOS.\n' >&2
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${VENV_DIR:-${ROOT_DIR}/.venv}"
TORCH_INDEX_URL="${TORCH_INDEX_URL:-https://download.pytorch.org/whl/cu128}"

if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
  "${ROOT_DIR}/scripts/bootstrap.sh"
fi

"${VENV_DIR}/bin/pip" install --upgrade torch --index-url "${TORCH_INDEX_URL}"
"${VENV_DIR}/bin/pip" install -e "${ROOT_DIR}[ml]"
printf 'GPU/ML environment ready: %s\n' "${VENV_DIR}"