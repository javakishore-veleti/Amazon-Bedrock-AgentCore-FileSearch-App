"""Facade layer interfaces (use-case orchestration)."""

from book_ingest.models.domain import BookIngestMessage
from book_ingest.models.dtos import (
    DatasetBuildReq,
    DatasetBuildResp,
    IngestPendingReq,
    IngestPendingResp,
    IngestStatusResp,
    ManifestBuildReq,
    ManifestBuildResp,
)


class DatasetManifestBuildFacade:
    def build_dataset(self, req: DatasetBuildReq) -> DatasetBuildResp:
        raise NotImplementedError

    def build_manifest(self, req: ManifestBuildReq) -> ManifestBuildResp:
        raise NotImplementedError


class BookIngestionFacade:
    def ingest_one(self, message: BookIngestMessage) -> dict:
        raise NotImplementedError


class VectorStoreIngestFacade:
    def queue_pending(self, req: IngestPendingReq) -> IngestPendingResp:
        raise NotImplementedError


class IngestStatusFacade:
    def status(self) -> IngestStatusResp:
        raise NotImplementedError
