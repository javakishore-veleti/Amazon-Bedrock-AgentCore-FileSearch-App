import logging

from fastapi import APIRouter, Depends

from common.interfaces.book_facades import VectorStoreIngestFacade
from book_ingest.jobs.job_service import AsyncJobService
from book_ingest.models.dtos import (
    IngestPendingReq,
    IngestStatusResp,
    JobAcceptedResp,
)
from book_ingest.providers import (
    get_async_job_service,
    get_vector_store_ingest_facade,
)

LOGGER = logging.getLogger(__name__)
router = APIRouter(prefix="/vector-store/ingest", tags=["book-ingest"])


@router.post("/pending", response_model=JobAcceptedResp)
async def ingest_pending(
    req: IngestPendingReq,
    facade: VectorStoreIngestFacade = Depends(get_vector_store_ingest_facade),
    jobs: AsyncJobService = Depends(get_async_job_service),
):
    """Queue pending books and start consumers. Queueing runs in the background
    (it may enqueue many books); poll GET /jobs/{job_id}. The ingestion itself
    then runs in the per-store consumers."""
    job_id = jobs.submit("ingest_pending", lambda: facade.queue_pending(req))
    return JobAcceptedResp(job_id=job_id, job_type="ingest_pending",
                           message="Ingestion queueing started; poll /jobs/{job_id}")


@router.get("/status", response_model=IngestStatusResp)
async def ingest_status(
    facade: VectorStoreIngestFacade = Depends(get_vector_store_ingest_facade),
):
    return facade.status()
