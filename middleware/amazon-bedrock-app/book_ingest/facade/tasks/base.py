from book_ingest.models.task_dtos import BookIngestTaskReq, BookIngestTaskResp


class BookIngestTask:
    """A thin, single-purpose step in the ingestion pipeline.

    Uniform contract: takes the shared context (BookIngestTaskReq), returns only
    the fields it changed (BookIngestTaskResp). No task-specific positional args.
    """

    name: str = "task"

    def execute(self, req: BookIngestTaskReq) -> BookIngestTaskResp:
        raise NotImplementedError
