"""Service layer interfaces (business logic)."""

from book_ingest.models.domain import BookIngestMessage
from book_ingest.models.dtos import (
    DatasetBuildReq,
    DatasetBuildResp,
    ManifestBuildReq,
    ManifestBuildResp,
)


class GutenbergTextCleaningService:
    def clean(self, raw_text: str) -> str:
        raise NotImplementedError


class BookMetadataExtractionService:
    def extract(self, clean_text: str, message: BookIngestMessage) -> dict:
        raise NotImplementedError


class DuplicateDetectionService:
    def compute_hash(self, clean_text: str) -> str:
        raise NotImplementedError

    def is_duplicate_for_store(self, source_hash: str, vector_store_name: str) -> bool:
        raise NotImplementedError


class GutenbergDatasetBuildService:
    def build(self, req: DatasetBuildReq) -> DatasetBuildResp:
        raise NotImplementedError


class ManifestBuildService:
    def build(self, req: ManifestBuildReq) -> ManifestBuildResp:
        raise NotImplementedError
