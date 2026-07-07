from pydantic import BaseModel, Field

from common.base_classes import BaseReqDto, BaseRespDto


class SearchHit(BaseModel):
    """One ranked snippet returned from a vector store search."""

    text: str
    score: float = 0.0
    metadata: dict = Field(default_factory=dict)
    provider_file_id: str = ""


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


class VectorSearchReq(BaseReqDto):
    """Input to a vector store adapter's search()."""

    query: str
    vector_store_id: str = ""
    top_k: int = 5
    # Optional metadata filters applied at the provider (ebook_id, author, etc.).
    filters: dict = Field(default_factory=dict)


class VectorSearchResp(BaseRespDto):
    """Output of a vector store adapter's search()."""

    query: str = ""
    hits: list[SearchHit] = Field(default_factory=list)
    status: str = ""
    message: str = ""
