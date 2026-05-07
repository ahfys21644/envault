"""Tests for envault.lint module."""

from pathlib import Path

import pytest

from envault.lint import LintIssue, LintResult, format_lint_result, lint_dotenv_file


@pytest.fixture
def dotenv_path(tmp_path):
    """Return a helper that writes a .env file and returns its path."""
    def _write(content: str) -> Path:
        p = tmp_path / ".env"
        p.write_text(content, encoding="utf-8")
        return p
    return _write


class TestLintDotenvFile:
    def test_missing_file_returns_error(self, tmp_path):
        result = lint_dotenv_file(tmp_path / "nonexistent.env")
        assert not result.ok
        assert result.error_count == 1
        assert "not found" in result.issues[0].message.lower()

    def test_valid_file_has_no_issues(self, dotenv_path):
        p = dotenv_path("DB_HOST=localhost\nDB_PORT=5432\n")
        result = lint_dotenv_file(p)
        assert result.ok
        assert result.issues == []

    def test_comments_and_blank_lines_ignored(self, dotenv_path):
        p = dotenv_path("# comment\n\nAPI_KEY=abc123\n")
        result = lint_dotenv_file(p)
        assert result.ok

    def test_invalid_key_value_line_is_error(self, dotenv_path):
        p = dotenv_path("NOTAVALIDLINE\n")
        result = lint_dotenv_file(p)
        assert not result.ok
        assert any("KEY=VALUE" in i.message for i in result.issues)

    def test_lowercase_key_is_warning(self, dotenv_path):
        p = dotenv_path("db_host=localhost\n")
        result = lint_dotenv_file(p)
        assert result.ok  # warnings don't fail
        assert result.warning_count == 1
        assert any("uppercase" in i.message for i in result.issues)

    def test_duplicate_key_is_warning(self, dotenv_path):
        p = dotenv_path("API_KEY=first\nAPI_KEY=second\n")
        result = lint_dotenv_file(p)
        assert result.warning_count >= 1
        assert any("Duplicate" in i.message for i in result.issues)

    def test_unclosed_quote_is_error(self, dotenv_path):
        p = dotenv_path('SECRET="unclosed\n')
        result = lint_dotenv_file(p)
        assert not result.ok
        assert any("unclosed quote" in i.message for i in result.issues)

    def test_line_number_reported_correctly(self, dotenv_path):
        p = dotenv_path("GOOD=ok\nBADLINE\nALSO_GOOD=yes\n")
        result = lint_dotenv_file(p)
        bad = [i for i in result.issues if "KEY=VALUE" in i.message]
        assert bad[0].line_number == 2

    def test_result_path_matches_input(self, dotenv_path):
        p = dotenv_path("X=1\n")
        result = lint_dotenv_file(p)
        assert result.path == str(p)


class TestFormatLintResult:
    def test_ok_message_when_no_issues(self):
        result = LintResult(path=".env", issues=[])
        output = format_lint_result(result)
        assert "OK" in output

    def test_error_and_warning_counts_shown(self):
        result = LintResult(path=".env", issues=[
            LintIssue(1, "bad", "some error", "error"),
            LintIssue(2, "warn", "some warning", "warning"),
        ])
        output = format_lint_result(result)
        assert "1 error" in output
        assert "1 warning" in output

    def test_each_issue_on_separate_line(self):
        result = LintResult(path=".env", issues=[
            LintIssue(1, "a", "first", "error"),
            LintIssue(2, "b", "second", "warning"),
        ])
        lines = format_lint_result(result).splitlines()
        assert len(lines) == 3  # header + 2 issues
