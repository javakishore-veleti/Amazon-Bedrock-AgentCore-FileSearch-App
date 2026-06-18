import logging
import os
import threading

from book_ingest.config.settings import BookIngestSettings
from common.di import component
from common.interfaces.book_repositories import AppStateRepository

LOGGER = logging.getLogger(__name__)

_CHUNKING_STRATEGY = {
    "type": "static",
    "static": {"max_chunk_size_tokens": 1000, "chunk_overlap_tokens": 200},
}
_STATE_KEY = "openai_vector_store_id"


@component(key="OpenAIVectorStoreClient",
           depends_on=["BookIngestSettings", "AppStateRepository"])
class OpenAIVectorStoreClient:
    """Thin wrapper over the OpenAI SDK. Lazily creates the SDK client and the
    vector store, persisting an auto-created store id so redeploys / new
    machines reuse it instead of creating duplicates."""

    def __init__(self, settings: BookIngestSettings, app_state: AppStateRepository):
        self.settings = settings
        self.app_state = app_state
        self._client = None
        self._lock = threading.Lock()

    def _client_or_raise(self):
        if self._client is None:
            api_key = os.getenv("VECTOR_DB_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError("OpenAI API key not configured")
            from openai import OpenAI
            self._client = OpenAI(api_key=api_key)
        return self._client

    def ensure_vector_store(self, name: str) -> str:
        """Return a usable vector store id, creating one if needed.

        Order: configured id (env/config) -> persisted auto-created id ->
        create a new store and persist its id.
        """
        configured = self.settings.openai_vector_store_id
        if configured:
            return configured
        saved = self.app_state.get(_STATE_KEY)
        if saved:
            return saved
        with self._lock:
            saved = self.app_state.get(_STATE_KEY)
            if saved:
                return saved
            vs = self._client_or_raise().vector_stores.create(name=name)
            self.app_state.set(_STATE_KEY, vs.id)
            LOGGER.info("Created OpenAI vector store %s (%s)", vs.id, name)
            return vs.id

    def upload_and_attach(self, file_path: str, vector_store_id: str,
                          attributes: dict) -> tuple[str, str]:
        client = self._client_or_raise()
        with open(file_path, "rb") as fh:
            uploaded = client.files.create(file=fh, purpose="assistants")
        vs_file = client.vector_stores.files.create_and_poll(
            vector_store_id=vector_store_id,
            file_id=uploaded.id,
            attributes=attributes,
            chunking_strategy=_CHUNKING_STRATEGY,
        )
        status = getattr(vs_file, "status", "completed")
        last_error = getattr(vs_file, "last_error", None)
        if last_error:
            raise RuntimeError(f"OpenAI indexing error: {last_error}")
        return uploaded.id, status
