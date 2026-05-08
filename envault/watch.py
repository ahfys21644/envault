"""Watch a .env file for changes and sync secrets into the vault automatically."""

from __future__ import annotations

import time
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from envault.export import parse_dotenv, import_dotenv_file
from envault.audit import record_event


@dataclass
class WatchState:
    path: Path
    vault_path: Path
    password: str
    last_mtime: float = 0.0
    changes_detected: int = 0
    errors: list[str] = field(default_factory=list)


def _get_mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except FileNotFoundError:
        return 0.0


def _sync_once(state: WatchState) -> bool:
    """Check file for changes; sync if modified. Returns True if synced."""
    current_mtime = _get_mtime(state.path)
    if current_mtime <= state.last_mtime:
        return False

    try:
        count = import_dotenv_file(state.path, state.vault_path, state.password)
        state.last_mtime = current_mtime
        state.changes_detected += 1
        record_event("watch_sync", {"file": str(state.path), "keys_imported": count})
        return True
    except Exception as exc:  # noqa: BLE001
        state.errors.append(str(exc))
        return False


def watch_file(
    dotenv_path: Path,
    vault_path: Path,
    password: str,
    interval: float = 1.0,
    max_iterations: Optional[int] = None,
    on_change: Optional[Callable[[WatchState], None]] = None,
) -> WatchState:
    """Poll *dotenv_path* and import changes into *vault_path*.

    Runs until interrupted (KeyboardInterrupt) or *max_iterations* is reached.
    """
    state = WatchState(
        path=dotenv_path,
        vault_path=vault_path,
        password=password,
        last_mtime=_get_mtime(dotenv_path),
    )

    iteration = 0
    try:
        while max_iterations is None or iteration < max_iterations:
            synced = _sync_once(state)
            if synced and on_change:
                on_change(state)
            time.sleep(interval)
            iteration += 1
    except KeyboardInterrupt:
        pass

    return state
