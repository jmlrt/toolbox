#!/usr/bin/env python3
"""
Workspace Comparison Script

Compares markdown files between two directories (reference and target)
using SHA-256 checksums to identify content matches regardless of file
location or name.

Output: reports all markdown files in the target directory that don't
have matching content in the reference directory, for manual review
before deleting or archiving the target directory.
"""

import argparse
import hashlib
from pathlib import Path


def get_checksum(file_path):
    """Calculate SHA-256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        sha256_hash.update(f.read())
    return sha256_hash.hexdigest()


def scan_workspace(path, exclude_folder, return_dict=False):
    """
    Scan a directory for markdown files and calculate checksums.

    Args:
        path: Directory path to scan
        exclude_folder: Folder name to skip
        return_dict: If True, return dict {checksum: filepath}, else return set of checksums

    Returns:
        Set of checksums or dict mapping checksums to file paths
    """
    workspace_path = Path(path)

    if return_dict:
        result = {}
    else:
        result = set()

    # Recursively find all .md files, excluding the configured folder
    for md_file in workspace_path.rglob("*.md"):
        if exclude_folder in md_file.parts:
            continue

        # Skip symlinks
        if md_file.is_symlink():
            continue

        try:
            checksum = get_checksum(md_file)

            if return_dict:
                # Store relative path from workspace root
                relative_path = md_file.relative_to(workspace_path)
                result[checksum] = relative_path
            else:
                result.add(checksum)

        except (PermissionError, OSError) as e:
            print(f"Warning: Could not read {md_file}: {e}")
            continue

    return result


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

    print("Scanning directories...\n")

    # Scan reference directory (only need checksums)
    reference_checksums = scan_workspace(args.reference, args.exclude)

    # Scan target directory (need file paths for reporting)
    target_files = scan_workspace(args.target, args.exclude, return_dict=True)

    # Find files in target not in reference
    unique_checksums = set(target_files.keys()) - reference_checksums

    # Generate report
    print("Workspace Comparison Report")
    print("=" * 50)
    print()
    print(f"Reference directory: {len(reference_checksums):,} markdown files scanned")
    print(f"Target directory: {len(target_files):,} markdown files scanned")
    print()
    print(
        f"Markdown files in target NOT found in reference: {len(unique_checksums)} files"
    )
    print("-" * 50)
    print()

    if unique_checksums:
        # Get file paths and sizes for unique files
        unique_files = []
        for checksum in unique_checksums:
            file_path = target_files[checksum]
            full_path = Path(args.target) / file_path
            try:
                file_size = full_path.stat().st_size
                unique_files.append((file_path, file_size))
            except OSError:
                unique_files.append((file_path, 0))

        # Sort by path for consistent output
        unique_files.sort()

        # Print numbered list
        for idx, (file_path, size) in enumerate(unique_files, 1):
            print(f"{idx}. {file_path} ({format_size(size)})")
    else:
        print(
            "All markdown files in the target directory have matching content in the reference directory!"
        )


if __name__ == "__main__":
    main()
