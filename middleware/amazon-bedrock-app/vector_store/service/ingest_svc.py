import logging

from common.di import component
from common.dtos import IngestReq, IngestResp, VectorIngestReq, VectorIngestResp
from common.interfaces.app_cache import AppCacheSvc
from common.interfaces.ingest import IngestService
from common.interfaces.vector_store import VectorStoreAdapter
from common.objects_factory import OBJECTS_FACTORY
from configs.end_points_master import VECTOR_STORE_TYPE

LOGGER = logging.getLogger(__name__)


@component(key=IngestService.__name__, depends_on=[AppCacheSvc.__name__])
class IngestServiceImpl(IngestService):
    def __init__(self, app_cache: AppCacheSvc):
        self.app_cache = app_cache

    def ingest(self, req: IngestReq) -> IngestResp:
        adapter = self._resolve_adapter(req.target_vector_store)

        vec_resp = VectorIngestResp(request_id=req.request_id)
        adapter.ingest(
            VectorIngestReq(
                request_id=req.request_id,
                file_path=req.file_path,
                file_type=req.file_type,
            ),
            vec_resp,
        )

        return IngestResp(
            request_id=req.request_id,
            status=vec_resp.status or "accepted",
            target_vector_store=req.target_vector_store,
            file_path=req.file_path,
            message=vec_resp.message,
        )

    def list_supported_stores(self) -> list[str]:
        """Cached store names whose impl is registered in the factory."""
        cached = self.app_cache.get_all(VECTOR_STORE_TYPE)
        return [name for name, oid in cached.items() if OBJECTS_FACTORY.has(oid)]

    def _resolve_adapter(self, store_name: str) -> VectorStoreAdapter:
        """Cache lookup: store name -> object_id -> adapter impl (factory)."""
        object_id = self.app_cache.get(VECTOR_STORE_TYPE, store_name)
        if object_id is None or not OBJECTS_FACTORY.has(object_id):
            raise ValueError(
                f"Unsupported or unavailable vector store '{store_name}'. "
                f"Available: {self.list_supported_stores()}"
            )
        return OBJECTS_FACTORY.get(object_id)
