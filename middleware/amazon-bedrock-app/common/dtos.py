from common.base_classes import BaseReqDto, BaseRespDto


class VectorIngestReq(BaseReqDto):
    """Input to a vector store adapter's ingest()."""

    file_path: str
    file_type: str = "txt"
    # Target store id (e.g. OpenAI vs_...); blank for stores that don't use one.
    vector_store_id: str = ""
    # Arbitrary metadata attached to the indexed document.
    attributes: dict = {}


class VectorIngestResp(BaseRespDto):
    """Output of a vector store adapter's ingest()."""

    status: str = ""
    message: str = ""
    provider_file_id: str = ""
    ingested_count: int = 0
