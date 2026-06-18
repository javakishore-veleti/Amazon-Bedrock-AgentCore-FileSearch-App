import logging

from book_ingest.integrations.gutenberg.client import GutenbergClient
from book_ingest.models.task_dtos import BookIngestTaskReq, BookIngestTaskResp
from book_ingest.facade.tasks.base import BookIngestTask

LOGGER = logging.getLogger(__name__)


class FetchTextTask(BookIngestTask):
    """Task: fetch the raw .txt content from Gutenberg."""

    name = "fetch_text"

    def __init__(self, gutenberg: GutenbergClient):
        self.gutenberg = gutenberg

    def execute(self, req: BookIngestTaskReq) -> BookIngestTaskResp:
        raw = self.gutenberg.fetch_text(req.txt_url)
        return BookIngestTaskResp(raw_text=raw)
