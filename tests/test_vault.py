"""Unit tests for envault.vault."""

import pytest
from pathlib import Path

from envault.vault import (
    load_vault, save_vault, set_secret,
    get_secret, delete_secret, list_keys,
)

PASSWORD = "test-password-123"


@pytest.fixture
def vault_path(tmp_path) -> Path:
    return tmp_path / ".envault"


class TestVaultOperations:
    def test_load_missing_vault_returns_empty(self, vault_path):
        assert load_vault(vault_path, PASSWORD) == {}

    def test_save_and_load_roundtrip(self, vault_path):
        data = {"KEY": "value", "OTHER": "123"}
        save_vault(data, vault_path, PASSWORD)
        loaded = load_vault(vault_path, PASSWORD)
        assert loaded == data

    def test_set_and_get_secret(self, vault_path):
        set_secret("DB_URL", "postgres://localhost/test", vault_path, PASSWORD)
        assert get_secret("DB_URL", vault_path, PASSWORD) == "postgres://localhost/test"

    def test_get_missing_key_returns_none(self, vault_path):
        assert get_secret("MISSING", vault_path, PASSWORD) is None

    def test_overwrite_existing_key(self, vault_path):
        set_secret("K", "old", vault_path, PASSWORD)
        set_secret("K", "new", vault_path, PASSWORD)
        assert get_secret("K", vault_path, PASSWORD) == "new"

    def test_delete_existing_key(self, vault_path):
        set_secret("TO_DELETE", "bye", vault_path, PASSWORD)
        result = delete_secret("TO_DELETE", vault_path, PASSWORD)
        assert result is True
        assert get_secret("TO_DELETE", vault_path, PASSWORD) is None

    def test_delete_missing_key_returns_false(self, vault_path):
        assert delete_secret("NOPE", vault_path, PASSWORD) is False

    def test_list_keys_sorted(self, vault_path):
        for k in ["ZEBRA", "APPLE", "MANGO"]:
            set_secret(k, "v", vault_path, PASSWORD)
        assert list_keys(vault_path, PASSWORD) == ["APPLE", "MANGO", "ZEBRA"]

    def test_list_keys_empty_vault(self, vault_path):
        assert list_keys(vault_path, PASSWORD) == []
