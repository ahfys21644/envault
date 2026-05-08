"""Tests for envault/ttl.py"""

import time
import pytest
from pathlib import Path

from envault.ttl import (
    set_ttl,
    get_ttl,
    remove_ttl,
    list_expired,
    purge_expired,
    _ttl_path,
)
from envault.vault import set_secret, get_secret


@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / ".envault"


class TestSetTTL:
    def test_returns_entry_dict(self, vault_path):
        result = set_ttl(vault_path, "API_KEY", 3600)
        assert result["key"] == "API_KEY"
        assert result["ttl_seconds"] == 3600
        assert result["expires_at"] > time.time()

    def test_ttl_file_created(self, vault_path):
        set_ttl(vault_path, "API_KEY", 60)
        assert _ttl_path(vault_path).exists()

    def test_multiple_keys_stored(self, vault_path):
        set_ttl(vault_path, "KEY_A", 100)
        set_ttl(vault_path, "KEY_B", 200)
        info_a = get_ttl(vault_path, "KEY_A")
        info_b = get_ttl(vault_path, "KEY_B")
        assert info_a is not None
        assert info_b is not None


class TestGetTTL:
    def test_returns_none_when_not_set(self, vault_path):
        assert get_ttl(vault_path, "MISSING") is None

    def test_remaining_seconds_positive_for_future(self, vault_path):
        set_ttl(vault_path, "TOKEN", 9999)
        info = get_ttl(vault_path, "TOKEN")
        assert info["remaining_seconds"] > 0
        assert not info["expired"]

    def test_expired_flag_set_for_past_expiry(self, vault_path):
        set_ttl(vault_path, "OLD", -1)  # already expired
        info = get_ttl(vault_path, "OLD")
        assert info["expired"] is True
        assert info["remaining_seconds"] == 0.0


class TestRemoveTTL:
    def test_remove_existing_returns_true(self, vault_path):
        set_ttl(vault_path, "K", 60)
        assert remove_ttl(vault_path, "K") is True

    def test_remove_missing_returns_false(self, vault_path):
        assert remove_ttl(vault_path, "NONEXISTENT") is False

    def test_after_remove_get_returns_none(self, vault_path):
        set_ttl(vault_path, "K", 60)
        remove_ttl(vault_path, "K")
        assert get_ttl(vault_path, "K") is None


class TestListExpired:
    def test_empty_when_no_ttls(self, vault_path):
        assert list_expired(vault_path) == []

    def test_returns_only_expired_keys(self, vault_path):
        set_ttl(vault_path, "LIVE", 9999)
        set_ttl(vault_path, "DEAD", -1)
        expired = list_expired(vault_path)
        assert "DEAD" in expired
        assert "LIVE" not in expired


class TestPurgeExpired:
    def test_purged_keys_removed_from_vault(self, vault_path):
        password = "testpass"
        set_secret(vault_path, "STALE", "old_value", password)
        set_ttl(vault_path, "STALE", -1)
        purged = purge_expired(vault_path, password)
        assert "STALE" in purged
        assert get_secret(vault_path, "STALE", password) is None

    def test_purge_clears_ttl_entry(self, vault_path):
        password = "testpass"
        set_secret(vault_path, "STALE", "v", password)
        set_ttl(vault_path, "STALE", -1)
        purge_expired(vault_path, password)
        assert get_ttl(vault_path, "STALE") is None

    def test_live_keys_not_purged(self, vault_path):
        password = "testpass"
        set_secret(vault_path, "LIVE", "v", password)
        set_ttl(vault_path, "LIVE", 9999)
        purged = purge_expired(vault_path, password)
        assert "LIVE" not in purged
