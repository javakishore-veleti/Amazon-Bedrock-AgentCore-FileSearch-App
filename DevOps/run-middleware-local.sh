#!/usr/bin/env bash
# Start the FastAPI middleware with local profile defaults (SQLite).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_DIR="$SCRIPT_DIR/env"
VENV_PYTHON="${VENV_PYTHON:-$HOME/runtime_data/python_venvs/Amazon-Bedrock-AgentCore-FileSearch-App/bin/python}"

# shellcheck source=env/local.sh
source "$ENV_DIR/local.sh"

if [ -f "$ENV_DIR/secrets.local.sh" ]; then
  # shellcheck source=env/secrets.local.sh
  source "$ENV_DIR/secrets.local.sh"
fi

if [ ! -x "$VENV_PYTHON" ]; then
  echo "Python venv not found at: $VENV_PYTHON" >&2
  echo "Run: npm run localhost:setup:python:venv" >&2
  exit 1
fi

cd "$REPO_ROOT/middleware/amazon-bedrock-app"
exec "$VENV_PYTHON" main.py
