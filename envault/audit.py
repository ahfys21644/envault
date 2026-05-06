"""Audit log for tracking vault operations (set, get, delete, import, export)."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DEFAULT_AUDIT_LOG = Path.home() / ".envault" / "audit.log"


def _audit_path(log_path: Optional[Path] = None) -> Path:
    path = log_path or DEFAULT_AUDIT_LOG
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def record_event(
    action: str,
    key: Optional[str] = None,
    vault: Optional[str] = None,
    success: bool = True,
    log_path: Optional[Path] = None,
) -> dict:
    """Append a structured audit event to the log file and return it."""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "key": key,
        "vault": vault,
        "success": success,
        "user": os.environ.get("USER") or os.environ.get("USERNAME") or "unknown",
    }
    path = _audit_path(log_path)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event) + "\n")
    return event


def read_events(log_path: Optional[Path] = None, limit: int = 50) -> list[dict]:
    """Read the most recent *limit* audit events from the log."""
    path = _audit_path(log_path)
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    events = []
    for line in lines:
        line = line.strip()
        if line:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events[-limit:]


def clear_log(log_path: Optional[Path] = None) -> None:
    """Erase all audit log entries."""
    path = _audit_path(log_path)
    if path.exists():
        path.write_text("", encoding="utf-8")
