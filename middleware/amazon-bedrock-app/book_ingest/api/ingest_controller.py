import logging

from fastapi import APIRouter, Depends

from book_ingest.facade.interfaces import IngestStatusFacade, VectorStoreIngestFacade
from book_ingest.models.dtos import (
    IngestPendingReq,
    IngestPendingResp,
    IngestStatusResp,
)
from book_ingest.providers import (
    get_ingest_status_facade,
    get_vector_store_ingest_facade,
)

LOGGER = logging.getLogger(__name__)
router = APIRouter(prefix="/vector-store/ingest", tags=["book-ingest"])


@router.post("/pending", response_model=IngestPendingResp)
async def ingest_pending(
    req: IngestPendingReq,
    facade: VectorStoreIngestFacade = Depends(get_vector_store_ingest_facade),
):
    return facade.queue_pending(req)


@router.get("/status", response_model=IngestStatusResp)
async def ingest_status(
    facade: IngestStatusFacade = Depends(get_ingest_status_facade),
):
    return facade.status()
