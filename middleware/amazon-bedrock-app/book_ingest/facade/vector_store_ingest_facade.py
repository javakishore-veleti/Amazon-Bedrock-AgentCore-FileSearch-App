import logging

from common.di import component
from common.interfaces.book_facades import VectorStoreIngestFacade
from common.objects_factory import OBJECTS_FACTORY
from book_ingest.models.domain import BookIngestMessage
from book_ingest.models.dtos import (
    IngestPendingReq,
    IngestPendingResp,
    IngestStatusResp,
)
from configs.end_points_master import VECTOR_STORE_TYPE

LOGGER = logging.getLogger(__name__)


@component(
    key="VectorStoreIngestFacade",
    depends_on=[
        "VectorIngestManifestRepository",
        "VectorIngestTargetRepository",
        "IngestMessagePublisher",
        "IngestConsumerManager",
        "IngestQueueFacade",
        "AppCacheSvc",
        "BookIngestSettings",
    ],
)
class VectorStoreIngestFacadeImpl(VectorStoreIngestFacade):
    def __init__(self, manifest_repo, target_repo, publisher, consumer_manager,
                 queue_facade, app_cache, settings):
        self.manifest_repo = manifest_repo
        self.target_repo = target_repo
        self.publisher = publisher
        self.consumer_manager = consumer_manager
        self.queue_facade = queue_facade
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

        # Ensure-store task: make sure each target store exists (create if not),
        # once, before processing the books.
        store_ids = {store: self._ensure_store(store) for store in stores}

        books = self.manifest_repo.find_pending_books(req.limit)
        queued = 0
        for book in books:
            for store in stores:
                vs_id = store_ids[store]
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

    def status(self) -> IngestStatusResp:
        return IngestStatusResp(
            counts_by_status=self.manifest_repo.count_by_status(),
            consumers_running=self.consumer_manager.running(),
            queue_depth=self.queue_facade.all_depths(),
        )

    def _is_available(self, store_name: str) -> bool:
        object_id = self.app_cache.get(VECTOR_STORE_TYPE, store_name)
        return bool(object_id) and OBJECTS_FACTORY.has(object_id)

    def _ensure_store(self, store_name: str) -> str:
        """Resolve the store's adapter and ensure its backing store exists."""
        object_id = self.app_cache.get(VECTOR_STORE_TYPE, store_name)
        adapter = OBJECTS_FACTORY.get(object_id)
        return adapter.ensure_store(store_name)
