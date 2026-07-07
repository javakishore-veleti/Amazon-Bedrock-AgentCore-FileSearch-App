# Local Postgres (Docker)

Postgres 16 for the filesearch local stack. Container: `filesearch-local-postgres`.

## Connection (host → container)

When the API runs on your laptop (not inside Docker) with `APP_PROFILE=docker`, point at the published port:

```text
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/filesearch
```

Override credentials via `POSTGRES_USER` / `POSTGRES_PASSWORD` in `.env` or the shell before `docker-all-up.sh`.

Inside the Docker network, other containers reach Postgres at hostname `filesearch-local-postgres` on port `5432`.

## Defaults

| Variable           | Default    |
|--------------------|------------|
| `POSTGRES_USER`    | `postgres` |
| `POSTGRES_PASSWORD`| `postgres` |
| `POSTGRES_DB`      | `filesearch` |

Data persists in volume `filesearch-local-postgres-data`. Init scripts in `init/` run only on first boot.
