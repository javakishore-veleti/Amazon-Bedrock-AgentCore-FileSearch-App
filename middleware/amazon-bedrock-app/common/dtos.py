from common.base_classes import BaseReqDto, BaseRespDto


class IngestReq(BaseReqDto):
    """Request to ingest a file into a vector store."""

    file_path: str
    file_type: str
    # Target vector store: an end point name from configs.end_points_master.
    target_vector_store: str = "OpenAPI Vector Store"


class IngestResp(BaseRespDto):
    """Result of an ingestion request."""

    status: str
    target_vector_store: str
    file_path: str
    message: str
