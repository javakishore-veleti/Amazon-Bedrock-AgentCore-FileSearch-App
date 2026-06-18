import logging
from datetime import datetime, timezone

from common.interfaces.book_repositories import VectorIngestLogRepository
from book_ingest.db.database import BookIngestDatabase
from book_ingest.models.orm import VectorIngestLog
from common.di import component

LOGGER = logging.getLogger(__name__)


@component(key="VectorIngestLogRepository", depends_on=["BookIngestDatabase"])
class VectorIngestLogRepositoryImpl(VectorIngestLogRepository):
    def __init__(self, database: BookIngestDatabase):
        self.database = database

    def append(self, manifest_id, vector_store_name, event, message="") -> None:
        with self.database.session() as s:
            s.add(VectorIngestLog(
                manifest_id=manifest_id,
                vector_store_name=vector_store_name,
                event=event,
                message=message,
                created_at=datetime.now(timezone.utc),
            ))
            s.commit()
