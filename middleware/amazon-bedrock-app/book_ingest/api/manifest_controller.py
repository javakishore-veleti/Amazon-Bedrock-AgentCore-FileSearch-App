import logging

from fastapi import APIRouter, Depends

from common.interfaces.book_facades import DatasetManifestBuildFacade
from book_ingest.jobs.job_service import AsyncJobService
from book_ingest.models.dtos import JobAcceptedResp, ManifestBuildReq
from book_ingest.providers import (
    get_async_job_service,
    get_dataset_manifest_build_facade,
)

LOGGER = logging.getLogger(__name__)
router = APIRouter(prefix="/manifest/novels", tags=["book-manifest"])


@router.post("/build", response_model=JobAcceptedResp)
async def build_manifest(
    req: ManifestBuildReq,
    facade: DatasetManifestBuildFacade = Depends(get_dataset_manifest_build_facade),
    jobs: AsyncJobService = Depends(get_async_job_service),
):
    """Load batch files into the manifest DB. Runs in the background; poll
    GET /jobs/{job_id}."""
    job_id = jobs.submit("manifest_build", lambda: facade.build_manifest(req))
    return JobAcceptedResp(job_id=job_id, job_type="manifest_build",
                           message="Manifest build started; poll /jobs/{job_id}")
