"""CLI integration tests for the pin command group."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_pin import pin_group
from envault.pin import pin_key


@pytest.fixture()
def setup(tmp_path):
    vault = str(tmp_path / "vault.enc")
    runner = CliRunner()
    return runner, vault


class TestPinCLI:
    def _run(self, runner, vault, *args):
        return runner.invoke(pin_group, [*args, "--vault", vault])

    def test_set_pin_success_message(self, setup):
        runner, vault = setup
        result = self._run(runner, vault, "set", "DB_PASS")
        assert result.exit_code == 0
        assert "Pinned 'DB_PASS'" in result.output

    def test_set_pin_with_reason(self, setup):
        runner, vault = setup
        result = self._run(runner, vault, "set", "API_KEY", "--reason", "prod")
        assert "prod" in result.output

    def test_unset_pinned_key(self, setup):
        runner, vault = setup
        pin_key(vault, "MY_KEY")
        result = self._run(runner, vault, "unset", "MY_KEY")
        assert result.exit_code == 0
        assert "Unpinned 'MY_KEY'" in result.output

    def test_unset_not_pinned_shows_error(self, setup):
        runner, vault = setup
        result = self._run(runner, vault, "unset", "GHOST")
        assert "was not pinned" in result.output

    def test_status_pinned(self, setup):
        runner, vault = setup
        pin_key(vault, "X")
        result = self._run(runner, vault, "status", "X")
        assert "PINNED" in result.output

    def test_status_not_pinned(self, setup):
        runner, vault = setup
        result = self._run(runner, vault, "status", "X")
        assert "not pinned" in result.output

    def test_list_shows_pinned_keys(self, setup):
        runner, vault = setup
        pin_key(vault, "A")
        pin_key(vault, "B")
        result = self._run(runner, vault, "list")
        assert "A" in result.output
        assert "B" in result.output

    def test_list_empty_message(self, setup):
        runner, vault = setup
        result = self._run(runner, vault, "list")
        assert "No keys are pinned" in result.output

    def test_clear_reports_count(self, setup):
        runner, vault = setup
        pin_key(vault, "A")
        pin_key(vault, "B")
        result = self._run(runner, vault, "clear")
        assert "2" in result.output
