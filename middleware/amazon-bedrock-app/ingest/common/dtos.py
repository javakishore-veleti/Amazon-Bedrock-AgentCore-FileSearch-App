from pydantic import BaseModel


class IngestReq(BaseModel):
    """Request to ingest a file into a vector store."""

    file_path: str
    file_type: str
    # Default vector store, can be extended to support multiple stores.
    target_vector_store: str = "openai"


class IngestResp(BaseModel):
    """Result of an ingestion request."""

    status: str
    target_vector_store: str
    file_path: str
    message: str
