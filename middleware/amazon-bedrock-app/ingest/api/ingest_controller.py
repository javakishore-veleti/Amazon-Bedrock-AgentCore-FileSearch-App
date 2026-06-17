"""FastAPI controller exposing the document-ingestion API."""

import logging

from fastapi import APIRouter, HTTPException

from common.dtos import IngestReq, IngestResp
from vector_store import OpenAIVectorStoreIngestFacade

logger = logging.getLogger(__name__)

# Same decorator style as @app.get in main.py, but scoped to this module.
# main.py wires it in with app.include_router(router).
router = APIRouter(prefix="/api/ingest", tags=["ingest"])

# Registry of supported vector stores -> facade class.
# Add a new facade here to support another store.
_FACADES = {
    "openai": OpenAIVectorStoreIngestFacade,
}


@router.post("", response_model=IngestResp)
async def ingest(req: IngestReq) -> IngestResp:
    """Ingest a single file into the requested vector store."""
    facade_cls = _FACADES.get(req.target_vector_store)
    if facade_cls is None:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported target_vector_store '{req.target_vector_store}'. "
                f"Supported: {sorted(_FACADES)}"
            ),
        )

    logger.info("Ingesting %s into %s", req.file_path, req.target_vector_store)

    # TODO: load and chunk the file at req.file_path, then construct a real
    # vector store client and call facade.ingest(documents).
    return IngestResp(
        status="accepted",
        target_vector_store=req.target_vector_store,
        file_path=req.file_path,
        message="Ingestion accepted; pipeline not yet implemented",
    )


@router.get("/stores")
async def list_supported_stores():
    """List the vector stores this service can ingest into."""
    return {"supported_stores": sorted(_FACADES)}
