import logging

from book_ingest.models.task_dtos import BookIngestTaskReq, BookIngestTaskResp
from common.interfaces.book_services import GutenbergTextCleaningService
from common.interfaces.book_task import BookIngestTask

LOGGER = logging.getLogger(__name__)


class CleanTextTask(BookIngestTask):
    """Task: strip Gutenberg boilerplate and normalize whitespace."""

    name = "clean_text"

    def __init__(self, cleaning: GutenbergTextCleaningService):
        self.cleaning = cleaning

    def execute(self, req: BookIngestTaskReq) -> BookIngestTaskResp:
        clean = self.cleaning.clean(req.raw_text or "")
        return BookIngestTaskResp(clean_text=clean)
