"""Merge secrets from one vault into another with conflict resolution."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from envault.vault import load_vault, save_vault, get_secret, set_secret


ConflictStrategy = Literal["ours", "theirs", "skip"]


@dataclass
class MergeResult:
    added: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)

    @property
    def total_changed(self) -> int:
        return len(self.added) + len(self.updated)


def merge_vaults(
    src_path: str,
    src_password: str,
    dst_path: str,
    dst_password: str,
    strategy: ConflictStrategy = "skip",
    keys: list[str] | None = None,
) -> MergeResult:
    """Merge secrets from src vault into dst vault.

    Args:
        src_path: Path to the source vault file.
        src_password: Password for the source vault.
        dst_path: Path to the destination vault file.
        dst_password: Password for the destination vault.
        strategy: How to handle conflicts — 'ours' keeps dst, 'theirs' uses src,
                  'skip' leaves conflicts untouched and records them.
        keys: Optional list of keys to merge; merges all if None.

    Returns:
        MergeResult summarising what changed.
    """
    src_vault = load_vault(src_path)
    dst_vault = load_vault(dst_path)

    result = MergeResult()

    candidates = keys if keys is not None else list(src_vault.keys())

    for key in candidates:
        src_value = get_secret(src_vault, key, src_password)
        if src_value is None:
            continue

        dst_value = get_secret(dst_vault, key, dst_password)

        if dst_value is None:
            set_secret(dst_vault, key, src_value, dst_password)
            result.added.append(key)
        elif dst_value == src_value:
            # identical — nothing to do
            pass
        else:
            # genuine conflict
            if strategy == "theirs":
                set_secret(dst_vault, key, src_value, dst_password)
                result.updated.append(key)
            elif strategy == "ours":
                result.skipped.append(key)
            else:  # "skip"
                result.conflicts.append(key)

    save_vault(dst_path, dst_vault)
    return result
