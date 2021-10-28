from glob import glob
import gnupg
import hashlib
import logging
import os
from pathlib import Path

CIPHER = "AES256"


def compare_files(src_file, dst_file):
    src_hash = hash_file(src_file)
    dst_hash = hash_file(dst_file)

    if src_hash != dst_hash:
        logging.error(f"{dst_file} doesn't match {src_file}")
        return False

    logging.error(f"{dst_file} and {src_file} are the same files")
    return True


def create_checksum_file(file):
    checksum_file = f"{file}.sha256"

    with open(checksum_file, "w") as f:
        f.write(f"{hash_file(file)} {file}\n")

    logging.info(f"Checksum file {checksum_file} created for {file}")
    return checksum_file


def encrypt_file(file, passphrase):
    encrypted_file = f"{file}.gpg"
    gpg = gnupg.GPG()

    with open(file, "rb") as f:
        gpg.encrypt_file(
            f,
            recipients=None,
            symmetric=CIPHER,
            passphrase=passphrase,
            output=encrypted_file,
        )

    logging.info(f"File {file} encrypted to {encrypted_file}")
    return encrypted_file


def decrypt_file(file, passphrase):
    file_path = Path(file)

    if file_path.suffix != ".gpg":
        raise Exception("ERROR: only files with gpg extension are supported")

    decrypted_file = str(file_path.with_suffix(""))
    gpg = gnupg.GPG()

    with open(file, "rb") as f:
        gpg.decrypt_file(f, passphrase=passphrase, output=decrypted_file)

    logging.info(f"File {file} decrypted to {decrypted_file}")
    return decrypted_file


def hash_file(file):
    """Calculate the sha256 hash of a given file.

    Source: https://www.geeksforgeeks.org/compare-two-files-using-hashing-in-python/
    """
    hash = hashlib.sha256()

    with open(file, "rb") as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            hash.update(data)

    return hash.hexdigest()


def rename_file(src_pattern, dst):
    files = glob(src_pattern)

    if len(files) == 0:
        raise FileNotFoundError()
    if len(files) > 1:
        raise ValueError()

    os.rename(files[0], dst)
    logging.info(f"File {files[0]} renamed to {dst}")


def shred_file(file):
    os.system(f"shred -u {file}")
    logging.info(f"File {file} wiped")
