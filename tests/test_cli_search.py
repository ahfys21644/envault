"""Integration tests for the search CLI commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_search import search_group
from envault.vault import save_vault, set_secret


PASSWORD = "cli-test-pass"


@pytest.fixture()
def setup(tmp_path):
    vault = {}
    for key, value in [
        ("DB_HOST", "db.internal"),
        ("DB_PASS", "s3cr3t"),
        ("REDIS_URL", "redis://localhost"),
    ]:
        set_secret(vault, PASSWORD, key, value)
    vault_path = str(tmp_path / "test.vault")
    save_vault(vault_path, vault)
    return vault_path


class TestSearchCLI:
    def _run(self, *args, vault_path: str):
        runner = CliRunner()
        return runner.invoke(
            search_group,
            args,
            input=f"{PASSWORD}\n",
            catch_exceptions=False,
        )

    def test_keys_glob_finds_matches(self, setup):
        result = self._run("keys", "DB_*", "--vault", setup, vault_path=setup)
        assert result.exit_code == 0
        assert "DB_HOST" in result.output
        assert "DB_PASS" in result.output
        assert "REDIS_URL" not in result.output

    def test_keys_no_match_message(self, setup):
        result = self._run("keys", "NOPE_*", "--vault", setup, vault_path=setup)
        assert result.exit_code == 0
        assert "No matches found" in result.output

    def test_keys_show_values_flag(self, setup):
        result = self._run(
            "keys", "DB_HOST", "--vault", setup, "--show-values", vault_path=setup
        )
        assert result.exit_code == 0
        assert "DB_HOST=db.internal" in result.output

    def test_values_substring_search(self, setup):
        result = self._run("values", "localhost", "--vault", setup, vault_path=setup)
        assert result.exit_code == 0
        assert "REDIS_URL" in result.output

    def test_values_reveals_matching_value(self, setup):
        result = self._run("values", "s3cr3t", "--vault", setup, vault_path=setup)
        assert result.exit_code == 0
        assert "DB_PASS=s3cr3t" in result.output

    def test_values_no_match_message(self, setup):
        result = self._run("values", "zzznomatch", "--vault", setup, vault_path=setup)
        assert result.exit_code == 0
        assert "No matches found" in result.output
