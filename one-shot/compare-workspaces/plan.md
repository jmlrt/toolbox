# Plan: Obsidian Workspace File Comparison Script

## Objective

Create a Python script to identify all files in the "Resources" workspace that don't have matching content in the "Perso" workspace, regardless of their location within the folder structure.

**Important**: This is a READ-ONLY analysis script. It will scan, compare, and report only - no files will be copied, moved, or deleted.

## Approach

### 1. File Discovery

- Recursively scan **only markdown files** (`.md` extension) in both `Perso/` and `Resources/` directories
- Skip `.obsidian/` folders
- Collect file paths for each markdown file

### 2. Checksum Calculation

- Use SHA-256 hash algorithm for content comparison
- Calculate checksum for each markdown file in both workspaces

### 3. Data Structure

- **Perso workspace**: Set of checksums (we only need to know which content exists)
- **Resources workspace**: Dict mapping checksum → file path (to report which files are unique)

### 4. Comparison Logic

- For each checksum in Resources dict:
  - If checksum NOT in Perso set → file is unique to Resources
  - Collect the file path for reporting

### 5. Output Report

Generate a simple report showing:

- Total markdown files scanned in each workspace
- Number of unique markdown files in Resources
- List of markdown files in Resources without matches in Perso:
  - File path relative to Resources/
  - File size (for context)

### 6. Edge Cases to Handle

- Symlinks (skip them)
- Permission errors (catch and continue processing)

## Implementation Details

### Libraries Needed

- `hashlib` - for SHA-256 checksum calculation
- `pathlib` - for file system operations and path handling
- Standard library only, no external dependencies

### Script Structure

```
0. Script header comment
   - Brief explanation: what the script does
   - Why: comparing workspaces before deleting Resources
   - What it reports: markdown files in Resources not found in Perso

1. Hardcoded configuration
   - PERSO_PATH = "Perso/"
   - RESOURCES_PATH = "Resources/"
   - Exclude: .obsidian folders

2. Function: get_checksum(file_path)
   - Read entire file content
   - Return SHA-256 hash

3. Function: scan_workspace(path, return_dict=False)
   - Walk directory tree
   - Find all .md files
   - If return_dict: return {checksum: filepath}
   - Else: return {checksum} set

4. Main execution
   - perso_checksums = scan_workspace(PERSO_PATH)  # returns set
   - resources_files = scan_workspace(RESOURCES_PATH, return_dict=True)  # returns dict
   - Find checksums in resources_files not in perso_checksums
   - Print simple report with file paths and sizes
```

### Output Format Example

```
Workspace Comparison Report
===========================

Perso workspace: 1,234 markdown files scanned
Resources workspace: 567 markdown files scanned

Markdown files in Resources NOT found in Perso: 45 files
---------------------------------------------------

1. Notes/old-project-notes.md (15.2 KB)
2. Projects/2024/archived-project.md (8.5 KB)
3. Daily/2025-01-15.md (3.2 KB)
...
```

## Usage Workflow

1. Run script to generate report of unique markdown files
2. Review list of unique markdown files from Resources
3. Manually decide for each markdown file:
   - Import to Perso (if needed)
   - Discard (if obsolete/duplicate)
4. Re-run script to verify (should show 0 unique markdown files)
5. Safely delete Resources workspace

**Note**: Attachments (images, PDFs, etc.) are not checked by this script. They should be reviewed separately or by checking references in the markdown files.

## Future Improvements

(To implement later only if needed)

### Similar Files Detection

Beyond exact checksum matches, add detection for:

- **Same filename, different content**: Files with identical names but different checksums (possible updated versions)
- **Similar content**: Files that are 95%+ similar using fuzzy matching (might indicate minor edits)
- **Same size + similar name**: Heuristic for finding potential matches that were slightly modified

### Two-Pass Process

Implement a more sophisticated analysis:

- **Pass 1**: Find exact matches (current checksum comparison)
- **Pass 2**: Generate a "suspicious files" report for manual review:
  - Files in Resources with names similar to Perso files
  - Recently modified files in Resources (might indicate active work)
  - Large files (representing significant content/time investment)
  - Files with many internal Obsidian links (central/important notes)
