from common.dtos import VectorIngestReq, VectorIngestResp


class VectorStoreAdapter:
    """Implemented by every vector store impl."""

    def ingest(self, req: VectorIngestReq, resp: VectorIngestResp):
        raise NotImplementedError("This method should be implemented by subclasses")
