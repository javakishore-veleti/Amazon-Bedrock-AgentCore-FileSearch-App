import logging
import os
from pathlib import Path

import yaml

from common.di import component

LOGGER = logging.getLogger(__name__)

_DEFAULT_CONFIG = Path(__file__).with_name("app_config.yaml")


@component(key="BookIngestSettings")
class BookIngestSettings:
    """Loads book_ingest config from YAML with selective env overrides."""

    def __init__(self):
        path = os.getenv("BOOK_INGEST_CONFIG", str(_DEFAULT_CONFIG))
        with open(path) as fh:
            self._cfg = yaml.safe_load(fh) or {}
        self._apply_env_overrides()
        LOGGER.info("Loaded book_ingest config from %s", path)

    def _apply_env_overrides(self):
        vs_id = os.getenv("VECTOR_DB_OPENAI_VECTOR_STORE_ID")
        if vs_id:
            self._cfg.setdefault("openai", {})["vector_store_id"] = vs_id
        db_url = os.getenv("BOOK_INGEST_DB_URL")
        if db_url:
            self._cfg.setdefault("database", {})["url"] = db_url

    def get(self, *keys, default=None):
        node = self._cfg
        for key in keys:
            if not isinstance(node, dict) or key not in node:
                return default
            node = node[key]
        return node

    @property
    def batch_output_dir(self) -> str:
        return self.get("dataset", "novels", "batch_output_dir",
                        default="DataSets/Novels/BatchFiles")

    @property
    def raw_dir(self) -> str:
        return self.get("dataset", "novels", "raw_dir", default="DataSets/Novels/Raw")

    @property
    def processed_dir(self) -> str:
        return self.get("dataset", "novels", "processed_dir",
                        default="DataSets/Novels/Processed")

    @property
    def batch_size(self) -> int:
        return int(self.get("dataset", "novels", "batch_size", default=1000))

    @property
    def database_url(self) -> str:
        return self.get("database", "url", default="sqlite:///./data/vector_ingest.db")

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
        return self.get("ingest", "target_vector_stores",
                        default=["OpenAPI Vector Store"])

    @property
    def openai_vector_store_id(self) -> str:
        return self.get("openai", "vector_store_id", default="")

    @property
    def gutenberg_top_100_url(self) -> str:
        return self.get("gutenberg", "top_100_url",
                        default="https://www.gutenberg.org/browse/scores/top")

    @property
    def gutenberg_user_agent(self) -> str:
        return self.get("gutenberg", "user_agent", default="BookVectorIngest/1.0")
