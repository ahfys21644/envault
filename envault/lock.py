"""Vault locking: mark a vault as read-only to prevent accidental writes."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

_LOCK_SUFFIX = ".lock"


def _lock_path(vault_path: str) -> Path:
    return Path(vault_path).with_suffix(_LOCK_SUFFIX)


def lock_vault(vault_path: str, reason: Optional[str] = None) -> dict:
    """Create a lock file for the given vault. Returns the lock entry."""
    lp = _lock_path(vault_path)
    if lp.exists():
        raise FileExistsError(f"Vault is already locked: {lp}")

    import datetime
    entry = {
        "locked_at": datetime.datetime.utcnow().isoformat() + "Z",
        "reason": reason or "",
    }
    lp.write_text(json.dumps(entry, indent=2))
    return entry


def unlock_vault(vault_path: str) -> bool:
    """Remove the lock file. Returns True if a lock was removed, False if none existed."""
    lp = _lock_path(vault_path)
    if not lp.exists():
        return False
    lp.unlink()
    return True


def is_locked(vault_path: str) -> bool:
    """Return True if the vault currently has a lock file."""
    return _lock_path(vault_path).exists()


def get_lock_info(vault_path: str) -> Optional[dict]:
    """Return the lock entry dict, or None if the vault is not locked."""
    lp = _lock_path(vault_path)
    if not lp.exists():
        return None
    return json.loads(lp.read_text())


def assert_unlocked(vault_path: str) -> None:
    """Raise PermissionError if the vault is locked."""
    info = get_lock_info(vault_path)
    if info is not None:
        reason = info.get("reason") or "no reason given"
        raise PermissionError(
            f"Vault is locked (since {info['locked_at']}): {reason}"
        )
