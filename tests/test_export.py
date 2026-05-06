"""Tests for envault.export — .env parse/render/import/export helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from envault.export import (
    export_dotenv_file,
    import_dotenv_file,
    parse_dotenv,
    render_dotenv,
)


class TestParseDotenv:
    def test_simple_key_value(self):
        result = parse_dotenv("FOO=bar")
        assert result == {"FOO": "bar"}

    def test_double_quoted_value(self):
        result = parse_dotenv('DB_URL="postgres://localhost/mydb"')
        assert result == {"DB_URL": "postgres://localhost/mydb"}

    def test_single_quoted_value(self):
        result = parse_dotenv("SECRET='my secret value'")
        assert result == {"SECRET": "my secret value"}

    def test_comments_are_ignored(self):
        content = "# This is a comment\nFOO=bar\n# Another comment"
        result = parse_dotenv(content)
        assert result == {"FOO": "bar"}

    def test_empty_lines_are_ignored(self):
        content = "\nFOO=bar\n\nBAZ=qux\n"
        result = parse_dotenv(content)
        assert result == {"FOO": "bar", "BAZ": "qux"}

    def test_multiple_entries(self):
        content = "API_KEY=abc123\nDEBUG=true\nPORT=8080"
        result = parse_dotenv(content)
        assert result == {"API_KEY": "abc123", "DEBUG": "true", "PORT": "8080"}

    def test_invalid_lines_are_skipped(self):
        content = "NOT_VALID\nFOO=bar"
        result = parse_dotenv(content)
        assert result == {"FOO": "bar"}


class TestRenderDotenv:
    def test_simple_values_unquoted(self):
        output = render_dotenv({"FOO": "bar"})
        assert "FOO=bar" in output

    def test_values_with_spaces_are_quoted(self):
        output = render_dotenv({"MSG": "hello world"})
        assert 'MSG="hello world"' in output

    def test_output_ends_with_newline(self):
        output = render_dotenv({"A": "1"})
        assert output.endswith("\n")

    def test_empty_dict_returns_empty_string(self):
        assert render_dotenv({}) == ""

    def test_roundtrip(self):
        original = {"API_KEY": "abc123", "DEBUG": "false", "PORT": "9000"}
        rendered = render_dotenv(original)
        parsed = parse_dotenv(rendered)
        assert parsed == original


class TestFileOperations:
    def test_import_dotenv_file(self, tmp_path: Path):
        env_file = tmp_path / ".env"
        env_file.write_text("FOO=bar\nBAZ=qux\n", encoding="utf-8")
        result = import_dotenv_file(env_file)
        assert result == {"FOO": "bar", "BAZ": "qux"}

    def test_import_missing_file_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            import_dotenv_file(tmp_path / "nonexistent.env")

    def test_export_dotenv_file(self, tmp_path: Path):
        out_file = tmp_path / ".env"
        export_dotenv_file({"KEY": "value", "NUM": "42"}, out_file)
        content = out_file.read_text(encoding="utf-8")
        parsed = parse_dotenv(content)
        assert parsed == {"KEY": "value", "NUM": "42"}
