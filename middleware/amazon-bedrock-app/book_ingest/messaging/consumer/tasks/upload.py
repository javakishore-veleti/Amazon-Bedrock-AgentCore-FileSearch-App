import logging
import os
import tempfile

from common.interfaces.book_repositories import (
    VectorIngestManifestRepository,
    VectorIngestTargetRepository,
)
from book_ingest.models.statuses import ManifestStatus
from book_ingest.models.task_dtos import BookIngestTaskReq, BookIngestTaskResp
from common.interfaces.book_task import BookIngestTask
from common.dtos import VectorIngestReq, VectorIngestResp
from common.interfaces.app_cache import AppCacheSvc
from common.objects_factory import OBJECTS_FACTORY
from configs.end_points_master import VECTOR_STORE_TYPE

LOGGER = logging.getLogger(__name__)


class UploadToVectorStoreTask(BookIngestTask):
    """Task: upload cleaned text to the target store via its VectorStoreAdapter,
    then mark the target INDEXED."""

    name = "upload"

    def __init__(self, app_cache: AppCacheSvc,
                 target_repo: VectorIngestTargetRepository,
                 manifest_repo: VectorIngestManifestRepository):
        self.app_cache = app_cache
        self.target_repo = target_repo
        self.manifest_repo = manifest_repo

    def execute(self, req: BookIngestTaskReq) -> BookIngestTaskResp:
        adapter = self._resolve_adapter(req.vector_store_name)
        attributes = {k: str(v) for k, v in (req.metadata or {}).items()
                      if v is not None}

        # Prefer the already-stored processed file; fall back to a temp file.
        path = req.processed_path
        temp = None
        if not path or not os.path.exists(path):
            temp = path = self._write_temp(req.clean_text or "")
        try:
            resp = VectorIngestResp(request_id=str(req.manifest_id))
            adapter.ingest(
                VectorIngestReq(file_path=path, file_type="txt",
                                vector_store_id=req.vector_store_id,
                                attributes=attributes),
                resp,
            )
        finally:
            if temp and os.path.exists(temp):
                os.remove(temp)

        self.target_repo.mark_indexed(req.target_id, resp.provider_file_id or "")
        self.manifest_repo.mark_indexed_if_all_targets_done(req.manifest_id)
        return BookIngestTaskResp(provider_file_id=resp.provider_file_id or "",
                                  status=ManifestStatus.INDEXED.value)

    def _resolve_adapter(self, vector_store_name: str):
        object_id = self.app_cache.get(VECTOR_STORE_TYPE, vector_store_name)
        if not object_id or not OBJECTS_FACTORY.has(object_id):
            raise ValueError(f"No adapter registered for '{vector_store_name}'")
        return OBJECTS_FACTORY.get(object_id)

    @staticmethod
    def _write_temp(text: str) -> str:
        fd, path = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        return path
