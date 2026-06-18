import logging
from datetime import datetime, timezone

from book_ingest.db.database import BookIngestDatabase
from book_ingest.models.orm import AppState
from common.di import component
from common.interfaces.book_repositories import AppStateRepository

LOGGER = logging.getLogger(__name__)


@component(key="AppStateRepository", depends_on=["BookIngestDatabase"])
class AppStateRepositoryImpl(AppStateRepository):
    def __init__(self, database: BookIngestDatabase):
        self.database = database

    def get(self, key: str) -> str | None:
        with self.database.session() as s:
            row = s.get(AppState, key)
            return row.value if row else None

    def set(self, key: str, value: str) -> None:
        with self.database.session() as s:
            row = s.get(AppState, key)
            if row:
                row.value = value
            else:
                row = AppState(key=key, value=value)
                s.add(row)
            row.updated_at = datetime.now(timezone.utc)
            s.commit()
