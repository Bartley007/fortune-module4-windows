# Cross-Platform Verification 0.2.0

Verified on 2026-09-21.

## Test Matrix

| Platform | Mode | Result |
| --- | --- | --- |
| Windows 11 | Native API with SQLite, hash embeddings, template explanations | Passed |
| Linux container | Native setup and API with SQLite | Passed |
| macOS | Remote Ollama Qwen3.8-27B Q8 | Passed |
| Windows client | SSH tunnel to remote Mac Qwen | Passed |
| PostgreSQL | Native Module 4 database | Passed |

## Windows Native

- `test_windows.bat`: Ruff, mypy, and 15 pytest tests passed.
- Native API started on port 8020 with SQLite, hash embeddings, and template explanations.
- `/health`, `/docs`, and `/openapi.json` returned HTTP 200.
- OpenAPI version: `0.2.0`.

## Linux Native

Verified in the official `python:3.12-slim` container with Windows virtual environments, secrets,
and databases excluded:

- `setup_linux.sh` installed dependencies and created `.env` from `linux.env.example`.
- `test_linux.sh` passed Ruff, mypy, and 15 pytest tests.
- `start_linux.sh` started Uvicorn successfully.
- `/health` returned `{"status":"ok","service":"fortune-module4"}`.

## macOS Remote Qwen

- MacBook M5 Max with 128 GB unified memory.
- Ollama model: `qwen3.8:27b-q8_0`.
- Model size: approximately 47 GB.
- Processor: `100% GPU`.
- `scripts/setup_mac_qwen.sh --check-only` passed over SSH.
- Mac Ollama listens on `127.0.0.1:11434` and is not exposed directly.

## Windows to Mac SSH Tunnel

- `start_remote_mac_qwen_windows.bat -SshTarget fortune-mac -CheckOnly` passed.
- Local forwarding: `127.0.0.1:11434 -> Mac 127.0.0.1:11434`.
- Live end-to-end verification passed with PostgreSQL and remote Qwen.
- Covered sessions, idempotent events, recommendations, similar cases, feedback, collections,
  notes, tags, privacy, exports, deletion, user isolation, and frontend compatibility routes.

## Version Management

- Package version: `0.2.0`.
- Git tag: `v0.2.0`.
- Changelog: `CHANGELOG.md`.
- Cross-platform deployment guide: `docs/deployment_modes.md`.