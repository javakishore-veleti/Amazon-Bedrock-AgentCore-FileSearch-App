"""BookIngestionFacade: controls the ingestion *lifecycle* for one book/message.

  Consumer (per vector DB) --> ingest_one(message, target_vector_db)

Lifecycle (facade):
  task 1: validate message
  task 2: check manifest/target state  (short-circuit if already done)
  task 3: mark IN_PROGRESS + log
  task 4: run the processing pipeline   <-- LangGraph
  task 5: finalize (log terminal event)

Processing pipeline (LangGraph, task 4) -- same for every store:
  fetch -> store_raw -> clean -> split -> store_processed -> metadata ->
  dedupe -> (skip | upload)

The target vector DB is passed in as context (never chosen by the graph); only
the upload task differs per store, via the resolved VectorStoreAdapter.
"""

import logging
from typing import Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from common.interfaces.book_facades import BookIngestionFacade
from book_ingest.models.domain import BookIngestMessage
from book_ingest.models.task_dtos import BookIngestTaskReq
from book_ingest.messaging.consumer.tasks.check_existing import CheckExistingIngestionTask
from book_ingest.messaging.consumer.tasks.clean_text import CleanTextTask
from book_ingest.messaging.consumer.tasks.duplicate_check import DuplicateCheckTask
from book_ingest.messaging.consumer.tasks.extract_metadata import ExtractMetadataTask
from book_ingest.messaging.consumer.tasks.fetch_text import FetchTextTask
from book_ingest.messaging.consumer.tasks.finalize import FinalizeTask
from book_ingest.messaging.consumer.tasks.lock_and_log import LockAndLogTask
from book_ingest.messaging.consumer.tasks.skip_duplicate import SkipDuplicateTask
from book_ingest.messaging.consumer.tasks.split_sections import SplitSectionsTask
from book_ingest.messaging.consumer.tasks.store_processed import StoreProcessedTask
from book_ingest.messaging.consumer.tasks.store_raw import StoreRawTask
from book_ingest.messaging.consumer.tasks.upload import UploadToVectorStoreTask
from book_ingest.messaging.consumer.tasks.validate_message import ValidateMessageTask
from common.di import component

LOGGER = logging.getLogger(__name__)


class GraphState(TypedDict, total=False):
    manifest_id: int
    target_id: int
    ebook_id: str
    title: str
    author: Optional[str]
    source_url: str
    txt_url: str
    vector_store_name: str
    vector_store_id: str
    raw_text: Optional[str]
    raw_path: Optional[str]
    clean_text: Optional[str]
    processed_path: Optional[str]
    sections: list
    source_hash: Optional[str]
    metadata: dict
    duplicate: bool
    provider_file_id: Optional[str]
    status: Optional[str]
    route: Optional[str]


@component(
    key="BookIngestionFacade",
    depends_on=[
        "GutenbergClient",
        "GutenbergTextCleaningService",
        "BookMetadataExtractionService",
        "DuplicateDetectionService",
        "VectorIngestManifestRepository",
        "VectorIngestTargetRepository",
        "VectorIngestLogRepository",
        "VectorIngestSectionRepository",
        "AppCacheSvc",
        "BookIngestSettings",
    ],
)
class BookIngestionFacadeImpl(BookIngestionFacade):
    def __init__(self, gutenberg, cleaning, metadata, duplicate, manifest_repo,
                 target_repo, log_repo, section_repo, app_cache, settings):
        # Lifecycle tasks (run directly by the facade).
        self.validate_task = ValidateMessageTask()
        self.check_task = CheckExistingIngestionTask(target_repo)
        self.lock_task = LockAndLogTask(log_repo, target_repo)
        self.finalize_task = FinalizeTask(log_repo)

        # Processing pipeline tasks (run by LangGraph, task 4).
        self.pipeline_tasks = {
            "fetch": FetchTextTask(gutenberg),
            "store_raw": StoreRawTask(settings),
            "clean": CleanTextTask(cleaning),
            "split": SplitSectionsTask(section_repo),
            "store_processed": StoreProcessedTask(settings),
            "metadata": ExtractMetadataTask(metadata, duplicate, manifest_repo),
            "duplicate_check": DuplicateCheckTask(duplicate),
            "skip": SkipDuplicateTask(target_repo),
            "upload": UploadToVectorStoreTask(app_cache, target_repo, manifest_repo),
        }
        self.pipeline = self._build_pipeline()

    def _wrap(self, key):
        task = self.pipeline_tasks[key]

        def node(state: GraphState) -> dict:
            return task.execute(BookIngestTaskReq(**state)).merge_dict()

        return node

    def _build_pipeline(self):
        g = StateGraph(GraphState)
        for key in self.pipeline_tasks:
            g.add_node(key, self._wrap(key))
        g.add_edge(START, "fetch")
        g.add_edge("fetch", "store_raw")
        g.add_edge("store_raw", "clean")
        g.add_edge("clean", "split")
        g.add_edge("split", "store_processed")
        g.add_edge("store_processed", "metadata")
        g.add_edge("metadata", "duplicate_check")
        g.add_conditional_edges(
            "duplicate_check",
            lambda s: s.get("route") or "upload",
            {"skip": "skip", "upload": "upload"},
        )
        g.add_edge("skip", END)
        g.add_edge("upload", END)
        return g.compile()

    def ingest_one(self, message: BookIngestMessage, target_vector_db: str = None) -> dict:
        if target_vector_db:
            message.vector_store_name = target_vector_db

        ctx = self._context(message)

        # task 1-3: lifecycle
        self.validate_task.execute(BookIngestTaskReq(**ctx))
        check = self.check_task.execute(BookIngestTaskReq(**ctx))
        if check.terminal:
            return {"status": check.status, "provider_file_id": None}
        self.lock_task.execute(BookIngestTaskReq(**ctx))

        # task 4: processing pipeline (LangGraph)
        final = self.pipeline.invoke(ctx)

        # task 5: finalize
        status = final.get("status")
        self.finalize_task.execute(BookIngestTaskReq(**{**ctx, "status": status}))
        return {"status": status, "provider_file_id": final.get("provider_file_id")}

    @staticmethod
    def _context(message: BookIngestMessage) -> GraphState:
        return {
            "manifest_id": message.manifest_id,
            "target_id": message.target_id,
            "ebook_id": message.ebook_id,
            "title": message.title,
            "author": message.author,
            "source_url": message.source_url,
            "txt_url": message.txt_url,
            "vector_store_name": message.vector_store_name,
            "vector_store_id": message.vector_store_id,
            "metadata": {},
            "sections": [],
            "duplicate": False,
        }
