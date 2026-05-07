"""Integration tests for the diff CLI command."""

from click.testing import CliRunner
import pytest

from envault.cli_diff import diff_group
from envault.vault import load_vault, save_vault, set_secret


PASSWORD = "clidiffpass"


@pytest.fixture()
def setup(tmp_path):
    vault_path = str(tmp_path / "test.envault")
    dotenv_path = str(tmp_path / ".env")

    vault = load_vault(vault_path)
    vault = set_secret(vault, "KEY_A", "value_a", PASSWORD)
    vault = set_secret(vault, "KEY_B", "old_b", PASSWORD)
    save_vault(vault, vault_path)

    with open(dotenv_path, "w") as fh:
        fh.write("KEY_B=new_b\nKEY_C=value_c\n")

    return vault_path, dotenv_path


class TestDiffCLI:
    def _run(self, args, password=PASSWORD):
        runner = CliRunner()
        return runner.invoke(diff_group, args, input=password + "\n", catch_exceptions=False)

    def test_diff_shows_summary(self, setup):
        vault_path, dotenv_path = setup
        result = self._run(["run", dotenv_path, "--vault", vault_path])
        assert "Summary:" in result.output

    def test_diff_detects_removed_key(self, setup):
        vault_path, dotenv_path = setup
        result = self._run(["run", dotenv_path, "--vault", vault_path])
        assert "- KEY_A" in result.output

    def test_diff_detects_added_key(self, setup):
        vault_path, dotenv_path = setup
        result = self._run(["run", dotenv_path, "--vault", vault_path])
        assert "+ KEY_C" in result.output

    def test_diff_detects_changed_key(self, setup):
        vault_path, dotenv_path = setup
        result = self._run(["run", dotenv_path, "--vault", vault_path])
        assert "~ KEY_B" in result.output

    def test_only_filter_limits_output(self, setup):
        vault_path, dotenv_path = setup
        result = self._run(["run", dotenv_path, "--vault", vault_path, "--only", "added"])
        assert "KEY_C" in result.output
        assert "KEY_A" not in result.output

    def test_show_values_flag(self, setup):
        vault_path, dotenv_path = setup
        result = self._run(["run", dotenv_path, "--vault", vault_path, "--show-values"])
        assert "->" in result.output

    def test_missing_dotenv_exits_with_error(self, setup):
        vault_path, _ = setup
        runner = CliRunner()
        result = runner.invoke(
            diff_group, ["run", "/nonexistent/.env", "--vault", vault_path],
            input=PASSWORD + "\n",
        )
        assert result.exit_code != 0
