import logging

from fastapi import APIRouter, Depends

from book_ingest.facade.interfaces import DatasetManifestBuildFacade
from book_ingest.models.dtos import ManifestBuildReq, ManifestBuildResp
from book_ingest.providers import get_dataset_manifest_build_facade

LOGGER = logging.getLogger(__name__)
router = APIRouter(prefix="/manifest/novels", tags=["book-manifest"])


@router.post("/build", response_model=ManifestBuildResp)
async def build_manifest(
    req: ManifestBuildReq,
    facade: DatasetManifestBuildFacade = Depends(get_dataset_manifest_build_facade),
):
    return facade.build_manifest(req)
