"""TTL (time-to-live) support for vault secrets."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

_TTL_FILENAME = ".envault_ttl.json"


def _ttl_path(vault_path: Path) -> Path:
    return vault_path.parent / _TTL_FILENAME


def _load_ttl(vault_path: Path) -> dict:
    p = _ttl_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_ttl(vault_path: Path, data: dict) -> None:
    _ttl_path(vault_path).write_text(json.dumps(data, indent=2))


def set_ttl(vault_path: Path, key: str, seconds: int) -> dict:
    """Set a TTL (in seconds from now) for a specific key."""
    data = _load_ttl(vault_path)
    expires_at = time.time() + seconds
    data[key] = {"expires_at": expires_at}
    _save_ttl(vault_path, data)
    return {"key": key, "expires_at": expires_at, "ttl_seconds": seconds}


def get_ttl(vault_path: Path, key: str) -> Optional[dict]:
    """Return TTL info for a key, or None if no TTL is set."""
    data = _load_ttl(vault_path)
    entry = data.get(key)
    if entry is None:
        return None
    remaining = entry["expires_at"] - time.time()
    return {
        "key": key,
        "expires_at": entry["expires_at"],
        "remaining_seconds": max(0.0, remaining),
        "expired": remaining <= 0,
    }


def remove_ttl(vault_path: Path, key: str) -> bool:
    """Remove TTL for a key. Returns True if it existed."""
    data = _load_ttl(vault_path)
    if key not in data:
        return False
    del data[key]
    _save_ttl(vault_path, data)
    return True


def list_expired(vault_path: Path) -> list[str]:
    """Return keys whose TTL has elapsed."""
    data = _load_ttl(vault_path)
    now = time.time()
    return [k for k, v in data.items() if v["expires_at"] <= now]


def purge_expired(vault_path: Path, password: str) -> list[str]:
    """Delete expired keys from the vault. Returns list of purged key names."""
    from envault.vault import delete_secret

    expired = list_expired(vault_path)
    for key in expired:
        delete_secret(vault_path, key, password)
        remove_ttl(vault_path, key)
    return expired
