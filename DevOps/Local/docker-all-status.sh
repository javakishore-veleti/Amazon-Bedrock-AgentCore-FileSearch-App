#!/usr/bin/env bash
# Show status of the filesearch local Docker network and containers.
set -euo pipefail

NETWORK_NAME="filesearch-local-net"
PREFIX="filesearch-local"

echo "=== Docker network: $NETWORK_NAME ==="
if docker network inspect "$NETWORK_NAME" >/dev/null 2>&1; then
  docker network inspect "$NETWORK_NAME" --format '  Name: {{.Name}}
  Driver: {{.Driver}}
  Containers: {{len .Containers}}'
else
  echo "  (not found — run npm run local:containers:start)"
fi

echo ""
echo "=== Containers matching prefix: $PREFIX ==="
if docker ps -a --filter "name=^/${PREFIX}" --format '{{.ID}}' | grep -q .; then
  docker ps -a --filter "name=^/${PREFIX}" \
    --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
else
  echo "  (none)"
fi

echo ""
echo "Quick filter: docker ps | grep $PREFIX"
