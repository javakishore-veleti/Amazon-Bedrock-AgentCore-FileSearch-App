from common.base_classes import BaseReqDto, BaseRespDto


class IngestReq(BaseReqDto):
    """Request to ingest a file into a vector store."""

    file_path: str
    file_type: str
    # Default vector store, can be extended to support multiple stores.
    target_vector_store: str = "openai"


class IngestResp(BaseRespDto):
    """Result of an ingestion request."""

    status: str
    target_vector_store: str
    file_path: str
    message: str
