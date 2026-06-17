from enum import Enum

from common.base_classes import BaseReqDto, BaseRespDto
from configs.end_points_master import END_POINTS_MASTER

# Dropdown of valid vector store names, built from the master catalog so Swagger
# shows a fixed list and invalid values are rejected (422) automatically.
VectorStoreName = Enum(
    "VectorStoreName",
    {entry.name.replace(" ", "_"): entry.name for entry in END_POINTS_MASTER},
    type=str,
)


class IngestReq(BaseReqDto):
    """Request to ingest a file into a vector store."""

    file_path: str
    file_type: str
    # Target vector store: one of the predefined end point names.
    target_vector_store: VectorStoreName = VectorStoreName(END_POINTS_MASTER[0].name)


class IngestResp(BaseRespDto):
    """Result of an ingestion request."""

    status: str
    target_vector_store: str
    file_path: str
    message: str


class VectorIngestReq(BaseReqDto):
    """Input to a vector store adapter's ingest()."""

    file_path: str
    file_type: str


class VectorIngestResp(BaseRespDto):
    """Output of a vector store adapter's ingest()."""

    status: str = ""
    message: str = ""
    ingested_count: int = 0
