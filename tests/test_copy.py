"""Tests for envault.copy — inter-vault key copying."""

from __future__ import annotations

import os
import pytest

from envault.vault import set_secret, get_secret
from envault.copy import copy_key, copy_keys, copy_all, CopyResult


@pytest.fixture()
def vault_pair(tmp_path):
    src = str(tmp_path / "src.vault")
    dst = str(tmp_path / "dst.vault")
    return src, dst


SRC_PASS = "src-password"
DST_PASS = "dst-password"


class TestCopyKey:
    def test_copies_value_to_destination(self, vault_pair):
        src, dst = vault_pair
        set_secret(src, SRC_PASS, "API_KEY", "abc123")
        result = copy_key("API_KEY", src, SRC_PASS, dst, DST_PASS)
        assert result.success is True
        assert get_secret(dst, DST_PASS, "API_KEY") == "abc123"

    def test_missing_key_returns_failure(self, vault_pair):
        src, dst = vault_pair
        result = copy_key("MISSING", src, SRC_PASS, dst, DST_PASS)
        assert result.success is False
        assert "not found" in result.error

    def test_existing_key_without_overwrite_fails(self, vault_pair):
        src, dst = vault_pair
        set_secret(src, SRC_PASS, "TOKEN", "original")
        set_secret(dst, DST_PASS, "TOKEN", "existing")
        result = copy_key("TOKEN", src, SRC_PASS, dst, DST_PASS, overwrite=False)
        assert result.success is False
        assert "overwrite" in result.error
        assert get_secret(dst, DST_PASS, "TOKEN") == "existing"

    def test_existing_key_with_overwrite_succeeds(self, vault_pair):
        src, dst = vault_pair
        set_secret(src, SRC_PASS, "TOKEN", "new-value")
        set_secret(dst, DST_PASS, "TOKEN", "old-value")
        result = copy_key("TOKEN", src, SRC_PASS, dst, DST_PASS, overwrite=True)
        assert result.success is True
        assert get_secret(dst, DST_PASS, "TOKEN") == "new-value"

    def test_result_has_correct_source_and_destination(self, vault_pair):
        src, dst = vault_pair
        set_secret(src, SRC_PASS, "X", "1")
        result = copy_key("X", src, SRC_PASS, dst, DST_PASS)
        assert result.source == src
        assert result.destination == dst
        assert result.key == "X"


class TestCopyKeys:
    def test_copies_multiple_keys(self, vault_pair):
        src, dst = vault_pair
        for k, v in [("A", "1"), ("B", "2"), ("C", "3")]:
            set_secret(src, SRC_PASS, k, v)
        results = copy_keys(["A", "B", "C"], src, SRC_PASS, dst, DST_PASS)
        assert all(r.success for r in results)
        assert get_secret(dst, DST_PASS, "B") == "2"

    def test_partial_failure_does_not_block_others(self, vault_pair):
        src, dst = vault_pair
        set_secret(src, SRC_PASS, "GOOD", "ok")
        results = copy_keys(["GOOD", "BAD"], src, SRC_PASS, dst, DST_PASS)
        successes = [r for r in results if r.success]
        failures = [r for r in results if not r.success]
        assert len(successes) == 1
        assert len(failures) == 1


class TestCopyAll:
    def test_copies_all_keys(self, vault_pair):
        src, dst = vault_pair
        secrets = {"K1": "v1", "K2": "v2", "K3": "v3"}
        for k, v in secrets.items():
            set_secret(src, SRC_PASS, k, v)
        results = copy_all(src, SRC_PASS, dst, DST_PASS)
        assert len(results) == 3
        assert all(r.success for r in results)

    def test_empty_source_vault_returns_empty_list(self, vault_pair):
        src, dst = vault_pair
        results = copy_all(src, SRC_PASS, dst, DST_PASS)
        assert results == []
