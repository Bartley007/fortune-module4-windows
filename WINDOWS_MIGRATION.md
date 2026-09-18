# Windows Migration Guide

This package contains the complete Fortune Module 4 backend, Windows launchers, tests, Alembic
migrations, API documentation, and a Git bundle that preserves the repository history.

## 1. Prerequisites

Install these on the Windows computer:

- Windows 10 or Windows 11, 64-bit.
- Python 3.12, 64-bit, with the Python launcher or `python` on `PATH`.
- Git for Windows, optional but recommended.
- Docker Desktop with WSL2, optional, for PostgreSQL + pgvector or vLLM containers.
- A current NVIDIA driver, optional, for GPU embedding or local LLM inference.

Do not copy `.venv` from macOS. Windows must create its own virtual environment.

## 2. Quick Start With SQLite

Extract the package, open PowerShell or Command Prompt in the project directory, then run:

```bat
setup_windows.bat
start_windows.bat
```

The first command creates `.venv`, installs the project, and copies `windows.env.example` to `.env`.
The second command starts the API.

Open:

- API documentation: <http://127.0.0.1:8000/docs>
- Health check: <http://127.0.0.1:8000/health>

The default Windows configuration uses SQLite at `module4.db`, `EMBEDDING_PROVIDER=hash`, and
`LLM_PROVIDER=template`. It runs without Docker, a model download, or a GPU.

## 3. Useful Windows Commands

```bat
test_windows.bat
seed_demo_windows.bat
migrate_windows.bat
start_windows.bat
```

- `test_windows.bat`: runs Ruff, mypy, and pytest.
- `seed_demo_windows.bat`: inserts the anonymous case and session demo data.
- `migrate_windows.bat`: runs `alembic upgrade head`; use it with PostgreSQL.
- `start_windows.bat`: starts Uvicorn on port 8000.

Set a different port before starting if needed:

```bat
set PORT=8010
start_windows.bat
```

## 4. PostgreSQL + pgvector

With Docker Desktop and WSL2 enabled, start the database:

```bat
docker compose up -d db
```

Edit `.env` so that it contains:

```dotenv
DATABASE_URL=postgresql+psycopg://fortune:fortune@localhost:5432/fortune_module4
AUTO_CREATE_TABLES=false
```

Then run:

```bat
migrate_windows.bat
start_windows.bat
```

The migration enables the `vector` extension before creating the embedding column.

## 5. NVIDIA GPU Options

Two independent workloads can use CUDA:

1. BGE embeddings through `sentence-transformers`.
2. Qwen3-8B explanation generation through an OpenAI-compatible server.

### 5.1 CUDA PyTorch and BGE

Run:

```bat
setup_windows_gpu.bat
```

The default script uses the PyTorch CUDA 12.8 wheel index. If the NVIDIA driver requires a different
wheel, pass a matching index URL:

```bat
setup_windows_gpu.bat -TorchIndexUrl "https://download.pytorch.org/whl/cu126"
```

Then update `.env`:

```dotenv
EMBEDDING_PROVIDER=sentence-transformers
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_DIM=1024
```

The first request downloads the model. `sentence-transformers` uses CUDA automatically when the
installed PyTorch build can see the NVIDIA GPU.

### 5.2 Qwen3-8B on Windows

Windows-native vLLM support is limited. Prefer one of these routes:

- WSL2 + vLLM, recommended for development and production-like testing.
- Docker Desktop + a CUDA-enabled vLLM container.
- Ollama or LM Studio for a simpler native Windows development setup.

Example with Ollama after pulling a Qwen3 8B model:

```bat
ollama serve
ollama pull qwen3:8b
```

Set:

```dotenv
LLM_PROVIDER=openai_compatible
LLM_MODEL=qwen3:8b
LLM_BASE_URL=http://127.0.0.1:11434/v1
LLM_API_KEY=ollama
```

The exact model tag depends on the model installed in Ollama or LM Studio. Module 4 only requires an
OpenAI-compatible `/v1/chat/completions` endpoint.

## 6. Git Bundle

The package includes `fortune_module4_git.bundle`. Restore the repository history with:

```bat
git clone fortune_module4_git.bundle fortune_module4
```

If the project was extracted from the source archive instead, initialize Git manually:

```bat
cd fortune_module4
git init -b main
git add .
git commit -m "feat: bootstrap module 4 backend"
```

Before pushing to GitHub, set the correct identity and remote:

```bat
git config user.name "Your Name"
git config user.email "you@example.com"
git remote add origin https://github.com/your-account/your-repository.git
git push -u origin main
```

## 7. Files Intentionally Recreated on Windows

The archive does not contain macOS virtual environments or secrets. The following are created locally:

- `.venv/`
- `.env`
- `module4.db`
- caches and test artifacts

Do not commit `.env`, API keys, user databases, or exported user data.

## 8. Current Runtime and Fallbacks

- Ranking, similar-case matching, feedback, collections, notes, tags, export, and deletion are pure
  Python/PostgreSQL logic and remain on CPU.
- `EMBEDDING_PROVIDER=hash` and `LLM_PROVIDER=template` remain valid fallbacks when no GPU is present.
- LLM output is restricted to explanations. It must not change charts, hexagrams, sign numbers,
  source text, or ranking results.

## 9. Troubleshooting

- PowerShell blocks scripts: use the supplied `.bat` launchers; they use `-ExecutionPolicy Bypass`.
- Wrong Python version: install 64-bit Python 3.12 and rerun `setup_windows.bat`.
- Port already in use: set `PORT=8010` before `start_windows.bat`.
- CUDA unavailable: verify `nvidia-smi`, then reinstall a matching PyTorch CUDA wheel.
- PostgreSQL connection failure: confirm Docker Desktop is running and port 5432 is free.
