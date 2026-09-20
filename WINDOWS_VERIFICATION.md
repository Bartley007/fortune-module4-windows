# Windows Verification

Verified on 2026-09-20 on Windows 11 build `10.0.26200`.

## Verified Runtime

- Python `3.12.10`.
- WSL `2.7.14.0`, default version 2.
- Docker Desktop `4.91.0`, Docker Engine `29.8.0`.
- Docker Linux backend: `linux/amd64`, 20 CPUs, approximately 15.5 GiB memory.
- NVIDIA GeForce RTX 5070 Laptop GPU, 8 GB, driver `581.08`.
- CUDA container `nvidia/cuda:12.8.0-base-ubuntu24.04` successfully runs `nvidia-smi`.
- PostgreSQL `pgvector/pgvector:pg16` container is healthy on `localhost:5432`.
- Alembic revision `20260918_0001`.
- `case_profiles.embedding` is stored as PostgreSQL `vector(1024)`.
- The public schema contains 11 application tables.

## Verified Application Behavior

Ruff, mypy, and all 15 pytest tests pass with:

- Development-only install: `pip install -e ".[dev]"`.
- ML install: `setup_windows_gpu.bat`.

The API was started with PostgreSQL, `BAAI/bge-m3`, and Ollama `qwen3.8:27b`:

- `/health` returns `{"status":"ok","service":"fortune-module4"}`.
- `/docs` and `/openapi.json` return HTTP 200.
- Recommendation score remains deterministic at `0.77`.
- Similar-case score remains deterministic at `1.0`.
- Recommendation and similar-case explanations are generated in Simplified Chinese.
- `ollama ps` reports `qwen3.8:27b` at `77% CPU / 23% GPU`, context 4096.
- Warm model generation runs at approximately 3 completion tokens per second.
- First Qwen3.8-27B load plus a short response took about 57 seconds on this computer.

## Frontend Compatibility

Module 4 now provides the two routes currently used by the `Slyvia0425/fortune` frontend:

- `POST /api/session/event`
- `POST /api/user/notes`

Both return the frontend envelope shape, including `meta` and source-reference objects. The native
Module 4 `/api/v1` endpoints remain unchanged. Integration tests verify event mapping, event
idempotency, note create/update/delete, response headers, and user mismatch rejection.

## Docker Runtime Recovery

After the Windows restart, Docker Desktop 4.91.0 hit the known Windows 11 build 26200 AF_UNIX
reparse-point issue: stale `sailor-ingest.sock` entries under `%LOCALAPPDATA%\Docker\run` and
`%LOCALAPPDATA%\docker-secrets-engine` could not be renamed. Docker was stopped and those two
runtime directories were renamed aside; the Docker VHDX, images, containers, and PostgreSQL volume
were not reset. Docker Desktop then started normally and the existing pgvector container was reused.

## GPU Memory Note

The RTX 5070 Laptop GPU has 8 GB of memory. Qwen3.8-27B Q4_K_M is about 18 GB at runtime and cannot
fit fully in VRAM, so Ollama uses a CPU/GPU split with about 20 GB of process memory. BGE-M3 and
Qwen3.8-27B must be loaded on demand and should not be assumed to remain resident simultaneously.

## Reproduced Issues Fixed

- Optional `sentence-transformers` imports type-check both when the `ml` extra is absent and installed.
- Ollama OpenAI-compatible requests set `reasoning_effort=none` so thinking tokens do not consume the explanation budget.
- Similar-case responses include the generated `explanation` field after deterministic top-k ranking.
- Frontend-shaped event and note payloads are adapted without changing the frontend or native contracts.