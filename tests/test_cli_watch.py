"""CLI tests for the watch command group."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envault.cli_watch import watch_group
from envault.watch import WatchState


PASSWORD = "cliwatch"


@pytest.fixture()
def setup(tmp_path: Path):
    dotenv = tmp_path / ".env"
    dotenv.write_text("ALPHA=one\nBETA=two\n")
    vault = tmp_path / "vault.json"
    return {"dotenv": dotenv, "vault": vault, "tmp": tmp_path}


def _run(args, password=PASSWORD):
    runner = CliRunner(mix_stderr=False)
    return runner.invoke(watch_group, args, input=f"{password}\n", catch_exceptions=False)


class TestWatchCLI:
    def test_start_prints_watching_message(self, setup):
        dotenv = setup["dotenv"]
        vault = setup["vault"]

        fake_state = WatchState(
            path=dotenv, vault_path=vault, password=PASSWORD, changes_detected=1
        )

        with patch("envault.cli_watch.watch_file", return_value=fake_state):
            result = _run(
                ["start", str(dotenv), "--vault", str(vault), "--interval", "0.1"]
            )

        assert result.exit_code == 0
        assert "Watching" in result.output

    def test_start_prints_stopped_summary(self, setup):
        dotenv = setup["dotenv"]
        vault = setup["vault"]

        fake_state = WatchState(
            path=dotenv, vault_path=vault, password=PASSWORD, changes_detected=3
        )

        with patch("envault.cli_watch.watch_file", return_value=fake_state):
            result = _run(
                ["start", str(dotenv), "--vault", str(vault), "--interval", "0.1"]
            )

        assert "Total syncs: 3" in result.output
        assert "errors: 0" in result.output

    def test_start_shows_errors(self, setup):
        dotenv = setup["dotenv"]
        vault = setup["vault"]

        fake_state = WatchState(
            path=dotenv,
            vault_path=vault,
            password=PASSWORD,
            changes_detected=0,
            errors=["something went wrong"],
        )

        with patch("envault.cli_watch.watch_file", return_value=fake_state):
            result = _run(
                ["start", str(dotenv), "--vault", str(vault), "--interval", "0.1"]
            )

        assert "something went wrong" in result.stderr
