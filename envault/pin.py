"""Pin/unpin secrets to prevent accidental modification or deletion."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _pin_path(vault_path: str) -> Path:
    return Path(vault_path).parent / ".envault_pins.json"


def _load_pins(vault_path: str) -> dict[str, Any]:
    p = _pin_path(vault_path)
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _save_pins(vault_path: str, pins: dict[str, Any]) -> None:
    p = _pin_path(vault_path)
    with p.open("w") as f:
        json.dump(pins, f, indent=2)


def pin_key(vault_path: str, key: str, reason: str = "") -> dict[str, Any]:
    """Pin a key to prevent modification or deletion."""
    pins = _load_pins(vault_path)
    entry = {"key": key, "reason": reason}
    pins[key] = entry
    _save_pins(vault_path, pins)
    return entry


def unpin_key(vault_path: str, key: str) -> bool:
    """Unpin a key. Returns True if it was pinned, False otherwise."""
    pins = _load_pins(vault_path)
    if key not in pins:
        return False
    del pins[key]
    _save_pins(vault_path, pins)
    return True


def is_pinned(vault_path: str, key: str) -> bool:
    """Return True if the given key is currently pinned."""
    pins = _load_pins(vault_path)
    return key in pins


def list_pins(vault_path: str) -> list[dict[str, Any]]:
    """Return all pinned keys with their metadata."""
    pins = _load_pins(vault_path)
    return list(pins.values())


def clear_pins(vault_path: str) -> int:
    """Remove all pins. Returns the number of pins cleared."""
    pins = _load_pins(vault_path)
    count = len(pins)
    _save_pins(vault_path, {})
    return count
