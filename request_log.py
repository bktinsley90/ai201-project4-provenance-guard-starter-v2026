"""Append structured HTTP request records to a local JSON Lines file."""

import json
import threading
from pathlib import Path

_lock = threading.Lock()


def append_record(path: Path, record: dict) -> None:
    """Append one JSON object as a line, creating the log directory if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
    with _lock:
        with path.open("a", encoding="utf-8") as log_file:
            log_file.write(line + "\n")
