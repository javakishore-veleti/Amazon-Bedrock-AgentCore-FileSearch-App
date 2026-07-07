"""Postgres + pgvector client for local vector storage and similarity search."""

from __future__ import annotations

import logging
import re
import threading
import uuid
import json
from typing import Any

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine

from book_ingest.integrations.pgvector.embeddings import LocalEmbeddingModel
from common.di import component
from config.app_settings import get_app_settings

LOGGER = logging.getLogger(__name__)

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_CHUNK_SIZE = 2000
_CHUNK_OVERLAP = 200


def _validate_identifier(value: str, label: str) -> str:
    if not _IDENTIFIER_RE.match(value):
        raise ValueError(f"Invalid SQL {label}: {value!r}")
    return value


@event.listens_for(Engine, "connect")
def _register_pgvector(dbapi_connection, _connection_record) -> None:
    from pgvector.psycopg2 import register_vector

    register_vector(dbapi_connection)


@component(key="PgVectorClient", depends_on=["LocalEmbeddingModel"])
class PgVectorClient:
    """Manages pgvector schema, ingest, and cosine-similarity search."""

    def __init__(self, embedding_model: LocalEmbeddingModel):
        self.embedding_model = embedding_model
        app_settings = get_app_settings()
        pg_cfg = app_settings.vector_store.pgvector
        self._schema = _validate_identifier(pg_cfg.db_schema, "schema")
        self._table = _validate_identifier(pg_cfg.table, "table")
        self._dimension = pg_cfg.embedding_dimension
        self._qualified_table = f"{self._schema}.{self._table}"
        self._engine = None
        self._init_lock = threading.Lock()
        self._store_ready = False

    def _database_url(self) -> str:
        url = get_app_settings().database.url
        if not url:
            raise RuntimeError("database.url is not configured for pgvector")
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg2://", 1)
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+psycopg2://", 1)
        return url

    def _engine_or_raise(self):
        if self._engine is None:
            self._engine = create_engine(
                self._database_url(),
                future=True,
                pool_pre_ping=True,
            )
        return self._engine

    def ensure_store(self, store_name: str) -> str:
        """Create extension, schema, and embeddings table if missing."""
        del store_name  # single shared table configured via YAML
        if self._store_ready:
            return self._qualified_table
        with self._init_lock:
            if self._store_ready:
                return self._qualified_table
            engine = self._engine_or_raise()
            with engine.begin() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {self._schema}"))
                conn.execute(
                    text(
                        f"""
                        CREATE TABLE IF NOT EXISTS {self._qualified_table} (
                            id BIGSERIAL PRIMARY KEY,
                            ebook_id TEXT,
                            title TEXT,
                            author TEXT,
                            metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb,
                            content TEXT NOT NULL,
                            embedding vector({self._dimension}) NOT NULL,
                            provider_file_id TEXT,
                            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                        )
                        """
                    )
                )
                conn.execute(
                    text(
                        f"""
                        CREATE INDEX IF NOT EXISTS idx_{self._table}_ebook_id
                        ON {self._qualified_table} (ebook_id)
                        """
                    )
                )
            self._store_ready = True
            LOGGER.info("PgVector store ready at %s", self._qualified_table)
        return self._qualified_table

    def ingest_file(self, file_path: str, attributes: dict) -> tuple[str, int]:
        with open(file_path, encoding="utf-8") as fh:
            text_content = fh.read()
        chunks = _chunk_text(text_content)
        if not chunks:
            return "", 0

        ebook_id = str(attributes.get("ebook_id") or "")
        title = str(attributes.get("title") or "")
        author = str(attributes.get("author") or "")
        provider_file_id = ebook_id or str(uuid.uuid4())
        embeddings = self.embedding_model.embed_documents(chunks)

        insert_sql = text(
            f"""
            INSERT INTO {self._qualified_table}
                (ebook_id, title, author, metadata, content, embedding, provider_file_id)
            VALUES
                (:ebook_id, :title, :author, CAST(:metadata AS jsonb), :content, :embedding, :provider_file_id)
            """
        )
        metadata = {k: str(v) for k, v in attributes.items() if v is not None}
        engine = self._engine_or_raise()
        with engine.begin() as conn:
            for chunk, embedding in zip(chunks, embeddings):
                conn.execute(
                    insert_sql,
                    {
                        "ebook_id": ebook_id or None,
                        "title": title or None,
                        "author": author or None,
                        "metadata": json.dumps(metadata),
                        "content": chunk,
                        "embedding": embedding,
                        "provider_file_id": provider_file_id,
                    },
                )
        LOGGER.info(
            "PgVector ingest complete: provider_file_id=%s chunks=%d",
            provider_file_id,
            len(chunks),
        )
        return provider_file_id, len(chunks)

    def search(
        self,
        query: str,
        top_k: int = 5,
        filters: dict | None = None,
    ) -> list[dict[str, Any]]:
        query_embedding = self.embedding_model.embed_query(query)
        where_sql, params = _filters_to_sql(filters or {})
        params["query_embedding"] = query_embedding
        params["top_k"] = top_k

        sql = f"""
            SELECT content,
                   metadata,
                   provider_file_id,
                   1 - (embedding <=> CAST(:query_embedding AS vector({self._dimension}))) AS score
            FROM {self._qualified_table}
            {where_sql}
            ORDER BY embedding <=> CAST(:query_embedding AS vector({self._dimension}))
            LIMIT :top_k
        """
        engine = self._engine_or_raise()
        with engine.connect() as conn:
            rows = conn.execute(text(sql), params).mappings().all()

        hits: list[dict[str, Any]] = []
        for row in rows:
            metadata = dict(row["metadata"] or {})
            hits.append(
                {
                    "text": row["content"] or "",
                    "score": float(row["score"] or 0.0),
                    "metadata": metadata,
                    "provider_file_id": row["provider_file_id"] or "",
                }
            )
        return hits


def _chunk_text(text_content: str, chunk_size: int = _CHUNK_SIZE, overlap: int = _CHUNK_OVERLAP) -> list[str]:
    text_content = text_content.strip()
    if not text_content:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(text_content):
        end = min(start + chunk_size, len(text_content))
        chunks.append(text_content[start:end])
        if end >= len(text_content):
            break
        start = max(end - overlap, start + 1)
    return chunks


def _filters_to_sql(filters: dict) -> tuple[str, dict[str, Any]]:
    clause, params = _filter_clause(filters, 0)
    if not clause:
        return "", {}
    return f"WHERE {clause}", params


def _filter_clause(filters: dict, index: int) -> tuple[str, dict[str, Any]]:
    filter_type = filters.get("type")
    if filter_type == "eq":
        key = str(filters.get("key", ""))
        if not _IDENTIFIER_RE.match(key):
            raise ValueError(f"Invalid metadata filter key: {key!r}")
        param_name = f"filter_{index}"
        return (
            f"metadata->>'{key}' = :{param_name}",
            {param_name: str(filters.get("value", ""))},
        )
    if filter_type == "and":
        sub_filters = filters.get("filters") or []
        clauses: list[str] = []
        params: dict[str, Any] = {}
        for sub_filter in sub_filters:
            clause, sub_params = _filter_clause(sub_filter, index + len(params))
            if clause:
                clauses.append(clause)
                params.update(sub_params)
        if not clauses:
            return "", {}
        return f"({' AND '.join(clauses)})", params
    return "", {}
