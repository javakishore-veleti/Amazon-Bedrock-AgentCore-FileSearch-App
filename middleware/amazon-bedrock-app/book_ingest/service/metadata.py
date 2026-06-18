import logging
import re

from book_ingest.models.domain import BookIngestMessage
from book_ingest.service.interfaces import BookMetadataExtractionService
from common.di import component

LOGGER = logging.getLogger(__name__)

_LANG_RE = re.compile(r"^\s*Language:\s*(.+)$", re.MULTILINE)
_TITLE_RE = re.compile(r"^\s*Title:\s*(.+)$", re.MULTILINE)
_AUTHOR_RE = re.compile(r"^\s*Author:\s*(.+)$", re.MULTILINE)


@component(key="BookMetadataExtractionService")
class BookMetadataExtractionServiceImpl(BookMetadataExtractionService):
    def extract(self, clean_text: str, message: BookIngestMessage) -> dict:
        head = clean_text[:5000]
        title = self._first(_TITLE_RE, head) or message.title
        author = self._first(_AUTHOR_RE, head) or message.author
        language = self._first(_LANG_RE, head) or "en"
        return {
            "title": title,
            "author": author,
            "language": language,
            "ebook_id": message.ebook_id,
            "source": "Project Gutenberg",
            "source_page_url": message.source_url,
            "txt_url": message.txt_url,
        }

    @staticmethod
    def _first(pattern, text):
        m = pattern.search(text)
        return m.group(1).strip() if m else None
