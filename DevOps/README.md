# DevOps scripts

Developer ergonomics for running the middleware and local Docker stack without memorizing `APP_PROFILE` or secret env var names.

## Quick start

```bash
# First-time: create Python venv and install deps
npm run localhost:setup:python:venv

# Start API (local profile, SQLite)
npm run local:middleware:start

# Start Postgres (and optional Airflow), then API with docker profile
npm run local:containers:start
npm run local:middleware:start:docker
```

## Environment profiles (`env/`)

Sourceable shell files export defaults for each runtime profile. Runner scripts source the right file automatically.

| File | `APP_PROFILE` | Purpose |
|------|---------------|---------|
| `env/local.sh` | `local` | Laptop dev, SQLite (`application-local.yaml`) |
| `env/docker.sh` | `docker` | Host API + local Postgres container |
| `env/production.sh` | `production` | Deploy stub — set secrets in CI/CD |

Optional personal secrets (never committed):

```bash
cp DevOps/env/secrets.local.sh.example DevOps/env/secrets.local.sh
# edit secrets.local.sh with your API keys
```

`run-middleware-*.sh` sources `secrets.local.sh` when the file exists.

## Runner scripts

| Script | Sources | Runs |
|--------|---------|------|
| `run-middleware-local.sh` | `env/local.sh` | `middleware/amazon-bedrock-app/main.py` |
| `run-middleware-docker.sh` | `env/docker.sh` | same, with Postgres URLs |

Python interpreter: `$HOME/runtime_data/python_venvs/Amazon-Bedrock-AgentCore-FileSearch-App/bin/python` (override with `VENV_PYTHON`).

## Local containers (`Local/`)

See [Local/README.md](Local/README.md). `docker-all-up.sh` sources `env/docker.sh` for consistent `COMPOSE_PROJECT_NAME` and `AIRFLOW_ENABLED`.

Configuration still loads from YAML profiles under `middleware/amazon-bedrock-app/config/` — these scripts only export the bootstrap selector and secrets.
