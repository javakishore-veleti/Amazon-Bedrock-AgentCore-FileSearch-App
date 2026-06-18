import logging

from book_ingest.models.task_dtos import BookIngestTaskReq, BookIngestTaskResp
from book_ingest.service.interfaces import DuplicateDetectionService
from book_ingest.messaging.consumer.tasks.base import BookIngestTask

LOGGER = logging.getLogger(__name__)


class DuplicateCheckTask(BookIngestTask):
    """Task: is this content already indexed in this store (by hash)?"""

    name = "duplicate_check"

    def __init__(self, duplicate: DuplicateDetectionService):
        self.duplicate = duplicate

    def execute(self, req: BookIngestTaskReq) -> BookIngestTaskResp:
        is_dup = self.duplicate.is_duplicate_for_store(
            req.source_hash or "", req.vector_store_name
        )
        return BookIngestTaskResp(duplicate=is_dup,
                                  route="skip" if is_dup else "upload")
