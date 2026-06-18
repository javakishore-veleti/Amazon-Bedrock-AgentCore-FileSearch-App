import logging

from book_ingest.dao.interfaces import (
    VectorIngestLogRepository,
    VectorIngestTargetRepository,
)
from book_ingest.models.statuses import ManifestStatus
from book_ingest.models.task_dtos import BookIngestTaskReq, BookIngestTaskResp
from book_ingest.facade.tasks.base import BookIngestTask

LOGGER = logging.getLogger(__name__)


class LockAndLogTask(BookIngestTask):
    """Task 2: create an ingestion log entry and mark the target IN_PROGRESS."""

    name = "lock_and_log"

    def __init__(self, log_repo: VectorIngestLogRepository,
                 target_repo: VectorIngestTargetRepository):
        self.log_repo = log_repo
        self.target_repo = target_repo

    def execute(self, req: BookIngestTaskReq) -> BookIngestTaskResp:
        self.log_repo.append(req.manifest_id, req.vector_store_name,
                             "book_ingest_started", req.txt_url)
        self.target_repo.mark_in_progress(req.target_id)
        return BookIngestTaskResp(status=ManifestStatus.IN_PROGRESS.value)
