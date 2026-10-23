#!/usr/bin/env python3
"""File encryption/decryption using Shamir's secret sharing."""

import argparse
import hashlib
import logging
import os
import string
import subprocess
from pathlib import Path
from typing import Optional

import gnupg
import pexpect

CIPHER = "AES256"
BITSIZE = 1024
SHARES = 6
THRESHOLD = 3
SOURCE = "https://www.trellix.com/en-us/assets/docs/atr-library/tr-shamirs-secret-sharing-key-shares.pdf"


# ============================================================================
# File Operations (from utils/files.py)
# ============================================================================


class FileAlreadyExistsError(Exception):
    """Raised when attempting to overwrite an existing file."""

    pass


def compare_files(src_file: str, dst_file: str) -> bool:
    """Compare two files by hash."""
    src_hash = hash_file(src_file)
    dst_hash = hash_file(dst_file)

    if src_hash != dst_hash:
        logging.error(f"{dst_file} doesn't match {src_file}")
        return False

    logging.info(f"{dst_file} and {src_file} are the same files")
    return True


def create_checksum_file(file: str) -> str:
    """Create a SHA256 checksum file."""
    checksum_file = f"{file}.sha256"

    if os.path.exists(checksum_file):
        raise FileAlreadyExistsError(f"{checksum_file} file already exists")

    with open(checksum_file, "w") as f:
        f.write(f"{hash_file(file)} {file}\n")

    logging.info(f"Checksum file {checksum_file} created for {file}")
    return checksum_file


def decrypt_file(
    file: str, passphrase: str, decrypted_file: Optional[str] = None
) -> str:
    """Decrypt a GPG file."""
    file_path = Path(file)

    if file_path.suffix != ".gpg":
        raise Exception("Only files with gpg extension are supported")

    if decrypted_file is None:
        decrypted_file = str(file_path.with_suffix(""))

    if os.path.exists(decrypted_file):
        raise FileAlreadyExistsError(f"{decrypted_file} file already exists")

    gpg = gnupg.GPG()

    with open(file, "rb") as f:
        result = gpg.decrypt_file(f, passphrase=passphrase, output=decrypted_file)

    if not result.ok:
        raise Exception(f"Decryption of {file} failed: {result.status}")

    logging.info(f"File {file} decrypted to {decrypted_file}")
    return decrypted_file


def encrypt_file(
    file: str, passphrase: str, encrypted_file: Optional[str] = None
) -> str:
    """Encrypt a file with GPG."""
    if encrypted_file is None:
        encrypted_file = f"{file}.gpg"

    if os.path.exists(encrypted_file):
        raise FileAlreadyExistsError(f"{encrypted_file} file already exists")

    gpg = gnupg.GPG()

    with open(file, "rb") as f:
        result = gpg.encrypt_file(
            f,
            recipients=None,
            symmetric=CIPHER,
            passphrase=passphrase,
            output=encrypted_file,
        )

    if not result.ok:
        raise Exception(f"Encryption of {file} failed: {result.status}")

    logging.info(f"File {file} encrypted to {encrypted_file}")
    return encrypted_file


def hash_file(file: str) -> str:
    """Calculate the SHA256 hash of a file."""
    hash_obj = hashlib.sha256()

    with open(file, "rb") as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            hash_obj.update(data)

    return hash_obj.hexdigest()


# ============================================================================
# Shell Operations (from utils/shell.py)
# ============================================================================


def check_command_in_path(command: str, help_message: str = "") -> bool:
    """Check if a command exists in PATH."""
    result = subprocess.run(["which", command], capture_output=True, text=True)
    if result.returncode != 0:
        if help_message:
            logging.error(help_message)
        raise Exception(f"Command '{command}' not found in PATH")
    return True


# ============================================================================
# Shamir Secret Sharing (from utils/secrets.py)
# ============================================================================


def generate_key(bits: int = 1024) -> str:
    """Generate a random encryption key."""
    import secrets as secrets_module

    characters = string.ascii_letters + string.digits + string.punctuation
    hex_string = "".join(
        [secrets_module.choice(characters) for _ in range(int(bits / 8))]
    )
    return hex_string


def combine(threshold: int) -> str:
    """Combine secret shares using ssss-combine."""
    check_command_in_path(
        "ssss-combine", "Please install ssss: http://point-at-infinity.org/ssss/"
    )
    s = f"ssss-combine -t {threshold} -Q"
    combine_proc = pexpect.spawnu(s)
    for _ in range(threshold):
        share = input("Share: ")
        combine_proc.sendline(share)
    output = combine_proc.read().split("\r\n")[-2]
    return output


def split(
    token: str, threshold: int = THRESHOLD, shares: int = SHARES, bitsize: int = BITSIZE
) -> None:
    """Split secret using ssss-split."""
    check_command_in_path(
        "ssss-split", "Please install ssss: http://point-at-infinity.org/ssss/"
    )
    key = generate_key(bitsize)
    shares_proc = subprocess.Popen(
        [
            "ssss-split",
            "-w",
            token,
            "-t",
            str(threshold),
            "-n",
            str(shares),
            "-s",
            str(bitsize),
            "-q",
        ],
        text=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    output = shares_proc.communicate(input=key)[0]
    print(output)


# ============================================================================
# Shamir File Encryption Wrapper
# ============================================================================


def encrypt_file_with_shamir(
    token: str,
    threshold: int,
    shares: int,
    bitsize: int,
    file: str,
) -> None:
    """Encrypt file using Shamir secret sharing scheme."""
    split(token, threshold, shares, bitsize)
    secret = combine(threshold)
    encrypt_file(file, secret)


def decrypt_file_with_shamir(threshold: int, encrypted_file: str) -> None:
    """Decrypt file using Shamir secret sharing scheme."""
    secret = combine(threshold)
    decrypt_file(encrypted_file, secret)


# ============================================================================
# CLI
# ============================================================================


def main() -> None:
    """Main entry point."""
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        prog="shamir",
        description="Encrypt/decrypt files using Shamir's secret sharing",
        epilog=f"Inspired by {SOURCE}",
    )
    parser.add_argument("command", choices=["encrypt-file", "decrypt-file"])
    parser.add_argument(
        "-f", "--filename", required=True, help="File to encrypt/decrypt"
    )
    parser.add_argument("-t", "--token", help="Token for splitting (encrypt-file only)")
    args = parser.parse_args()

    if args.command == "encrypt-file":
        if not args.token:
            parser.error("--token is required for encrypt-file")
        encrypt_file_with_shamir(args.token, THRESHOLD, SHARES, BITSIZE, args.filename)
    elif args.command == "decrypt-file":
        decrypt_file_with_shamir(THRESHOLD, args.filename)


if __name__ == "__main__":
    main()
