"""Tests for envault.snapshots."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.snapshots import (
    create_snapshot,
    delete_snapshot,
    list_snapshots,
    restore_snapshot,
)
from envault.vault import save_vault, load_vault
from envault.crypto import encrypt

PASSWORD = "test-pass"


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    path = tmp_path / ".envault"
    data = {
        "API_KEY": encrypt("abc123", PASSWORD),
        "DB_URL": encrypt("postgres://localhost/db", PASSWORD),
    }
    save_vault(path, data)
    return path


class TestCreateSnapshot:
    def test_returns_entry_with_label(self, vault_path: Path) -> None:
        entry = create_snapshot(vault_path, PASSWORD, "v1")
        assert entry["label"] == "v1"

    def test_entry_contains_vault_data(self, vault_path: Path) -> None:
        vault = load_vault(vault_path)
        entry = create_snapshot(vault_path, PASSWORD, "v1")
        assert entry["data"] == vault

    def test_entry_has_timestamp(self, vault_path: Path) -> None:
        entry = create_snapshot(vault_path, PASSWORD, "v1")
        assert isinstance(entry["timestamp"], float)
        assert entry["timestamp"] > 0

    def test_overwrite_existing_label(self, vault_path: Path) -> None:
        create_snapshot(vault_path, PASSWORD, "v1")
        # Modify vault then overwrite snapshot
        save_vault(vault_path, {})
        entry = create_snapshot(vault_path, PASSWORD, "v1")
        assert entry["data"] == {}


class TestListSnapshots:
    def test_empty_when_none_created(self, vault_path: Path) -> None:
        assert list_snapshots(vault_path) == []

    def test_returns_all_snapshots(self, vault_path: Path) -> None:
        create_snapshot(vault_path, PASSWORD, "v1")
        create_snapshot(vault_path, PASSWORD, "v2")
        entries = list_snapshots(vault_path)
        labels = [e["label"] for e in entries]
        assert "v1" in labels and "v2" in labels

    def test_sorted_by_timestamp(self, vault_path: Path) -> None:
        create_snapshot(vault_path, PASSWORD, "first")
        create_snapshot(vault_path, PASSWORD, "second")
        entries = list_snapshots(vault_path)
        assert entries[0]["timestamp"] <= entries[1]["timestamp"]


class TestRestoreSnapshot:
    def test_restores_secrets_count(self, vault_path: Path) -> None:
        create_snapshot(vault_path, PASSWORD, "v1")
        save_vault(vault_path, {})  # wipe vault
        count = restore_snapshot(vault_path, PASSWORD, "v1")
        assert count == 2

    def test_vault_contains_restored_data(self, vault_path: Path) -> None:
        original = load_vault(vault_path)
        create_snapshot(vault_path, PASSWORD, "v1")
        save_vault(vault_path, {})
        restore_snapshot(vault_path, PASSWORD, "v1")
        assert load_vault(vault_path) == original

    def test_missing_label_raises_key_error(self, vault_path: Path) -> None:
        with pytest.raises(KeyError, match="nope"):
            restore_snapshot(vault_path, PASSWORD, "nope")


class TestDeleteSnapshot:
    def test_returns_true_when_deleted(self, vault_path: Path) -> None:
        create_snapshot(vault_path, PASSWORD, "v1")
        assert delete_snapshot(vault_path, "v1") is True

    def test_returns_false_when_not_found(self, vault_path: Path) -> None:
        assert delete_snapshot(vault_path, "ghost") is False

    def test_snapshot_no_longer_listed(self, vault_path: Path) -> None:
        create_snapshot(vault_path, PASSWORD, "v1")
        delete_snapshot(vault_path, "v1")
        labels = [e["label"] for e in list_snapshots(vault_path)]
        assert "v1" not in labels
