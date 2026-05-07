"""Key rotation: re-encrypt all secrets with a new password."""

from __future__ import annotations

from typing import Any

from envault.crypto import decrypt, encrypt
from envault.vault import load_vault, save_vault
from envault.audit import record_event


def rotate_key(vault_path: str, old_password: str, new_password: str) -> dict[str, Any]:
    """Re-encrypt every secret in *vault_path* using *new_password*.

    Returns a summary dict with keys:
        - rotated  : number of secrets successfully re-encrypted
        - skipped  : number of entries that could not be decrypted (wrong old key)
        - vault    : the new vault data (already persisted)
    """
    vault = load_vault(vault_path, old_password)

    rotated = 0
    skipped = 0
    new_secrets: dict[str, str] = {}

    for key, ciphertext in vault.get("secrets", {}).items():
        try:
            plaintext = decrypt(old_password, ciphertext)
            new_secrets[key] = encrypt(new_password, plaintext)
            rotated += 1
        except Exception:
            # Keep the old ciphertext untouched so data is not lost.
            new_secrets[key] = ciphertext
            skipped += 1

    new_vault: dict[str, Any] = dict(vault)
    new_vault["secrets"] = new_secrets

    save_vault(vault_path, new_vault, new_password)

    record_event(
        "rotate_key",
        {"vault": vault_path, "rotated": rotated, "skipped": skipped},
    )

    return {"rotated": rotated, "skipped": skipped, "vault": new_vault}
