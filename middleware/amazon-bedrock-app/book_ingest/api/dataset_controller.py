import logging

from fastapi import APIRouter, Depends, Request

from common.interfaces.book_facades import DatasetManifestBuildFacade
from book_ingest.jobs.job_service import AsyncJobService
from book_ingest.models.dtos import DatasetBuildReq, JobAcceptedResp
from book_ingest.providers import (
    get_async_job_service,
    get_dataset_manifest_build_facade,
)

LOGGER = logging.getLogger(__name__)
router = APIRouter(prefix="/datasets/novels/gutenberg/top100", tags=["book-dataset"])


@router.post("/build", response_model=JobAcceptedResp)
async def build_dataset(
    request: Request,
    req: DatasetBuildReq,
    facade: DatasetManifestBuildFacade = Depends(get_dataset_manifest_build_facade),
    jobs: AsyncJobService = Depends(get_async_job_service),
):
    """Crawl Gutenberg Top 100 and write batch files (runs in background)."""
    job_id = jobs.submit("dataset_build", lambda: facade.build_dataset(req))
    return JobAcceptedResp(job_id=job_id, job_type="dataset_build",
                           status_url=f"{request.base_url}jobs/{job_id}",
                           message="Dataset build started; open status_url to track")
