import logging

from book_ingest.config.paths import resolve_path
from common.di import component
from config.app_settings import get_app_settings

LOGGER = logging.getLogger(__name__)


@component(key="BookIngestSettings")
class BookIngestSettings:
    """Book ingest settings sourced from the shared profile configuration."""

    def __init__(self):
        app_settings = get_app_settings()
        self._cfg = dict(app_settings.book_ingest)
        self._database_url = app_settings.database.url
        self._openai_vector_store_id = app_settings.vector_store.openai.vector_store_id
        LOGGER.info(
            "Loaded book_ingest config from profile '%s'",
            app_settings.profile,
        )

    def get(self, *keys, default=None):
        node = self._cfg
        for key in keys:
            if not isinstance(node, dict) or key not in node:
                return default
            node = node[key]
        return node

    @property
    def batch_output_dir(self) -> str:
        return resolve_path(self.get("dataset", "novels", "batch_output_dir",
                                     default="DataSets/Novels/BatchFiles"))

    @property
    def raw_dir(self) -> str:
        return resolve_path(self.get("dataset", "novels", "raw_dir",
                                     default="DataSets/Novels/Raw"))

    @property
    def processed_dir(self) -> str:
        return resolve_path(self.get("dataset", "novels", "processed_dir",
                                     default="DataSets/Novels/Processed"))

    @property
    def batch_size(self) -> int:
        return int(self.get("dataset", "novels", "batch_size", default=1000))

    @property
    def database_url(self) -> str:
        url = self.get("database", "url") or self._database_url
        if url:
            return url
        path = self.get("database", "path", default="DataSets/db/vector_ingest.db")
        return f"sqlite:///{resolve_path(path)}"

    @property
    def consumer_count(self) -> int:
        return int(self.get("ingest", "consumer_count", default=10))

    @property
    def max_retries(self) -> int:
        return int(self.get("ingest", "max_retries", default=3))

    @property
    def poll_interval_seconds(self) -> float:
        return float(self.get("ingest", "poll_interval_seconds", default=2))

    @property
    def target_vector_stores(self) -> list[str]:
        return self.get("ingest", "target_vector_stores", default=["PgVector"])

    @property
    def openai_vector_store_id(self) -> str:
        return self._openai_vector_store_id or self.get("openai", "vector_store_id", default="")

    @property
    def gutenberg_top_100_url(self) -> str:
        return self.get("gutenberg", "top_100_url",
                        default="https://www.gutenberg.org/browse/scores/top")

    @property
    def gutenberg_user_agent(self) -> str:
        return self.get("gutenberg", "user_agent", default="BookVectorIngest/1.0")
