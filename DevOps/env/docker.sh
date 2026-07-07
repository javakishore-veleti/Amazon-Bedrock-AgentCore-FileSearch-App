#!/usr/bin/env bash
# Local Docker stack defaults (APP_PROFILE=docker, Postgres on localhost).
# Start containers first: npm run local:containers:start
# Source from runner scripts or: source DevOps/env/docker.sh

export APP_PROFILE=docker
export LOG_LEVEL=INFO
export PYTHON_PORT=8000

# Shared Docker Compose project (matches DevOps/Local/docker-all-*.sh)
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-filesearch-local}"
export AIRFLOW_ENABLED="${AIRFLOW_ENABLED:-0}"

# Host middleware → filesearch-local-postgres on localhost:5432
export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/filesearch}"
export BOOK_INGEST_DB_URL="${BOOK_INGEST_DB_URL:-postgresql://postgres:postgres@localhost:5432/filesearch}"

# Secrets — set in DevOps/env/secrets.local.sh (gitignored) or export manually:
# export AWS_ACCESS_KEY_ID=
# export AWS_SECRET_ACCESS_KEY=
# export BEDROCK_AGENT_ALIAS_ID=
# export VECTOR_DB_OPENAI_API_KEY=
# export OPENAI_API_KEY=
# export VECTOR_DB_OPENAI_ORG_ID=
# export VECTOR_DB_OPENAI_VECTOR_STORE_ID=
