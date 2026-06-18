import logging

from common.di import component
from common.interfaces.book_facades import BookPipelineFacade
from book_ingest.models.dtos import (
    DatasetBuildReq,
    IngestPendingReq,
    ManifestBuildReq,
    RunAllReq,
)

LOGGER = logging.getLogger(__name__)


@component(
    key="BookPipelineFacade",
    depends_on=["DatasetManifestBuildFacade", "VectorStoreIngestFacade"],
)
class BookPipelineFacadeImpl(BookPipelineFacade):
    """One-click pipeline: dataset build -> manifest build -> ingest pending."""

    def __init__(self, dataset_facade, ingest_facade):
        self.dataset_facade = dataset_facade
        self.ingest_facade = ingest_facade

    def run_all(self, req: RunAllReq) -> dict:
        dataset = self.dataset_facade.build_dataset(
            DatasetBuildReq(target_count=req.target_count, overwrite=req.overwrite)
        )
        manifest = self.dataset_facade.build_manifest(ManifestBuildReq())
        ingest = self.ingest_facade.queue_pending(
            IngestPendingReq(limit=req.limit, vector_stores=req.vector_stores,
                             consumer_count=req.consumer_count)
        )
        LOGGER.info("run_all complete: written=%s inserted=%s queued=%s",
                    dataset.books_written, manifest.records_inserted,
                    ingest.queued_count)
        return {
            "dataset": dataset.model_dump(),
            "manifest": manifest.model_dump(),
            "ingest": ingest.model_dump(),
        }
