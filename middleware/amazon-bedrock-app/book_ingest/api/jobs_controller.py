import json
import logging

from fastapi import APIRouter, Depends, HTTPException

from book_ingest.jobs.job_service import AsyncJobService
from book_ingest.models.dtos import JobStatusResp
from book_ingest.providers import get_async_job_service

LOGGER = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobStatusResp])
async def list_jobs(jobs: AsyncJobService = Depends(get_async_job_service)):
    """All executions, newest first (one API can have many; shows lineage)."""
    return [_to_resp(job) for job in jobs.list()]


@router.get("/{job_id}", response_model=JobStatusResp)
async def get_job(
    job_id: str,
    jobs: AsyncJobService = Depends(get_async_job_service),
):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Unknown job id '{job_id}'")
    return _to_resp(job)


def _to_resp(job: dict) -> JobStatusResp:
    result = job.get("result")
    if isinstance(result, str):  # persisted rows store result as JSON text
        try:
            result = json.loads(result)
        except (ValueError, TypeError):
            result = {"raw": result}
    return JobStatusResp(
        job_id=job.get("job_id", ""), job_type=job.get("job_type", ""),
        status=job.get("status", ""), result=result, error=job.get("error"),
        picked_up=job.get("picked_up"), picked_up_by_id=job.get("picked_up_by_id"),
    )
