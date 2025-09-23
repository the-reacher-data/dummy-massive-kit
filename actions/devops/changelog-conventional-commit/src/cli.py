# type: ignore
"""
CLI to generate changelog from conventional commits.

Modes:
- pr: collect commits from PR branch
- release: use squash commit body

If --version is missing, use commit title/body as fallback.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Dict
from jinja2 import Environment, FileSystemLoader

DEFAULT_TEMPLATE = str(Path(__file__).parent / "templates" / "default.md.j2")

def get_commits_pr(branch: str) -> List[str]:
    """Get commit messages for PR branch compared to origin/main."""
    try:
        base = subprocess.check_output(
            ["git", "merge-base", branch, "origin/main"], text=True
        ).strip()
        commits = subprocess.check_output(
            ["git", "log", f"{base}..HEAD", "--pretty=format:%s"], text=True
        ).splitlines()
        return commits
    except subprocess.CalledProcessError:
        return []

def get_commit_body() -> str:
    """Get body of the last commit (squash)."""
    return subprocess.check_output(
        ["git", "log", "-1", "--pretty=%B"], text=True
    )

def parse_commits(commits: List[str]) -> Dict[str, List[str]]:
    """Group commits by conventional type, ignore wip."""
    grouped: Dict[str, List[str]] = {}
    for msg in commits:
        msg = msg.strip()
        if not msg or msg.startswith("wip:"):
            continue
        if ":" in msg:
            typ, rest = msg.split(":", 1)
            typ = typ.strip()
            grouped.setdefault(typ, []).append(rest.strip())
        else:
            grouped.setdefault("other", []).append(msg)
    return grouped

def render(template_path: str, version: str, commits: Dict[str, List[str]]) -> str:
    env = Environment(
        loader=FileSystemLoader(Path(template_path).parent),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    tmpl = env.get_template(Path(template_path).name)
    return tmpl.render(version=version, commits=commits)

def cli():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", required=True, choices=["pr", "release"])
    p.add_argument("--branch", required=True)
    p.add_argument("--version", required=False)
    p.add_argument("--template", required=False, default=DEFAULT_TEMPLATE)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    if args.mode == "pr":
        commits = get_commits_pr(args.branch)
        title = args.version or f"Changelog Preview for {args.branch}"
    else:
        body = get_commit_body()
        commits = body.splitlines()
        title = args.version or commits[0] if commits else "Unreleased"

    grouped = parse_commits(commits)
    md = render(args.template, title, grouped)

    Path(args.output).write_text(md, encoding="utf-8")
    print(md)

    if args.mode == "release":
        changelog = Path("CHANGELOG.md")
        if changelog.exists():
            old = changelog.read_text(encoding="utf-8")
            changelog.write_text(md + "\n\n" + old, encoding="utf-8")
        else:
            changelog.write_text(md, encoding="utf-8")

        subprocess.run(["git", "add", "CHANGELOG.md"], check=False)
        subprocess.run(["git", "commit", "-m", f"chore(release): {title}"], check=False)

if __name__ == "__main__":
    cli()
