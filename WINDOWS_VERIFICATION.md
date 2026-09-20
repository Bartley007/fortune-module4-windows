# Windows Verification

Verified on 2026-09-21 on Windows 11 build `10.0.26200` with a remote MacBook M5 Max Qwen server.

## Verified Runtime

- Python `3.12.10`.
- WSL `2.7.14.0`, default version 2.
- Docker Desktop `4.91.0`, Docker Engine `29.8.0`.
- PostgreSQL `pgvector/pgvector:pg16` is healthy on `localhost:5432`.
- Alembic revision `20260918_0001`.
- `case_profiles.embedding` is stored as PostgreSQL `vector(1024)`.
- The public schema contains 11 application tables.

## Remote Qwen Runtime

- MacBook M5 Max with 128 GB unified memory.
- Ollama model: `qwen3.8:27b-q8_0`.
- Runtime size: approximately 47 GB.
- Processor: `100% GPU`.
- Context: 262144.
- Windows accesses Ollama through SSH local forwarding:
  `127.0.0.1:11434 -> MacBook 127.0.0.1:11434`.
- Windows `.env` uses `LLM_MODEL=qwen3.8:27b-q8_0` and `LLM_BASE_URL=http://127.0.0.1:11434/v1`.

## Verified Application Behavior

Ruff, mypy, and all 24 pytest tests pass with:

- Development-only install: `pip install -e ".[dev]"`.
- ML install: `setup_windows_gpu.bat`.

The live end-to-end script passes against PostgreSQL and remote Qwen:

```bat
verify_end_to_end_windows.bat
```

Verified stages:

- Health and OpenAPI availability.
- Privacy and consent update.
- Session creation.
- Event ingestion, ordering, and idempotency.
- Deterministic recommendation ranking plus remote Qwen explanation.
- Explicit feedback.
- Private collection, note, and tag persistence.
- Per-user isolation.
- JSON export.
- Similar-case matching plus remote Qwen explanation.
- User-data deletion and privacy reset.

The end-to-end script creates a temporary user, verifies every stage, and deletes that user before exit.

## Frontend Compatibility

Module 4 provides the two routes currently used by the `Slyvia0425/fortune` frontend:

- `POST /api/session/event`
- `POST /api/user/notes`

Both return the frontend envelope shape, including `meta` and source-reference objects. Native
Module 4 `/api/v1` endpoints remain unchanged. Tests cover event mapping, event idempotency, note
create/update/delete, validation envelopes, and user mismatch rejection.

## Knowledge Dataset Validation

The upstream 764-record dataset has complete required fields, valid source types and categories, no duplicate URLs, and 764 unique derived source IDs. The upstream file still lacks `source_id` and `content_checksum`; Module 4 reports that strict contract gap and can generate deterministic source IDs without modifying the dataset.

## Docker Runtime Recovery

Docker Desktop 4.91.0 hit the known Windows 11 build 26200 AF_UNIX reparse-point issue: stale
`sailor-ingest.sock` and secrets-engine entries could not be renamed. Docker was stopped and the
runtime directories under `%LOCALAPPDATA%\Docker\run` and `%LOCALAPPDATA%\docker-secrets-engine`
were renamed aside. The Docker VHDX, images, containers, and PostgreSQL volume were preserved.

## Reproduced Issues Fixed

- Optional `sentence-transformers` imports type-check both when the `ml` extra is absent and installed.
- Ollama OpenAI-compatible requests set `reasoning_effort=none` so thinking tokens do not consume the explanation budget.
- Similar-case responses include the generated `explanation` field after deterministic top-k ranking.
- Frontend-shaped event and note payloads are adapted without changing the frontend or native contracts.