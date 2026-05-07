"""Tests for envault.merge."""

import os
import pytest

from envault.vault import load_vault, save_vault, set_secret
from envault.merge import merge_vaults, MergeResult


SRC_PASS = "src-pass"
DST_PASS = "dst-pass"


@pytest.fixture()
def vault_pair(tmp_path):
    src = str(tmp_path / "src.vault")
    dst = str(tmp_path / "dst.vault")

    src_vault = load_vault(src)
    set_secret(src_vault, "API_KEY", "abc123", SRC_PASS)
    set_secret(src_vault, "DB_URL", "postgres://src", SRC_PASS)
    set_secret(src_vault, "SHARED", "same-value", SRC_PASS)
    save_vault(src, src_vault)

    dst_vault = load_vault(dst)
    set_secret(dst_vault, "DB_URL", "postgres://dst", DST_PASS)  # conflict
    set_secret(dst_vault, "SHARED", "same-value", DST_PASS)      # identical
    set_secret(dst_vault, "LOCAL", "only-in-dst", DST_PASS)
    save_vault(dst, dst_vault)

    return src, dst


class TestMergeVaults:
    def test_new_key_is_added(self, vault_pair):
        src, dst = vault_pair
        result = merge_vaults(src, SRC_PASS, dst, DST_PASS, strategy="skip")
        assert "API_KEY" in result.added

    def test_identical_key_not_reported(self, vault_pair):
        src, dst = vault_pair
        result = merge_vaults(src, SRC_PASS, dst, DST_PASS, strategy="skip")
        assert "SHARED" not in result.added
        assert "SHARED" not in result.updated
        assert "SHARED" not in result.conflicts
        assert "SHARED" not in result.skipped

    def test_conflict_recorded_with_skip_strategy(self, vault_pair):
        src, dst = vault_pair
        result = merge_vaults(src, SRC_PASS, dst, DST_PASS, strategy="skip")
        assert "DB_URL" in result.conflicts

    def test_conflict_resolved_with_theirs_strategy(self, vault_pair):
        src, dst = vault_pair
        result = merge_vaults(src, SRC_PASS, dst, DST_PASS, strategy="theirs")
        assert "DB_URL" in result.updated
        assert result.conflicts == []

    def test_conflict_kept_with_ours_strategy(self, vault_pair):
        src, dst = vault_pair
        result = merge_vaults(src, SRC_PASS, dst, DST_PASS, strategy="ours")
        assert "DB_URL" in result.skipped
        assert result.conflicts == []

    def test_total_changed_counts_added_and_updated(self, vault_pair):
        src, dst = vault_pair
        result = merge_vaults(src, SRC_PASS, dst, DST_PASS, strategy="theirs")
        assert result.total_changed == len(result.added) + len(result.updated)

    def test_selective_keys_merge(self, vault_pair):
        src, dst = vault_pair
        result = merge_vaults(
            src, SRC_PASS, dst, DST_PASS, strategy="skip", keys=["API_KEY"]
        )
        assert result.added == ["API_KEY"]
        assert result.conflicts == []

    def test_missing_src_key_in_keys_list_ignored(self, vault_pair):
        src, dst = vault_pair
        result = merge_vaults(
            src, SRC_PASS, dst, DST_PASS, strategy="skip", keys=["NONEXISTENT"]
        )
        assert result.added == []
        assert result.conflicts == []
