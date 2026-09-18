# Module 4 Windows Handoff Summary

## Current Repository State

Project: `fortune_module4`

Purpose: Module 4 backend for session history, next-action recommendation, anonymous similar-case
matching, feedback, collections, notes, tags, privacy, export, and deletion.

Stack:

- Python 3.12+ with FastAPI
- SQLAlchemy 2 and Alembic
- SQLite for local Windows startup
- PostgreSQL + pgvector for production and vector search
- Pytest, Ruff, mypy, pre-commit, and GitHub Actions

Implemented API areas:

- Session creation/resume and ordered event retrieval.
- Idempotent event ingestion with `X-Idempotency-Key`.
- Deterministic recommendation ranking with the documented 0.35/0.30/0.20/0.10/0.05 weights.
- Similar-case matching with consent gating and missing-feature renormalization.
- Explicit and implicit feedback.
- Private collections, notes, tags, and source references.
- JSON export, privacy settings, and user data deletion.
- Fixed response envelope and structured error format.

Current local defaults:

- `EMBEDDING_PROVIDER=hash`
- `LLM_PROVIDER=template`
- `DATABASE_URL=sqlite:///./module4.db`

These defaults require no model download and no GPU. They are intended for integration testing and
demo use.

## Verification Status

- 10 end-to-end API tests passed on macOS.
- Ruff passed.
- mypy passed for all application source files.
- Alembic successfully upgraded a fresh SQLite database to revision `20260918_0001`.
- PostgreSQL type compilation produced `VECTOR(1024)`.
- The API was started and manually checked through health, recommendation, similar-case, and
  OpenAPI endpoints.
- Docker was not installed on the source computer, so container build execution remains unverified.

## Windows Migration State

Windows-specific files added:

- `setup_windows.bat` and `scripts/bootstrap_windows.ps1`
- `start_windows.bat` and `scripts/start_windows.ps1`
- `test_windows.bat` and `scripts/test_windows.ps1`
- `migrate_windows.bat` and `scripts/migrate_windows.ps1`
- `seed_demo_windows.bat` and `scripts/seed_demo_windows.ps1`
- `setup_windows_gpu.bat` and `scripts/setup_windows_gpu.ps1`
- `windows.env.example`
- `WINDOWS_MIGRATION.md`

## GPU Target

Embedding options:

- `BAAI/bge-m3`, preferred quality.
- `BAAI/bge-small-zh-v1.5`, lower memory and CPU cost.

Explanation model:

- `Qwen3-8B-Instruct` or an equivalent Chinese instruction model through an OpenAI-compatible API.

Recommended deployment:

- Windows-native CUDA PyTorch for BGE embeddings.
- WSL2 + vLLM or Docker Desktop + vLLM for Qwen3-8B.
- Ollama or LM Studio as simpler native Windows alternatives.

The LLM is never allowed to calculate or modify deterministic facts or ranking.

## Known Limitations and Next Work

- The default setup is the CPU fallback, not the final GPU deployment.
- Docker Compose and CUDA container execution still need testing on the Windows NVIDIA computer.
- The embedding adapter currently relies on automatic CUDA selection. Add explicit
  `EMBEDDING_DEVICE` and `EMBEDDING_DTYPE` settings if multi-GPU control is required.
- PostgreSQL + pgvector should be enabled before performance and integration evaluation.
- Recommendation and case evaluation reports are still required.

## Prompt To Use On Windows

Copy the following prompt into Codex on the Windows computer:

```text
Continue the fortune_module4 project on this Windows machine. First read WINDOWS_MIGRATION.md,
README.md, docs/cross_module_contract.md, docs/model_selection.md, and PROMPT_SUMMARY.md.

Start by running setup_windows.bat and test_windows.bat without changing application behavior.
Confirm Python version, virtual environment creation, Ruff, mypy, pytest, API startup, and the
health endpoint. Then inspect the NVIDIA environment with nvidia-smi and identify the installed
CUDA driver version.

Preserve the existing response envelope, user_id isolation, source_id usage, idempotent event
ingestion, deterministic ranking rules, privacy controls, and the rule that the LLM only generates
explanations. Do not replace deterministic facts or ranking with an LLM.

After the baseline checks pass, migrate the runtime in this order:
1. Enable SQLite quick start on Windows and verify all tests.
2. Enable PostgreSQL + pgvector through Docker Desktop or WSL2 and run Alembic.
3. Install a CUDA-compatible PyTorch wheel and run BGE-M3 or bge-small-zh-v1.5 on the NVIDIA GPU.
4. Start Qwen3-8B through WSL2/vLLM, Docker/vLLM, Ollama, or LM Studio.
5. Set LLM_PROVIDER=openai_compatible and verify recommendation and similar-case explanations.
6. Add explicit embedding device and dtype settings if the machine has multiple GPUs.

Run test_windows.bat after each change. Report what was verified natively, what was verified through
WSL2 or Docker, and what still requires GPU hardware access.
```
