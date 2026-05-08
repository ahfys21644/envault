"""Tests for envault.lock module."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from envault.lock import (
    lock_vault,
    unlock_vault,
    is_locked,
    get_lock_info,
    assert_unlocked,
)


@pytest.fixture
def vault_path(tmp_path: Path) -> str:
    p = tmp_path / "vault.json"
    p.write_text("{}")
    return str(p)


class TestLockVault:
    def test_lock_creates_lock_file(self, vault_path: str) -> None:
        lock_vault(vault_path)
        assert Path(vault_path).with_suffix(".lock").exists()

    def test_lock_returns_entry_dict(self, vault_path: str) -> None:
        entry = lock_vault(vault_path)
        assert "locked_at" in entry
        assert "reason" in entry

    def test_lock_stores_reason(self, vault_path: str) -> None:
        lock_vault(vault_path, reason="deployment freeze")
        info = get_lock_info(vault_path)
        assert info["reason"] == "deployment freeze"

    def test_double_lock_raises(self, vault_path: str) -> None:
        lock_vault(vault_path)
        with pytest.raises(FileExistsError):
            lock_vault(vault_path)

    def test_is_locked_true_after_lock(self, vault_path: str) -> None:
        lock_vault(vault_path)
        assert is_locked(vault_path) is True

    def test_is_locked_false_before_lock(self, vault_path: str) -> None:
        assert is_locked(vault_path) is False


class TestUnlockVault:
    def test_unlock_removes_lock_file(self, vault_path: str) -> None:
        lock_vault(vault_path)
        unlock_vault(vault_path)
        assert not is_locked(vault_path)

    def test_unlock_returns_true_when_lock_existed(self, vault_path: str) -> None:
        lock_vault(vault_path)
        assert unlock_vault(vault_path) is True

    def test_unlock_returns_false_when_no_lock(self, vault_path: str) -> None:
        assert unlock_vault(vault_path) is False


class TestGetLockInfo:
    def test_returns_none_when_unlocked(self, vault_path: str) -> None:
        assert get_lock_info(vault_path) is None

    def test_returns_dict_when_locked(self, vault_path: str) -> None:
        lock_vault(vault_path, reason="test")
        info = get_lock_info(vault_path)
        assert isinstance(info, dict)
        assert info["reason"] == "test"

    def test_locked_at_ends_with_z(self, vault_path: str) -> None:
        lock_vault(vault_path)
        info = get_lock_info(vault_path)
        assert info["locked_at"].endswith("Z")


class TestAssertUnlocked:
    def test_no_error_when_unlocked(self, vault_path: str) -> None:
        assert_unlocked(vault_path)  # should not raise

    def test_raises_permission_error_when_locked(self, vault_path: str) -> None:
        lock_vault(vault_path, reason="frozen")
        with pytest.raises(PermissionError, match="frozen"):
            assert_unlocked(vault_path)
