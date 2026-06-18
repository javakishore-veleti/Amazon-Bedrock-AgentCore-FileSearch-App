import logging

from common.interfaces.book_repositories import (
    DatasetBatchFileDao,
    VectorIngestManifestRepository,
)
from book_ingest.models.dtos import ManifestBuildReq, ManifestBuildResp
from common.interfaces.book_services import ManifestBuildService
from common.di import component

LOGGER = logging.getLogger(__name__)


@component(
    key="ManifestBuildService",
    depends_on=["DatasetBatchFileDao", "VectorIngestManifestRepository"],
)
class ManifestBuildServiceImpl(ManifestBuildService):
    def __init__(self, batch_dao: DatasetBatchFileDao,
                 manifest_repo: VectorIngestManifestRepository):
        self.batch_dao = batch_dao
        self.manifest_repo = manifest_repo

    def build(self, req: ManifestBuildReq) -> ManifestBuildResp:
        LOGGER.info("manifest_build_started input_dir=%s", req.input_dir)
        batches = self.batch_dao.read_batches(req.input_dir)

        items = []
        for batch in batches:
            items.extend(batch.get("items", []))

        result = self.manifest_repo.insert_discovered_books(
            items, initial_status=req.initial_status, dedupe_by_url=req.dedupe_by_url
        )

        LOGGER.info("manifest_build_completed files=%d found=%d inserted=%d skipped=%d",
                    len(batches), len(items), result["inserted"], result["skipped"])
        return ManifestBuildResp(
            request_id=req.request_id,
            status="completed",
            files_read=len(batches),
            records_found=len(items),
            records_inserted=result["inserted"],
            records_skipped_duplicate=result["skipped"],
            message="Manifest repository built successfully",
        )
