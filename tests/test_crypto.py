"""Unit tests for envault.crypto."""

import pytest
from cryptography.exceptions import InvalidTag

from envault.crypto import encrypt, decrypt


class TestEncryptDecrypt:
    def test_roundtrip(self):
        plaintext = "SECRET_KEY=supersecret\nDB_URL=postgres://localhost/db"
        password = "correct-horse-battery"
        encoded = encrypt(plaintext, password)
        assert decrypt(encoded, password) == plaintext

    def test_wrong_password_raises(self):
        encoded = encrypt("hello", "rightpass")
        with pytest.raises(InvalidTag):
            decrypt(encoded, "wrongpass")

    def test_ciphertext_is_base64(self):
        import base64
        encoded = encrypt("data", "pw")
        # Should not raise
        base64.b64decode(encoded.encode())

    def test_unique_ciphertexts(self):
        """Same input should produce different ciphertexts (random nonce/salt)."""
        a = encrypt("same", "same")
        b = encrypt("same", "same")
        assert a != b

    def test_empty_string(self):
        encoded = encrypt("", "pw")
        assert decrypt(encoded, "pw") == ""

    def test_unicode_content(self):
        plaintext = "KEY=こんにちは"
        encoded = encrypt(plaintext, "pw")
        assert decrypt(encoded, "pw") == plaintext
