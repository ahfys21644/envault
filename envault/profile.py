"""Profile management: named sets of secrets for different environments."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


def _profiles_path(vault_path: Path) -> Path:
    return vault_path.parent / (vault_path.stem + ".profiles.json")


def _load_profiles(vault_path: Path) -> Dict[str, List[str]]:
    p = _profiles_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_profiles(vault_path: Path, data: Dict[str, List[str]]) -> None:
    _profiles_path(vault_path).write_text(json.dumps(data, indent=2))


@dataclass
class ProfileResult:
    ok: bool
    profile: str
    keys: List[str] = field(default_factory=list)
    message: str = ""


def create_profile(vault_path: Path, profile: str) -> ProfileResult:
    data = _load_profiles(vault_path)
    if profile in data:
        return ProfileResult(ok=False, profile=profile, message=f"Profile '{profile}' already exists.")
    data[profile] = []
    _save_profiles(vault_path, data)
    return ProfileResult(ok=True, profile=profile, message=f"Profile '{profile}' created.")


def delete_profile(vault_path: Path, profile: str) -> ProfileResult:
    data = _load_profiles(vault_path)
    if profile not in data:
        return ProfileResult(ok=False, profile=profile, message=f"Profile '{profile}' not found.")
    del data[profile]
    _save_profiles(vault_path, data)
    return ProfileResult(ok=True, profile=profile, message=f"Profile '{profile}' deleted.")


def assign_key(vault_path: Path, profile: str, key: str) -> ProfileResult:
    data = _load_profiles(vault_path)
    if profile not in data:
        return ProfileResult(ok=False, profile=profile, message=f"Profile '{profile}' not found.")
    if key not in data[profile]:
        data[profile].append(key)
        _save_profiles(vault_path, data)
    return ProfileResult(ok=True, profile=profile, keys=list(data[profile]), message=f"Key '{key}' assigned to '{profile}'.")


def unassign_key(vault_path: Path, profile: str, key: str) -> ProfileResult:
    data = _load_profiles(vault_path)
    if profile not in data:
        return ProfileResult(ok=False, profile=profile, message=f"Profile '{profile}' not found.")
    if key not in data[profile]:
        return ProfileResult(ok=False, profile=profile, message=f"Key '{key}' not in profile '{profile}'.")
    data[profile].remove(key)
    _save_profiles(vault_path, data)
    return ProfileResult(ok=True, profile=profile, keys=list(data[profile]), message=f"Key '{key}' removed from '{profile}'.")


def list_profiles(vault_path: Path) -> Dict[str, List[str]]:
    return _load_profiles(vault_path)


def get_profile_keys(vault_path: Path, profile: str) -> Optional[List[str]]:
    data = _load_profiles(vault_path)
    return data.get(profile)
