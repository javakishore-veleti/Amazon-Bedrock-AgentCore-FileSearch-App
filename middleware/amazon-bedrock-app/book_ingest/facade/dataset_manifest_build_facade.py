import logging

from book_ingest.facade.interfaces import DatasetManifestBuildFacade
from book_ingest.models.dtos import (
    DatasetBuildReq,
    DatasetBuildResp,
    ManifestBuildReq,
    ManifestBuildResp,
)
from common.di import component

LOGGER = logging.getLogger(__name__)


@component(
    key="DatasetManifestBuildFacade",
    depends_on=["GutenbergDatasetBuildService", "ManifestBuildService"],
)
class DatasetManifestBuildFacadeImpl(DatasetManifestBuildFacade):
    def __init__(self, dataset_build_service, manifest_build_service):
        self.dataset_build_service = dataset_build_service
        self.manifest_build_service = manifest_build_service

    def build_dataset(self, req: DatasetBuildReq) -> DatasetBuildResp:
        return self.dataset_build_service.build(req)

    def build_manifest(self, req: ManifestBuildReq) -> ManifestBuildResp:
        return self.manifest_build_service.build(req)
