#!/usr/bin/env python3
"""Bitwarden backup with GPG encryption."""

import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

import gnupg

# Cipher for symmetric encryption
CIPHER = "AES256"

# Security note:
# - User's master password is never captured (handled interactively by bw CLI)
# - BW_SESSION token and GPG passphrase are stored in memory as Python strings
#   and passed to subprocesses via environment variables (standard practice)
# - These are cleared (set to None) in finally blocks after use
# - Note: Python strings cannot be reliably zeroed in memory due to the managed
#   runtime, but sensitive data lifetime is minimized
# - Logging is filtered to redact messages containing "BW_SESSION" or "passphrase"
# - This tool is designed for short-lived, single-run execution


# Custom exceptions
class BitwardenError(Exception):
    """Raised when Bitwarden CLI operations fail."""

    pass


class EncryptionError(Exception):
    """Raised when GPG encryption/decryption fails."""

    pass


class ValidationError(Exception):
    """Raised when validation checks fail."""

    pass


# Logging setup
class SecretFilter(logging.Filter):
    """Redact sensitive credential values from logs."""

    def filter(self, record):
        # Redact BW_SESSION token values and GPG passphrase values from messages and args
        if isinstance(record.msg, str):
            record.msg = self._redact_secrets(record.msg)
        if record.args and isinstance(record.args, dict):
            record.args = {
                k: self._redact_secrets(str(v)) if isinstance(v, str) else v
                for k, v in record.args.items()
            }
        elif record.args and isinstance(record.args, tuple):
            record.args = tuple(
                self._redact_secrets(str(arg)) if isinstance(arg, str) else arg
                for arg in record.args
            )
        return True

    @staticmethod
    def _redact_secrets(text: str) -> str:
        """Redact BW_SESSION=... and passphrase=... patterns from text."""
        text = re.sub(r"BW_SESSION=\S+", "BW_SESSION=***REDACTED***", text)
        text = re.sub(r"passphrase=\S+", "passphrase=***REDACTED***", text)
        return text


def setup_logging() -> None:
    """Configure logging with SecretFilter to redact sensitive data."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    logging.getLogger().addFilter(SecretFilter())


# Environment and validation functions
def check_commands() -> None:
    """Raise FileNotFoundError if required commands (bw, shred) not in PATH."""
    required_commands = ["bw", "shred"]
    for cmd in required_commands:
        if shutil.which(cmd) is None:
            raise FileNotFoundError(f"Required command not found in PATH: {cmd}")
    logging.info("All required commands available in PATH")


def check_env_vars() -> dict:
    """Return dict of required env vars or raise EnvironmentError."""
    required = [
        "BW_ORGANIZATION_ID",
        "BW_GPG_PASSPHRASE_ID",
        "BW_EXPORT_PATH",
        "BW_GPG_PASSPHRASE_FIELD",
    ]
    env = {}
    missing = []
    for var in required:
        value = os.getenv(var)
        # Reject None or empty/whitespace-only strings
        if not value or not value.strip():
            missing.append(var)
        else:
            env[var] = value
    if missing:
        raise EnvironmentError(
            f"Missing or empty required environment variables: {', '.join(missing)}"
        )
    logging.info("All required environment variables are set")
    return env


def check_export_path(path: str) -> None:
    """Raise if BW_EXPORT_PATH does not exist or is not a directory."""
    export_path = Path(path)
    if not export_path.exists():
        raise FileNotFoundError(f"BW_EXPORT_PATH does not exist: {path}")
    if not export_path.is_dir():
        raise NotADirectoryError(f"BW_EXPORT_PATH is not a directory: {path}")
    logging.info(f"Export path exists and is a directory: {path}")


def check_gpg() -> None:
    """Validate GPG is functional with encrypt/decrypt test."""
    try:
        gpg = gnupg.GPG()
        test_data = b"test data for gpg validation"

        # Encrypt with symmetric cipher (recipients=None for symmetric mode)
        encrypted = gpg.encrypt(
            test_data, recipients=None, symmetric=CIPHER, passphrase="test"
        )
        if not encrypted.ok:
            raise EncryptionError(f"GPG encryption failed: {encrypted.status}")

        # Decrypt to verify
        decrypted = gpg.decrypt(str(encrypted), passphrase="test")
        if not decrypted.ok:
            raise EncryptionError(f"GPG decryption failed: {decrypted.status}")

        if str(decrypted).encode() != test_data:
            raise EncryptionError("GPG roundtrip validation failed: data mismatch")

        logging.info("GPG validation successful")
    except Exception as e:
        if isinstance(e, EncryptionError):
            raise
        raise EncryptionError(f"GPG validation error: {e}")


# Bitwarden functions
def bw_unlock() -> str:
    """
    Run 'bw unlock --raw' interactively (user types master password).
    Returns BW_SESSION string. Raises BitwardenError on failure.
    Note: stderr is not captured to allow password prompt to display.
    """
    try:
        result = subprocess.run(
            ["bw", "unlock", "--raw"],
            stdout=subprocess.PIPE,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            raise BitwardenError(
                "bw unlock failed. Check that you are logged in: bw login"
            )
        session = result.stdout.strip()
        logging.info("Successfully unlocked Bitwarden vault")
        return session
    except subprocess.TimeoutExpired:
        raise BitwardenError("bw unlock timed out")
    except Exception as e:
        if isinstance(e, BitwardenError):
            raise
        raise BitwardenError(f"bw unlock error: {e}")


def get_gpg_passphrase(bw_session: str, item_id: str, field_name: str) -> str:
    """
    Run 'bw get item <item_id>' and extract field value.
    Returns passphrase string. Never logs it.
    Raises BitwardenError on failure or if passphrase is empty.
    """
    try:
        env = os.environ.copy()
        env["BW_SESSION"] = bw_session
        result = subprocess.run(
            ["bw", "get", "item", item_id],
            capture_output=True,
            text=True,
            env=env,
            timeout=30,
        )
        if result.returncode != 0:
            raise BitwardenError(f"bw get item failed: {result.stderr}")

        item = json.loads(result.stdout)
        fields = item.get("fields", [])
        for field in fields:
            if field.get("name") == field_name:
                passphrase = field.get("value")
                if not isinstance(passphrase, str) or not passphrase.strip():
                    raise BitwardenError(
                        f"Field '{field_name}' in item {item_id} is missing a non-empty value"
                    )
                logging.info("Successfully retrieved GPG passphrase from Bitwarden")
                return passphrase

        raise BitwardenError(f"Field '{field_name}' not found in item {item_id}")
    except json.JSONDecodeError as e:
        raise BitwardenError(f"Failed to parse bw get item output: {e}")
    except Exception as e:
        if isinstance(e, BitwardenError):
            raise
        raise BitwardenError(f"get_gpg_passphrase error: {e}")


def bw_export(
    bw_session: str, output_file: str, fmt: str, org_id: Optional[str] = None
) -> None:
    """
    Run 'bw export' with given format and output path.
    If org_id is given, includes --organizationid flag.
    Raises BitwardenError on non-zero exit.
    """
    try:
        cmd = ["bw", "export", "--format", fmt, "--output", output_file]
        if org_id:
            cmd.extend(["--organizationid", org_id])

        env = os.environ.copy()
        env["BW_SESSION"] = bw_session
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=60,
        )
        if result.returncode != 0:
            raise BitwardenError(f"bw export failed: {result.stderr}")

        org_label = f" (org: {org_id})" if org_id else " (personal)"
        logging.info(f"Successfully exported Bitwarden vault{org_label}")
    except subprocess.TimeoutExpired:
        raise BitwardenError("bw export timed out")
    except Exception as e:
        if isinstance(e, BitwardenError):
            raise
        raise BitwardenError(f"bw_export error: {e}")


# File operations
def encrypt_file(file: str, passphrase: str) -> str:
    """
    Encrypt file with GPG symmetric encryption (AES256).
    Returns path to .gpg file. Raises EncryptionError on failure.
    """
    try:
        gpg = gnupg.GPG()
        encrypted_file = f"{file}.gpg"

        with open(file, "rb") as f:
            result = gpg.encrypt_file(
                f,
                recipients=None,
                symmetric=CIPHER,
                passphrase=passphrase,
                output=encrypted_file,
            )

        if not result.ok:
            raise EncryptionError(f"GPG encryption failed: {result.status}")

        logging.info(f"Successfully encrypted file: {encrypted_file}")
        return encrypted_file
    except EncryptionError:
        raise
    except Exception as e:
        raise EncryptionError(f"encrypt_file error: {e}")


def decrypt_file(
    encrypted_file: str, passphrase: str, output_file: Optional[str] = None
) -> str:
    """
    Decrypt .gpg file. If output_file is None, creates temp file in same directory.
    Returns path to decrypted file.
    Raises EncryptionError on failure.
    """
    if not encrypted_file.endswith(".gpg"):
        raise EncryptionError(f"File does not have .gpg extension: {encrypted_file}")

    try:
        gpg = gnupg.GPG()

        if output_file is None:
            # Create temp file in same directory as encrypted file
            encrypted_dir = os.path.dirname(encrypted_file)
            fd, output_file = tempfile.mkstemp(dir=encrypted_dir)
            os.close(fd)

        with open(encrypted_file, "rb") as f:
            result = gpg.decrypt_file(
                f,
                passphrase=passphrase,
                output=output_file,
            )

        if not result.ok:
            # Clean up temp file if decryption failed
            if os.path.exists(output_file):
                os.remove(output_file)
            raise EncryptionError(f"GPG decryption failed: {result.status}")

        return output_file
    except EncryptionError:
        raise
    except Exception as e:
        raise EncryptionError(f"decrypt_file error: {e}")


def hash_file(file: str) -> str:
    """Return sha256 hex digest of file (chunk-reads)."""
    sha256_hash = hashlib.sha256()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def compare_files(src: str, dst: str) -> bool:
    """Compare two files by hash. Returns True if identical."""
    return hash_file(src) == hash_file(dst)


def create_checksum_file(file: str) -> str:
    """Create <file>.sha256 with sha256 hash. Returns checksum path."""
    hash_value = hash_file(file)
    checksum_file = f"{file}.sha256"
    with open(checksum_file, "w") as f:
        f.write(f"{hash_value}  {os.path.basename(file)}\n")
    logging.info(f"Created checksum file: {checksum_file}")
    return checksum_file


def shred_file(file: str) -> None:
    """Securely delete file using 'shred -u'. Raises error if shredding fails."""
    try:
        result = subprocess.run(
            ["shred", "-u", file],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(f"shred failed for {file}: {result.stderr}")
        logging.info(f"Securely shredded: {file}")
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"shred timed out for {file}")


# Orchestration
def export_and_backup(env: dict) -> None:
    """
    Full workflow. Called by main().
    Sensitive data (passphrase, session) cleared in finally block.
    """
    passphrase = None
    bw_session = None
    try:
        bw_session = bw_unlock()
        passphrase = get_gpg_passphrase(
            bw_session,
            env["BW_GPG_PASSPHRASE_ID"],
            env["BW_GPG_PASSPHRASE_FIELD"],
        )

        today = datetime.today().strftime("%Y%m%d")
        exports = [
            (f"{today}_bitwarden_perso_export.json", "json", None),
            (f"{today}_bitwarden_org_export.json", "json", env["BW_ORGANIZATION_ID"]),
        ]

        for filename, fmt, org_id in exports:
            output = os.path.join(env["BW_EXPORT_PATH"], filename)
            bw_export(bw_session, output, fmt, org_id)

            encrypted = encrypt_file(output, passphrase)

            # Validate encryption success before destroying plaintext.
            # Decrypts to temp file in BW_EXPORT_PATH to catch silent corruption.
            decrypted = None
            try:
                decrypted = decrypt_file(encrypted, passphrase, output_file=None)
                if not compare_files(output, decrypted):
                    raise ValidationError(f"Validation failed for {encrypted}")
            finally:
                # Always clean up decrypted temp file, even on validation failure
                if decrypted is not None:
                    shred_file(decrypted)

            create_checksum_file(encrypted)
            shred_file(output)

        logging.info("Backup completed successfully")
    finally:
        # Clear sensitive data from memory
        passphrase = None
        bw_session = None


def main() -> None:
    """Validate environment, then run backup."""
    setup_logging()
    try:
        check_commands()
        env = check_env_vars()
        check_export_path(env["BW_EXPORT_PATH"])
        check_gpg()
        export_and_backup(env)
    except (FileNotFoundError, EnvironmentError, EncryptionError, ValidationError) as e:
        logging.error(str(e))
        raise SystemExit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
