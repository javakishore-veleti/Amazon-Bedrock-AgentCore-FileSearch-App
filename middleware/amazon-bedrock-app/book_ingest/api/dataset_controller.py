import logging

from fastapi import APIRouter, Depends

from book_ingest.facade.interfaces import DatasetManifestBuildFacade
from book_ingest.models.dtos import DatasetBuildResp, DatasetBuildReq
from book_ingest.providers import get_dataset_manifest_build_facade

LOGGER = logging.getLogger(__name__)
router = APIRouter(prefix="/datasets/novels/gutenberg/top100", tags=["book-dataset"])


@router.post("/build", response_model=DatasetBuildResp)
async def build_dataset(
    req: DatasetBuildReq,
    facade: DatasetManifestBuildFacade = Depends(get_dataset_manifest_build_facade),
):
    return facade.build_dataset(req)
