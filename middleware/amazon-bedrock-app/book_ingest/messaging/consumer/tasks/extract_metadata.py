import logging

from common.interfaces.book_repositories import VectorIngestManifestRepository
from book_ingest.models.task_dtos import BookIngestTaskReq, BookIngestTaskResp
from common.interfaces.book_services import (
    BookMetadataExtractionService,
    DuplicateDetectionService,
)
from common.interfaces.book_task import BookIngestTask

LOGGER = logging.getLogger(__name__)


class ExtractMetadataTask(BookIngestTask):
    """Task: extract metadata and compute the content SHA256 hash."""

    name = "extract_metadata"

    def __init__(self, metadata: BookMetadataExtractionService,
                 duplicate: DuplicateDetectionService,
                 manifest_repo: VectorIngestManifestRepository):
        self.metadata = metadata
        self.duplicate = duplicate
        self.manifest_repo = manifest_repo

    def execute(self, req: BookIngestTaskReq) -> BookIngestTaskResp:
        meta = self.metadata.extract(req.clean_text or "", req)
        source_hash = self.duplicate.compute_hash(req.clean_text or "")
        self.manifest_repo.set_source_hash(req.manifest_id, source_hash)
        return BookIngestTaskResp(metadata=meta, source_hash=source_hash)
