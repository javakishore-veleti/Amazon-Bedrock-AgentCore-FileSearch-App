import logging

from book_ingest.dao.interfaces import VectorIngestTargetRepository
from book_ingest.models.statuses import ManifestStatus
from book_ingest.models.task_dtos import BookIngestTaskReq, BookIngestTaskResp
from book_ingest.messaging.consumer.tasks.base import BookIngestTask

LOGGER = logging.getLogger(__name__)


class SkipDuplicateTask(BookIngestTask):
    """Task: mark the target SKIPPED_DUPLICATE."""

    name = "skip_duplicate"

    def __init__(self, target_repo: VectorIngestTargetRepository):
        self.target_repo = target_repo

    def execute(self, req: BookIngestTaskReq) -> BookIngestTaskResp:
        self.target_repo.mark_skipped_duplicate(req.target_id)
        return BookIngestTaskResp(status=ManifestStatus.SKIPPED_DUPLICATE.value)
