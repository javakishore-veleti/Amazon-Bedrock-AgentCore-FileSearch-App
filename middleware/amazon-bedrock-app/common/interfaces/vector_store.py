from common.dtos import VectorIngestReq, VectorIngestResp, VectorSearchReq, VectorSearchResp


class VectorStoreAdapter:
    """Implemented by every vector store impl."""

    def ensure_store(self, store_name: str) -> str:
        """Make sure the backing store exists; return its id (or "" if the
        store needs no id). Called once before ingestion."""
        return ""

    def ingest(self, req: VectorIngestReq, resp: VectorIngestResp):
        raise NotImplementedError("This method should be implemented by subclasses")

    def search(self, req: VectorSearchReq, resp: VectorSearchResp):
        raise NotImplementedError("search() is not implemented for this vector store")
