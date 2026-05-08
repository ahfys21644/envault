"""Integration tests for TTL CLI commands."""

import pytest
from pathlib import Path
from click.testing import CliRunner

from envault.cli_ttl import ttl_group
from envault.ttl import set_ttl
from envault.vault import set_secret


@pytest.fixture
def setup(tmp_path):
    vault = tmp_path / ".envault"
    password = "secret"
    set_secret(vault, "DB_PASS", "hunter2", password)
    return {"vault": vault, "password": password}


class TestTTLCLI:
    def _run(self, args, vault, input_text=None):
        runner = CliRunner()
        full_args = args + ["--vault", str(vault)]
        return runner.invoke(ttl_group, full_args, input=input_text)

    def test_set_ttl_shows_expiry(self, setup):
        result = self._run(["set", "DB_PASS", "3600"], setup["vault"])
        assert result.exit_code == 0
        assert "DB_PASS" in result.output
        assert "3600s" in result.output

    def test_get_ttl_shows_remaining(self, setup):
        set_ttl(setup["vault"], "DB_PASS", 9999)
        result = self._run(["get", "DB_PASS"], setup["vault"])
        assert result.exit_code == 0
        assert "remaining" in result.output

    def test_get_ttl_no_ttl_set(self, setup):
        result = self._run(["get", "DB_PASS"], setup["vault"])
        assert result.exit_code == 0
        assert "No TTL" in result.output

    def test_get_ttl_expired(self, setup):
        set_ttl(setup["vault"], "DB_PASS", -1)
        result = self._run(["get", "DB_PASS"], setup["vault"])
        assert result.exit_code == 0
        assert "EXPIRED" in result.output

    def test_remove_ttl_success(self, setup):
        set_ttl(setup["vault"], "DB_PASS", 300)
        result = self._run(["remove", "DB_PASS"], setup["vault"])
        assert result.exit_code == 0
        assert "removed" in result.output

    def test_remove_ttl_not_set(self, setup):
        result = self._run(["remove", "DB_PASS"], setup["vault"])
        assert result.exit_code == 0
        assert "No TTL was set" in result.output

    def test_list_expired_shows_key(self, setup):
        set_ttl(setup["vault"], "DB_PASS", -1)
        result = self._run(["list-expired"], setup["vault"])
        assert result.exit_code == 0
        assert "DB_PASS" in result.output

    def test_list_expired_empty(self, setup):
        result = self._run(["list-expired"], setup["vault"])
        assert result.exit_code == 0
        assert "No expired" in result.output
