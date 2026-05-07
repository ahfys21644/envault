"""Tag management for vault secrets — group and filter secrets by tag."""

from __future__ import annotations

from typing import Dict, List

from envault.vault import load_vault, save_vault, get_secret, set_secret

TAGS_META_KEY = "__tags__"


def _load_tags(vault_path: str, password: str) -> Dict[str, List[str]]:
    """Return the tags mapping {key: [tag, ...]} stored in the vault."""
    raw = get_secret(vault_path, password, TAGS_META_KEY)
    if raw is None:
        return {}
    import json
    return json.loads(raw)


def _save_tags(vault_path: str, password: str, tags: Dict[str, List[str]]) -> None:
    import json
    set_secret(vault_path, password, TAGS_META_KEY, json.dumps(tags))


def add_tag(vault_path: str, password: str, key: str, tag: str) -> None:
    """Add *tag* to *key*.  No-op if the tag already exists."""
    tags = _load_tags(vault_path, password)
    bucket = tags.setdefault(key, [])
    if tag not in bucket:
        bucket.append(tag)
    _save_tags(vault_path, password, tags)


def remove_tag(vault_path: str, password: str, key: str, tag: str) -> bool:
    """Remove *tag* from *key*.  Returns True if the tag was present."""
    tags = _load_tags(vault_path, password)
    bucket = tags.get(key, [])
    if tag not in bucket:
        return False
    bucket.remove(tag)
    if not bucket:
        tags.pop(key, None)
    _save_tags(vault_path, password, tags)
    return True


def list_tags(vault_path: str, password: str, key: str) -> List[str]:
    """Return all tags for *key*."""
    return _load_tags(vault_path, password).get(key, [])


def keys_for_tag(vault_path: str, password: str, tag: str) -> List[str]:
    """Return all secret keys that carry *tag*."""
    tags = _load_tags(vault_path, password)
    return sorted(k for k, bucket in tags.items() if tag in bucket)


def purge_key_tags(vault_path: str, password: str, key: str) -> None:
    """Remove all tag entries for *key* (call when a secret is deleted)."""
    tags = _load_tags(vault_path, password)
    if key in tags:
        tags.pop(key)
        _save_tags(vault_path, password, tags)
