import logging

from book_ingest.models.task_dtos import BookIngestTaskReq, BookIngestTaskResp
from book_ingest.messaging.consumer.tasks.base import BookIngestTask

LOGGER = logging.getLogger(__name__)

_REQUIRED = ("manifest_id", "target_id", "txt_url", "vector_store_name")


class ValidateMessageTask(BookIngestTask):
    """Lifecycle task 1: validate the incoming message has required fields."""

    name = "validate_message"

    def execute(self, req: BookIngestTaskReq) -> BookIngestTaskResp:
        missing = [field for field in _REQUIRED if not getattr(req, field)]
        if missing:
            raise ValueError(f"Invalid ingest message; missing: {missing}")
        return BookIngestTaskResp()
