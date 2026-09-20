#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${VENV_DIR:-${ROOT_DIR}/.venv}"

if [[ ! -x "${VENV_DIR}/bin/pytest" ]]; then
  "${ROOT_DIR}/scripts/bootstrap.sh"
fi

cd "${ROOT_DIR}"
"${VENV_DIR}/bin/ruff" check app alembic scripts tests
"${VENV_DIR}/bin/mypy" app
"${VENV_DIR}/bin/pytest" -q