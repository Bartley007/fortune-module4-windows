# Deployment Modes

Module 4 supports three deployment modes without changing its API contracts.

## 1. Windows Local

Use this mode for development, demos, or machines without a GPU:

```bat
setup_windows.bat
test_windows.bat
seed_demo_windows.bat
start_windows.bat
```

Defaults:

- SQLite
- Hash embeddings
- Template explanations

For PostgreSQL and pgvector, start `docker compose up -d db`, then update `.env` and run
`migrate_windows.bat`.

For Windows GPU embeddings:

```bat
setup_windows_gpu.bat
```

## 2. Linux Local

Use this mode on Linux servers or workstations:

```bash
bash setup_linux.sh
bash test_linux.sh
bash seed_demo_linux.sh
bash start_linux.sh
```

The default environment template is `linux.env.example` and uses SQLite, hash embeddings, and
template explanations.

Optional CUDA/ML dependencies:

```bash
bash setup_linux_gpu.sh
```

For PostgreSQL, use `docker compose up -d db`, update `.env`, and run:

```bash
bash migrate_linux.sh
```

## 3. Remote Mac Qwen

This mode keeps Module 4 and PostgreSQL on Windows or Linux while the MacBook runs Ollama.

### MacBook

Install Ollama, then run:

```bash
bash scripts/setup_mac_qwen.sh
```

The script verifies or starts Ollama at `127.0.0.1:11434` and ensures
`qwen3.8:27b-q8_0` is available. It does not expose Ollama to the public network.

### Windows Client

Set the SSH target and start the tunnel:

```bat
start_remote_mac_qwen_windows.bat -SshTarget user@macbook-host
```

Check-only mode:

```bat
start_remote_mac_qwen_windows.bat -SshTarget user@macbook-host -CheckOnly
```

### Linux or macOS Client

```bash
export MAC_QWEN_SSH_TARGET=user@macbook-host
bash start_remote_mac_qwen_tunnel.sh --background
```

Check-only mode:

```bash
bash start_remote_mac_qwen_tunnel.sh --check-only
```

### Module 4 Configuration

Copy the remote template:

```bash
cp remote_mac_qwen.env.example .env
```

The template uses:

```dotenv
LLM_PROVIDER=openai_compatible
LLM_MODEL=qwen3.8:27b-q8_0
LLM_BASE_URL=http://127.0.0.1:11434/v1
LLM_API_KEY=ollama
LLM_TIMEOUT_SECONDS=600
LLM_REASONING_EFFORT=none
```

The SSH tunnel maps the Mac Ollama endpoint to the client's localhost. Ollama is not exposed directly
to the LAN or Internet.

## Model Responsibilities

- Deterministic facts, scoring, matching, and ranking remain inside Module 4.
- The LLM receives only ranked candidates or anonymized case features.
- The LLM may generate explanations only.
- The LLM must never modify scores, ordering, source identifiers, charts, hexagrams, or source text.