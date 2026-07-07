"""Local sentence-transformer embeddings (no OpenAI vector cost)."""

from __future__ import annotations

import logging
import threading

from common.di import component
from config.app_settings import get_app_settings

LOGGER = logging.getLogger(__name__)


@component(key="LocalEmbeddingModel")
class LocalEmbeddingModel:
    """Singleton embedding engine; model is loaded lazily on first use."""

    def __init__(self):
        cfg = get_app_settings().vector_store.pgvector
        self._model_name = cfg.embedding_model
        self._dimension = cfg.embedding_dimension
        self._model = None
        self._lock = threading.Lock()

    @property
    def dimension(self) -> int:
        return self._dimension

    def _model_or_raise(self):
        if self._model is None:
            with self._lock:
                if self._model is None:
                    from sentence_transformers import SentenceTransformer

                    LOGGER.info("Loading embedding model %s", self._model_name)
                    self._model = SentenceTransformer(self._model_name)
        return self._model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors = self._model_or_raise().encode(texts, normalize_embeddings=True)
        return [vector.tolist() for vector in vectors]

    def embed_query(self, query: str) -> list[float]:
        return self.embed_documents([query])[0]
