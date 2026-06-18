from book_ingest.models.domain import BookIngestMessage


class IngestMessagePublisher:
    def publish(self, message: BookIngestMessage) -> None:
        raise NotImplementedError
