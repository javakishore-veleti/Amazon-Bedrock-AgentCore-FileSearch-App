import logging
import threading
from collections import defaultdict

from book_ingest.messaging.consumer.consumer_impl import IngestConsumerImpl
from common.di import component

LOGGER = logging.getLogger(__name__)


@component(
    key="IngestConsumerManager",
    depends_on=[
        "IngestQueueFacade",
        "IngestMessagePublisher",
        "BookIngestionFacade",
        "VectorIngestTargetRepository",
        "BookIngestSettings",
    ],
)
class IngestConsumerManager:
    """Starts consumers once per (node, vector store). Repeated ingest calls do
    not spawn duplicate consumers for a store already running on this node."""

    def __init__(self, queue_facade, publisher, facade, target_repo, settings):
        self.queue_facade = queue_facade
        self.publisher = publisher
        self.facade = facade
        self.target_repo = target_repo
        self.settings = settings
        self._started: dict[str, bool] = {}
        self._threads: dict[str, list] = defaultdict(list)
        self._stop_events: dict[str, threading.Event] = {}
        self._lock = threading.Lock()

    def start_if_not_running(self, store_name: str, consumer_count: int) -> bool:
        with self._lock:
            if self._started.get(store_name):
                return False
            stop_event = threading.Event()
            self._stop_events[store_name] = stop_event
            for i in range(consumer_count):
                worker = IngestConsumerImpl(
                    worker_id=i,
                    store_name=store_name,
                    queue_facade=self.queue_facade,
                    facade=self.facade,
                    publisher=self.publisher,
                    target_repo=self.target_repo,
                    settings=self.settings,
                    stop_event=stop_event,
                )
                thread = threading.Thread(
                    target=worker.run, name=f"ingest-{store_name}-{i}", daemon=True
                )
                thread.start()
                self._threads[store_name].append(thread)
            self._started[store_name] = True
            LOGGER.info("consumers_started store=%s count=%d", store_name, consumer_count)
            return True

    def running(self) -> dict:
        with self._lock:
            return {store: len(threads) for store, threads in self._threads.items()}

    def stop_all(self):
        with self._lock:
            for event in self._stop_events.values():
                event.set()
            self._started.clear()
            self._threads.clear()
            self._stop_events.clear()
