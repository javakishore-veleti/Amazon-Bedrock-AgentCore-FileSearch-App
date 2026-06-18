import logging
import os

from book_ingest.config.settings import BookIngestSettings
from book_ingest.models.task_dtos import BookIngestTaskReq, BookIngestTaskResp
from common.interfaces.book_task import BookIngestTask

LOGGER = logging.getLogger(__name__)


class StoreRawTask(BookIngestTask):
    """Pipeline task: persist the raw fetched .txt to the raw dir."""

    name = "store_raw"

    def __init__(self, settings: BookIngestSettings):
        self.settings = settings

    def execute(self, req: BookIngestTaskReq) -> BookIngestTaskResp:
        os.makedirs(self.settings.raw_dir, exist_ok=True)
        path = os.path.join(self.settings.raw_dir, f"pg{req.ebook_id}.txt")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(req.raw_text or "")
        return BookIngestTaskResp(raw_path=path)
