# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Early-stage scaffold for a file-search service built on Amazon Bedrock Agent Core. The FastAPI backend in `middleware/amazon-bedrock-app/main.py` exposes the API surface, but the core endpoints (`/api/search`, `/api/files`, `/api/files/{id}`) are stubs marked with `TODO` — they return placeholder payloads, not real results. The `ingest/` package is the in-progress document-ingestion layer. Expect to implement, not just modify, when working here.

## Commands

```bash
# First-time setup (creates venv, installs deps, copies .env.example -> .env)
bash DevOps/setup.sh

# Activate the environment before running anything
source venv/bin/activate          # setup.sh creates ./venv

# Run the API (serves on PYTHON_PORT, default 8000; reloads when DEBUG=true)
python middleware/amazon-bedrock-app/main.py

# All runtime + dev dependencies live in the root requirements.txt
pip install -r requirements.txt

# Tests (pytest config lives in pyproject.toml; testpaths = middleware/)
pytest                            # runs with -v and HTML coverage by default
pytest middleware/path/test_x.py::test_name   # single test

# Lint / format / type-check
black .                           # line-length 100
isort .                          # black profile
flake8 middleware/
mypy middleware/
```

Note: the README references a `Makefile` and `make dev`/`make test` targets, but no Makefile exists in the repo — use the commands above directly. `.env` is required at the working-directory root (loaded via `load_dotenv()` from wherever the process starts); run from the repo root.

## Architecture

- **API layer** (`middleware/amazon-bedrock-app/main.py`): single-file FastAPI app. The Bedrock client (`bedrock-agent-runtime`) is created lazily in `initialize_bedrock_client()` on the FastAPI `startup` event and held in a module-level global `bedrock_client`. New endpoints that call Bedrock should use that global rather than constructing their own client. CORS is wide open (`allow_origins=["*"]`) — intended for local dev.

- **Ingestion layer** (`middleware/amazon-bedrock-app/ingest/`): designed to be vector-store-agnostic. `common/dtos.py` defines `IngestReq` with a `target_vector_store` field (default `"openai"`) — the routing key for which backend handles a request. `vector_store/openai_ingest_facade.py` (`OpenAIVectorStoreIngestFacade`) is the first facade implementation; add a new facade per vector store and dispatch on `target_vector_store`. The ingest pipeline is not yet wired into the API endpoints.

## Configuration

All runtime config comes from `.env` (see `.env.example`). Key variables: `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `BEDROCK_MODEL_ID`, `BEDROCK_AGENT_ALIAS_ID`, `PYTHON_PORT`, `DEBUG`, `LOG_LEVEL`, and file-search limits (`MAX_FILE_SIZE_MB`, `SUPPORTED_FILE_TYPES`).
