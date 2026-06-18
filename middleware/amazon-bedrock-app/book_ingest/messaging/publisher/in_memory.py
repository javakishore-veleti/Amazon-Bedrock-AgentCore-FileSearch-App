import logging

from common.interfaces.ingest_messaging import IngestMessagePublisher
from common.interfaces.ingest_messaging import IngestQueueFacade
from book_ingest.models.domain import BookIngestMessage
from common.di import component

LOGGER = logging.getLogger(__name__)


@component(key="IngestMessagePublisher", depends_on=["IngestQueueFacade"])
class InMemoryIngestMessagePublisher(IngestMessagePublisher):
    def __init__(self, queue_facade: IngestQueueFacade):
        self.queue_facade = queue_facade

    def publish(self, message: BookIngestMessage) -> None:
        # Route by vector store name -> that store's queue (its own consumers).
        self.queue_facade.publish(message.vector_store_name, message)
