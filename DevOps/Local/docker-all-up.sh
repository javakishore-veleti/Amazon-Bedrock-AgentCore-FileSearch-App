#!/usr/bin/env bash
# Start all local Docker services for the filesearch stack.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Align container defaults with middleware docker profile (COMPOSE_PROJECT_NAME, AIRFLOW_ENABLED).
# shellcheck source=../env/docker.sh
source "$REPO_ROOT/DevOps/env/docker.sh"
NETWORK_NAME="filesearch-local-net"

if ! docker network inspect "$NETWORK_NAME" >/dev/null 2>&1; then
  echo "Creating Docker network: $NETWORK_NAME"
  docker network create "$NETWORK_NAME"
else
  echo "Docker network already exists: $NETWORK_NAME"
fi

echo "Starting Postgres..."
docker compose -f "$SCRIPT_DIR/Postgres/docker-compose.yaml" up -d

if [ "${AIRFLOW_ENABLED:-0}" = "1" ]; then
  echo "Starting Airflow (AIRFLOW_ENABLED=1)..."
  docker compose -f "$SCRIPT_DIR/Airflow/docker-compose.yaml" up -d
else
  echo "Skipping Airflow (v1 stub). Set AIRFLOW_ENABLED=1 when compose services are enabled."
fi

echo ""
echo "Local containers started. Run: npm run local:containers:status"
