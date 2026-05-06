"""Sync vault data to/from a remote backend (file-based remote over SSH/SCP or local path)."""

import json
import os
import shutil
import subprocess
from pathlib import Path


def _is_remote(path: str) -> bool:
    """Return True if the path looks like a remote SCP target (user@host:/path)."""
    return ":" in path and not path.startswith("/")


def push_vault(local_vault_path: Path, remote: str) -> None:
    """
    Push the local vault file to a remote destination.

    Args:
        local_vault_path: Path to the local .envault file.
        remote: Remote destination string. Can be:
                - A local filesystem path (e.g. /mnt/shared/project.envault)
                - An SCP-style remote (e.g. user@host:/remote/path/project.envault)

    Raises:
        FileNotFoundError: If the local vault does not exist.
        RuntimeError: If the SCP transfer fails.
    """
    if not local_vault_path.exists():
        raise FileNotFoundError(f"Local vault not found: {local_vault_path}")

    if _is_remote(remote):
        result = subprocess.run(
            ["scp", str(local_vault_path), remote],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"SCP push failed: {result.stderr.strip()}")
    else:
        dest = Path(remote)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(local_vault_path, dest)


def pull_vault(remote: str, local_vault_path: Path) -> None:
    """
    Pull a vault file from a remote destination to the local path.

    Args:
        remote: Remote source string (local path or SCP-style).
        local_vault_path: Destination path on the local machine.

    Raises:
        RuntimeError: If the SCP transfer fails.
    """
    local_vault_path.parent.mkdir(parents=True, exist_ok=True)

    if _is_remote(remote):
        result = subprocess.run(
            ["scp", remote, str(local_vault_path)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"SCP pull failed: {result.stderr.strip()}")
    else:
        src = Path(remote)
        if not src.exists():
            raise FileNotFoundError(f"Remote vault not found: {src}")
        shutil.copy2(src, local_vault_path)
