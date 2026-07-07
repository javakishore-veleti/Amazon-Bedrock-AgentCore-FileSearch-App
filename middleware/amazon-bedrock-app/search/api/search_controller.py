import logging

from fastapi import APIRouter, Depends, HTTPException

from common.interfaces.search import SearchFacade
from search.models.dtos import SearchReq, SearchResp
from search.providers import get_search_facade

LOGGER = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["search"])


@router.post("/search", response_model=SearchResp)
async def search_files(
    req: SearchReq,
    search_facade: SearchFacade = Depends(get_search_facade),
) -> SearchResp:
    """Search ingested books in the configured vector store."""
    try:
        return search_facade.search(req)
    except ValueError as exc:
        LOGGER.warning("Search rejected: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        LOGGER.error("Search failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
