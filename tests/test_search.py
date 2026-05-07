"""Tests for envault.search module."""

from __future__ import annotations

import pytest

from envault.vault import save_vault, set_secret, load_vault
from envault.search import search_keys, search_values, format_results, SearchResult


PASSWORD = "hunter2"


@pytest.fixture()
def vault_path(tmp_path):
    path = str(tmp_path / "test.vault")
    vault = {}
    for key, value in [
        ("DB_HOST", "localhost"),
        ("DB_PORT", "5432"),
        ("API_KEY", "secret-api-key"),
        ("APP_ENV", "production"),
    ]:
        set_secret(vault, PASSWORD, key, value)
    save_vault(path, vault)
    return path


class TestSearchKeys:
    def test_exact_match(self, vault_path):
        results = search_keys(vault_path, PASSWORD, "DB_HOST")
        assert len(results) == 1
        assert results[0].key == "DB_HOST"

    def test_glob_prefix(self, vault_path):
        results = search_keys(vault_path, PASSWORD, "DB_*")
        keys = [r.key for r in results]
        assert "DB_HOST" in keys
        assert "DB_PORT" in keys
        assert "API_KEY" not in keys

    def test_no_match_returns_empty(self, vault_path):
        results = search_keys(vault_path, PASSWORD, "NONEXISTENT_*")
        assert results == []

    def test_case_insensitive_pattern(self, vault_path):
        results = search_keys(vault_path, PASSWORD, "db_*")
        assert len(results) == 2

    def test_values_hidden_by_default(self, vault_path):
        results = search_keys(vault_path, PASSWORD, "DB_HOST")
        assert results[0].value is None

    def test_reveal_values(self, vault_path):
        results = search_keys(vault_path, PASSWORD, "DB_HOST", reveal_values=True)
        assert results[0].value == "localhost"

    def test_results_sorted_alphabetically(self, vault_path):
        results = search_keys(vault_path, PASSWORD, "*")
        keys = [r.key for r in results]
        assert keys == sorted(keys)


class TestSearchValues:
    def test_substring_match(self, vault_path):
        results = search_values(vault_path, PASSWORD, "localhost")
        assert len(results) == 1
        assert results[0].key == "DB_HOST"

    def test_partial_substring(self, vault_path):
        results = search_values(vault_path, PASSWORD, "secret")
        keys = [r.key for r in results]
        assert "API_KEY" in keys

    def test_case_insensitive_value_search(self, vault_path):
        results = search_values(vault_path, PASSWORD, "PRODUCTION")
        assert any(r.key == "APP_ENV" for r in results)

    def test_no_match_returns_empty(self, vault_path):
        results = search_values(vault_path, PASSWORD, "zzznomatch")
        assert results == []

    def test_values_always_revealed(self, vault_path):
        results = search_values(vault_path, PASSWORD, "localhost")
        assert results[0].value == "localhost"


class TestFormatResults:
    def test_empty_results_message(self):
        assert format_results([]) == "No matches found."

    def test_keys_only_format(self):
        results = [SearchResult(key="FOO"), SearchResult(key="BAR")]
        output = format_results(results, reveal_values=False)
        assert "FOO" in output
        assert "BAR" in output
        assert "=" not in output

    def test_key_value_format(self):
        results = [SearchResult(key="FOO", value="bar")]
        output = format_results(results, reveal_values=True)
        assert "FOO=bar" in output
