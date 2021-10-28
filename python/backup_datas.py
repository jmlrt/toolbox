from utils.files import (
    create_checksum_file,
    compare_files,
    decrypt_file,
    encrypt_file,
    rename_file,
    shred_file,
)

from datetime import datetime
import logging
import os


date = datetime.today().strftime("%Y%m%d")
work_dir = f"{os.environ['HOME']}/Downloads"
gpg_passphrase = os.environ["GPG_PASSPHRASE"]

standard_backups = {
    f"{date}_pocket_bookmarks.html": "ril_export.html",
    f"{date}_shaarli_bookmarks.html": f"bookmarks_all_{date}_*.html",
}
encrypted_backups = {
    f"{date}_bitwarden_perso_export.csv": f"bitwarden_export_{date}*.csv",
    f"{date}_bitwarden_perso_export.json": f"bitwarden_export_{date}*.json",
    f"{date}_bitwarden_org_jj_export.csv": f"bitwarden_org_export_{date}*.csv",
    f"{date}_bitwarden_org_jj_export.json": f"bitwarden_org_export_{date}*.json",
}


def backup_files(files_patterns):
    for file in files_patterns.keys():
        try:
            rename_file(f"{work_dir}/{files_patterns[file]}", f"{work_dir}/{file}")
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


def main():
    logging.basicConfig(level=logging.INFO)

    backups = standard_backups | encrypted_backups
    for file in backups:
        try:
            rename_file(f"{work_dir}/{backups[file]}", f"{work_dir}/{file}")
        except FileNotFoundError:
            logging.info(f"No file found matching {backups[file]}")

    if gpg_passphrase is None:
        raise Exception("GPG_PASSPHRASE environment variable missing")
    for file in encrypted_backups.keys():
        encrypt_backup(f"{work_dir}/{file}", gpg_passphrase)


if __name__ == "__main__":
    main()
