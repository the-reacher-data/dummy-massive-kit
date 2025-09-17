"""
Generate a unique PEP 440–compliant development version string.

Format: <base_version>.dev<timestamp>+g<commit_sha>
Example: 1.2.0.dev1705328700+g1a2b3c4
"""

import re
import sys
import time
from pathlib import Path
import subprocess


def get_base_version(pyproject_path: str = "pyproject.toml") -> str:
    """Extract base version from pyproject.toml or fallback to 0.1.0."""
    try:
        content = Path(pyproject_path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return "0.1.0"

    match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
    return match.group(1) if match else "0.1.0"


def get_commit_sha(short: bool = True) -> str:
    """Get the current git commit hash."""
    try:
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
        return sha[:7] if short else sha
    except Exception:
        return "nogit"


def generate_dev_version(base_version: str, sha: str) -> str:
    """Generate a valid dev version with timestamp and commit hash."""
    epoch = int(time.time())
    return f"{base_version}.dev{epoch}+g{sha}"


def main() -> None:
    base_version = sys.argv[1] if len(sys.argv) > 1 else get_base_version()
    sha = get_commit_sha()
    dev_version = generate_dev_version(base_version, sha)
    print(dev_version)


if __name__ == "__main__":
    main()
