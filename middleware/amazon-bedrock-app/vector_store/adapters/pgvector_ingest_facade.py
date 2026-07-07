import logging
import os

from book_ingest.integrations.pgvector.client import PgVectorClient
from common.di import component
from common.dtos import (
    SearchHit,
    VectorIngestReq,
    VectorIngestResp,
    VectorSearchReq,
    VectorSearchResp,
)
from common.interfaces.vector_store import VectorStoreAdapter
from configs.end_points_master import PGVECTOR

LOGGER = logging.getLogger(__name__)


@component(key=PGVECTOR, depends_on=["PgVectorClient"])
class PgVectorVectorStoreIngestFacade(VectorStoreAdapter):
    """Ingests cleaned text into Postgres pgvector and runs local similarity search."""

    def __init__(self, pgvector_client: PgVectorClient):
        self.pgvector_client = pgvector_client

    def ensure_store(self, store_name: str) -> str:
        return self.pgvector_client.ensure_store(store_name)

    def ingest(self, req: VectorIngestReq, resp: VectorIngestResp):
        if not req.file_path or not os.path.exists(req.file_path):
            resp.status = "skipped"
            resp.message = "No file to ingest"
            return resp

        self.pgvector_client.ensure_store(req.vector_store_id or "PgVector")
        provider_file_id, ingested_count = self.pgvector_client.ingest_file(
            file_path=req.file_path,
            attributes=req.attributes,
        )
        resp.provider_file_id = provider_file_id
        resp.status = "completed" if ingested_count else "skipped"
        resp.message = f"Indexed {ingested_count} chunk(s) into pgvector"
        resp.ingested_count = ingested_count
        LOGGER.info(
            "PgVector ingest complete: provider_file_id=%s chunks=%d",
            provider_file_id,
            ingested_count,
        )
        return resp

    def search(self, req: VectorSearchReq, resp: VectorSearchResp):
        self.pgvector_client.ensure_store(req.vector_store_id or "PgVector")
        raw_hits = self.pgvector_client.search(
            query=req.query,
            top_k=req.top_k,
            filters=req.filters or None,
        )
        resp.query = req.query
        resp.hits = [SearchHit(**hit) for hit in raw_hits]
        resp.status = "completed"
        resp.message = f"Found {len(resp.hits)} result(s)"
        LOGGER.info("PgVector search complete: query=%r hits=%d", req.query, len(resp.hits))
        return resp
