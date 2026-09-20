#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${VENV_DIR:-${ROOT_DIR}/.venv}"

if [[ ! -x "${VENV_DIR}/bin/alembic" ]]; then
  "${ROOT_DIR}/scripts/bootstrap.sh"
fi

cd "${ROOT_DIR}"
exec "${VENV_DIR}/bin/alembic" upgrade head