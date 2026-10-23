"""Tests for shamir module."""

import os
import tempfile

import pytest

from shamir import (
    compare_files,
    decrypt_file,
    encrypt_file,
    hash_file,
)


@pytest.fixture
def temp_file():
    """Create a temporary file with test content."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("test content")
        temp_path = f.name
    yield temp_path
    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture
def passphrase():
    """Test passphrase."""
    return "test_passphrase_12345"


class TestFileHash:
    """Tests for file hashing."""

    def test_hash_file(self, temp_file):
        """Test that hash_file returns consistent results."""
        hash1 = hash_file(temp_file)
        hash2 = hash_file(temp_file)
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex is 64 chars

    def test_hash_different_files(self, temp_file):
        """Test that different files have different hashes."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("different content")
            temp_file2 = f.name

        try:
            hash1 = hash_file(temp_file)
            hash2 = hash_file(temp_file2)
            assert hash1 != hash2
        finally:
            os.remove(temp_file2)


class TestEncryptDecrypt:
    """Tests for GPG encryption/decryption."""

    def test_encrypt_file(self, temp_file, passphrase):
        """Test file encryption."""
        encrypted_file = encrypt_file(temp_file, passphrase)
        assert os.path.exists(encrypted_file)
        assert encrypted_file == f"{temp_file}.gpg"

        # Cleanup
        os.remove(encrypted_file)

    def test_decrypt_file(self, temp_file, passphrase):
        """Test file decryption."""
        encrypted_file = encrypt_file(temp_file, passphrase)
        decrypted_file = f"{encrypted_file}.dec"

        decrypt_file(encrypted_file, passphrase, decrypted_file)
        assert os.path.exists(decrypted_file)

        # Verify content matches
        assert compare_files(temp_file, decrypted_file)

        # Cleanup
        os.remove(encrypted_file)
        os.remove(decrypted_file)

    def test_encrypt_file_already_exists(self, temp_file, passphrase):
        """Test that encrypting to existing file raises error."""
        encrypted_file = encrypt_file(temp_file, passphrase)
        with pytest.raises(Exception):
            encrypt_file(temp_file, passphrase)

        # Cleanup
        os.remove(encrypted_file)

    def test_decrypt_wrong_passphrase(self, temp_file, passphrase):
        """Decryption with a wrong passphrase must raise, not fail silently."""
        encrypted_file = encrypt_file(temp_file, passphrase)

        with pytest.raises(Exception):
            decrypt_file(encrypted_file, "wrong_passphrase")

        # Cleanup
        os.remove(encrypted_file)


class TestCompareFiles:
    """Tests for file comparison."""

    def test_compare_identical_files(self, temp_file):
        """Test comparing identical files."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            temp_file2 = f.name

        try:
            assert compare_files(temp_file, temp_file2)
        finally:
            os.remove(temp_file2)

    def test_compare_different_files(self, temp_file):
        """Test comparing different files."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("different content")
            temp_file2 = f.name

        try:
            assert not compare_files(temp_file, temp_file2)
        finally:
            os.remove(temp_file2)
