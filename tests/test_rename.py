"""Tests for envault.rename."""

from __future__ import annotations

import os
import pytest

from envault.vault import save_vault
from envault.crypto import encrypt
from envault.tags import add_tag, list_tags
from envault.rename import rename_key

PASSWORD = "test-pass"


@pytest.fixture()
def vault_path(tmp_path):
    path = str(tmp_path / "vault.json")
    data = {
        "FOO": encrypt("bar", PASSWORD),
        "BAZ": encrypt("qux", PASSWORD),
    }
    save_vault(path, data)
    return path


class TestRenameKey:
    def test_rename_succeeds(self, vault_path):
        result = rename_key(vault_path, "FOO", "FOO_NEW", PASSWORD)
        assert result.success is True

    def test_old_key_removed(self, vault_path):
        rename_key(vault_path, "FOO", "FOO_NEW", PASSWORD)
        from envault.vault import load_vault
        vault = load_vault(vault_path)
        assert "FOO" not in vault

    def test_new_key_present(self, vault_path):
        rename_key(vault_path, "FOO", "FOO_NEW", PASSWORD)
        from envault.vault import load_vault
        vault = load_vault(vault_path)
        assert "FOO_NEW" in vault

    def test_value_preserved(self, vault_path):
        rename_key(vault_path, "FOO", "FOO_NEW", PASSWORD)
        from envault.vault import get_secret
        assert get_secret(vault_path, "FOO_NEW", PASSWORD) == "bar"

    def test_unaffected_key_preserved(self, vault_path):
        """Renaming one key should not alter other keys in the vault."""
        rename_key(vault_path, "FOO", "FOO_NEW", PASSWORD)
        from envault.vault import get_secret
        assert get_secret(vault_path, "BAZ", PASSWORD) == "qux"

    def test_missing_key_returns_failure(self, vault_path):
        result = rename_key(vault_path, "MISSING", "ANYTHING", PASSWORD)
        assert result.success is False
        assert "not found" in result.message

    def test_same_key_returns_failure(self, vault_path):
        result = rename_key(vault_path, "FOO", "FOO", PASSWORD)
        assert result.success is False
        assert "identical" in result.message

    def test_existing_destination_without_overwrite_fails(self, vault_path):
        result = rename_key(vault_path, "FOO", "BAZ", PASSWORD)
        assert result.success is False
        assert "overwrite" in result.message.lower()

    def test_existing_destination_with_overwrite_succeeds(self, vault_path):
        result = rename_key(vault_path, "FOO", "BAZ", PASSWORD, overwrite=True)
        assert result.success is True

    def test_tags_migrated_to_new_key(self, vault_path):
        add_tag(vault_path, "FOO", "important")
        rename_key(vault_path, "FOO", "FOO_NEW", PASSWORD)
        assert "important" in list_tags(vault_path, "FOO_NEW")

    def test_tags_removed_from_old_key(self, vault_path):
        add_tag(vault_path, "FOO", "important")
        rename_key(vault_path, "FOO", "FOO_NEW", PASSWORD)
        assert list_tags(vault_path, "FOO") == []
