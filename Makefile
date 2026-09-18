PYTHON ?= python3
VENV ?= .venv
PIP := $(VENV)/bin/pip
PY := $(VENV)/bin/python

.PHONY: install dev run test lint format migrate revision docker-up docker-down openapi seed clean

install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"

dev: install

run:
	$(VENV)/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	$(PY) -m pytest

lint:
	$(VENV)/bin/ruff check app alembic scripts tests
	$(VENV)/bin/mypy app

format:
	$(VENV)/bin/ruff check --fix app alembic scripts tests
	$(VENV)/bin/ruff format app alembic scripts tests

migrate:
	$(VENV)/bin/alembic upgrade head

revision:
	$(VENV)/bin/alembic revision --autogenerate -m "$(m)"

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

openapi:
	$(PY) scripts/export_openapi.py

seed:
	$(PY) scripts/seed_demo.py

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
