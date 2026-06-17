"""FastAPI controller exposing the document-ingestion API."""

import logging

from fastapi import APIRouter, Depends, HTTPException

from common.dtos import IngestReq, IngestResp
from common.interfaces.ingest import IngestService
from vector_store.service.ingest_svc_provider import get_ingest_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ingest", tags=["ingest"])


@router.post("", response_model=IngestResp)
async def ingest(
    req: IngestReq,
    ingest_service: IngestService = Depends(get_ingest_service),
) -> IngestResp:
    """Ingest a single file into the requested vector store."""
    try:
        return ingest_service.ingest(req)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/stores")
async def list_supported_stores(
    ingest_service: IngestService = Depends(get_ingest_service),
):
    """List the vector stores this service can ingest into."""
    return {"supported_stores": ingest_service.list_supported_stores()}
