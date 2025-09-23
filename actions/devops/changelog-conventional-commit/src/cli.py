#!/usr/bin/env python3
# type: ignore
"""
CLI to generate changelog from conventional commits.

Modes:
- pr: collect commits from PR branch (with SHA + link per commit)
- release: use squash commit body (one global SHA + list of messages, no per-commit SHAs)

Features:
- Group commits by type (feat, fix, docs, etc.)
- Sub-group by scope, or "(no scope)" if none
- Include SHA references and GitHub links
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Dict
from jinja2 import Environment, FileSystemLoader
import re
from collections import defaultdict

DEFAULT_TEMPLATE = str(Path(__file__).parent / "templates" / "report.md.j2")


def get_commits_pr(branch: str) -> List[dict]:
    """Get commits for a PR branch compared to origin/main."""
    base = subprocess.check_output(
        ["git", "merge-base", branch, "origin/main"], text=True
    ).strip()
    raw = subprocess.check_output(
        [
            "git",
            "log",
            f"{base}..HEAD",
            "--pretty=format:%h|%H|%s|%b---END---",
        ],
        text=True,
    )
    commits: List[dict] = []
    for chunk in raw.split("---END---"):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts = chunk.split("|", 3)
        if len(parts) < 4:
            continue
        short, full, subject, body = parts
        if subject.startswith("wip:"):
            continue
        commits.append(
            {
                "sha": short,
                "sha_full": full,
                "subject": subject.strip(),
                "body": body.strip(),
            }
        )
    return commits


def get_commit_squash() -> dict:
    """Get the squash commit (subject + body)."""
    raw = subprocess.check_output(
        ["git", "log", "-1", "--pretty=format:%h|%H|%s|%b"], text=True
    ).strip()
    short, full, subject, body = raw.split("|", 3)
    lines = [l.strip() for l in body.splitlines() if l.strip()]
    commits = []
    for line in lines:
        if line.startswith("wip:"):
            continue
        commits.append({"subject": line, "body": ""})
    return {
        "sha": short,
        "sha_full": full,
        "subject": subject,
        "commits": commits,
    }


def group_commits(commits: List[dict]) -> Dict[str, Dict[str, List[dict]]]:
    """Group commits by type and scope."""
    grouped: Dict[str, Dict[str, List[dict]]] = defaultdict(lambda: defaultdict(list))
    regex = re.compile(r"^(?P<type>\w+)(\((?P<scope>[^)]+)\))?:\s*(?P<desc>.+)$")

    for c in commits:
        subject = c["subject"]
        body = c.get("body", "")
        match = regex.match(subject)
        if match:
            typ = match.group("type")
            scope = match.group("scope") or "(no scope)"
            desc = match.group("desc")
            grouped[typ][scope].append(
                {
                    "title": desc.strip(),
                    "scope": scope,
                    "body": body,
                    "sha": c.get("sha"),
                    "sha_full": c.get("sha_full"),
                }
            )
        else:
            grouped["other"]["(no scope)"].append(
                {
                    "title": subject.strip(),
                    "scope": "(no scope)",
                    "body": body,
                    "sha": c.get("sha"),
                    "sha_full": c.get("sha_full"),
                }
            )
    return grouped


def render(template_path: str, version: str, commits, repo_url: str, squash: dict | None) -> str:
    env = Environment(
        loader=FileSystemLoader(Path(template_path).parent),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    tmpl = env.get_template(Path(template_path).name)
    return tmpl.render(version=version, commits=commits, repo_url=repo_url, squash=squash)


def cli():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", required=True, choices=["pr", "release"])
    p.add_argument("--branch", required=True)
    p.add_argument("--version", required=False)
    p.add_argument("--template", required=False, default=DEFAULT_TEMPLATE)
    p.add_argument("--output", required=True)
    p.add_argument(
        "--repo-url",
        required=False,
        default="https://github.com/${{ github.repository }}",
        help="Base repository URL for commit links",
    )
    args = p.parse_args()

    if args.mode == "pr":
        commits = get_commits_pr(args.branch)
        grouped = group_commits(commits)
        title = args.version or f"Changelog preview for {args.branch}"
        md = render(args.template, title, grouped, args.repo_url, squash=None)
    else:
        squash = get_commit_squash()
        grouped = group_commits(squash["commits"])
        title = args.version or squash["subject"]
        md = render(args.template, title, grouped, args.repo_url, squash=squash)

        # Update CHANGELOG.md in release mode
        changelog = Path("CHANGELOG.md")
        if changelog.exists():
            old = changelog.read_text(encoding="utf-8")
            changelog.write_text(md + "\n\n" + old, encoding="utf-8")
        else:
            changelog.write_text(md, encoding="utf-8")

        subprocess.run(["git", "add", "CHANGELOG.md"], check=False)
        subprocess.run(["git", "commit", "-m", f"chore(release): {title}"], check=False)

    Path(args.output).write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    cli()
