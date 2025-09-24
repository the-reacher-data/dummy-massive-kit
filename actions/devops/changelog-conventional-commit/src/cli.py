# type: ignore
"""
CLI to generate changelog from conventional commits.

Modes:
- pr: collect commits from PR branch (with SHA + link per commit)
- release: use squash commit body (one global SHA + list of messages, no per-commit SHAs)

Features:
- Group by type (feat, fix, docs, style, refactor, perf, test, chore, other)
- Sub-group by scope; "(no scope)" if absent
- SHA reference and GitHub links in PR mode
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from jinja2 import Environment, FileSystemLoader

HERE = Path(__file__).parent
DEFAULT_TEMPLATE = str(HERE / "templates" / "report.md.j2")


def _default_repo_url() -> str:
    """Build repo URL from GITHUB envs to avoid literal ${{ github.repository }} in output."""
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com").rstrip("/")
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip("/")
    return f"{server}/{repo}" if repo else server


def get_commits_pr(branch: str) -> List[dict]:
    """Get commits for a PR branch compared to origin/main."""
    base = subprocess.check_output(
        ["git", "merge-base", branch, "origin/main"], text=True
    ).strip()
    raw = subprocess.check_output(
        ["git", "log", f"{base}..HEAD", "--pretty=format:%h|%H|%s|%b---END---"],
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


def get_commit_squash() -> dict:
    """Get the squash commit (subject + body)."""
    raw = subprocess.check_output(
        ["git", "log", "-1", "--pretty=format:%h|%H|%s|%b"], text=True
    ).strip()
    short, full, subject, body = raw.split("|", 3)
    commits = []
    for line in (l.strip() for l in body.splitlines()):
        if not line or line.lower().startswith("wip:"):
            continue
        # Treat each non-empty line as a subject; body omitted in squash items.
        commits.append({"subject": line, "body": ""})
    return {"sha": short, "sha_full": full, "subject": subject, "commits": commits}


def group_commits(commits: List[dict]) -> Dict[str, Dict[str, List[dict]]]:
    """Group commits by type and scope."""
    grouped: Dict[str, Dict[str, List[dict]]] = defaultdict(lambda: defaultdict(list))
    rx = re.compile(r"^(?P<type>\w+)(\((?P<scope>[^)]+)\))?:\s*(?P<desc>.+)$")

    for c in commits:
        subject = c["subject"]
        body = c.get("body", "")
        m = rx.match(subject)
        if m:
            typ = m.group("type")
            scope = m.group("scope") or "(no scope)"
            desc = m.group("desc").strip()
        else:
            typ = "other"
            scope = "(no scope)"
            desc = subject.strip()

        grouped[typ][scope].append(
            {
                "title": desc,
                "scope": scope,
                "body": body,
                "sha": c.get("sha"),
                "sha_full": c.get("sha_full"),
            }
        )
    return grouped


def render(template_path: str, version: str, commits, repo_url: str, squash: dict | None, is_unreleased: bool) -> str:
    env = Environment(
        loader=FileSystemLoader(Path(template_path).parent),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    tmpl = env.get_template(Path(template_path).name)
    return tmpl.render(version=version, commits=commits, repo_url=repo_url, squash=squash, is_unreleased=is_unreleased)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", required=True, choices=["pr", "release"])
    p.add_argument("--branch", required=True)
    p.add_argument("--version", required=False)
    p.add_argument("--template", default=DEFAULT_TEMPLATE)
    p.add_argument("--output", required=True)
    p.add_argument("--repo-url", default=_default_repo_url())
    args = p.parse_args()

    is_unreleased = str(args.version).upper() == "UNRELEASED" 
    if args.mode == "pr":
        commits = get_commits_pr(args.branch)
        grouped = group_commits(commits)
        title = args.version if not is_unreleased else f"Changelog preview for {args.branch}"
        md = render(args.template, title, grouped, args.repo_url, squash=None, is_unreleased=is_unreleased)
    else:
        squash = get_commit_squash()
        grouped = group_commits(squash["commits"])
        title = args.version if not is_unreleased else squash["subject"]
        md = render(args.template, title, grouped, args.repo_url, squash=squash, is_unreleased=is_unreleased)

        # Update CHANGELOG.md in release mode
        changelog = Path("CHANGELOG.md")
        previous = changelog.read_text(encoding="utf-8") if changelog.exists() else ""
        changelog.write_text((md + "\n\n" + previous).rstrip() + "\n", encoding="utf-8")

    Path(args.output).write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
