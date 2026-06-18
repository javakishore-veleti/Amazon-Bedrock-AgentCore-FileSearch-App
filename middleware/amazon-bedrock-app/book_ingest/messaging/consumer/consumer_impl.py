import logging

from book_ingest.models.domain import BookIngestMessage

LOGGER = logging.getLogger(__name__)


class IngestConsumerImpl:
    """A single consumer worker bound to one vector store's queue.

    Loop: consume -> facade.ingest_one -> ack; on failure classify retryable vs
    permanent, update target state, and requeue or dead-letter.
    """

    def __init__(self, worker_id, store_name, queue_facade, facade, publisher,
                 target_repo, settings, stop_event):
        self.worker_id = worker_id
        self.store_name = store_name
        self.queue_facade = queue_facade
        self.facade = facade
        self.publisher = publisher
        self.target_repo = target_repo
        self.settings = settings
        self.stop_event = stop_event

    def run(self):
        LOGGER.info("consumer_started store=%s worker=%s", self.store_name, self.worker_id)
        while not self.stop_event.is_set():
            message = self.queue_facade.consume(
                self.store_name, timeout=self.settings.poll_interval_seconds
            )
            if message is None:
                continue
            self._process(message)

    def _process(self, message: BookIngestMessage):
        try:
            # This consumer is bound to one vector DB; it selects the target.
            self.facade.ingest_one(message, target_vector_db=self.store_name)
            self.queue_facade.ack(message)
        except Exception as exc:  # noqa: BLE001 - consumers must not die
            self._handle_failure(message, exc)

    def _handle_failure(self, message: BookIngestMessage, exc: Exception):
        permanent = isinstance(exc, (ValueError, KeyError))
        attempt = message.attempt + 1
        if not permanent and attempt <= self.settings.max_retries:
            self.target_repo.mark_failed_retryable(message.target_id, str(exc))
            message.attempt = attempt
            self.publisher.publish(message)  # requeue to same store queue
            LOGGER.warning("book_ingest_failed retry store=%s target=%s attempt=%s err=%s",
                           self.store_name, message.target_id, attempt, exc)
        else:
            self.target_repo.mark_failed_permanent(message.target_id, str(exc))
            self.queue_facade.nack(message, exc)
            LOGGER.error("book_ingest_failed permanent store=%s target=%s err=%s",
                         self.store_name, message.target_id, exc)
