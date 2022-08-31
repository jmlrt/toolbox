import argparse
import logging
import os
import subprocess
from datetime import datetime
from getpass import getpass

from utils.files import (
    compare_files,
    create_checksum_file,
    decrypt_file,
    encrypt_file,
    rename_file,
    shred_file,
)
from utils.shell import check_command_in_path, check_environment_variable

DATE = datetime.today()
FORMATED_DATE = DATE.strftime("%Y%m%d")
WORK_DIR = f"{os.environ['HOME']}/Downloads"

FILES_TO_RENAME = {
    f"{FORMATED_DATE}_pocket_bookmarks.html": "ril_export.html",
    f"{FORMATED_DATE}_shaarli_bookmarks.html": f"bookmarks_all_{FORMATED_DATE}_*.html",
    f"{FORMATED_DATE}_firefox_bookmarks.html": "bookmarks.html",
    f"{FORMATED_DATE}_firefox_bookmarks.json": f"bookmarks-{DATE.strftime('%Y-%m-%d')}.json",
    f"{FORMATED_DATE}_chrome_bookmarks.html": f"bookmarks_{DATE.strftime('%d_%m_%Y')}.html",
    f"{FORMATED_DATE}_todoist.zip": f"Todoist backup {DATE.strftime('%Y-%m-%d')}.zip",
}
BITWARDEN_EXPORTS = [
    ("personal", "json", f"{WORK_DIR}/{FORMATED_DATE}_bitwarden_perso_export.json"),
    ("personal", "csv", f"{WORK_DIR}/{FORMATED_DATE}_bitwarden_perso_export.csv"),
    ("organization", "json", f"{WORK_DIR}/{FORMATED_DATE}_bitwarden_org_export.json"),
    ("organization", "csv", f"{WORK_DIR}/{FORMATED_DATE}_bitwarden_org_export.csv"),
]


def backup_files(files_patterns):
    for file in files_patterns.keys():
        try:
            rename_file(f"{WORK_DIR}/{files_patterns[file]}", f"{WORK_DIR}/{file}")
        except FileNotFoundError:
            logging.info(f"No file found matching {files_patterns[file]}")


def encrypt_backup(file, passphrase):
    encrypted_file = encrypt_file(file, passphrase)

    # verify encrypted file
    decrypted_file = decrypt_file(encrypted_file, passphrase, f"{encrypted_file}.tmp")

    if compare_files(file, decrypted_file) is not True:
        raise Exception(f"{decrypted_file} hash doesn't match {file} hash")

    # write gpg file digest
    create_checksum_file(file)

    # shred original and tmp files
    shred_file(file)
    shred_file(decrypted_file)


def export_bitwarden_secrets():
    check_environment_variable("BW_SESSION", "You must be logged in to Bitwarden")
    gpg_passphrase = check_environment_variable("GPG_PASSPHRASE")
    organization_id = check_environment_variable("BW_ORGANIZATION_ID")
    check_command_in_path(
        "bw", "Please install Bitwarden CLI: https://bitwarden.com/help/article/cli/"
    )

    def export_bitwarden_command(vault, password, file_format, file_path):
        bw_cmd = [
            "bw",
            "export",
            password,
            "--output",
            file_path,
            "--format",
            file_format,
        ]
        if vault == "organization":
            bw_cmd.extend(["--organizationid", organization_id])
        subprocess.run(bw_cmd)
        logging.info(f"Bitwarden {vault} vault exported in {file_format.upper()}")

    password = getpass("Enter Bitwarden password: ")

    for vault, file_format, file_path in BITWARDEN_EXPORTS:
        export_bitwarden_command(vault, password, file_format, file_path)
        encrypt_backup(file_path, gpg_passphrase)


def rename_exports():
    for file in FILES_TO_RENAME:
        try:
            rename_file(f"{WORK_DIR}/{FILES_TO_RENAME[file]}", f"{WORK_DIR}/{file}")
        except FileNotFoundError:
            logging.info(f"No file found matching {FILES_TO_RENAME[file]}")


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    command = parser.parse_args().command
    print(command)
    if command == "export-secrets":
        export_bitwarden_secrets()
    elif command == "rename-exports":
        rename_exports()
    else:
        logging.error("Command not found")


if __name__ == "__main__":
    main()
