# Local Docker infrastructure

Shared local containers for filesearch development. All services join one network and share a naming prefix for easy discovery.

| Item              | Value                    |
|-------------------|--------------------------|
| Prefix            | `filesearch-local`       |
| Network           | `filesearch-local-net`   |
| Compose project   | `filesearch-local`       |

## Quick start

```bash
# From repo root
npm run local:containers:start
npm run local:containers:status
npm run local:containers:stop
```

Equivalent shell scripts:

```bash
bash DevOps/Local/docker-all-up.sh
bash DevOps/Local/docker-all-status.sh
bash DevOps/Local/docker-all-down.sh
```

## Services

| Path | Container(s) | Notes |
|------|--------------|-------|
| `Postgres/` | `filesearch-local-postgres` | Postgres 16 + **pgvector** on `localhost:5432` (default vector store) |
| `Airflow/` | `filesearch-local-airflow-*` | v1 stub — not started unless `AIRFLOW_ENABLED=1` |

## App profile

Run the API on the host with the docker profile (no manual exports):

```bash
npm run local:middleware:start:docker
```

This sources `DevOps/env/docker.sh`, which sets `APP_PROFILE=docker` and `DATABASE_URL` for `filesearch-local-postgres` on `localhost:5432`.

See `Postgres/README.md` for details.

## Options

| Variable | Default | Purpose |
|----------|---------|---------|
| `AIRFLOW_ENABLED` | `0` | Set to `1` to start Airflow compose (after uncommenting services) |
| `REMOVE_NETWORK` | `0` | Set to `1` on down to remove `filesearch-local-net` |
| `COMPOSE_PROJECT_NAME` | `filesearch-local` | Docker Compose project name |
