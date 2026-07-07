import logging

from book_ingest.config.settings import BookIngestSettings
from common.di import component
from common.dtos import VectorSearchReq, VectorSearchResp
from common.interfaces.app_cache import AppCacheSvc
from common.interfaces.search import SearchFacade
from common.objects_factory import OBJECTS_FACTORY
from configs.end_points_master import VECTOR_STORE_TYPE
from search.models.dtos import SearchReq, SearchResp

LOGGER = logging.getLogger(__name__)


def _build_metadata_filters(ebook_id: str, author: str) -> dict:
    """Build an OpenAI vector-store metadata filter from optional fields."""
    clauses: list[dict] = []
    if ebook_id:
        clauses.append({"type": "eq", "key": "ebook_id", "value": ebook_id})
    if author:
        clauses.append({"type": "eq", "key": "author", "value": author})
    if not clauses:
        return {}
    if len(clauses) == 1:
        return clauses[0]
    return {"type": "and", "filters": clauses}


@component(
    key="SearchFacade",
    depends_on=["AppCacheSvc", "BookIngestSettings"],
)
class SearchFacadeImpl(SearchFacade):
    """Routes search requests to the configured vector-store adapter."""

    def __init__(self, app_cache: AppCacheSvc, settings: BookIngestSettings):
        self.app_cache = app_cache
        self.settings = settings

    def search(self, req: SearchReq) -> SearchResp:
        store_name = req.vector_store_name or self._default_store_name()
        adapter = self._resolve_adapter(store_name)
        vector_store_id = adapter.ensure_store(store_name)
        filters = _build_metadata_filters(req.ebook_id, req.author)

        adapter_resp = VectorSearchResp(request_id=req.request_id)
        adapter.search(
            VectorSearchReq(
                request_id=req.request_id,
                query=req.query,
                vector_store_id=vector_store_id,
                top_k=req.top_k,
                filters=filters,
            ),
            adapter_resp,
        )

        LOGGER.info(
            "search complete store=%r query=%r hits=%d",
            store_name,
            req.query,
            len(adapter_resp.hits),
        )
        return SearchResp(
            request_id=req.request_id,
            query=req.query,
            vector_store_name=store_name,
            hits=adapter_resp.hits,
            message=adapter_resp.message,
        )

    def _default_store_name(self) -> str:
        stores = self.settings.target_vector_stores
        if not stores:
            raise ValueError("No default vector store configured")
        return stores[0]

    def _resolve_adapter(self, store_name: str):
        object_id = self.app_cache.get(VECTOR_STORE_TYPE, store_name)
        if not object_id or not OBJECTS_FACTORY.has(object_id):
            raise ValueError(f"No search adapter registered for '{store_name}'")
        return OBJECTS_FACTORY.get(object_id)
