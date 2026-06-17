import logging

from common.di import component
from common.dtos import VectorIngestReq, VectorIngestResp
from common.interfaces.vector_store import VectorStoreAdapter
from configs.end_points_master import OPENAPI_VECTOR_STORE

LOGGER = logging.getLogger(__name__)


@component(key=OPENAPI_VECTOR_STORE)
class OpenAIVectorStoreIngestFacade(VectorStoreAdapter):
    def __init__(self, vector_store_client=None):
        self.vector_store_client = vector_store_client

    def ingest(self, req: VectorIngestReq, resp: VectorIngestResp):
        LOGGER.info("OpenAI vector store ingest: %s", req.file_path)
        # TODO: load + chunk req.file_path, embed, and push to the OpenAI
        # vector store via self.vector_store_client.
        resp.status = "accepted"
        resp.message = "Ingestion accepted; pipeline not yet implemented"
        return resp
