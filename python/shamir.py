import argparse
import logging

import utils.files
from utils.secrets import combine, split

BITSIZE = 1024
SHARES = 6
SOURCE = "https://www.trellix.com/en-us/assets/docs/atr-library/tr-shamirs-secret-sharing-key-shares.pdf"
THRESHOLD = 3


def encrypt_file(token, threshold, shares, bitsize, file):
    split(token, threshold, shares, bitsize)
    secret = combine(threshold)
    utils.files.encrypt_file(file, secret)


def decrypt_file(threshold, encrypted_file):
    secret = combine(threshold)
    utils.files.decrypt_file(encrypted_file, secret)


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        prog="shamir",
        description="encrypt/decrypt file using shamir",
        epilog=f"Inspired by {SOURCE}",
    )
    parser.add_argument("command", choices=["encrypt-file", "decrypt-file"])
    parser.add_argument("-f", "--filename", required=True)
    parser.add_argument("-t", "--token", required=True)
    args = parser.parse_args()
    if args.command == "encrypt-file":
        encrypt_file(args.token, THRESHOLD, SHARES, BITSIZE, args.filename)
    if args.command == "decrypt-file":
        decrypt_file(THRESHOLD, args.filename)


if __name__ == "__main__":
    main()
