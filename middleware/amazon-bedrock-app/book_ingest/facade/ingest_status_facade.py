import logging

from common.interfaces.book_facades import IngestStatusFacade
from book_ingest.models.dtos import IngestStatusResp
from common.di import component

LOGGER = logging.getLogger(__name__)


@component(
    key="IngestStatusFacade",
    depends_on=["VectorIngestManifestRepository", "IngestConsumerManager",
                "IngestQueueFacade"],
)
class IngestStatusFacadeImpl(IngestStatusFacade):
    def __init__(self, manifest_repo, consumer_manager, queue_facade):
        self.manifest_repo = manifest_repo
        self.consumer_manager = consumer_manager
        self.queue_facade = queue_facade

    def status(self) -> IngestStatusResp:
        return IngestStatusResp(
            counts_by_status=self.manifest_repo.count_by_status(),
            consumers_running=self.consumer_manager.running(),
            queue_depth=self.queue_facade.all_depths(),
        )
