#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${VENV_DIR:-${ROOT_DIR}/.venv}"

if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
  "${ROOT_DIR}/scripts/bootstrap.sh"
fi

cd "${ROOT_DIR}"
export PYTHONUTF8=1
exec "${VENV_DIR}/bin/python" scripts/seed_demo.py