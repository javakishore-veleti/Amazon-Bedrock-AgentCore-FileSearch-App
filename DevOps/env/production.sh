#!/usr/bin/env bash
# Production deploy stub — override values in your deploy platform or secrets manager.
# Do not run locally unless you know the target environment.

export APP_PROFILE=production
export LOG_LEVEL=INFO
export PYTHON_PORT=8000

# Required in production (set via CI/CD, K8s secrets, etc.):
# export DATABASE_URL=postgresql://user:password@host:5432/filesearch
# export BOOK_INGEST_DB_URL=postgresql://user:password@host:5432/filesearch
# export AWS_ACCESS_KEY_ID=
# export AWS_SECRET_ACCESS_KEY=
# export BEDROCK_AGENT_ALIAS_ID=
# export VECTOR_DB_OPENAI_API_KEY=
# export VECTOR_DB_OPENAI_VECTOR_STORE_ID=

# Optional observability (off by default in application-prod.yaml):
# export OTEL_ENABLED=true
# export OTEL_EXPORTER_OTLP_ENDPOINT=https://otel-collector.example.com:4317
