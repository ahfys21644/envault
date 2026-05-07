"""Diff utilities for comparing vault secrets against a .env file."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from envault.export import parse_dotenv
from envault.vault import get_secret, load_vault


@dataclass
class DiffEntry:
    key: str
    status: str  # 'added' | 'removed' | 'changed' | 'unchanged'
    vault_value: Optional[str] = None
    file_value: Optional[str] = None


def diff_vault_vs_file(
    vault_path: str,
    dotenv_path: str,
    password: str,
) -> List[DiffEntry]:
    """Return a list of DiffEntry comparing vault secrets to a .env file."""
    vault_data = load_vault(vault_path)
    vault_keys: Dict[str, str] = {}
    for key in vault_data.get("secrets", {}):
        try:
            vault_keys[key] = get_secret(vault_data, key, password)
        except Exception:
            vault_keys[key] = "<decryption-error>"

    with open(dotenv_path, "r", encoding="utf-8") as fh:
        file_keys = parse_dotenv(fh.read())

    all_keys = set(vault_keys) | set(file_keys)
    entries: List[DiffEntry] = []

    for key in sorted(all_keys):
        in_vault = key in vault_keys
        in_file = key in file_keys

        if in_vault and in_file:
            if vault_keys[key] == file_keys[key]:
                status = "unchanged"
            else:
                status = "changed"
            entries.append(DiffEntry(key, status, vault_keys[key], file_keys[key]))
        elif in_vault:
            entries.append(DiffEntry(key, "removed", vault_value=vault_keys[key]))
        else:
            entries.append(DiffEntry(key, "added", file_value=file_keys[key]))

    return entries


def format_diff(entries: List[DiffEntry], show_values: bool = False) -> str:
    """Render diff entries as a human-readable string."""
    lines: List[str] = []
    symbols = {"added": "+", "removed": "-", "changed": "~", "unchanged": " "}
    for entry in entries:
        sym = symbols[entry.status]
        if show_values and entry.status == "changed":
            lines.append(f"{sym} {entry.key}: {entry.vault_value!r} -> {entry.file_value!r}")
        else:
            lines.append(f"{sym} {entry.key}")
    return "\n".join(lines) if lines else "(no differences)"
