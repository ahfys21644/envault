"""Tests for envault.history."""

from __future__ import annotations

import os
import pytest

from envault.history import (
    clear_key_history,
    get_key_history,
    list_keys_with_history,
    record_change,
)


@pytest.fixture()
def vault_path(tmp_path: pytest.TempPathFactory) -> str:
    return str(tmp_path / "vault.enc")


class TestRecordChange:
    def test_returns_entry_dict(self, vault_path: str) -> None:
        entry = record_change(vault_path, "API_KEY", "set")
        assert entry["action"] == "set"
        assert "timestamp" in entry

    def test_entry_stored_for_key(self, vault_path: str) -> None:
        record_change(vault_path, "DB_URL", "set")
        entries = get_key_history(vault_path, "DB_URL")
        assert len(entries) == 1
        assert entries[0]["action"] == "set"

    def test_old_value_recorded(self, vault_path: str) -> None:
        record_change(vault_path, "TOKEN", "update", old_value="old_secret")
        entries = get_key_history(vault_path, "TOKEN")
        assert entries[0]["old_value"] == "old_secret"

    def test_multiple_changes_appended(self, vault_path: str) -> None:
        record_change(vault_path, "KEY", "set")
        record_change(vault_path, "KEY", "update", old_value="v1")
        record_change(vault_path, "KEY", "delete")
        entries = get_key_history(vault_path, "KEY")
        assert len(entries) == 3
        assert [e["action"] for e in entries] == ["set", "update", "delete"]

    def test_different_keys_independent(self, vault_path: str) -> None:
        record_change(vault_path, "A", "set")
        record_change(vault_path, "B", "set")
        assert len(get_key_history(vault_path, "A")) == 1
        assert len(get_key_history(vault_path, "B")) == 1


class TestGetKeyHistory:
    def test_missing_key_returns_empty(self, vault_path: str) -> None:
        assert get_key_history(vault_path, "MISSING") == []

    def test_missing_history_file_returns_empty(self, vault_path: str) -> None:
        assert get_key_history(vault_path, "ANY") == []


class TestClearKeyHistory:
    def test_returns_count_of_removed_entries(self, vault_path: str) -> None:
        record_change(vault_path, "X", "set")
        record_change(vault_path, "X", "update")
        assert clear_key_history(vault_path, "X") == 2

    def test_history_empty_after_clear(self, vault_path: str) -> None:
        record_change(vault_path, "X", "set")
        clear_key_history(vault_path, "X")
        assert get_key_history(vault_path, "X") == []

    def test_clear_missing_key_returns_zero(self, vault_path: str) -> None:
        assert clear_key_history(vault_path, "NOPE") == 0

    def test_other_keys_unaffected(self, vault_path: str) -> None:
        record_change(vault_path, "A", "set")
        record_change(vault_path, "B", "set")
        clear_key_history(vault_path, "A")
        assert len(get_key_history(vault_path, "B")) == 1


class TestListKeysWithHistory:
    def test_empty_when_no_history(self, vault_path: str) -> None:
        assert list_keys_with_history(vault_path) == []

    def test_lists_all_keys(self, vault_path: str) -> None:
        record_change(vault_path, "Z", "set")
        record_change(vault_path, "A", "set")
        keys = list_keys_with_history(vault_path)
        assert keys == ["A", "Z"]

    def test_cleared_key_not_listed(self, vault_path: str) -> None:
        record_change(vault_path, "GONE", "set")
        clear_key_history(vault_path, "GONE")
        assert "GONE" not in list_keys_with_history(vault_path)
