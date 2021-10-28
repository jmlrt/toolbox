from utils.files import (
    compare_files,
    create_checksum_file,
    decrypt_file,
    encrypt_file,
    hash_file,
    rename_file,
)

import os


GPG_PASSPHRASE = "mypassphrase"


def test_compare_files():
    assert compare_files("tests/fixtures/hello.txt", "tests/fixtures/hello.bak")
    assert not compare_files("tests/fixtures/hello.txt", "tests/fixtures/foo.txt")


def test_create_checksum_file():
    checksum_file = "tests/fixtures/hello.txt.sha256"
    assert create_checksum_file("tests/fixtures/hello.txt") == checksum_file
    assert os.path.exists(checksum_file)
    with open(checksum_file) as f:
        data = f.readline()
    assert "d9014c4624844aa5bac314773d6b689ad467fa4e1d1a50a1b8a99d5a95f72ff5" in data
    # teardown
    os.remove(checksum_file)


def test_encrypt_file():
    encrypted_file = "tests/fixtures/hello.bak.gpg"
    assert encrypt_file("tests/fixtures/hello.bak", GPG_PASSPHRASE) == encrypted_file
    assert (
        os.system(
            f"echo {GPG_PASSPHRASE} | gpg -d --passphrase-fd 0 --batch {encrypted_file}"
        )
        == 0
    )
    # teardown
    os.remove(encrypted_file)


def test_decrypt_file():
    decrypted_file = "tests/fixtures/bar.txt"
    assert decrypt_file("tests/fixtures/bar.txt.gpg", GPG_PASSPHRASE) == decrypted_file
    with open(decrypted_file) as f:
        data = f.readline()
    assert data == "bar"
    # teardown
    os.remove(decrypted_file)


def test_hash_file():
    assert (
        hash_file("tests/fixtures/hello.txt")
        == "d9014c4624844aa5bac314773d6b689ad467fa4e1d1a50a1b8a99d5a95f72ff5"
    )
    assert (
        hash_file("tests/fixtures/hello.txt.gpg")
        == "4945b77be7da46b8081ea62f7c586f1bfa97c20dc219f547cfcdef2b3bf21552"
    )


def test_rename_file():
    file = "file.txt"
    new_file = "newfile.txt"
    open(file, "a").close()
    rename_file(file, new_file)
    assert os.path.exists(new_file)
    assert not os.path.exists(file)
    # teardown
    os.remove(new_file)
