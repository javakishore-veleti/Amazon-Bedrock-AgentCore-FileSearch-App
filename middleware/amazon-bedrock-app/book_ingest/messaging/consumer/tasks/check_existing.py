import logging

from book_ingest.dao.interfaces import VectorIngestTargetRepository
from book_ingest.models.statuses import ManifestStatus
from book_ingest.models.task_dtos import BookIngestTaskReq, BookIngestTaskResp
from book_ingest.messaging.consumer.tasks.base import BookIngestTask

LOGGER = logging.getLogger(__name__)

_TERMINAL = {ManifestStatus.IN_PROGRESS.value, ManifestStatus.INDEXED.value}


class CheckExistingIngestionTask(BookIngestTask):
    """Task 1: short-circuit if this book is already in-progress/indexed here."""

    name = "check_existing"

    def __init__(self, target_repo: VectorIngestTargetRepository):
        self.target_repo = target_repo

    def execute(self, req: BookIngestTaskReq) -> BookIngestTaskResp:
        status = self.target_repo.get_status(req.target_id)
        if status in _TERMINAL:
            LOGGER.info("skip ebook=%s store=%s already=%s",
                        req.ebook_id, req.vector_store_name, status)
            return BookIngestTaskResp(terminal=True, status=f"ALREADY_{status}")
        return BookIngestTaskResp(terminal=False)
