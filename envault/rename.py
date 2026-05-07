"""Rename keys within a vault, preserving value and tags."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from envault.vault import load_vault, save_vault
from envault.tags import _load_tags, _save_tags


@dataclass
class RenameResult:
    old_key: str
    new_key: str
    success: bool
    message: str


def rename_key(
    vault_path: str,
    old_key: str,
    new_key: str,
    password: str,
    overwrite: bool = False,
) -> RenameResult:
    """Rename *old_key* to *new_key* inside the vault.

    Migrates any tags associated with the old key to the new key.
    Returns a :class:`RenameResult` describing the outcome.
    """
    if old_key == new_key:
        return RenameResult(old_key, new_key, False, "Source and destination keys are identical.")

    vault = load_vault(vault_path)

    if old_key not in vault:
        return RenameResult(old_key, new_key, False, f"Key '{old_key}' not found in vault.")

    if new_key in vault and not overwrite:
        return RenameResult(
            old_key,
            new_key,
            False,
            f"Key '{new_key}' already exists. Use --overwrite to replace it.",
        )

    # Move the encrypted blob
    vault[new_key] = vault.pop(old_key)
    save_vault(vault_path, vault)

    # Migrate tags
    tags = _load_tags(vault_path)
    if old_key in tags:
        existing = tags.get(new_key, [])
        merged = list(dict.fromkeys(existing + tags.pop(old_key)))
        tags[new_key] = merged
        _save_tags(vault_path, tags)

    return RenameResult(old_key, new_key, True, f"Renamed '{old_key}' → '{new_key}'.")
