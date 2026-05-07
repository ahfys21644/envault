"""Search secrets in the vault by key pattern or value substring."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from typing import List, Optional

from envault.vault import load_vault, get_secret
from envault.crypto import decrypt


@dataclass
class SearchResult:
    key: str
    value: Optional[str] = None  # None when --no-values flag is used


def search_keys(
    vault_path: str,
    password: str,
    pattern: str,
    reveal_values: bool = False,
) -> List[SearchResult]:
    """Return secrets whose keys match *pattern* (glob-style)."""
    vault = load_vault(vault_path)
    results: List[SearchResult] = []

    for key in vault:
        if fnmatch.fnmatch(key.lower(), pattern.lower()):
            value = get_secret(vault, password, key) if reveal_values else None
            results.append(SearchResult(key=key, value=value))

    return sorted(results, key=lambda r: r.key)


def search_values(
    vault_path: str,
    password: str,
    substring: str,
) -> List[SearchResult]:
    """Return secrets whose decrypted values contain *substring*."""
    vault = load_vault(vault_path)
    results: List[SearchResult] = []

    for key in vault:
        value = get_secret(vault, password, key)
        if substring.lower() in value.lower():
            results.append(SearchResult(key=key, value=value))

    return sorted(results, key=lambda r: r.key)


def format_results(results: List[SearchResult], reveal_values: bool = False) -> str:
    """Render search results as a human-readable string."""
    if not results:
        return "No matches found."
    lines = []
    for r in results:
        if reveal_values and r.value is not None:
            lines.append(f"{r.key}={r.value}")
        else:
            lines.append(r.key)
    return "\n".join(lines)
