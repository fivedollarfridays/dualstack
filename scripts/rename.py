#!/usr/bin/env python3
"""Rename/rebrand the DualStack 'items' entity to your domain entity.

Usage:
    python scripts/rename.py --from item --to project
    python scripts/rename.py --from item --to project --dry-run
    python scripts/rename.py --from item --to person --to-plural people
"""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path
from typing import Optional


def derive_plural(singular: str, override: Optional[str] = None) -> str:
    """Derive plural form from singular, or use override if provided."""
    if override:
        return override
    return singular + "s"


def build_replacements(
    from_singular: str,
    from_plural: str,
    to_singular: str,
    to_plural: str,
) -> list[tuple[str, str]]:
    """Build ordered list of (old, new) replacement pairs.

    Plural forms are listed first to prevent partial matches
    (e.g., 'items' must be replaced before 'item').
    """
    return [
        # Plurals first (all cases)
        (from_plural, to_plural),
        (from_plural.capitalize(), to_plural.capitalize()),
        (from_plural.upper(), to_plural.upper()),
        # Then singulars
        (from_singular, to_singular),
        (from_singular.capitalize(), to_singular.capitalize()),
        (from_singular.upper(), to_singular.upper()),
    ]


def apply_replacements(content: str, replacements: list[tuple[str, str]]) -> str:
    """Apply all replacements to content string."""
    for old, new in replacements:
        content = content.replace(old, new)
    return content


# Directory mappings relative to project root
DIRECTORY_TEMPLATES = [
    "backend/app/{plural}",
    "backend/tests/{plural}",
    "frontend/src/components/{plural}",
    "frontend/src/app/(dashboard)/{plural}",
]

# File extensions to process for content replacement
CONTENT_EXTENSIONS = {".py", ".ts", ".tsx", ".md"}

# Directories to skip entirely (relative to project root)
SKIP_DIRS = {
    "node_modules", "__pycache__", ".next", "coverage", "scripts",
    ".git", ".paircoder", ".claude", "dist", "build", ".venv", "venv",
}


def find_project_root(script_path: str) -> Path:
    """Find project root (parent of scripts/)."""
    return Path(script_path).resolve().parent.parent


def get_directories_to_rename(
    root: Path, from_plural: str, to_plural: str
) -> list[tuple[Path, Path]]:
    """Return list of (old_dir, new_dir) pairs for directories to rename."""
    pairs = []
    for template in DIRECTORY_TEMPLATES:
        old_dir = root / template.format(plural=from_plural)
        new_dir = root / template.format(plural=to_plural)
        if old_dir.exists():
            pairs.append((old_dir, new_dir))
    return pairs


def find_files_to_rename(
    root: Path, replacements: list[tuple[str, str]]
) -> list[tuple[Path, Path]]:
    """Find files whose names contain the old entity name."""
    pairs = []
    for dirpath, _, filenames in os.walk(root):
        dirpath_p = Path(dirpath)
        # Skip hidden dirs, node_modules, __pycache__, .git
        parts = dirpath_p.relative_to(root).parts
        if any(p.startswith(".") or p in SKIP_DIRS for p in parts):
            continue
        for filename in filenames:
            new_name = apply_replacements(filename, replacements)
            if new_name != filename:
                old_path = dirpath_p / filename
                new_path = dirpath_p / new_name
                pairs.append((old_path, new_path))
    return pairs


def find_content_files(root: Path) -> list[Path]:
    """Find all files eligible for content replacement."""
    files = []
    for dirpath, _, filenames in os.walk(root):
        dirpath_p = Path(dirpath)
        parts = dirpath_p.relative_to(root).parts
        if any(p.startswith(".") or p in SKIP_DIRS for p in parts):
            continue
        for filename in filenames:
            ext = Path(filename).suffix
            if ext in CONTENT_EXTENSIONS:
                files.append(dirpath_p / filename)
    return files


def replace_file_contents(
    filepath: Path, replacements: list[tuple[str, str]]
) -> int:
    """Replace content in a file. Returns number of replacements made."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return 0

    new_content = apply_replacements(content, replacements)
    if new_content != content:
        count = sum(
            content.count(old) for old, _ in replacements if old in content
        )
        filepath.write_text(new_content, encoding="utf-8")
        return count
    return 0


def run_rename(
    from_singular: str,
    from_plural: str,
    to_singular: str,
    to_plural: str,
    dry_run: bool = False,
    root: Optional[Path] = None,
) -> dict[str, int]:
    """Execute the rename operation.

    Returns dict with counts: dirs_renamed, files_renamed, files_modified,
    replacements_made.
    """
    if root is None:
        root = find_project_root(__file__)

    replacements = build_replacements(from_singular, from_plural, to_singular, to_plural)

    stats = {
        "dirs_renamed": 0,
        "files_renamed": 0,
        "files_modified": 0,
        "replacements_made": 0,
    }

    # 1. Rename directories
    dir_pairs = get_directories_to_rename(root, from_plural, to_plural)
    for old_dir, new_dir in dir_pairs:
        if dry_run:
            print(f"  [dir] {old_dir.relative_to(root)} -> {new_dir.relative_to(root)}")
        else:
            shutil.move(str(old_dir), str(new_dir))
        stats["dirs_renamed"] += 1

    # 2. Find and rename files with entity name
    file_rename_pairs = find_files_to_rename(root, replacements)
    for old_path, new_path in file_rename_pairs:
        if dry_run:
            try:
                rel_old = old_path.relative_to(root)
                rel_new = new_path.relative_to(root)
            except ValueError:
                rel_old, rel_new = old_path, new_path
            print(f"  [file] {rel_old} -> {rel_new}")
        else:
            old_path.rename(new_path)
        stats["files_renamed"] += 1

    # 3. Replace content in eligible files
    content_files = find_content_files(root)
    for filepath in content_files:
        if dry_run:
            try:
                content = filepath.read_text(encoding="utf-8")
            except (UnicodeDecodeError, PermissionError):
                continue
            new_content = apply_replacements(content, replacements)
            if new_content != content:
                count = sum(
                    content.count(old) for old, _ in replacements if old in content
                )
                try:
                    rel = filepath.relative_to(root)
                except ValueError:
                    rel = filepath
                print(f"  [content] {rel} ({count} replacements)")
                stats["files_modified"] += 1
                stats["replacements_made"] += count
        else:
            count = replace_file_contents(filepath, replacements)
            if count:
                stats["files_modified"] += 1
                stats["replacements_made"] += count

    return stats


def print_summary(stats: dict[str, int], dry_run: bool = False) -> None:
    """Print summary of changes."""
    prefix = "[DRY RUN] " if dry_run else ""
    print(f"\n{prefix}Summary:")
    print(f"  Directories renamed: {stats['dirs_renamed']}")
    print(f"  Files renamed:       {stats['files_renamed']}")
    print(f"  Files modified:      {stats['files_modified']}")
    print(f"  Replacements made:   {stats['replacements_made']}")


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Rename the DualStack entity (e.g., 'item' -> 'project')"
    )
    parser.add_argument(
        "--from", dest="from_singular", required=True,
        help="Current entity name, singular (e.g., 'item')",
    )
    parser.add_argument(
        "--to", dest="to_singular", required=True,
        help="New entity name, singular (e.g., 'project')",
    )
    parser.add_argument(
        "--from-plural", dest="from_plural", default=None,
        help="Override plural form of --from (default: adds 's')",
    )
    parser.add_argument(
        "--to-plural", dest="to_plural", default=None,
        help="Override plural form of --to (default: adds 's')",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview changes without modifying files",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> None:
    """Main entry point."""
    args = parse_args(argv)

    from_singular = args.from_singular.lower()
    to_singular = args.to_singular.lower()
    from_plural = derive_plural(from_singular, args.from_plural)
    to_plural = derive_plural(to_singular, args.to_plural)

    print(f"Renaming: {from_singular}/{from_plural} -> {to_singular}/{to_plural}")
    if args.dry_run:
        print("(dry run -- no files will be modified)\n")

    stats = run_rename(
        from_singular, from_plural, to_singular, to_plural,
        dry_run=args.dry_run,
    )
    print_summary(stats, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
