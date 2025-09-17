#!/usr/bin/env python3
"""
Update version in pyproject.toml file.

Usage:
    python patch_version.py <new_version>

Example:
    python patch_version.py 1.2.0.dev1705328400+feature-api
"""

import pathlib
import re
import sys
from re import Match


def update_version_in_file(new_version: str, file_path: str = "pyproject.toml") -> None:
    """
    Update version in pyproject.toml file.

    Args:
        new_version: New version string
        file_path: Path to pyproject.toml file
    """
    try:
        p = pathlib.Path(file_path)
        content = p.read_text(encoding="utf-8")

        def repl(m: Match[str]) -> str:
            """Replace version string with new version."""
            print(f"✅ Updating version: {m.group(1)} → {new_version}")
            return f'version = "{new_version}"'

        # Replace version line
        updated_content = re.sub(r'(?m)^\s*version\s*=\s*"([^"]+)"\s*$', repl, content)

        # Write updated content
        p.write_text(updated_content, encoding="utf-8")

    except Exception as e:
        print(f"❌ Error updating version: {e}")
        sys.exit(1)


def main() -> None:
    """CLI interface for the script."""
    min_args = 2
    if len(sys.argv) < min_args:
        print("Usage: python patch_version.py <new_version>")
        print("Example: python patch_version.py 1.2.0.dev1705328400+feature-api")
        sys.exit(1)

    new_version = sys.argv[1]
    update_version_in_file(new_version)


if __name__ == "__main__":
    main()
