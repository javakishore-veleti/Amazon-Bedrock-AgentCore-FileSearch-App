#!/usr/bin/env bash
# Stop all local Docker services for the filesearch stack.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-filesearch-local}"
NETWORK_NAME="filesearch-local-net"
REMOVE_NETWORK="${REMOVE_NETWORK:-0}"

echo "Stopping Airflow (if running)..."
docker compose -f "$SCRIPT_DIR/Airflow/docker-compose.yaml" down --remove-orphans 2>/dev/null || true

echo "Stopping Postgres..."
docker compose -f "$SCRIPT_DIR/Postgres/docker-compose.yaml" down --remove-orphans

if [ "$REMOVE_NETWORK" = "1" ]; then
  if docker network inspect "$NETWORK_NAME" >/dev/null 2>&1; then
    echo "Removing Docker network: $NETWORK_NAME"
    docker network rm "$NETWORK_NAME" || echo "Network still in use; not removed."
  fi
else
  echo "Keeping Docker network $NETWORK_NAME (set REMOVE_NETWORK=1 to delete)."
fi

echo ""
echo "Local containers stopped."
