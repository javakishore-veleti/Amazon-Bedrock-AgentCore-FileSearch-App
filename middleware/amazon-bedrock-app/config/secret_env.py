"""Explicit environment-variable overrides for secrets (no dotenv)."""

from __future__ import annotations

import os
from typing import Any

# (env_var, nested config path, only_if_missing)
SECRET_ENV_MAPPINGS: list[tuple[str, tuple[str, ...], bool]] = [
    ("AWS_ACCESS_KEY_ID", ("aws", "access_key_id"), False),
    ("AWS_SECRET_ACCESS_KEY", ("aws", "secret_access_key"), False),
    ("BEDROCK_AGENT_ALIAS_ID", ("bedrock", "agent_alias_id"), False),
    ("VECTOR_DB_OPENAI_API_KEY", ("vector_store", "openai", "api_key"), False),
    ("OPENAI_API_KEY", ("vector_store", "openai", "api_key"), True),
    ("VECTOR_DB_OPENAI_ORG_ID", ("vector_store", "openai", "org_id"), False),
    ("VECTOR_DB_OPENAI_VECTOR_STORE_ID", ("vector_store", "openai", "vector_store_id"), False),
    ("VECTOR_DB_PINECONE_API_KEY", ("vector_store", "pinecone", "api_key"), False),
    ("VECTOR_DB_CHROMA_AUTH_TOKEN", ("vector_store", "chroma", "auth_token"), False),
    ("VECTOR_DB_MONGODB_PASSWORD", ("vector_store", "mongodb", "password"), False),
    ("VECTOR_DB_PGVECTOR_PASSWORD", ("vector_store", "pgvector", "password"), False),
    ("VECTOR_DB_AZURE_CLIENT_SECRET", ("vector_store", "azure", "client_secret"), False),
    ("VECTOR_DB_GCP_SERVICE_ACCOUNT_JSON", ("vector_store", "gcp", "service_account_json"), False),
    ("DATABASE_URL", ("database", "url"), False),
    ("BOOK_INGEST_DB_URL", ("book_ingest", "database", "url"), False),
]


def _get_nested(config: dict[str, Any], path: tuple[str, ...]) -> Any:
    node: Any = config
    for key in path:
        if not isinstance(node, dict):
            return None
        node = node.get(key)
    return node


def _set_nested(config: dict[str, Any], path: tuple[str, ...], value: str) -> None:
    node = config
    for key in path[:-1]:
        child = node.setdefault(key, {})
        if not isinstance(child, dict):
            child = {}
            node[key] = child
        node = child
    node[path[-1]] = value


def apply_secret_overrides(config: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of *config* with secret env vars applied per explicit mapping."""
    merged = dict(config)
    for env_name, path, only_if_missing in SECRET_ENV_MAPPINGS:
        value = os.environ.get(env_name)
        if not value:
            continue
        if only_if_missing and _get_nested(merged, path):
            continue
        _set_nested(merged, path, value)
    return merged
