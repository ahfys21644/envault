"""Snapshot support: capture and restore full vault states."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from envault.vault import load_vault, save_vault

_SNAPSHOTS_FILE = ".envault_snapshots.json"


def _snapshots_path(vault_path: Path) -> Path:
    return vault_path.parent / _SNAPSHOTS_FILE


def _load_snapshots(vault_path: Path) -> dict[str, Any]:
    path = _snapshots_path(vault_path)
    if not path.exists():
        return {}
    with path.open("r") as fh:
        return json.load(fh)


def _save_snapshots(vault_path: Path, data: dict[str, Any]) -> None:
    path = _snapshots_path(vault_path)
    with path.open("w") as fh:
        json.dump(data, fh, indent=2)


def create_snapshot(vault_path: Path, password: str, label: str) -> dict[str, Any]:
    """Capture the current vault state and store it under *label*."""
    vault = load_vault(vault_path)
    snapshots = _load_snapshots(vault_path)
    entry = {
        "label": label,
        "timestamp": time.time(),
        "data": vault,
    }
    snapshots[label] = entry
    _save_snapshots(vault_path, snapshots)
    return entry


def restore_snapshot(vault_path: Path, password: str, label: str) -> int:
    """Overwrite the vault with the snapshot identified by *label*.

    Returns the number of secrets restored.
    """
    snapshots = _load_snapshots(vault_path)
    if label not in snapshots:
        raise KeyError(f"Snapshot '{label}' not found.")
    snapshot_data = snapshots[label]["data"]
    save_vault(vault_path, snapshot_data)
    return len(snapshot_data)


def list_snapshots(vault_path: Path) -> list[dict[str, Any]]:
    """Return all snapshots sorted by timestamp (oldest first)."""
    snapshots = _load_snapshots(vault_path)
    return sorted(snapshots.values(), key=lambda e: e["timestamp"])


def delete_snapshot(vault_path: Path, label: str) -> bool:
    """Remove a snapshot. Returns True if it existed, False otherwise."""
    snapshots = _load_snapshots(vault_path)
    if label not in snapshots:
        return False
    del snapshots[label]
    _save_snapshots(vault_path, snapshots)
    return True
