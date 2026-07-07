import logging
import threading

from book_ingest.config.settings import BookIngestSettings
from common.di import component
from common.interfaces.book_repositories import AppStateRepository
from config.app_settings import get_app_settings

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
        self._openai_cfg = get_app_settings().vector_store.openai
        self._client = None
        self._lock = threading.Lock()

    def _client_or_raise(self):
        if self._client is None:
            api_key = self._openai_cfg.api_key
            if not api_key:
                raise RuntimeError("OpenAI API key not configured")
            from openai import OpenAI
            kwargs: dict = {"api_key": api_key}
            if self._openai_cfg.base_url:
                kwargs["base_url"] = self._openai_cfg.base_url
            if self._openai_cfg.org_id:
                kwargs["organization"] = self._openai_cfg.org_id
            self._client = OpenAI(**kwargs)
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

    def search(
        self,
        vector_store_id: str,
        query: str,
        top_k: int = 5,
        filters: dict | None = None,
    ) -> list[dict]:
        """Run a semantic search against an OpenAI vector store."""
        client = self._client_or_raise()
        kwargs: dict = {"query": query, "max_num_results": top_k}
        if filters:
            kwargs["filters"] = filters
        page = client.vector_stores.search(vector_store_id=vector_store_id, **kwargs)
        hits: list[dict] = []
        for item in page.data:
            hits.append({
                "text": self._extract_hit_text(item),
                "score": float(getattr(item, "score", 0.0) or 0.0),
                "metadata": dict(getattr(item, "attributes", None) or {}),
                "provider_file_id": getattr(item, "file_id", "") or "",
            })
        return hits

    @staticmethod
    def _extract_hit_text(item) -> str:
        content = getattr(item, "content", None) or []
        parts: list[str] = []
        for chunk in content:
            text = getattr(chunk, "text", None)
            if text:
                parts.append(text)
                continue
            if isinstance(chunk, dict) and chunk.get("text"):
                parts.append(chunk["text"])
        return "\n".join(parts)
