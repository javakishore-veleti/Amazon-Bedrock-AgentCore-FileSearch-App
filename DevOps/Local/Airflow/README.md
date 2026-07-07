# Local Airflow (v1 stub)

Airflow is **not started by default**. The compose file documents the intended layout; services are commented out to keep the local stack lightweight.

## When you are ready

1. Uncomment and finish the service blocks in `docker-compose.yaml`.
2. Create an `airflow` database in Postgres (or extend `Postgres/init/`).
3. Start with Airflow enabled:

```bash
AIRFLOW_ENABLED=1 npm run local:containers:start
```

Expected container names use the `filesearch-local-airflow-*` prefix (e.g. `filesearch-local-airflow-webserver`, `filesearch-local-airflow-scheduler`).
