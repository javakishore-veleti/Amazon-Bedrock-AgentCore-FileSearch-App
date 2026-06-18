import logging
import queue
import threading
from collections import defaultdict

from book_ingest.messaging.queue.interfaces import IngestQueueFacade
from common.di import component

LOGGER = logging.getLogger(__name__)


@component(key="IngestQueueFacade")
class InMemoryQueueFacade(IngestQueueFacade):
    """Per-node in-memory queues, one per vector store name. Swap for Kinesis /
    Kafka / SQS / Redis Streams in multi-node deployments."""

    def __init__(self):
        self._queues: dict[str, queue.Queue] = defaultdict(queue.Queue)
        self._lock = threading.Lock()

    def _q(self, queue_name: str) -> queue.Queue:
        with self._lock:
            return self._queues[queue_name]

    def publish(self, queue_name, message) -> None:
        self._q(queue_name).put(message)

    def consume(self, queue_name, timeout=1.0):
        try:
            return self._q(queue_name).get(timeout=timeout)
        except queue.Empty:
            return None

    def ack(self, message) -> None:
        pass

    def nack(self, message, error) -> None:
        LOGGER.warning("nack: %s", error)

    def depth(self, queue_name) -> int:
        return self._q(queue_name).qsize()

    def all_depths(self) -> dict:
        with self._lock:
            return {name: q.qsize() for name, q in self._queues.items()}
