import logging
import os
from urllib.parse import urlparse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from book_ingest.config.settings import BookIngestSettings
from book_ingest.models.orm import Base
from common.di import component

LOGGER = logging.getLogger(__name__)


@component(key="BookIngestDatabase", depends_on=["BookIngestSettings"])
class BookIngestDatabase:
    """Owns the SQLAlchemy engine + session factory. Creates tables on startup.

    Swappable by database url/type via config (SQLite now, Postgres/Aurora
    later). Alembic is the migration tool of record; create_all here keeps the
    default SQLite setup runnable out of the box.
    """

    def __init__(self, settings: BookIngestSettings):
        self.url = settings.database_url
        self._ensure_sqlite_dir(self.url)
        connect_args = {}
        if self.url.startswith("sqlite"):
            # Consumers run in worker threads; allow cross-thread use.
            connect_args = {"check_same_thread": False, "timeout": 30}
        self.engine = create_engine(self.url, future=True, connect_args=connect_args)
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)
        Base.metadata.create_all(self.engine)
        LOGGER.info("Database ready: %s", self.url)

    @staticmethod
    def _ensure_sqlite_dir(url: str):
        if url.startswith("sqlite") and ":///" in url:
            path = url.split(":///", 1)[1]
            directory = os.path.dirname(path)
            if directory:
                os.makedirs(directory, exist_ok=True)

    def session(self):
        return self.session_factory()
