#!/usr/bin/env bash
# Local laptop development defaults (APP_PROFILE=local, SQLite).
# Source from runner scripts or: source DevOps/env/local.sh

export APP_PROFILE=local
export LOG_LEVEL=INFO
export PYTHON_PORT=8000

# Docker Compose naming (used if you start containers alongside local dev)
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-filesearch-local}"
export AIRFLOW_ENABLED="${AIRFLOW_ENABLED:-0}"

# Secrets — set in DevOps/env/secrets.local.sh (gitignored) or export manually:
# export AWS_ACCESS_KEY_ID=
# export AWS_SECRET_ACCESS_KEY=
# export BEDROCK_AGENT_ALIAS_ID=
# export VECTOR_DB_OPENAI_API_KEY=
# export OPENAI_API_KEY=
# export VECTOR_DB_OPENAI_ORG_ID=
# export VECTOR_DB_OPENAI_VECTOR_STORE_ID=
