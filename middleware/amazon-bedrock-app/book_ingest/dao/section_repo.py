import logging
from datetime import datetime, timezone

from common.interfaces.book_repositories import VectorIngestSectionRepository
from book_ingest.db.database import BookIngestDatabase
from book_ingest.models.orm import VectorIngestSection
from common.di import component

LOGGER = logging.getLogger(__name__)


@component(key="VectorIngestSectionRepository", depends_on=["BookIngestDatabase"])
class VectorIngestSectionRepositoryImpl(VectorIngestSectionRepository):
    def __init__(self, database: BookIngestDatabase):
        self.database = database

    def save_sections(self, manifest_id, sections) -> None:
        with self.database.session() as s:
            for sec in sections:
                s.add(VectorIngestSection(
                    manifest_id=manifest_id,
                    section_type=sec.get("section_type"),
                    section_title=sec.get("section_title"),
                    chapter_title=sec.get("chapter_title"),
                    start_char=sec.get("start_char"),
                    end_char=sec.get("end_char"),
                    chunk_file_name=sec.get("chunk_file_name"),
                    openai_file_id=sec.get("openai_file_id"),
                    created_at=datetime.now(timezone.utc),
                ))
            s.commit()

    def update_section_file_id(self, section_id, openai_file_id) -> None:
        with self.database.session() as s:
            row = s.get(VectorIngestSection, section_id)
            if row:
                row.openai_file_id = openai_file_id
                s.commit()
