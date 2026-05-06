"""Read, write, and manage encrypted vault files."""

import json
from pathlib import Path
from typing import Optional

from envault.crypto import encrypt, decrypt

DEFAULT_VAULT = Path(".envault")


def load_vault(vault_path: Path, password: str) -> dict:
    """
    Load and decrypt a vault file.
    Returns an empty dict if the file does not exist.
    """
    if not vault_path.exists():
        return {}
    encoded = vault_path.read_text(encoding="utf-8").strip()
    raw = decrypt(encoded, password)
    return json.loads(raw)


def save_vault(data: dict, vault_path: Path, password: str) -> None:
    """Encrypt and persist vault data to disk."""
    raw = json.dumps(data, indent=2)
    encoded = encrypt(raw, password)
    vault_path.write_text(encoded, encoding="utf-8")


def set_secret(key: str, value: str, vault_path: Path, password: str) -> None:
    """Insert or update a key-value pair in the vault."""
    data = load_vault(vault_path, password)
    data[key] = value
    save_vault(data, vault_path, password)


def get_secret(key: str, vault_path: Path, password: str) -> Optional[str]:
    """Retrieve a single secret by key; returns None if not found."""
    data = load_vault(vault_path, password)
    return data.get(key)


def delete_secret(key: str, vault_path: Path, password: str) -> bool:
    """Remove a key from the vault. Returns True if the key existed."""
    data = load_vault(vault_path, password)
    if key not in data:
        return False
    del data[key]
    save_vault(data, vault_path, password)
    return True


def list_keys(vault_path: Path, password: str) -> list:
    """Return a sorted list of all stored keys."""
    data = load_vault(vault_path, password)
    return sorted(data.keys())
