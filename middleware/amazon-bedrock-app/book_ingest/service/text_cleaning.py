import logging
import re

from book_ingest.service.interfaces import GutenbergTextCleaningService
from common.di import component

LOGGER = logging.getLogger(__name__)

_START_MARKER = "*** START OF THE PROJECT GUTENBERG EBOOK"
_END_MARKER = "*** END OF THE PROJECT GUTENBERG EBOOK"


@component(key="GutenbergTextCleaningService")
class GutenbergTextCleaningServiceImpl(GutenbergTextCleaningService):
    def clean(self, raw_text: str) -> str:
        text = raw_text

        start = text.find(_START_MARKER)
        if start != -1:
            nl = text.find("\n", start)
            text = text[nl + 1:] if nl != -1 else text[start + len(_START_MARKER):]

        end = text.find(_END_MARKER)
        if end != -1:
            text = text[:end]

        # Normalize whitespace safely (do NOT collapse all newlines).
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{4,}", "\n\n\n", text)
        return text.strip()
