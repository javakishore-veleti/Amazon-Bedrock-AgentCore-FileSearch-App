"""Book-ingest messaging interfaces: queue + publisher.

Named queues let each vector store have its own queue (and consumers), so
stores scale independently.
"""

from book_ingest.models.domain import BookIngestMessage


class IngestQueueFacade:
    def publish(self, queue_name: str, message) -> None:
        raise NotImplementedError

    def consume(self, queue_name: str, timeout: float = 1.0):
        """Return a message or None if nothing is available within timeout."""
        raise NotImplementedError

    def ack(self, message) -> None:
        raise NotImplementedError

    def nack(self, message, error: Exception) -> None:
        raise NotImplementedError

    def depth(self, queue_name: str) -> int:
        raise NotImplementedError

    def all_depths(self) -> dict:
        raise NotImplementedError


class IngestMessagePublisher:
    def publish(self, message: BookIngestMessage) -> None:
        raise NotImplementedError
