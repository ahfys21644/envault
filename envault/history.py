"""Track a per-key change history inside the vault metadata."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

_HISTORY_FILENAME = ".envault_history.json"


def _history_path(vault_path: str) -> str:
    directory = os.path.dirname(os.path.abspath(vault_path))
    return os.path.join(directory, _HISTORY_FILENAME)


def _load_history(vault_path: str) -> dict[str, list[dict[str, Any]]]:
    path = _history_path(vault_path)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_history(vault_path: str, data: dict[str, list[dict[str, Any]]]) -> None:
    path = _history_path(vault_path)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def record_change(vault_path: str, key: str, action: str, old_value: str | None = None) -> dict[str, Any]:
    """Append a change event for *key* and return the new entry."""
    history = _load_history(vault_path)
    entry: dict[str, Any] = {
        "action": action,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if old_value is not None:
        entry["old_value"] = old_value
    history.setdefault(key, []).append(entry)
    _save_history(vault_path, history)
    return entry


def get_key_history(vault_path: str, key: str) -> list[dict[str, Any]]:
    """Return all recorded changes for *key*, oldest first."""
    history = _load_history(vault_path)
    return history.get(key, [])


def clear_key_history(vault_path: str, key: str) -> int:
    """Delete history for *key*. Returns number of entries removed."""
    history = _load_history(vault_path)
    removed = len(history.pop(key, []))
    _save_history(vault_path, history)
    return removed


def list_keys_with_history(vault_path: str) -> list[str]:
    """Return all keys that have at least one history entry."""
    return sorted(_load_history(vault_path).keys())
