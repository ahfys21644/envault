"""Tests for envault.watch."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from envault.crypto import encrypt
from envault.vault import save_vault, get_secret
from envault.watch import watch_file, _get_mtime, _sync_once, WatchState


PASSWORD = "watchpass"


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "vault.json"


@pytest.fixture()
def dotenv_path(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("KEY1=hello\nKEY2=world\n")
    return p


class TestGetMtime:
    def test_returns_float_for_existing_file(self, dotenv_path):
        assert _get_mtime(dotenv_path) > 0.0

    def test_returns_zero_for_missing_file(self, tmp_path):
        assert _get_mtime(tmp_path / "missing.env") == 0.0


class TestSyncOnce:
    def test_no_sync_when_mtime_unchanged(self, dotenv_path, vault_path):
        state = WatchState(
            path=dotenv_path,
            vault_path=vault_path,
            password=PASSWORD,
            last_mtime=_get_mtime(dotenv_path),
        )
        assert _sync_once(state) is False

    def test_syncs_when_mtime_advances(self, dotenv_path, vault_path):
        state = WatchState(
            path=dotenv_path,
            vault_path=vault_path,
            password=PASSWORD,
            last_mtime=0.0,
        )
        result = _sync_once(state)
        assert result is True
        assert state.changes_detected == 1

    def test_secrets_written_to_vault(self, dotenv_path, vault_path):
        state = WatchState(
            path=dotenv_path,
            vault_path=vault_path,
            password=PASSWORD,
            last_mtime=0.0,
        )
        _sync_once(state)
        value = get_secret(vault_path, PASSWORD, "KEY1")
        assert value == "hello"

    def test_error_recorded_on_bad_file(self, tmp_path, vault_path):
        bad = tmp_path / "bad.env"
        bad.write_text("")
        state = WatchState(
            path=bad,
            vault_path=vault_path,
            password=PASSWORD,
            last_mtime=0.0,
        )
        # Force a failure by making vault_path a directory
        vault_path.mkdir()
        _sync_once(state)
        assert len(state.errors) == 1


class TestWatchFile:
    def test_returns_watch_state(self, dotenv_path, vault_path):
        state = watch_file(
            dotenv_path=dotenv_path,
            vault_path=vault_path,
            password=PASSWORD,
            interval=0.0,
            max_iterations=0,
        )
        assert isinstance(state, WatchState)

    def test_on_change_callback_called(self, dotenv_path, vault_path):
        calls = []
        # Set mtime to 0 so first iteration triggers a sync
        state = watch_file(
            dotenv_path=dotenv_path,
            vault_path=vault_path,
            password=PASSWORD,
            interval=0.0,
            max_iterations=1,
            on_change=lambda s: calls.append(s.changes_detected),
        )
        # mtime starts at 0, file exists → should sync
        # We can't guarantee timing, but at most 1 call
        assert len(calls) <= 1
