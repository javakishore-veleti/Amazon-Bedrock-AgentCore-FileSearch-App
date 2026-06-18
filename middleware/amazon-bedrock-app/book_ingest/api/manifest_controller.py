import logging

from fastapi import APIRouter, Depends, Request

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
    request: Request,
    req: ManifestBuildReq,
    facade: DatasetManifestBuildFacade = Depends(get_dataset_manifest_build_facade),
    jobs: AsyncJobService = Depends(get_async_job_service),
):
    """Load batch files into the manifest DB (runs in background). Picks up the
    latest dataset_build execution (lineage)."""
    job_id = jobs.submit("manifest_build", lambda: facade.build_manifest(req),
                         consumes="dataset_build")
    return JobAcceptedResp(job_id=job_id, job_type="manifest_build",
                           status_url=f"{request.base_url}jobs/{job_id}",
                           message="Manifest build started; open status_url to track")
