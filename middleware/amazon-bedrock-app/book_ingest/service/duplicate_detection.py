import hashlib
import logging

from book_ingest.dao.interfaces import VectorIngestTargetRepository
from book_ingest.service.interfaces import DuplicateDetectionService
from common.di import component

LOGGER = logging.getLogger(__name__)


@component(key="DuplicateDetectionService",
           depends_on=["VectorIngestTargetRepository"])
class DuplicateDetectionServiceImpl(DuplicateDetectionService):
    def __init__(self, target_repo: VectorIngestTargetRepository):
        self.target_repo = target_repo

    def compute_hash(self, clean_text: str) -> str:
        return hashlib.sha256(clean_text.encode("utf-8")).hexdigest()

    def is_duplicate_for_store(self, source_hash: str, vector_store_name: str) -> bool:
        return self.target_repo.find_indexed_by_hash_for_store(
            source_hash, vector_store_name
        )
