"""Tests for envault/profile.py"""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.profile import (
    create_profile,
    delete_profile,
    assign_key,
    unassign_key,
    list_profiles,
    get_profile_keys,
    _profiles_path,
)


@pytest.fixture
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "vault.enc"


class TestCreateProfile:
    def test_create_returns_ok(self, vault_path):
        result = create_profile(vault_path, "production")
        assert result.ok is True

    def test_create_profile_appears_in_list(self, vault_path):
        create_profile(vault_path, "staging")
        profiles = list_profiles(vault_path)
        assert "staging" in profiles

    def test_create_duplicate_returns_error(self, vault_path):
        create_profile(vault_path, "dev")
        result = create_profile(vault_path, "dev")
        assert result.ok is False
        assert "already exists" in result.message

    def test_new_profile_has_empty_keys(self, vault_path):
        create_profile(vault_path, "ci")
        keys = get_profile_keys(vault_path, "ci")
        assert keys == []

    def test_profiles_file_created(self, vault_path):
        create_profile(vault_path, "prod")
        assert _profiles_path(vault_path).exists()


class TestDeleteProfile:
    def test_delete_existing_profile(self, vault_path):
        create_profile(vault_path, "temp")
        result = delete_profile(vault_path, "temp")
        assert result.ok is True
        assert "temp" not in list_profiles(vault_path)

    def test_delete_missing_profile_returns_error(self, vault_path):
        result = delete_profile(vault_path, "ghost")
        assert result.ok is False
        assert "not found" in result.message


class TestAssignKey:
    def test_assign_key_to_profile(self, vault_path):
        create_profile(vault_path, "prod")
        result = assign_key(vault_path, "prod", "DB_URL")
        assert result.ok is True
        assert "DB_URL" in result.keys

    def test_assign_duplicate_key_is_idempotent(self, vault_path):
        create_profile(vault_path, "prod")
        assign_key(vault_path, "prod", "API_KEY")
        assign_key(vault_path, "prod", "API_KEY")
        keys = get_profile_keys(vault_path, "prod")
        assert keys.count("API_KEY") == 1

    def test_assign_to_missing_profile_returns_error(self, vault_path):
        result = assign_key(vault_path, "nonexistent", "KEY")
        assert result.ok is False


class TestUnassignKey:
    def test_unassign_removes_key(self, vault_path):
        create_profile(vault_path, "dev")
        assign_key(vault_path, "dev", "SECRET")
        result = unassign_key(vault_path, "dev", "SECRET")
        assert result.ok is True
        assert "SECRET" not in get_profile_keys(vault_path, "dev")

    def test_unassign_key_not_in_profile_returns_error(self, vault_path):
        create_profile(vault_path, "dev")
        result = unassign_key(vault_path, "dev", "MISSING")
        assert result.ok is False
        assert "not in profile" in result.message


class TestListAndGet:
    def test_list_multiple_profiles(self, vault_path):
        create_profile(vault_path, "dev")
        create_profile(vault_path, "prod")
        profiles = list_profiles(vault_path)
        assert set(profiles.keys()) == {"dev", "prod"}

    def test_get_nonexistent_profile_returns_none(self, vault_path):
        assert get_profile_keys(vault_path, "missing") is None

    def test_missing_profiles_file_returns_empty_dict(self, vault_path):
        assert list_profiles(vault_path) == {}
