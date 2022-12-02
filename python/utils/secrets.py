import secrets
import string
import subprocess

import pexpect
from utils.shell import check_command_in_path


def combine(threshold):
    check_command_in_path(
        "ssss-combine", "Please install ssss: http://point-at-infinity.org/ssss/"
    )
    s = f"ssss-combine -t {threshold} -Q"
    combine = pexpect.spawnu(s)
    for _ in range(threshold):
        share = input("Share:")
        combine.sendline(share)
    output = combine.read().split("\r\n")[-2]
    return output


def split(token, threshold=3, shares=6, bitsize=1024):
    check_command_in_path(
        "ssss-split", "Please install ssss: http://point-at-infinity.org/ssss/"
    )
    key = generate_key(bitsize)
    shares = subprocess.Popen(
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
    output = shares.communicate(input=key)[0]
    print(output)


def generate_key(bits=1024):
    characters = string.ascii_letters + string.digits + string.punctuation
    hex_string = "".join([secrets.choice(characters) for _ in range(int(bits / 8))])
    return hex_string
