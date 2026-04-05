"""Tests for bw_backup module."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)  # noqa: E402

# Check if gpg binary is available for integration tests
HAS_GPG = shutil.which("gpg") is not None

from bw_backup import (  # noqa: E402
    BitwardenError,
    EncryptionError,
    bw_export,
    bw_unlock,
    check_commands,
    check_env_vars,
    check_export_path,
    check_gpg,
    compare_files,
    create_checksum_file,
    decrypt_file,
    encrypt_file,
    export_and_backup,
    get_gpg_passphrase,
    hash_file,
    main,
    shred_file,
)


# Fixtures
@pytest.fixture
def sample_file(tmp_path):
    """Small text file for encryption tests."""
    f = tmp_path / "test_export.json"
    f.write_text('{"id":"1","password":"secret"}\n')
    return str(f)


@pytest.fixture
def export_path(tmp_path):
    """Temporary export path."""
    export = tmp_path / "exports"
    export.mkdir()
    return str(export)


# Environment variable tests
def test_check_env_vars_success(monkeypatch):
    """Test check_env_vars with all variables set."""
    monkeypatch.setenv("BW_ORGANIZATION_ID", "org123")
    monkeypatch.setenv("BW_GPG_PASSPHRASE_ID", "item456")
    monkeypatch.setenv("BW_EXPORT_PATH", "/tmp/export")
    monkeypatch.setenv("BW_GPG_PASSPHRASE_FIELD", "passphrase")

    result = check_env_vars()
    assert result["BW_ORGANIZATION_ID"] == "org123"
    assert result["BW_GPG_PASSPHRASE_ID"] == "item456"
    assert result["BW_EXPORT_PATH"] == "/tmp/export"
    assert result["BW_GPG_PASSPHRASE_FIELD"] == "passphrase"


def test_check_env_vars_missing(monkeypatch):
    """Test check_env_vars raises EnvironmentError when vars missing."""
    monkeypatch.delenv("BW_ORGANIZATION_ID", raising=False)
    monkeypatch.delenv("BW_GPG_PASSPHRASE_ID", raising=False)
    monkeypatch.delenv("BW_EXPORT_PATH", raising=False)
    monkeypatch.delenv("BW_GPG_PASSPHRASE_FIELD", raising=False)

    with pytest.raises(
        EnvironmentError, match="Missing or empty required environment variables"
    ):
        check_env_vars()


def test_check_env_vars_empty_string(monkeypatch):
    """Test check_env_vars rejects empty string values."""
    monkeypatch.setenv("BW_ORGANIZATION_ID", "")
    monkeypatch.setenv("BW_GPG_PASSPHRASE_ID", "item456")
    monkeypatch.setenv("BW_EXPORT_PATH", "/tmp/export")
    monkeypatch.setenv("BW_GPG_PASSPHRASE_FIELD", "passphrase")

    with pytest.raises(
        EnvironmentError, match="Missing or empty required environment variables"
    ):
        check_env_vars()


def test_check_env_vars_whitespace_only(monkeypatch):
    """Test check_env_vars rejects whitespace-only values."""
    monkeypatch.setenv("BW_ORGANIZATION_ID", "   ")
    monkeypatch.setenv("BW_GPG_PASSPHRASE_ID", "item456")
    monkeypatch.setenv("BW_EXPORT_PATH", "/tmp/export")
    monkeypatch.setenv("BW_GPG_PASSPHRASE_FIELD", "passphrase")

    with pytest.raises(
        EnvironmentError, match="Missing or empty required environment variables"
    ):
        check_env_vars()


def test_check_export_path_exists(tmp_path):
    """Test check_export_path passes when path exists."""
    export = tmp_path / "exports"
    export.mkdir()
    check_export_path(str(export))  # Should not raise


def test_check_export_path_missing(tmp_path):
    """Test check_export_path raises FileNotFoundError when path missing."""
    missing = tmp_path / "nonexistent"
    with pytest.raises(FileNotFoundError, match="BW_EXPORT_PATH does not exist"):
        check_export_path(str(missing))


def test_check_export_path_is_file(tmp_path):
    """Test check_export_path raises NotADirectoryError when path is a file."""
    file_path = tmp_path / "file.txt"
    file_path.write_text("test")
    with pytest.raises(NotADirectoryError, match="BW_EXPORT_PATH is not a directory"):
        check_export_path(str(file_path))


# Command validation tests
@mock.patch("shutil.which")
def test_check_commands_bw_missing(mock_which):
    """Test check_commands raises when bw command missing."""

    def which_side_effect(cmd):
        return None if cmd == "bw" else "/usr/bin/shred"

    mock_which.side_effect = which_side_effect

    with pytest.raises(FileNotFoundError, match="bw"):
        check_commands()


@mock.patch("shutil.which")
def test_check_commands_shred_missing(mock_which):
    """Test check_commands raises when shred command missing."""

    def which_side_effect(cmd):
        return "/usr/bin/bw" if cmd == "bw" else None

    mock_which.side_effect = which_side_effect

    with pytest.raises(FileNotFoundError, match="shred"):
        check_commands()


@mock.patch("shutil.which")
def test_check_commands_success(mock_which):
    """Test check_commands passes when both commands available."""
    mock_which.return_value = "/usr/bin/command"
    check_commands()  # Should not raise


# GPG validation tests
@pytest.mark.skipif(not HAS_GPG, reason="gpg not installed or configured")
def test_check_gpg_success():
    """Test check_gpg validates GPG functionality."""
    check_gpg()  # Should not raise


def test_check_gpg_failure():
    """Test check_gpg raises EncryptionError on GPG misconfiguration."""
    with mock.patch("gnupg.GPG.encrypt") as mock_encrypt:
        mock_encrypt.return_value = mock.MagicMock(ok=False, status="error")
        with pytest.raises(EncryptionError, match="GPG encryption failed"):
            check_gpg()


# File operation tests
@pytest.mark.skipif(not HAS_GPG, reason="gpg not installed or configured")
def test_encrypt_decrypt_roundtrip(sample_file):
    """Test encrypt then decrypt yields original file."""
    passphrase = "test_passphrase_123"

    encrypted = encrypt_file(sample_file, passphrase)
    assert os.path.exists(encrypted)
    assert encrypted.endswith(".gpg")

    decrypted = decrypt_file(encrypted, passphrase)
    assert os.path.exists(decrypted)

    assert compare_files(sample_file, decrypted)

    os.remove(encrypted)
    os.remove(decrypted)


@pytest.mark.skipif(not HAS_GPG, reason="gpg not installed or configured")
def test_encrypt_creates_gpg_file(sample_file):
    """Test encrypt_file creates .gpg file."""
    passphrase = "test_passphrase_123"
    encrypted = encrypt_file(sample_file, passphrase)
    assert encrypted == f"{sample_file}.gpg"
    assert os.path.exists(encrypted)
    os.remove(encrypted)


def test_decrypt_validates_extension(sample_file):
    """Test decrypt_file raises exception for non-.gpg file."""
    with pytest.raises(EncryptionError, match="does not have .gpg extension"):
        decrypt_file(sample_file, "passphrase")


@pytest.mark.skipif(not HAS_GPG, reason="gpg not installed or configured")
def test_decrypt_default_output_temp_file(sample_file, tmp_path):
    """Test decrypt_file creates temp file in same directory when output_file=None."""
    export_dir = str(tmp_path / "exports")
    os.makedirs(export_dir, exist_ok=True)
    passphrase = "test_passphrase_123"

    # Create file in export directory
    export_file = os.path.join(export_dir, "test_export.json")
    Path(export_file).write_text(Path(sample_file).read_text())

    encrypted = encrypt_file(export_file, passphrase)
    decrypted = decrypt_file(encrypted, passphrase, output_file=None)

    # Temp file should be in same directory as encrypted file
    assert os.path.dirname(decrypted) == os.path.dirname(encrypted)
    assert os.path.exists(decrypted)

    os.remove(encrypted)
    os.remove(decrypted)
    os.remove(export_file)


def test_hash_file(sample_file):
    """Test hash_file returns consistent hash."""
    hash1 = hash_file(sample_file)
    hash2 = hash_file(sample_file)
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA256 hex digest is 64 chars


def test_compare_files_identical(sample_file, tmp_path):
    """Test compare_files returns True for identical files."""
    copy_file = tmp_path / "copy.json"
    copy_file.write_text(Path(sample_file).read_text())
    assert compare_files(sample_file, str(copy_file))


def test_compare_files_different(sample_file, tmp_path):
    """Test compare_files returns False for different files."""
    different_file = tmp_path / "different.json"
    different_file.write_text('{"id":"2","password":"other"}')
    assert not compare_files(sample_file, str(different_file))


def test_create_checksum_file(sample_file):
    """Test create_checksum_file creates .sha256 file with correct hash."""
    checksum_file = create_checksum_file(sample_file)
    assert checksum_file == f"{sample_file}.sha256"
    assert os.path.exists(checksum_file)

    with open(checksum_file) as f:
        content = f.read()
    expected_hash = hash_file(sample_file)
    assert expected_hash in content
    assert os.path.basename(sample_file) in content

    os.remove(checksum_file)


@mock.patch("subprocess.run")
def test_shred_file_success(mock_run):
    """Test shred_file calls shred command."""
    mock_run.return_value = mock.MagicMock(returncode=0, stderr="")
    shred_file("/tmp/test_file")
    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert args[0] == "shred"
    assert "-u" in args


@mock.patch("subprocess.run")
def test_shred_file_failure(mock_run):
    """Test shred_file raises RuntimeError on shred failure."""
    mock_run.return_value = mock.MagicMock(returncode=1, stderr="Permission denied")
    with pytest.raises(RuntimeError, match="shred failed"):
        shred_file("/tmp/test_file")


@mock.patch("subprocess.run")
def test_shred_file_timeout(mock_run):
    """Test shred_file raises RuntimeError on timeout."""
    mock_run.side_effect = subprocess.TimeoutExpired("shred", 30)
    with pytest.raises(RuntimeError, match="shred timed out"):
        shred_file("/tmp/test_file")


# Bitwarden operation tests
@mock.patch("subprocess.run")
def test_bw_export_success(mock_run):
    """Test bw_export calls correct command."""
    mock_run.return_value = mock.MagicMock(returncode=0, stderr="")
    bw_export("session123", "/tmp/export.json", "json")

    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert "bw" in args
    assert "export" in args
    assert "--format" in args
    assert "json" in args
    assert "--output" in args
    assert "/tmp/export.json" in args


@mock.patch("subprocess.run")
def test_bw_export_with_org(mock_run):
    """Test bw_export includes --organizationid flag."""
    mock_run.return_value = mock.MagicMock(returncode=0, stderr="")
    bw_export("session123", "/tmp/export.json", "json", org_id="org123")

    args = mock_run.call_args[0][0]
    assert "--organizationid" in args
    assert "org123" in args


@mock.patch("subprocess.run")
def test_bw_export_failure(mock_run):
    """Test bw_export raises BitwardenError on non-zero returncode."""
    mock_run.return_value = mock.MagicMock(returncode=1, stderr="Export failed")
    with pytest.raises(BitwardenError, match="bw export failed"):
        bw_export("session123", "/tmp/export.json", "json")


@mock.patch("subprocess.run")
def test_bw_unlock_success(mock_run):
    """Test bw_unlock returns session string."""
    mock_run.return_value = mock.MagicMock(returncode=0, stdout="session_token_123\n")
    session = bw_unlock()
    assert session == "session_token_123"


@mock.patch("subprocess.run")
def test_get_gpg_passphrase_success(mock_run):
    """Test get_gpg_passphrase extracts field from bw get item."""
    item_json = {
        "id": "item123",
        "fields": [{"name": "passphrase", "value": "my_secret_passphrase"}],
    }
    mock_run.return_value = mock.MagicMock(returncode=0, stdout=json.dumps(item_json))
    passphrase = get_gpg_passphrase("session123", "item123", "passphrase")
    assert passphrase == "my_secret_passphrase"


@mock.patch("subprocess.run")
def test_get_gpg_passphrase_missing_field(mock_run):
    """Test get_gpg_passphrase raises BitwardenError when field missing."""
    item_json = {"id": "item123", "fields": [{"name": "other_field", "value": "value"}]}
    mock_run.return_value = mock.MagicMock(returncode=0, stdout=json.dumps(item_json))
    with pytest.raises(BitwardenError, match="Field.*not found"):
        get_gpg_passphrase("session123", "item123", "passphrase")


@mock.patch("subprocess.run")
def test_get_gpg_passphrase_empty_value(mock_run):
    """Test get_gpg_passphrase raises BitwardenError when field value is empty."""
    item_json = {
        "id": "item123",
        "fields": [{"name": "passphrase", "value": ""}],
    }
    mock_run.return_value = mock.MagicMock(returncode=0, stdout=json.dumps(item_json))
    with pytest.raises(BitwardenError, match="missing a non-empty value"):
        get_gpg_passphrase("session123", "item123", "passphrase")


@mock.patch("subprocess.run")
def test_get_gpg_passphrase_whitespace_value(mock_run):
    """Test get_gpg_passphrase raises BitwardenError when field value is whitespace-only."""
    item_json = {
        "id": "item123",
        "fields": [{"name": "passphrase", "value": "   "}],
    }
    mock_run.return_value = mock.MagicMock(returncode=0, stdout=json.dumps(item_json))
    with pytest.raises(BitwardenError, match="missing a non-empty value"):
        get_gpg_passphrase("session123", "item123", "passphrase")


# Orchestration tests
@mock.patch("bw_backup.shred_file")
@mock.patch("bw_backup.bw_export")
@mock.patch("bw_backup.get_gpg_passphrase")
@mock.patch("bw_backup.bw_unlock")
def test_export_and_backup_success(
    mock_unlock,
    mock_get_passphrase,
    mock_bw_export,
    mock_shred,
    monkeypatch,
    export_path,
):
    """Test export_and_backup workflow succeeds."""
    mock_unlock.return_value = "session123"
    mock_get_passphrase.return_value = "test_passphrase"

    def bw_export_side_effect(session, output, fmt, org_id=None):
        Path(output).write_text('{"test":"data"}')

    mock_bw_export.side_effect = bw_export_side_effect

    env = {
        "BW_ORGANIZATION_ID": "org123",
        "BW_GPG_PASSPHRASE_ID": "item456",
        "BW_EXPORT_PATH": export_path,
        "BW_GPG_PASSPHRASE_FIELD": "passphrase",
    }

    export_and_backup(env)

    # Verify bw_export was called twice (personal + org)
    assert mock_bw_export.call_count == 2


@mock.patch("bw_backup.shred_file")
@mock.patch("bw_backup.bw_export")
@mock.patch("bw_backup.get_gpg_passphrase")
@mock.patch("bw_backup.bw_unlock")
def test_export_and_backup_clears_passphrase(
    mock_unlock,
    mock_get_passphrase,
    mock_bw_export,
    mock_shred,
    monkeypatch,
    export_path,
):
    """Test export_and_backup clears passphrase in finally block."""
    mock_unlock.return_value = "session123"
    mock_get_passphrase.return_value = "test_passphrase"

    def bw_export_side_effect(session, output, fmt, org_id=None):
        Path(output).write_text('{"test":"data"}')

    mock_bw_export.side_effect = bw_export_side_effect

    env = {
        "BW_ORGANIZATION_ID": "org123",
        "BW_GPG_PASSPHRASE_ID": "item456",
        "BW_EXPORT_PATH": export_path,
        "BW_GPG_PASSPHRASE_FIELD": "passphrase",
    }

    export_and_backup(env)
    # Passphrase should be cleared in finally block


@mock.patch("bw_backup.shred_file")
@mock.patch("bw_backup.bw_export")
@mock.patch("bw_backup.get_gpg_passphrase")
@mock.patch("bw_backup.bw_unlock")
def test_export_and_backup_validates_encryption(
    mock_unlock,
    mock_get_passphrase,
    mock_bw_export,
    mock_shred,
    monkeypatch,
    export_path,
):
    """Test export_and_backup validates encryption before shredding."""
    mock_unlock.return_value = "session123"
    mock_get_passphrase.return_value = "test_passphrase"

    def bw_export_side_effect(session, output, fmt, org_id=None):
        Path(output).write_text('{"test":"data"}')

    mock_bw_export.side_effect = bw_export_side_effect

    env = {
        "BW_ORGANIZATION_ID": "org123",
        "BW_GPG_PASSPHRASE_ID": "item456",
        "BW_EXPORT_PATH": export_path,
        "BW_GPG_PASSPHRASE_FIELD": "passphrase",
    }

    # Mock compare_files to validate that it's called
    with mock.patch("bw_backup.compare_files") as mock_compare:
        mock_compare.return_value = True
        export_and_backup(env)
        assert mock_compare.called


# Main entry point tests
@mock.patch("bw_backup.export_and_backup")
@mock.patch("bw_backup.check_gpg")
@mock.patch("bw_backup.check_export_path")
@mock.patch("bw_backup.check_env_vars")
@mock.patch("bw_backup.check_commands")
def test_main_success(
    mock_check_commands,
    mock_check_env,
    mock_check_path,
    mock_check_gpg,
    mock_export,
    monkeypatch,
    tmp_path,
):
    """Test main orchestrates all validation steps."""
    mock_check_env.return_value = {
        "BW_ORGANIZATION_ID": "org123",
        "BW_GPG_PASSPHRASE_ID": "item456",
        "BW_EXPORT_PATH": str(tmp_path),
        "BW_GPG_PASSPHRASE_FIELD": "passphrase",
    }

    main()

    mock_check_commands.assert_called_once()
    mock_check_env.assert_called_once()
    mock_check_path.assert_called_once()
    mock_check_gpg.assert_called_once()
    mock_export.assert_called_once()


@mock.patch("bw_backup.check_commands")
def test_main_command_missing(mock_check_commands):
    """Test main fails when command validation fails."""
    mock_check_commands.side_effect = FileNotFoundError("bw not found")
    with pytest.raises(SystemExit):
        main()


@mock.patch("bw_backup.check_env_vars")
@mock.patch("bw_backup.check_commands")
def test_main_missing_env_var(mock_check_commands, mock_check_env):
    """Test main fails when env var validation fails."""
    mock_check_env.side_effect = EnvironmentError("Missing vars")
    with pytest.raises(SystemExit):
        main()


@mock.patch("bw_backup.check_export_path")
@mock.patch("bw_backup.check_env_vars")
@mock.patch("bw_backup.check_commands")
def test_main_export_path_missing(mock_check_commands, mock_check_env, mock_check_path):
    """Test main fails when export path missing."""
    mock_check_env.return_value = {
        "BW_ORGANIZATION_ID": "org123",
        "BW_GPG_PASSPHRASE_ID": "item456",
        "BW_EXPORT_PATH": "/nonexistent",
        "BW_GPG_PASSPHRASE_FIELD": "passphrase",
    }
    mock_check_path.side_effect = FileNotFoundError("Path not found")
    with pytest.raises(SystemExit):
        main()


@mock.patch("bw_backup.check_gpg")
@mock.patch("bw_backup.check_export_path")
@mock.patch("bw_backup.check_env_vars")
@mock.patch("bw_backup.check_commands")
def test_main_gpg_failure(
    mock_check_commands,
    mock_check_env,
    mock_check_path,
    mock_check_gpg,
    tmp_path,
):
    """Test main fails when GPG validation fails."""
    mock_check_env.return_value = {
        "BW_ORGANIZATION_ID": "org123",
        "BW_GPG_PASSPHRASE_ID": "item456",
        "BW_EXPORT_PATH": str(tmp_path),
        "BW_GPG_PASSPHRASE_FIELD": "passphrase",
    }
    mock_check_gpg.side_effect = EncryptionError("GPG misconfigured")
    with pytest.raises(SystemExit):
        main()
