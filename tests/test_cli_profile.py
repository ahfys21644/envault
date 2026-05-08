"""Tests for envault/cli_profile.py"""

from __future__ import annotations

import pytest
from pathlib import Path
from click.testing import CliRunner

from envault.cli_profile import profile_group
from envault.profile import create_profile, assign_key


@pytest.fixture
def setup(tmp_path: Path):
    vault = tmp_path / "vault.enc"
    runner = CliRunner()
    return runner, vault


class TestProfileCLI:
    def _run(self, runner, vault, *args):
        return runner.invoke(profile_group, [*args, "--vault", str(vault)])

    def test_create_profile_success_message(self, setup):
        runner, vault = setup
        result = self._run(runner, vault, "create", "production")
        assert result.exit_code == 0
        assert "created" in result.output

    def test_create_duplicate_shows_error(self, setup):
        runner, vault = setup
        self._run(runner, vault, "create", "dev")
        result = self._run(runner, vault, "create", "dev")
        assert "already exists" in result.output

    def test_delete_profile_success_message(self, setup):
        runner, vault = setup
        create_profile(vault, "temp")
        result = self._run(runner, vault, "delete", "temp")
        assert result.exit_code == 0
        assert "deleted" in result.output

    def test_delete_missing_profile_shows_error(self, setup):
        runner, vault = setup
        result = self._run(runner, vault, "delete", "ghost")
        assert "not found" in result.output

    def test_assign_key_success_message(self, setup):
        runner, vault = setup
        create_profile(vault, "prod")
        result = self._run(runner, vault, "assign", "prod", "DB_URL")
        assert result.exit_code == 0
        assert "assigned" in result.output

    def test_list_shows_all_profiles(self, setup):
        runner, vault = setup
        create_profile(vault, "dev")
        create_profile(vault, "prod")
        result = self._run(runner, vault, "list")
        assert "dev" in result.output
        assert "prod" in result.output

    def test_list_empty_shows_no_profiles_message(self, setup):
        runner, vault = setup
        result = self._run(runner, vault, "list")
        assert "No profiles" in result.output

    def test_show_profile_keys(self, setup):
        runner, vault = setup
        create_profile(vault, "ci")
        assign_key(vault, "ci", "CI_TOKEN")
        result = self._run(runner, vault, "show", "ci")
        assert "CI_TOKEN" in result.output

    def test_show_missing_profile_error(self, setup):
        runner, vault = setup
        result = self._run(runner, vault, "show", "unknown")
        assert "not found" in result.output
