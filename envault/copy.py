"""Copy secrets between vaults or duplicate keys within a vault."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from envault.vault import load_vault, save_vault, get_secret, set_secret


@dataclass
class CopyResult:
    key: str
    source: str
    destination: str
    success: bool
    error: str = ""


def copy_key(
    key: str,
    src_vault: str,
    src_password: str,
    dst_vault: str,
    dst_password: str,
    overwrite: bool = False,
) -> CopyResult:
    """Copy a single key from one vault to another."""
    value = get_secret(src_vault, src_password, key)
    if value is None:
        return CopyResult(
            key=key,
            source=src_vault,
            destination=dst_vault,
            success=False,
            error=f"Key '{key}' not found in source vault.",
        )

    dst_data = load_vault(dst_vault, dst_password)
    if key in dst_data and not overwrite:
        return CopyResult(
            key=key,
            source=src_vault,
            destination=dst_vault,
            success=False,
            error=f"Key '{key}' already exists in destination vault. Use --overwrite to replace.",
        )

    set_secret(dst_vault, dst_password, key, value)
    return CopyResult(key=key, source=src_vault, destination=dst_vault, success=True)


def copy_keys(
    keys: List[str],
    src_vault: str,
    src_password: str,
    dst_vault: str,
    dst_password: str,
    overwrite: bool = False,
) -> List[CopyResult]:
    """Copy multiple keys from one vault to another."""
    return [
        copy_key(key, src_vault, src_password, dst_vault, dst_password, overwrite)
        for key in keys
    ]


def copy_all(
    src_vault: str,
    src_password: str,
    dst_vault: str,
    dst_password: str,
    overwrite: bool = False,
) -> List[CopyResult]:
    """Copy every key from the source vault into the destination vault."""
    src_data = load_vault(src_vault, src_password)
    return copy_keys(
        list(src_data.keys()),
        src_vault,
        src_password,
        dst_vault,
        dst_password,
        overwrite,
    )
