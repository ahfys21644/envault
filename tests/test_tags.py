"""Unit tests for envault.tags."""

from __future__ import annotations

import pytest

from envault.vault import set_secret
from envault.tags import (
    add_tag,
    remove_tag,
    list_tags,
    keys_for_tag,
    purge_key_tags,
)

PASSWORD = "test-secret-pw"


@pytest.fixture()
def vault_path(tmp_path):
    p = tmp_path / "vault.enc"
    # Seed a couple of secrets so the vault exists
    set_secret(str(p), PASSWORD, "DB_HOST", "localhost")
    set_secret(str(p), PASSWORD, "DB_PORT", "5432")
    set_secret(str(p), PASSWORD, "API_KEY", "abc123")
    return str(p)


class TestAddTag:
    def test_add_single_tag(self, vault_path):
        add_tag(vault_path, PASSWORD, "DB_HOST", "database")
        assert "database" in list_tags(vault_path, PASSWORD, "DB_HOST")

    def test_add_multiple_tags(self, vault_path):
        add_tag(vault_path, PASSWORD, "DB_HOST", "database")
        add_tag(vault_path, PASSWORD, "DB_HOST", "production")
        tags = list_tags(vault_path, PASSWORD, "DB_HOST")
        assert "database" in tags
        assert "production" in tags

    def test_duplicate_tag_not_added_twice(self, vault_path):
        add_tag(vault_path, PASSWORD, "API_KEY", "external")
        add_tag(vault_path, PASSWORD, "API_KEY", "external")
        assert list_tags(vault_path, PASSWORD, "API_KEY").count("external") == 1


class TestRemoveTag:
    def test_remove_existing_tag_returns_true(self, vault_path):
        add_tag(vault_path, PASSWORD, "DB_PORT", "database")
        result = remove_tag(vault_path, PASSWORD, "DB_PORT", "database")
        assert result is True
        assert "database" not in list_tags(vault_path, PASSWORD, "DB_PORT")

    def test_remove_missing_tag_returns_false(self, vault_path):
        result = remove_tag(vault_path, PASSWORD, "DB_PORT", "nonexistent")
        assert result is False

    def test_remove_last_tag_cleans_up_key(self, vault_path):
        add_tag(vault_path, PASSWORD, "API_KEY", "solo")
        remove_tag(vault_path, PASSWORD, "API_KEY", "solo")
        assert list_tags(vault_path, PASSWORD, "API_KEY") == []


class TestKeysForTag:
    def test_returns_all_keys_with_tag(self, vault_path):
        add_tag(vault_path, PASSWORD, "DB_HOST", "database")
        add_tag(vault_path, PASSWORD, "DB_PORT", "database")
        keys = keys_for_tag(vault_path, PASSWORD, "database")
        assert "DB_HOST" in keys
        assert "DB_PORT" in keys

    def test_returns_empty_for_unknown_tag(self, vault_path):
        assert keys_for_tag(vault_path, PASSWORD, "ghost") == []

    def test_tag_isolation(self, vault_path):
        add_tag(vault_path, PASSWORD, "API_KEY", "external")
        add_tag(vault_path, PASSWORD, "DB_HOST", "internal")
        assert keys_for_tag(vault_path, PASSWORD, "external") == ["API_KEY"]


class TestPurgeKeyTags:
    def test_purge_removes_all_tags(self, vault_path):
        add_tag(vault_path, PASSWORD, "DB_HOST", "a")
        add_tag(vault_path, PASSWORD, "DB_HOST", "b")
        purge_key_tags(vault_path, PASSWORD, "DB_HOST")
        assert list_tags(vault_path, PASSWORD, "DB_HOST") == []

    def test_purge_unknown_key_is_noop(self, vault_path):
        purge_key_tags(vault_path, PASSWORD, "NONEXISTENT")
