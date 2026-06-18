import logging

from fastapi import APIRouter, Depends, HTTPException

from book_ingest.jobs.job_service import AsyncJobService
from book_ingest.models.dtos import JobStatusResp
from book_ingest.providers import get_async_job_service

LOGGER = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobStatusResp)
async def get_job(
    job_id: str,
    jobs: AsyncJobService = Depends(get_async_job_service),
):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Unknown job id '{job_id}'")
    return JobStatusResp(**job)
