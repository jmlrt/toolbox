#!/usr/bin/env python3
"""
Workspace Comparison Script

Compares markdown files between two directories (reference and target)
using SHA-256 checksums to identify content matches regardless of file
location or name.

Output: reports all markdown files in the target directory that don't
have matching content in the reference directory, for manual review
before deleting or archiving the target directory.

Aborts with a nonzero exit status on invalid paths or unreadable files:
a pre-deletion report must never claim completeness it doesn't have.
"""

import argparse
import hashlib
import sys
from pathlib import Path


def get_checksum(file_path):
    """Calculate SHA-256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        sha256_hash.update(f.read())
    return sha256_hash.hexdigest()


def scan_workspace(path, exclude_folder):
    """
    Scan a directory for markdown files and calculate checksums.

    Args:
        path: Directory path to scan
        exclude_folder: Folder name to skip

    Returns:
        Tuple (contents, scanned) where contents maps each checksum to
        the list of file paths with that content (relative to path), and
        scanned is the number of markdown files read.
    """
    workspace_path = Path(path)
    contents = {}
    scanned = 0

    # Recursively find all .md files, excluding the configured folder
    for md_file in workspace_path.rglob("*.md"):
        if exclude_folder in md_file.parts:
            continue

        # Skip symlinks
        if md_file.is_symlink():
            continue

        try:
            checksum = get_checksum(md_file)
        except (PermissionError, OSError) as e:
            sys.exit(f"error: could not read {md_file}: {e}")

        relative_path = md_file.relative_to(workspace_path)
        contents.setdefault(checksum, []).append(relative_path)
        scanned += 1

    return contents, scanned


def format_size(size_bytes):
    """Format file size in human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description="Report markdown files in the target directory that have "
        "no content match in the reference directory."
    )
    parser.add_argument(
        "reference", help="Reference directory whose content counts as present"
    )
    parser.add_argument(
        "target", help="Target directory checked for unique markdown files"
    )
    parser.add_argument(
        "-x",
        "--exclude",
        default=".obsidian",
        help="Folder name to skip (default: %(default)s)",
    )
    args = parser.parse_args()

    for path in (args.reference, args.target):
        if not Path(path).is_dir():
            sys.exit(f"error: {path} is not an existing directory")

    print("Scanning directories...\n")

    reference_contents, reference_scanned = scan_workspace(args.reference, args.exclude)
    target_contents, target_scanned = scan_workspace(args.target, args.exclude)

    # Find target files whose content is absent from the reference
    unique_files = []
    for checksum, paths in target_contents.items():
        if checksum in reference_contents:
            continue
        for file_path in paths:
            full_path = Path(args.target) / file_path
            try:
                file_size = full_path.stat().st_size
            except OSError:
                file_size = 0
            unique_files.append((file_path, file_size))

    # Sort by path for consistent output
    unique_files.sort()

    # Generate report
    print("Workspace Comparison Report")
    print("=" * 50)
    print()
    print(f"Reference directory: {reference_scanned:,} markdown files scanned")
    print(f"Target directory: {target_scanned:,} markdown files scanned")
    print()
    print(f"Markdown files in target NOT found in reference: {len(unique_files)} files")
    print("-" * 50)
    print()

    if unique_files:
        for idx, (file_path, size) in enumerate(unique_files, 1):
            print(f"{idx}. {file_path} ({format_size(size)})")
    else:
        print(
            "All markdown files in the target directory have matching content in the reference directory!"
        )


if __name__ == "__main__":
    main()
