# shamir

File encryption/decryption using Shamir's secret sharing scheme.

## What it does

Encrypts/decrypts files using a multi-party secret sharing model where:

- To encrypt: splits a token into N shares, requires M of N to reconstruct the secret
- To decrypt: combines M shares to recover the secret, decrypts the file

Uses `ssss` (Shamir's Secret Sharing Scheme) CLI tool and GPG for symmetric encryption (AES256).

## Prerequisites

- `ssss` CLI (Shamir secret sharing): http://point-at-infinity.org/ssss/
- `gnupg`
- Python 3.11+
- `uv` (for installation)

## Install

```bash
uv tool install ./shamir
```

## Usage

### Encrypt a file

```bash
shamir encrypt-file --filename secret.txt --token "my-secret-token"
```

This will:

1. Split your token into 6 shares (you define any 3 to reconstruct)
2. Prompt you to enter 3 shares to combine into the encryption secret
3. Encrypt `secret.txt` with GPG/AES256
4. Output: `secret.txt.gpg`

### Decrypt a file

```bash
shamir decrypt-file --filename secret.txt.gpg
```

This will:

1. Prompt you to enter 3 shares to combine into the decryption secret
2. Decrypt the file
3. Output: `secret.txt`

## Configuration

Constants in `shamir.py`:

- `THRESHOLD` (default 3) — shares required to reconstruct secret
- `SHARES` (default 6) — total shares generated
- `BITSIZE` (default 1024) — key bitsize

## Testing

```bash
uv run pytest tests/
```

## References

- [Shamir's Secret Sharing](https://en.wikipedia.org/wiki/Shamir%27s_Secret_Sharing)
- [SSSS Tool](http://point-at-infinity.org/ssss/)
- Original inspiration: https://www.trellix.com/en-us/assets/docs/atr-library/tr-shamirs-secret-sharing-key-shares.pdf
