from dataclasses import dataclass


@dataclass
class BookIngestMessage:
    """One unit of work: ingest one book into one vector store.

    For multi-store ingestion the same book produces one message per target
    store, each routed to that store's own queue/consumers.
    """

    manifest_id: int
    source_url: str
    txt_url: str
    title: str
    author: str
    ebook_id: str
    # Routing key into END_POINTS_MASTER / ObjectsFactory (the store adapter).
    vector_store_name: str
    # Per (book, store) row id in vector_ingest_targets.
    target_id: int = 0
    # Concrete target store id (e.g. OpenAI vs_...); may be empty for stores
    # that don't use one.
    vector_store_id: str = ""
    attempt: int = 0
