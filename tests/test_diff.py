"""Tests for envault.diff module."""

import os
import pytest

from envault.diff import DiffEntry, diff_vault_vs_file, format_diff
from envault.vault import load_vault, save_vault, set_secret


PASSWORD = "diffpassword"


@pytest.fixture()
def vault_path(tmp_path):
    path = str(tmp_path / "test.envault")
    vault = load_vault(path)
    vault = set_secret(vault, "SHARED_KEY", "same_value", PASSWORD)
    vault = set_secret(vault, "VAULT_ONLY", "vault_secret", PASSWORD)
    vault = set_secret(vault, "CHANGED_KEY", "old_value", PASSWORD)
    save_vault(vault, path)
    return path


@pytest.fixture()
def dotenv_path(tmp_path):
    path = str(tmp_path / ".env")
    content = "SHARED_KEY=same_value\nFILE_ONLY=file_secret\nCHANGED_KEY=new_value\n"
    with open(path, "w") as fh:
        fh.write(content)
    return path


class TestDiffVaultVsFile:
    def test_unchanged_key_detected(self, vault_path, dotenv_path):
        entries = diff_vault_vs_file(vault_path, dotenv_path, PASSWORD)
        statuses = {e.key: e.status for e in entries}
        assert statuses["SHARED_KEY"] == "unchanged"

    def test_vault_only_key_is_removed(self, vault_path, dotenv_path):
        entries = diff_vault_vs_file(vault_path, dotenv_path, PASSWORD)
        statuses = {e.key: e.status for e in entries}
        assert statuses["VAULT_ONLY"] == "removed"

    def test_file_only_key_is_added(self, vault_path, dotenv_path):
        entries = diff_vault_vs_file(vault_path, dotenv_path, PASSWORD)
        statuses = {e.key: e.status for e in entries}
        assert statuses["FILE_ONLY"] == "added"

    def test_changed_key_detected(self, vault_path, dotenv_path):
        entries = diff_vault_vs_file(vault_path, dotenv_path, PASSWORD)
        statuses = {e.key: e.status for e in entries}
        assert statuses["CHANGED_KEY"] == "changed"

    def test_changed_entry_has_both_values(self, vault_path, dotenv_path):
        entries = diff_vault_vs_file(vault_path, dotenv_path, PASSWORD)
        changed = next(e for e in entries if e.key == "CHANGED_KEY")
        assert changed.vault_value == "old_value"
        assert changed.file_value == "new_value"

    def test_missing_dotenv_raises(self, vault_path, tmp_path):
        with pytest.raises(FileNotFoundError):
            diff_vault_vs_file(vault_path, str(tmp_path / "missing.env"), PASSWORD)

    def test_returns_sorted_keys(self, vault_path, dotenv_path):
        entries = diff_vault_vs_file(vault_path, dotenv_path, PASSWORD)
        keys = [e.key for e in entries]
        assert keys == sorted(keys)


class TestFormatDiff:
    def test_added_shows_plus(self):
        entries = [DiffEntry("FOO", "added", file_value="bar")]
        assert format_diff(entries).startswith("+")

    def test_removed_shows_minus(self):
        entries = [DiffEntry("FOO", "removed", vault_value="bar")]
        assert format_diff(entries).startswith("-")

    def test_changed_shows_tilde(self):
        entries = [DiffEntry("FOO", "changed", vault_value="a", file_value="b")]
        assert format_diff(entries).startswith("~")

    def test_show_values_includes_arrow(self):
        entries = [DiffEntry("FOO", "changed", vault_value="a", file_value="b")]
        output = format_diff(entries, show_values=True)
        assert "->" in output

    def test_empty_entries_returns_placeholder(self):
        assert format_diff([]) == "(no differences)"
