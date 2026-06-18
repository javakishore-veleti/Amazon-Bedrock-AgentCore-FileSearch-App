import logging
import re

from common.interfaces.book_repositories import VectorIngestSectionRepository
from book_ingest.models.task_dtos import BookIngestTaskReq, BookIngestTaskResp
from common.interfaces.book_task import BookIngestTask

LOGGER = logging.getLogger(__name__)

_CHAPTER_RE = re.compile(r"(?im)^\s*(chapter\s+[\w.\-]+.*)$")


class SplitSectionsTask(BookIngestTask):
    """Pipeline task: split cleaned text into chapter sections and persist them."""

    name = "split_sections"

    def __init__(self, section_repo: VectorIngestSectionRepository):
        self.section_repo = section_repo

    def execute(self, req: BookIngestTaskReq) -> BookIngestTaskResp:
        sections = self._split(req.clean_text or "")
        self.section_repo.save_sections(req.manifest_id, sections)
        return BookIngestTaskResp(sections=sections)

    @staticmethod
    def _split(text: str) -> list:
        matches = list(_CHAPTER_RE.finditer(text))
        if not matches:
            return [{"section_type": "full", "section_title": "full",
                     "start_char": 0, "end_char": len(text)}]
        sections = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            title = match.group(1).strip()[:200]
            sections.append({
                "section_type": "chapter",
                "section_title": title,
                "chapter_title": title,
                "start_char": start,
                "end_char": end,
            })
        return sections
