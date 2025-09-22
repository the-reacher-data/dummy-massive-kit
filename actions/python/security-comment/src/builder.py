#!/usr/bin/env python3
# type: ignore
"""
Generate Bandit markdown report for GitHub Actions.

- Reads bandit.json (Bandit analysis results)
- Renders a Jinja2 template provided via --template
- Writes outputs for GitHub Actions
- Supports --fail-on to decide when to exit 1
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from dataclasses import dataclass

from jinja2 import Environment, FileSystemLoader

# ---------------------------
# Models
# ---------------------------


@dataclass
class BanditIssue:
    filename: str
    line_number: int
    severity: str
    confidence: str
    test_id: str
    test_name: str
    issue_text: str


# Severity ranking for threshold
SEVERITY_ORDER = {"none": 0, "low": 1, "medium": 2, "high": 3}


# ---------------------------
# Parsing
# ---------------------------


def load_bandit(path: str) -> list[BanditIssue]:
    """Load bandit.json and return list of issues."""
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    issues: list[BanditIssue] = []
    for i in data.get("results", []):
        issues.append(
            BanditIssue(
                filename=i.get("filename", ""),
                line_number=i.get("line_number", 0),
                severity=i.get("issue_severity", "LOW"),
                confidence=i.get("issue_confidence", "LOW"),
                test_id=i.get("test_id", ""),
                test_name=i.get("test_name", ""),
                issue_text=i.get("issue_text", "").strip(),
            )
        )
    return issues


def filter_failures(issues: list[BanditIssue], fail_on: str) -> bool:
    """Return True if any issue meets or exceeds the fail_on severity."""
    threshold = SEVERITY_ORDER.get(fail_on.lower(), 0)
    if threshold == 0:
        return False
    for i in issues:
        if SEVERITY_ORDER.get(i.severity.lower(), 0) >= threshold:
            return True
    return False


# ---------------------------
# Rendering
# ---------------------------


def render(issues: list[BanditIssue], template_path: str, output: str) -> None:
    """Render report from template and write markdown file."""
    env = Environment(
        loader=FileSystemLoader(str(pathlib.Path(template_path).parent)),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(pathlib.Path(template_path).name)
    markdown = template.render(count=len(issues), issues=issues)
    pathlib.Path(output).write_text(markdown, encoding="utf-8")


# ---------------------------
# Outputs
# ---------------------------


def write_outputs(outputs_path: str | None, issues: list[BanditIssue], exit_code: int) -> None:
    """Write GitHub Action outputs."""
    if not outputs_path:
        return
    with open(outputs_path, "a", encoding="utf-8") as f:
        f.write(f"bandit_issues={len(issues)}\n")
        f.write(f"bandit_exit={exit_code}\n")


# ---------------------------
# CLI
# ---------------------------


def cli() -> None:
    parser = argparse.ArgumentParser(description="Build Bandit markdown report for GitHub Actions.")
    parser.add_argument("--input", default="bandit.json", help="Bandit JSON input file")
    parser.add_argument("--template", required=True, help="Path to Jinja2 template")
    parser.add_argument("--output", default="security_comment.md", help="Markdown output file")
    parser.add_argument("--outputs", help="Path to GitHub outputs file")
    parser.add_argument(
        "--fail-on",
        default="none",
        choices=["none", "low", "medium", "high"],
        help="Severity level to fail on",
    )
    args = parser.parse_args()

    issues = load_bandit(args.input)
    render(issues, args.template, args.output)

    exit_code = 1 if filter_failures(issues, args.fail_on) else 0
    write_outputs(args.outputs, issues, exit_code)

    if exit_code != 0:
        print(f"❌ Bandit found issues >= {args.fail_on.upper()}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
