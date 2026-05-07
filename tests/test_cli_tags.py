"""Integration tests for the tags CLI commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_tags import tags_group
from envault.vault import set_secret

PASSWORD = "cli-tag-pw"


@pytest.fixture()
def setup(tmp_path):
    vault = str(tmp_path / "vault.enc")
    set_secret(vault, PASSWORD, "DB_URL", "postgres://localhost/db")
    set_secret(vault, PASSWORD, "REDIS_URL", "redis://localhost")
    return vault


class TestTagsCLI:
    def _run(self, vault, *args):
        runner = CliRunner()
        return runner.invoke(
            tags_group,
            [*args, "--vault", vault, "--password", PASSWORD],
        )

    def test_add_tag_success_message(self, setup):
        result = self._run(setup, "add", "DB_URL", "database")
        assert result.exit_code == 0
        assert "added" in result.output

    def test_list_shows_added_tag(self, setup):
        self._run(setup, "add", "DB_URL", "database")
        result = self._run(setup, "list", "DB_URL")
        assert result.exit_code == 0
        assert "database" in result.output

    def test_list_no_tags_message(self, setup):
        result = self._run(setup, "list", "REDIS_URL")
        assert result.exit_code == 0
        assert "No tags" in result.output

    def test_remove_existing_tag(self, setup):
        self._run(setup, "add", "DB_URL", "prod")
        result = self._run(setup, "remove", "DB_URL", "prod")
        assert result.exit_code == 0
        assert "removed" in result.output

    def test_remove_missing_tag_message(self, setup):
        result = self._run(setup, "remove", "DB_URL", "ghost")
        assert result.exit_code == 0
        assert "was not set" in result.output

    def test_find_returns_tagged_keys(self, setup):
        self._run(setup, "add", "DB_URL", "storage")
        self._run(setup, "add", "REDIS_URL", "storage")
        result = self._run(setup, "find", "storage")
        assert result.exit_code == 0
        assert "DB_URL" in result.output
        assert "REDIS_URL" in result.output

    def test_find_no_match_message(self, setup):
        result = self._run(setup, "find", "nonexistent")
        assert result.exit_code == 0
        assert "No secrets tagged" in result.output
