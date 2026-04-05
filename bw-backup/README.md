# bw-backup

Bitwarden backup with GPG encryption.

## What it does

Exports personal and org Bitwarden vaults to JSON, encrypts with GPG (AES256), creates SHA256 checksums, and securely deletes plaintext files using `shred`.

## Prerequisites

- `bw` CLI (Bitwarden)
- `gnupg`
- `shred` (secure file deletion)
- Python 3.13+
- `uv` (for installation)

## Install

```bash
uv tool install ./bw-backup
```

## Environment variables

Required:

- `BW_ORGANIZATION_ID` — Org ID
- `BW_GPG_PASSPHRASE_ID` — Bitwarden item ID containing GPG passphrase
- `BW_EXPORT_PATH` — Destination directory (must exist)
- `BW_GPG_PASSPHRASE_FIELD` — Field name in item with passphrase

## Usage

```bash
export BW_ORGANIZATION_ID=...
export BW_GPG_PASSPHRASE_ID=...
export BW_EXPORT_PATH=/path/to/backups
export BW_GPG_PASSPHRASE_FIELD=passphrase

bw-backup
```

Creates:

- `YYYYMMDD_bitwarden_perso_export.json.gpg`
- `YYYYMMDD_bitwarden_perso_export.json.gpg.sha256`
- `YYYYMMDD_bitwarden_org_export.json.gpg`
- `YYYYMMDD_bitwarden_org_export.json.gpg.sha256`

## Decrypt a backup

```bash
gpg --decrypt YYYYMMDD_bitwarden_perso_export.json.gpg > backup.json
```

You'll be prompted for the GPG passphrase.

## Testing

```bash
uv run pytest tests/
```
