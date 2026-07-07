import logging
import os

from common.di import component
from common.dtos import (
    SearchHit,
    VectorIngestReq,
    VectorIngestResp,
    VectorSearchReq,
    VectorSearchResp,
)
from common.interfaces.vector_store import VectorStoreAdapter
from configs.end_points_master import OPENAPI_VECTOR_STORE

LOGGER = logging.getLogger(__name__)


@component(key=OPENAPI_VECTOR_STORE, depends_on=["OpenAIVectorStoreClient"])
class OpenAIVectorStoreIngestFacade(VectorStoreAdapter):
    """Ingests a cleaned text file into an OpenAI Vector Store."""

    def __init__(self, openai_client):
        self.openai_client = openai_client

    def ensure_store(self, store_name: str) -> str:
        return self.openai_client.ensure_vector_store(store_name)

    def ingest(self, req: VectorIngestReq, resp: VectorIngestResp):
        if not req.file_path or not os.path.exists(req.file_path):
            resp.status = "skipped"
            resp.message = "No file to ingest"
            return resp

        # Use the id ensured at queue time; fall back to ensuring one.
        vector_store_id = req.vector_store_id or self.openai_client.ensure_vector_store(
            "Book Vector Store"
        )
        file_id, status = self.openai_client.upload_and_attach(
            file_path=req.file_path,
            vector_store_id=vector_store_id,
            attributes=req.attributes,
        )
        resp.provider_file_id = file_id
        resp.status = status or "completed"
        resp.message = "Indexed into OpenAI vector store"
        resp.ingested_count = 1
        LOGGER.info("OpenAI ingest complete: file_id=%s status=%s", file_id, status)
        return resp

    def search(self, req: VectorSearchReq, resp: VectorSearchResp):
        vector_store_id = req.vector_store_id or self.openai_client.ensure_vector_store(
            "Book Vector Store"
        )
        raw_hits = self.openai_client.search(
            vector_store_id=vector_store_id,
            query=req.query,
            top_k=req.top_k,
            filters=req.filters or None,
        )
        resp.query = req.query
        resp.hits = [SearchHit(**hit) for hit in raw_hits]
        resp.status = "completed"
        resp.message = f"Found {len(resp.hits)} result(s)"
        LOGGER.info("OpenAI search complete: query=%r hits=%d", req.query, len(resp.hits))
        return resp
