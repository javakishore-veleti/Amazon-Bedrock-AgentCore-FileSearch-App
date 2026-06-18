import logging

from fastapi import APIRouter, Depends, Request

from common.interfaces.book_facades import BookPipelineFacade, VectorStoreIngestFacade
from book_ingest.jobs.job_service import AsyncJobService
from book_ingest.models.dtos import (
    IngestPendingReq,
    IngestStatusResp,
    JobAcceptedResp,
    RunAllReq,
)
from book_ingest.providers import (
    get_async_job_service,
    get_book_pipeline_facade,
    get_vector_store_ingest_facade,
)

LOGGER = logging.getLogger(__name__)
router = APIRouter(prefix="/vector-store/ingest", tags=["book-ingest"])


@router.post("/pending", response_model=JobAcceptedResp)
async def ingest_pending(
    request: Request,
    req: IngestPendingReq,
    facade: VectorStoreIngestFacade = Depends(get_vector_store_ingest_facade),
    jobs: AsyncJobService = Depends(get_async_job_service),
):
    """Queue pending books and start consumers (runs in background). Picks up the
    latest manifest_build execution (lineage)."""
    job_id = jobs.submit("ingest_pending", lambda: facade.queue_pending(req),
                         consumes="manifest_build")
    return JobAcceptedResp(job_id=job_id, job_type="ingest_pending",
                           status_url=f"{request.base_url}jobs/{job_id}",
                           message="Ingestion queueing started; open status_url to track")


@router.post("/run-all", response_model=JobAcceptedResp)
async def run_all(
    request: Request,
    req: RunAllReq,
    pipeline: BookPipelineFacade = Depends(get_book_pipeline_facade),
    jobs: AsyncJobService = Depends(get_async_job_service),
):
    """One click: dataset build -> manifest build -> ingest pending."""
    job_id = jobs.submit("run_all", lambda: pipeline.run_all(req))
    return JobAcceptedResp(job_id=job_id, job_type="run_all",
                           status_url=f"{request.base_url}jobs/{job_id}",
                           message="Full pipeline started; open status_url to track")


@router.get("/status", response_model=IngestStatusResp)
async def ingest_status(
    facade: VectorStoreIngestFacade = Depends(get_vector_store_ingest_facade),
):
    return facade.status()
