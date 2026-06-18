import logging

from common.interfaces.book_facades import VectorStoreIngestFacade
from book_ingest.models.domain import BookIngestMessage
from book_ingest.models.dtos import IngestPendingReq, IngestPendingResp
from common.di import component
from common.objects_factory import OBJECTS_FACTORY
from configs.end_points_master import OPENAPI_VECTOR_STORE, VECTOR_STORE_TYPE

LOGGER = logging.getLogger(__name__)


@component(
    key="VectorStoreIngestFacade",
    depends_on=[
        "VectorIngestManifestRepository",
        "VectorIngestTargetRepository",
        "IngestMessagePublisher",
        "IngestConsumerManager",
        "AppCacheSvc",
        "BookIngestSettings",
    ],
)
class VectorStoreIngestFacadeImpl(VectorStoreIngestFacade):
    def __init__(self, manifest_repo, target_repo, publisher, consumer_manager,
                 app_cache, settings):
        self.manifest_repo = manifest_repo
        self.target_repo = target_repo
        self.publisher = publisher
        self.consumer_manager = consumer_manager
        self.app_cache = app_cache
        self.settings = settings

    def queue_pending(self, req: IngestPendingReq) -> IngestPendingResp:
        requested = req.vector_stores or self.settings.target_vector_stores
        stores = [s for s in requested if self._is_available(s)]
        if not stores:
            return IngestPendingResp(
                request_id=req.request_id, status="rejected", queued_count=0,
                consumer_started=False, consumer_count=0, vector_stores=[],
                message="No requested vector stores are available/registered",
            )

        books = self.manifest_repo.find_pending_books(req.limit)
        queued = 0
        for book in books:
            for store in stores:
                vs_id = self._vector_store_id_for(store)
                target_id = self.target_repo.upsert_queued(book["id"], store, vs_id)
                self.publisher.publish(BookIngestMessage(
                    manifest_id=book["id"],
                    source_url=book.get("source_page_url") or "",
                    txt_url=book["txt_url"],
                    title=book.get("title") or "",
                    author=book.get("author"),
                    ebook_id=book.get("ebook_id") or "",
                    vector_store_name=store,
                    target_id=target_id,
                    vector_store_id=vs_id,
                ))
                queued += 1
            self.manifest_repo.mark_queued(book["id"])

        consumer_count = req.consumer_count or self.settings.consumer_count
        started_any = False
        for store in stores:
            started_any = self.consumer_manager.start_if_not_running(
                store, consumer_count) or started_any

        LOGGER.info("books_queued=%d stores=%s consumer_count=%d",
                    queued, stores, consumer_count)
        return IngestPendingResp(
            request_id=req.request_id, status="accepted", queued_count=queued,
            consumer_started=started_any, consumer_count=consumer_count,
            vector_stores=stores, message="Pending books queued for ingestion",
        )

    def _is_available(self, store_name: str) -> bool:
        object_id = self.app_cache.get(VECTOR_STORE_TYPE, store_name)
        return bool(object_id) and OBJECTS_FACTORY.has(object_id)

    def _vector_store_id_for(self, store_name: str) -> str:
        object_id = self.app_cache.get(VECTOR_STORE_TYPE, store_name)
        if object_id == OPENAPI_VECTOR_STORE:
            return self.settings.openai_vector_store_id
        return ""
