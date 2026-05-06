"""Manage per-project sync configuration stored in .envault-sync.json."""

import json
from pathlib import Path
from typing import Optional

SYNC_CONFIG_FILENAME = ".envault-sync.json"


def _config_path(project_dir: Path) -> Path:
    return project_dir / SYNC_CONFIG_FILENAME


def load_sync_config(project_dir: Path) -> dict:
    """
    Load sync configuration from the project directory.

    Returns an empty dict if no config file exists.
    """
    path = _config_path(project_dir)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_sync_config(project_dir: Path, config: dict) -> None:
    """Persist sync configuration to disk."""
    path = _config_path(project_dir)
    with path.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
        f.write("\n")


def set_remote(project_dir: Path, remote: str) -> None:
    """Set (or update) the remote destination in the sync config."""
    config = load_sync_config(project_dir)
    config["remote"] = remote
    save_sync_config(project_dir, config)


def get_remote(project_dir: Path) -> Optional[str]:
    """Return the configured remote, or None if not set."""
    config = load_sync_config(project_dir)
    return config.get("remote")


def clear_remote(project_dir: Path) -> None:
    """Remove the remote setting from the sync config."""
    config = load_sync_config(project_dir)
    config.pop("remote", None)
    save_sync_config(project_dir, config)
