"""Path resolution: dataset artifacts live at the repo root, not inside the
codebase or wherever the process happens to be started from.

book_ingest/config/paths.py -> parents[4] == repo root:
  .../<repo>/middleware/amazon-bedrock-app/book_ingest/config/paths.py
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]


def resolve_path(path: str) -> str:
    """Return an absolute path; relative inputs are resolved against the repo root."""
    p = Path(path)
    return str(p if p.is_absolute() else (PROJECT_ROOT / p))
