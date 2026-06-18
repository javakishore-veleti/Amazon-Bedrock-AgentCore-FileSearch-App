import glob
import json
import logging
import os
import re

from book_ingest.config.paths import resolve_path
from common.interfaces.book_repositories import DatasetBatchFileDao
from common.di import component

LOGGER = logging.getLogger(__name__)

_BATCH_RE = re.compile(r"novels_batch_(\d+)\.json$")


@component(key="DatasetBatchFileDao")
class DatasetBatchFileDaoImpl(DatasetBatchFileDao):
    """Reads/writes sequence-numbered batch JSON files on the filesystem.

    Relative dirs resolve to the repo root so DataSets/ lives at the repo root,
    not inside the codebase or the process cwd.
    """

    def next_sequence(self, output_dir: str) -> int:
        output_dir = resolve_path(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        existing = []
        for path in glob.glob(os.path.join(output_dir, "novels_batch_*.json")):
            m = _BATCH_RE.search(os.path.basename(path))
            if m:
                existing.append(int(m.group(1)))
        return (max(existing) + 1) if existing else 1

    def write_batch(self, output_dir: str, batch: dict) -> str:
        output_dir = resolve_path(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        batch_id = batch["batch_id"]
        path = os.path.join(output_dir, f"{batch_id}.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(batch, fh, ensure_ascii=False, indent=2)
        LOGGER.info("Wrote batch file %s (%d items)", path, batch.get("count", 0))
        return path

    def read_batches(self, input_dir: str) -> list:
        input_dir = resolve_path(input_dir)
        batches = []
        for path in sorted(glob.glob(os.path.join(input_dir, "novels_batch_*.json"))):
            with open(path, encoding="utf-8") as fh:
                batches.append(json.load(fh))
        return batches
