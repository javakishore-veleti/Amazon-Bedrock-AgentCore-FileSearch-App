"""FastAPI controller exposing the document-ingestion API."""

import logging

from fastapi import APIRouter, HTTPException

from common.dtos import IngestReq, IngestResp
from common.objects_factory import OBJECTS_FACTORY
from configs.end_points_master import END_POINTS_BY_NAME, END_POINTS_MASTER

logger = logging.getLogger(__name__)

# Same decorator style as @app.get in main.py, but scoped to this module.
# main.py wires it in with app.include_router(router).
router = APIRouter(prefix="/api/ingest", tags=["ingest"])


def _available_stores() -> list[str]:
    """End point names whose impl is actually registered in the factory."""
    return [e.name for e in END_POINTS_MASTER if OBJECTS_FACTORY.has(e.object_id)]


@router.post("", response_model=IngestResp)
async def ingest(req: IngestReq) -> IngestResp:
    """Ingest a single file into the requested vector store."""
    # Resolve the target store -> object_id (master catalog) -> facade (factory).
    object_id = END_POINTS_BY_NAME.get(req.target_vector_store)
    if object_id is None or not OBJECTS_FACTORY.has(object_id):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported or unavailable vector store "
                f"'{req.target_vector_store}'. Available: {_available_stores()}"
            ),
        )

    facade = OBJECTS_FACTORY.get(object_id)
    logger.info("Ingesting %s into %s", req.file_path, req.target_vector_store)

    # TODO: load and chunk the file at req.file_path, then call
    # facade.ingest(documents) with a configured vector store client.
    return IngestResp(
        status="accepted",
        target_vector_store=req.target_vector_store,
        file_path=req.file_path,
        message="Ingestion accepted; pipeline not yet implemented",
    )


@router.get("/stores")
async def list_supported_stores():
    """List the vector stores this service can ingest into."""
    return {"supported_stores": _available_stores()}
