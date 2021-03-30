#!/usr/bin/env python3

from datetime import datetime
from pathlib import Path
from shutil import copy
import logging
import os

import gnupg

logging.basicConfig(level=logging.INFO)
home_dir = os.environ["HOME"]
download_dir = f"{home_dir}/Downloads"
backup_dir = f"{home_dir}/Archives/Backup/Secrets"
# date = datetime.datetime.now().strftime('%Y%m%d')
date = "20210328"

# tuples: (source, destination)
bitwarden_patterns = {
    "perso": (f"bitwarden_export_{date}*", f"{date}_bitwarden_perso_export"),
    "jj": (f"bitwarden_org_export_{date}*", f"{date}_bitwarden_org_jj_export"),
}


def copy_bitwarden_files():
    for org in list(bitwarden_patterns):
        pattern_source = bitwarden_patterns[org][0]
        pattern_destination = bitwarden_patterns[org][1]
        files = sorted(Path(download_dir).glob(pattern_source))

        logging.debug(f"Files matching pattern: {pattern_source}:")
        logging.debug(str(files))

        for file in files:
            if file.suffix in [".csv", ".json"]:
                file_destination = f"{backup_dir}/{pattern_destination}{file.suffix}"
                logging.info(f"copy {str(file)} to {file_destination}")
                copy(file, file_destination)
            else:
                logging.info(f"skip {str(file)} - unknown extension")


def encrypt_files():
    gpg = gnupg.GPG(gnupghome=home_dir)


def main():
    copy_bitwarden_files()


if __name__ == "__main__":
    main()
