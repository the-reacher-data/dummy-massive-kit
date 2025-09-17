#!/usr/bin/env python3
"""
Generate development versions for TestPyPI following PEP 440.

Format: X.Y.Z.dev{EPOCH}+{IDENTIFIER}
Example: 1.2.0.dev1705328400+feature-api-auth
"""

import re
import sys
import time


def get_base_version(pyproject_path: str = "pyproject.toml") -> str:
    """
    Extract base version from pyproject.toml.

    Returns:
        Base version like "0.1.0"
    """
    try:
        with open(pyproject_path, encoding="utf-8") as f:
            content = f.read()

        match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
        else:
            return "0.1.0"  # Fallback
    except FileNotFoundError:
        return "0.1.0"  # Fallback


def sanitize_identifier(identifier: str) -> str:
    """
    Sanitize identifier for PEP 440 compliance.

    Args:
        identifier: Raw identifier (branch name, PR number, etc.)

    Returns:
        Sanitized identifier safe for version string
    """
    # Remove refs/heads/ if present
    identifier = identifier.replace("refs/heads/", "")

    # Replace invalid characters with hyphens
    identifier = re.sub(r"[^a-zA-Z0-9\-\.]", "-", identifier)

    # Remove consecutive hyphens
    identifier = re.sub(r"-+", "-", identifier)

    # Remove leading/trailing hyphens
    identifier = identifier.strip("-")

    # Limit length to 20 chars
    if len(identifier) > 20:
        identifier = identifier[:20]

    return identifier.lower()


def generate_dev_version(base_version: str, identifier: str) -> str:
    """
    Generate a development version string.

    Args:
        base_version: Base version like "1.2.0"
        identifier: Unique identifier (branch, PR, etc.)

    Returns:
        Development version like "1.2.0.dev1705328400+feature-api"
    """
    # Get current epoch timestamp
    epoch = int(time.time())

    # Sanitize identifier
    clean_identifier = sanitize_identifier(identifier)

    # Generate dev version
    dev_version = f"{base_version}.dev{epoch}.{clean_identifier}"

    return dev_version


def main() -> None:
    """CLI interface for the script."""
    min_args = 2
    if len(sys.argv) < min_args:
        print("Usage: python generate_dev_version.py <identifier> [base_version]")
        print("Examples:")
        print("  python generate_dev_version.py feature/api-auth")
        print("  python generate_dev_version.py pr123")
        print("  python generate_dev_version.py release/next 2.0.0")
        sys.exit(1)

    identifier = sys.argv[1]
    base_version = sys.argv[2] if len(sys.argv) > 2 else get_base_version()

    dev_version = generate_dev_version(base_version, identifier)
    print(dev_version)


if __name__ == "__main__":
    main()
