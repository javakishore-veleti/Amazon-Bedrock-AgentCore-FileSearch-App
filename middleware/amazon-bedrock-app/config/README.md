# Profile-based configuration

This app uses Spring Boot-style layered YAML instead of `.env` / `load_dotenv()`.

**Developers:** use `npm run` — you do not need to export `APP_PROFILE` manually. See [DevOps/README.md](../../../DevOps/README.md).

## Bootstrap selector

Only one environment variable selects the active profile at startup. Runner scripts in `DevOps/` set it for you:

| npm command | Profile | Env script |
|-------------|---------|------------|
| `npm run local:middleware:start` | `local` | `DevOps/env/local.sh` |
| `npm run local:middleware:start:docker` | `docker` | `DevOps/env/docker.sh` |

For manual runs or CI, export `APP_PROFILE` yourself:

```bash
export APP_PROFILE=local    # default
export APP_PROFILE=docker   # local Docker stack
export APP_PROFILE=production   # or APP_PROFILE=prod
```

## Config files

| File | Purpose |
|------|---------|
| `application.yaml` | Shared defaults for all profiles |
| `application-local.yaml` | Laptop development (Postgres pgvector on localhost, SQLite ingest metadata) |
| `application-docker.yaml` | Docker Compose (Postgres service hostnames) |
| `application-prod.yaml` | Production stub (OTEL on, Postgres URLs) |

Loading order: `application.yaml` deep-merged with `application-{profile}.yaml`.

## Secrets

Non-secret settings live in YAML. **Secrets are never committed** — provide them via environment variables or secret mounts (Kubernetes secrets, Docker secrets, etc.).

For local development, copy the template and fill in keys (gitignored):

```bash
cp DevOps/env/secrets.local.sh.example DevOps/env/secrets.local.sh
```

Runner scripts source `DevOps/env/secrets.local.sh` automatically when present.

The loader applies only explicitly mapped env vars:

| Environment variable | Config path |
|---------------------|-------------|
| `AWS_ACCESS_KEY_ID` | `aws.access_key_id` |
| `AWS_SECRET_ACCESS_KEY` | `aws.secret_access_key` |
| `BEDROCK_AGENT_ALIAS_ID` | `bedrock.agent_alias_id` |
| `VECTOR_DB_OPENAI_API_KEY` | `vector_store.openai.api_key` |
| `OPENAI_API_KEY` | `vector_store.openai.api_key` (fallback if key empty) |
| `VECTOR_DB_OPENAI_ORG_ID` | `vector_store.openai.org_id` |
| `VECTOR_DB_OPENAI_VECTOR_STORE_ID` | `vector_store.openai.vector_store_id` |
| `DATABASE_URL` | `database.url` |
| `BOOK_INGEST_DB_URL` | `book_ingest.database.url` |

## Vector store (default: pgvector)

The default `vector_store.provider` is **pgvector**. Embeddings are generated locally with `sentence-transformers` (`all-MiniLM-L6-v2`, 384 dimensions) and stored in Postgres via the pgvector extension — no OpenAI API key is required for vector ingest/search.

| Setting | Default | Purpose |
|---------|---------|---------|
| `vector_store.pgvector.schema` | `ingest_ops` | Postgres schema for embedding rows |
| `vector_store.pgvector.table` | `document_embeddings` | Table name |
| `vector_store.pgvector.embedding_dimension` | `384` | Must match the embedding model |
| `vector_store.pgvector.embedding_model` | `all-MiniLM-L6-v2` | Local sentence-transformers model |

Connection uses the top-level `database.url`. Start local Postgres with pgvector via `npm run local:containers:start` (or `bash DevOps/Local/docker-all-up.sh`).

Use **`PgVector`** as `book_ingest.ingest.target_vector_stores` / API `vector_store_name` (matches `END_POINTS_MASTER`). OpenAI remains available as an optional secondary store when `VECTOR_DB_OPENAI_API_KEY` is set.

## Usage

```bash
# Recommended — local profile (pgvector on localhost:5432)
npm run local:containers:start
npm run local:middleware:start

# Docker profile — start containers first
npm run local:containers:start
npm run local:middleware:start:docker

# Production (deploy platform sets secrets)
# source DevOps/env/production.sh and run via your orchestrator
```

Settings are loaded once at startup via `load_app_settings()` and are immutable thereafter.

## OpenTelemetry

OTEL is **off in all default profiles** (local, docker, production). Set `observability.otel_enabled: true` only for incident debugging. When enabled, install optional deps:

```bash
pip install -r requirements-otel.txt
```
