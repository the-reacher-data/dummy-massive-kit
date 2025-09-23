#!/usr/bin/env python3
import argparse
import sys
import subprocess
from pathlib import Path
import tomllib
import tomli_w
import re

def load_config(path: str) -> dict:
    f = Path(path)
    if not f.exists():
        sys.exit(f"❌ Config file not found: {path}")
    return tomllib.loads(f.read_text(encoding="utf-8"))

def matches(branch: str, patterns) -> bool:
    if not patterns:
        return False
    if isinstance(patterns, str):
        patterns = [patterns]
    return any(re.fullmatch(p, branch) for p in patterns)

def bump(base: str, part: str) -> str:
    major, minor, patch = map(int, base.split("."))
    if part == "major":
        major += 1; minor = 0; patch = 0
    elif part == "minor":
        minor += 1; patch = 0
    elif part == "patch":
        patch += 1
    return f"{major}.{minor}.{patch}"

def calc_next_version(cfg: dict, branch: str, prerelease: bool, current: str) -> tuple[str,bool]:
    # ignore rules
    if prerelease and matches(branch, cfg.get("prerelease-ignore", [])):
        return current, False
    if not prerelease and matches(branch, cfg.get("release-ignore", [])):
        return current, False

    bump_type = "patch"
    if matches(branch, cfg.get("minor", [])):
        bump_type = "minor"
    elif matches(branch, cfg.get("major", [])):
        bump_type = "major"
    elif matches(branch, cfg.get("patch", [])):
        bump_type = "patch"

    nextv = bump(current, bump_type)

    if prerelease and matches(branch, cfg.get("prerelease", [])):
        count = subprocess.check_output(
            ["git", "rev-list", "--count", "HEAD"], text=True
        ).strip()
        return f"{nextv}.dev{count}", True

    if not prerelease and matches(branch, cfg.get("release", [])):
        return nextv, True

    return current, False

def update_pyproject(data: dict, path: Path, new_version: str):
    if "project" not in data:
        data["project"] = {}
    data["project"]["version"] = new_version
    path.write_text(tomli_w.dumps(data), encoding="utf-8")

def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", required=True)
    parser.add_argument("--prerelease", required=False, default="false")
    parser.add_argument("--config", required=False, default="pyproject.toml")
    args = parser.parse_args()

    data = load_config(args.config)
    cfg = data.get("tool", {}).get("semantic-branch", {})
    current = data.get("project", {}).get("version", "0.1.0")
    prerelease = args.prerelease.lower() == "true"

    version, deploy = calc_next_version(cfg, args.branch, prerelease, current)

    # update only for release mode
    if  deploy and Path(args.config).name == "pyproject.toml":
        update_pyproject(data, Path(args.config), version)

    print(f"version={version}")
    print(f"deploy={'true' if deploy else 'false'}")

if __name__ == "__main__":
    cli()
