# Windows Verification

Verified on 2026-09-18 on Windows 11 build `10.0.26200`.

## Verified Runtime

- Python `3.12.10`.
- WSL `2.7.14.0`, default version 2.
- Docker Desktop `4.91.0`, Docker Engine `29.8.0`.
- Docker Linux backend: `linux/amd64`, 20 CPUs, approximately 15.5 GiB memory.
- NVIDIA GeForce RTX 5070 Laptop GPU, driver `581.08`.
- CUDA container `nvidia/cuda:12.8.0-base-ubuntu24.04` successfully runs `nvidia-smi`.
- PostgreSQL `pgvector/pgvector:pg16` container is healthy on `localhost:5432`.
- Alembic revision `20260918_0001`.
- `case_profiles.embedding` is stored as PostgreSQL `vector(1024)`.
- The public schema contains 11 application tables.

## Verified Commands

Ruff, mypy, and all 11 pytest tests pass in both configurations:

- Development-only install: `pip install -e ".[dev]"`.
- ML install: `setup_windows_gpu.bat`.

The API was started with PostgreSQL, `BAAI/bge-m3`, and Ollama `qwen3:8b`:

- `/health` returns `{"status":"ok","service":"fortune-module4"}`.
- `/docs` and `/openapi.json` return HTTP 200.
- Recommendation score remains deterministic at `0.77`.
- Similar-case score remains deterministic at `1.0`.
- Qwen3 only generates recommendation and similar-case explanations.
- `ollama ps` reports `qwen3:8b` running at `100% GPU`.

## GPU Memory Note

The RTX 5070 Laptop GPU has 8 GB of memory. Qwen3 8B uses about 5.6 GB while loaded. BGE-M3 should be loaded only when embeddings are required; do not assume BGE-M3 and Qwen3 can remain resident together on this GPU.

## Reproduced Issues Fixed

- Optional `sentence-transformers` imports now type-check both when the `ml` extra is absent and when it is installed.
- Ollama OpenAI-compatible requests set `reasoning_effort=none` for Qwen3 so thinking tokens do not consume the explanation budget.
- Similar-case responses include the generated `explanation` field after deterministic top-k ranking.