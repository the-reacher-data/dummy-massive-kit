#!/usr/bin/env python3
"""
CLI to generate changelogs from conventional commits.

Modes:
- pr: collect commits from PR branch (with SHA + link per commit)
- release: use squash commit body (single global SHA + list of messages)

Features:
- Group by type (feat, fix, docs, style, refactor, perf, test, chore, other)
- Sub-group by scope; uses "(no scope)" if absent
- SHA references and GitHub links in PR mode
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader

HERE = Path(__file__).parent
DEFAULT_TEMPLATE = str(HERE / "templates" / "report.md.j2")


def _default_repo_url() -> str:
    """Build GitHub repository URL from environment variables."""
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com").rstrip("/")
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip("/")
    return f"{server}/{repo}" if repo else server


def get_commits_pr(branch: str) -> List[Dict[str, str]]:
    """Retrieve commits for a PR branch compared to origin/main."""
    base = subprocess.check_output(
        ["git", "merge-base", branch, "origin/main"], text=True
    ).strip()
    raw = subprocess.check_output(
        ["git", "log", f"{base}..HEAD", "--pretty=format:%h|%H|%s|%b---END---"],
        text=True,
    )

    commits: List[Dict[str, str]] = []
    for chunk in raw.split("---END---"):
        chunk = chunk.strip()
        if not chunk:
            continue

        parts = chunk.split("|", 3)
        if len(parts) < 4:
            continue

        short, full, subject, body = parts
        subject = subject.strip()

        if subject.lower().startswith("wip:"):
            continue

        commits.append(
            {
                "sha": short,
                "sha_full": full,
                "subject": subject,
                "body": body.strip(),
            }
        )
    return commits


def get_commit_squash() -> Dict[str, Any]:
    """
    Retrieve the squash commit (subject + body).

    Each non-empty line in the body is treated as a commit message.
    Leading `*` or `-` characters are stripped to avoid double markers.
    """
    raw = subprocess.check_output(
        ["git", "log", "-1", "--pretty=format:%h|%H|%s|%b"], text=True
    ).strip()
    short, full, subject, body = raw.split("|", 3)

    commits: List[Dict[str, str]] = []
    for line in (line.strip() for line in body.splitlines()):
        if not line or line.lower().startswith("wip:"):
            continue

        # Normalize bullet points in squash body
        cleaned = re.sub(r"^[*-]\s*", "", line)

        commits.append({"subject": cleaned, "body": ""})

    return {"sha": short, "sha_full": full, "subject": subject, "commits": commits}


def group_commits(commits: List[Dict[str, str]]) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    """
    Group commits by type and scope based on conventional commit format.

    Example commit subject:
        feat(api): add new endpoint
    """
    grouped: Dict[str, Dict[str, List[Dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    pattern = re.compile(r"^(?P<type>\w+)(\((?P<scope>[^)]+)\))?:\s*(?P<desc>.+)$")

    for commit in commits:
        subject = commit["subject"]
        body = commit.get("body", "")

        match = pattern.match(subject)
        if match:
            commit_type = match.group("type")
            scope = match.group("scope") or "(no scope)"
            desc = match.group("desc").strip()
        else:
            commit_type = "other"
            scope = "(no scope)"
            desc = subject.strip()

        grouped[commit_type][scope].append(
            {
                "title": desc,
                "scope": scope,
                "body": body,
                "sha": commit.get("sha"),
                "sha_full": commit.get("sha_full"),
            }
        )
    return grouped


def render(
    template_path: str,
    version: str,
    commits: Dict[str, Dict[str, List[Dict[str, Any]]]],
    repo_url: str,
    squash: Dict[str, Any] | None,
    is_unreleased: bool,
) -> str:
    """Render the changelog using Jinja2 template."""
    env = Environment(
        loader=FileSystemLoader(Path(template_path).parent),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(Path(template_path).name)
    return template.render(
        version=version,
        commits=commits,
        repo_url=repo_url,
        squash=squash,
        is_unreleased=is_unreleased,
    )


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Generate changelog from conventional commits")
    parser.add_argument("--mode", required=True, choices=["pr", "release"], help="Mode of changelog generation")
    parser.add_argument("--branch", required=True, help="Branch name")
    parser.add_argument("--version", required=False, help="Release version or UNRELEASED")
    parser.add_argument("--template", default=DEFAULT_TEMPLATE, help="Path to Jinja2 template")
    parser.add_argument("--output", required=True, help="Output markdown file path")
    parser.add_argument("--repo-url", default=_default_repo_url(), help="Repository URL")
    args = parser.parse_args()

    is_unreleased = str(args.version).upper() == "UNRELEASED"

    if args.mode == "pr":
        commits = get_commits_pr(args.branch)
        grouped = group_commits(commits)
        title = args.version if not is_unreleased else f"Changelog preview for {args.branch}"
        md = render(args.template, title, grouped, args.repo_url, squash=None, is_unreleased=is_unreleased)
    else:  # release mode
        squash = get_commit_squash()
        grouped = group_commits(squash["commits"])
        title = args.version if not is_unreleased else squash["subject"]
        md = render(args.template, title, grouped, args.repo_url, squash=squash, is_unreleased=is_unreleased)

        changelog = Path("CHANGELOG.md")
        previous = changelog.read_text(encoding="utf-8") if changelog.exists() else ""
        changelog.write_text((md + "\n\n" + previous).rstrip() + "\n", encoding="utf-8")

    Path(args.output).write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
