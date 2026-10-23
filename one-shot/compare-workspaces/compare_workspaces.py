#!/usr/bin/env python3
"""
Obsidian Workspace Comparison Script

This script compares markdown files between two Obsidian workspaces (Perso and Resources)
using SHA-256 checksums to identify content matches regardless of file location.

Purpose: Before deleting the Resources workspace, ensure all its content has been imported
into the Perso workspace.

Output: Reports all markdown files in Resources that don't have matching content in Perso,
so they can be reviewed manually for import or deletion.
"""

import hashlib
from pathlib import Path

# Configuration
PERSO_PATH = "Perso/"
RESOURCES_PATH = "Resources/"
EXCLUDE_FOLDER = ".obsidian"


def get_checksum(file_path):
    """Calculate SHA-256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        sha256_hash.update(f.read())
    return sha256_hash.hexdigest()


def scan_workspace(path, return_dict=False):
    """
    Scan workspace for markdown files and calculate checksums.

    Args:
        path: Directory path to scan
        return_dict: If True, return dict {checksum: filepath}, else return set of checksums

    Returns:
        Set of checksums or dict mapping checksums to file paths
    """
    workspace_path = Path(path)

    if return_dict:
        result = {}
    else:
        result = set()

    # Recursively find all .md files, excluding .obsidian folders
    for md_file in workspace_path.rglob("*.md"):
        # Skip files in .obsidian folders
        if EXCLUDE_FOLDER in md_file.parts:
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
    print("Scanning workspaces...\n")

    # Scan Perso workspace (only need checksums)
    perso_checksums = scan_workspace(PERSO_PATH)

    # Scan Resources workspace (need file paths for reporting)
    resources_files = scan_workspace(RESOURCES_PATH, return_dict=True)

    # Find files in Resources not in Perso
    unique_checksums = set(resources_files.keys()) - perso_checksums

    # Generate report
    print("Workspace Comparison Report")
    print("=" * 50)
    print()
    print(f"Perso workspace: {len(perso_checksums):,} markdown files scanned")
    print(f"Resources workspace: {len(resources_files):,} markdown files scanned")
    print()
    print(
        f"Markdown files in Resources NOT found in Perso: {len(unique_checksums)} files"
    )
    print("-" * 50)
    print()

    if unique_checksums:
        # Get file paths and sizes for unique files
        unique_files = []
        for checksum in unique_checksums:
            file_path = resources_files[checksum]
            full_path = Path(RESOURCES_PATH) / file_path
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
        print("All markdown files in Resources have matching content in Perso!")


if __name__ == "__main__":
    main()
