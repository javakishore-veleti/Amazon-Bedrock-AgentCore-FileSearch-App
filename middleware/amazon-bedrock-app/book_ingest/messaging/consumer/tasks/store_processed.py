import logging
import os

from book_ingest.config.settings import BookIngestSettings
from book_ingest.models.task_dtos import BookIngestTaskReq, BookIngestTaskResp
from book_ingest.messaging.consumer.tasks.base import BookIngestTask

LOGGER = logging.getLogger(__name__)


class StoreProcessedTask(BookIngestTask):
    """Pipeline task: persist the cleaned text to the processed dir."""

    name = "store_processed"

    def __init__(self, settings: BookIngestSettings):
        self.settings = settings

    def execute(self, req: BookIngestTaskReq) -> BookIngestTaskResp:
        os.makedirs(self.settings.processed_dir, exist_ok=True)
        path = os.path.join(self.settings.processed_dir, f"pg{req.ebook_id}.txt")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(req.clean_text or "")
        return BookIngestTaskResp(processed_path=path)
