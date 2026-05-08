"""Tests for envault.template module."""

from __future__ import annotations

from pathlib import Path

import pytest

from envault.crypto import encrypt
from envault.vault import save_vault
from envault.template import render_template, render_template_file, RenderResult


PASSWORD = "test-pass"


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    path = tmp_path / ".envault"
    data = {
        "DB_HOST": encrypt("localhost", PASSWORD),
        "DB_PORT": encrypt("5432", PASSWORD),
        "API_KEY": encrypt("secret123", PASSWORD),
    }
    save_vault(path, data)
    return path


class TestRenderTemplate:
    def test_single_substitution(self):
        result = render_template("host={{ DB_HOST }}", {"DB_HOST": "localhost"})
        assert result.output == "host=localhost"
        assert "DB_HOST" in result.substituted
        assert result.missing == []

    def test_multiple_substitutions(self):
        result = render_template("{{ A }} and {{ B }}", {"A": "foo", "B": "bar"})
        assert result.output == "foo and bar"
        assert len(result.substituted) == 2

    def test_missing_key_left_intact(self):
        result = render_template("value={{ MISSING }}", {})
        assert "{{ MISSING }}" in result.output
        assert "MISSING" in result.missing

    def test_ok_true_when_no_missing(self):
        result = render_template("x={{ X }}", {"X": "1"})
        assert result.ok is True

    def test_ok_false_when_missing(self):
        result = render_template("x={{ X }}", {})
        assert result.ok is False

    def test_no_placeholders_unchanged(self):
        text = "no placeholders here"
        result = render_template(text, {"X": "1"})
        assert result.output == text
        assert result.substituted == []
        assert result.missing == []

    def test_whitespace_inside_braces(self):
        result = render_template("{{  KEY  }}", {"KEY": "value"})
        assert result.output == "value"


class TestRenderTemplateFile:
    def test_renders_from_vault(self, vault_path: Path, tmp_path: Path):
        tmpl = tmp_path / "config.tmpl"
        tmpl.write_text("host={{ DB_HOST }}\nport={{ DB_PORT }}")

        result = render_template_file(tmpl, vault_path, PASSWORD)
        assert result.output == "host=localhost\nport=5432"
        assert set(result.substituted) == {"DB_HOST", "DB_PORT"}

    def test_writes_output_file(self, vault_path: Path, tmp_path: Path):
        tmpl = tmp_path / "config.tmpl"
        tmpl.write_text("key={{ API_KEY }}")
        out = tmp_path / "config.rendered"

        render_template_file(tmpl, vault_path, PASSWORD, output_path=out)
        assert out.read_text() == "key=secret123"

    def test_missing_key_reported(self, vault_path: Path, tmp_path: Path):
        tmpl = tmp_path / "config.tmpl"
        tmpl.write_text("x={{ NO_SUCH_KEY }}")

        result = render_template_file(tmpl, vault_path, PASSWORD)
        assert "NO_SUCH_KEY" in result.missing
        assert result.ok is False

    def test_wrong_password_skips_keys(self, vault_path: Path, tmp_path: Path):
        tmpl = tmp_path / "config.tmpl"
        tmpl.write_text("host={{ DB_HOST }}")

        result = render_template_file(tmpl, vault_path, "wrong-password")
        assert result.missing != [] or "{{ DB_HOST }}" in result.output
