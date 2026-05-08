"""Tests for envault/pin.py."""

from __future__ import annotations

import pytest

from envault.pin import (
    clear_pins,
    is_pinned,
    list_pins,
    pin_key,
    unpin_key,
)


@pytest.fixture()
def vault_path(tmp_path) -> str:
    return str(tmp_path / "vault.enc")


class TestPinKey:
    def test_returns_entry_dict(self, vault_path):
        entry = pin_key(vault_path, "DB_PASSWORD")
        assert entry["key"] == "DB_PASSWORD"

    def test_entry_stores_reason(self, vault_path):
        entry = pin_key(vault_path, "API_KEY", reason="production secret")
        assert entry["reason"] == "production secret"

    def test_pin_file_created(self, vault_path, tmp_path):
        pin_key(vault_path, "X")
        assert (tmp_path / ".envault_pins.json").exists()

    def test_is_pinned_after_pin(self, vault_path):
        pin_key(vault_path, "MY_KEY")
        assert is_pinned(vault_path, "MY_KEY") is True

    def test_unpinned_key_not_pinned(self, vault_path):
        assert is_pinned(vault_path, "GHOST") is False

    def test_multiple_keys_pinned(self, vault_path):
        pin_key(vault_path, "A")
        pin_key(vault_path, "B")
        assert is_pinned(vault_path, "A") is True
        assert is_pinned(vault_path, "B") is True


class TestUnpinKey:
    def test_unpin_returns_true_when_pinned(self, vault_path):
        pin_key(vault_path, "K")
        assert unpin_key(vault_path, "K") is True

    def test_unpin_returns_false_when_not_pinned(self, vault_path):
        assert unpin_key(vault_path, "MISSING") is False

    def test_key_no_longer_pinned_after_unpin(self, vault_path):
        pin_key(vault_path, "K")
        unpin_key(vault_path, "K")
        assert is_pinned(vault_path, "K") is False


class TestListPins:
    def test_empty_when_no_pins(self, vault_path):
        assert list_pins(vault_path) == []

    def test_lists_all_pinned_keys(self, vault_path):
        pin_key(vault_path, "A", reason="r1")
        pin_key(vault_path, "B", reason="r2")
        keys = [e["key"] for e in list_pins(vault_path)]
        assert set(keys) == {"A", "B"}


class TestClearPins:
    def test_returns_count_of_cleared_pins(self, vault_path):
        pin_key(vault_path, "A")
        pin_key(vault_path, "B")
        assert clear_pins(vault_path) == 2

    def test_no_pins_after_clear(self, vault_path):
        pin_key(vault_path, "A")
        clear_pins(vault_path)
        assert list_pins(vault_path) == []

    def test_clear_on_empty_returns_zero(self, vault_path):
        assert clear_pins(vault_path) == 0
