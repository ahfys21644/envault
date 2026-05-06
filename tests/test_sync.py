"""Tests for envault.sync and envault.sync_config."""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from envault.sync import pull_vault, push_vault
from envault.sync_config import (
    clear_remote,
    get_remote,
    load_sync_config,
    save_sync_config,
    set_remote,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_vault(tmp_path):
    vault = tmp_path / "project.envault"
    vault.write_text('{"secrets": {}}')
    return vault


# ---------------------------------------------------------------------------
# sync_config tests
# ---------------------------------------------------------------------------

class TestSyncConfig:
    def test_load_missing_returns_empty(self, tmp_path):
        assert load_sync_config(tmp_path) == {}

    def test_save_and_load_roundtrip(self, tmp_path):
        config = {"remote": "/mnt/share/project.envault"}
        save_sync_config(tmp_path, config)
        assert load_sync_config(tmp_path) == config

    def test_set_remote(self, tmp_path):
        set_remote(tmp_path, "user@host:/path/to/vault")
        assert get_remote(tmp_path) == "user@host:/path/to/vault"

    def test_get_remote_none_when_missing(self, tmp_path):
        assert get_remote(tmp_path) is None

    def test_clear_remote(self, tmp_path):
        set_remote(tmp_path, "/some/path")
        clear_remote(tmp_path)
        assert get_remote(tmp_path) is None

    def test_clear_remote_noop_when_not_set(self, tmp_path):
        # Should not raise
        clear_remote(tmp_path)


# ---------------------------------------------------------------------------
# push / pull (local path) tests
# ---------------------------------------------------------------------------

class TestSyncLocalPath:
    def test_push_copies_file(self, tmp_vault, tmp_path):
        dest = tmp_path / "backup" / "project.envault"
        push_vault(tmp_vault, str(dest))
        assert dest.exists()
        assert dest.read_text() == tmp_vault.read_text()

    def test_pull_copies_file(self, tmp_vault, tmp_path):
        local = tmp_path / "local.envault"
        pull_vault(str(tmp_vault), local)
        assert local.exists()
        assert local.read_text() == tmp_vault.read_text()

    def test_push_raises_if_local_missing(self, tmp_path):
        missing = tmp_path / "nonexistent.envault"
        with pytest.raises(FileNotFoundError):
            push_vault(missing, str(tmp_path / "dest.envault"))

    def test_pull_raises_if_remote_missing(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            pull_vault(str(tmp_path / "nonexistent.envault"), tmp_path / "local.envault")


# ---------------------------------------------------------------------------
# push / pull (remote SCP) tests
# ---------------------------------------------------------------------------

class TestSyncRemoteSCP:
    def test_push_calls_scp(self, tmp_vault):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            push_vault(tmp_vault, "user@host:/remote/project.envault")
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert args[0] == "scp"
            assert str(tmp_vault) in args

    def test_pull_calls_scp(self, tmp_path):
        local = tmp_path / "local.envault"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            pull_vault("user@host:/remote/project.envault", local)
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert args[0] == "scp"

    def test_push_raises_on_scp_failure(self, tmp_vault):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stderr="Permission denied")
            with pytest.raises(RuntimeError, match="SCP push failed"):
                push_vault(tmp_vault, "user@host:/remote/project.envault")

    def test_pull_raises_on_scp_failure(self, tmp_path):
        local = tmp_path / "local.envault"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stderr="Host unreachable")
            with pytest.raises(RuntimeError, match="SCP pull failed"):
                pull_vault("user@host:/remote/project.envault", local)
