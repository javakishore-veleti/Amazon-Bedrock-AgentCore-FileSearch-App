from common.dtos import IngestReq, IngestResp


class IngestService:
    def ingest(self, req: IngestReq) -> IngestResp:
        raise NotImplementedError("This method should be implemented by subclasses")

    def list_supported_stores(self) -> list[str]:
        raise NotImplementedError("This method should be implemented by subclasses")
