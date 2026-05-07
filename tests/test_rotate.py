"""Tests for envault.rotate — key rotation."""

from __future__ import annotations

import json
import os
import pytest

from envault.vault import load_vault, save_vault, set_secret
from envault.rotate import rotate_key


@pytest.fixture()
def vault_path(tmp_path):
    return str(tmp_path / "test.vault")


class TestRotateKey:
    def test_rotated_count_matches_secrets(self, vault_path):
        password = "old-pass"
        set_secret(vault_path, password, "KEY1", "value1")
        set_secret(vault_path, password, "KEY2", "value2")

        result = rotate_key(vault_path, password, "new-pass")

        assert result["rotated"] == 2
        assert result["skipped"] == 0

    def test_secrets_readable_with_new_password(self, vault_path):
        old_pw, new_pw = "old-pass", "new-pass"
        set_secret(vault_path, old_pw, "TOKEN", "secret-token")

        rotate_key(vault_path, old_pw, new_pw)

        new_vault = load_vault(vault_path, new_pw)
        from envault.crypto import decrypt
        plaintext = decrypt(new_pw, new_vault["secrets"]["TOKEN"])
        assert plaintext == "secret-token"

    def test_old_password_no_longer_works(self, vault_path):
        old_pw, new_pw = "old", "new"
        set_secret(vault_path, old_pw, "X", "y")
        rotate_key(vault_path, old_pw, new_pw)

        new_vault = load_vault(vault_path, new_pw)
        from envault.crypto import decrypt
        with pytest.raises(Exception):
            decrypt(old_pw, new_vault["secrets"]["X"])

    def test_empty_vault_returns_zero_counts(self, vault_path):
        save_vault(vault_path, {"secrets": {}}, "pass")
        result = rotate_key(vault_path, "pass", "new-pass")
        assert result["rotated"] == 0
        assert result["skipped"] == 0

    def test_vault_file_is_updated_on_disk(self, vault_path):
        pw = "pw"
        set_secret(vault_path, pw, "A", "1")
        mtime_before = os.path.getmtime(vault_path)

        import time; time.sleep(0.05)
        rotate_key(vault_path, pw, "new-pw")

        mtime_after = os.path.getmtime(vault_path)
        assert mtime_after > mtime_before
