import logging
import os

from book_ingest.config.settings import BookIngestSettings
from common.di import component

LOGGER = logging.getLogger(__name__)

_CHUNKING_STRATEGY = {
    "type": "static",
    "static": {"max_chunk_size_tokens": 1000, "chunk_overlap_tokens": 200},
}


@component(key="OpenAIVectorStoreClient", depends_on=["BookIngestSettings"])
class OpenAIVectorStoreClient:
    """Thin wrapper over the OpenAI SDK: upload a file and attach it to a
    vector store. The SDK client is created lazily so the app boots without
    credentials."""

    def __init__(self, settings: BookIngestSettings):
        self.settings = settings
        self._client = None

    def _client_or_raise(self):
        if self._client is None:
            api_key = os.getenv("VECTOR_DB_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError("OpenAI API key not configured")
            from openai import OpenAI
            self._client = OpenAI(api_key=api_key)
        return self._client

    def ensure_vector_store(self, vector_store_id: str, name: str) -> str:
        if vector_store_id:
            return vector_store_id
        client = self._client_or_raise()
        vs = client.vector_stores.create(name=name)
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
