import logging

from book_ingest.dao.interfaces import VectorIngestLogRepository
from book_ingest.models.statuses import ManifestStatus
from book_ingest.models.task_dtos import BookIngestTaskReq, BookIngestTaskResp
from book_ingest.messaging.consumer.tasks.base import BookIngestTask

LOGGER = logging.getLogger(__name__)

_EVENT = {
    ManifestStatus.INDEXED.value: "book_ingest_completed",
    ManifestStatus.SKIPPED_DUPLICATE.value: "duplicate_skipped",
}


class FinalizeTask(BookIngestTask):
    """Task: write the terminal ingestion-log event."""

    name = "finalize"

    def __init__(self, log_repo: VectorIngestLogRepository):
        self.log_repo = log_repo

    def execute(self, req: BookIngestTaskReq) -> BookIngestTaskResp:
        event = _EVENT.get(req.status or "", "book_ingest_finished")
        self.log_repo.append(req.manifest_id, req.vector_store_name, event,
                             req.status or "")
        return BookIngestTaskResp()
