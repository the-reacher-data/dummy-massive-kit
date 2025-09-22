#!/usr/bin/env python3
# type: ignore
"""
Generate Bandit markdown report for GitHub Actions.

- Reads bandit.json (Bandit analysis results)
- Renders a Jinja2 template (bandit_report.md.j2)
- Writes GitHub Action outputs
- Supports --check-exit to exit with 1 if issues meet or exceed --fail-on severity
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass

from jinja2 import Environment, FileSystemLoader

# ---------------------------
# Data models
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


SEVERITY_ORDER = {"none": 0, "low": 1, "medium": 2, "high": 3}


# ---------------------------
# Parsing
# ---------------------------


def parse_bandit(bandit_path: str) -> list[BanditIssue]:
    """Parse bandit.json and return a list of BanditIssue objects."""
    with open(bandit_path, encoding="utf-8") as f:
        data = json.load(f)

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
    """Return True if any issue meets or exceeds the --fail-on severity."""
    threshold = SEVERITY_ORDER.get(fail_on.lower(), 0)
    if threshold == 0:  # "none"
        return False
    for i in issues:
        sev = i.severity.lower()
        if SEVERITY_ORDER.get(sev, 0) >= threshold:
            return True
    return False


# ---------------------------
# Render
# ---------------------------


def render_report(issues: list[BanditIssue]) -> str:
    """Render markdown report using Jinja2 template."""
    base_dir = os.path.dirname(__file__)
    template_dir = os.path.join(base_dir, "templates")
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("bandit_report.md.j2")
    return template.render(count=len(issues), issues=issues)


# ---------------------------
# Outputs
# ---------------------------


def write_outputs(outputs_path: str, issues: list[BanditIssue], exit_code: int) -> None:
    """Write GitHub Actions outputs (issue count and exit code)."""
    if not outputs_path:
        return
    with open(outputs_path, "a", encoding="utf-8") as f:
        f.write(f"bandit_issues={len(issues)}\n")
        f.write(f"bandit_exit={exit_code}\n")


# ---------------------------
# Main + CLI
# ---------------------------


def main(
    bandit_path: str,
    output_path: str,
    outputs_path: str,
    fail_on: str,
    check_exit: bool,
) -> None:
    """Main workflow: parse, render, write outputs, and handle exit codes."""
    issues = parse_bandit(bandit_path)
    body = render_report(issues)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(body)

    exit_code = 1 if filter_failures(issues, fail_on) else 0

    if outputs_path:
        write_outputs(outputs_path, issues, exit_code)

    if check_exit and exit_code != 0:
        print(f"❌ Bandit found issues >= {fail_on.upper()}")
        sys.exit(1)


def cli() -> None:
    """CLI entrypoint for GitHub Actions integration."""
    parser = argparse.ArgumentParser(description="Build Bandit markdown report for GitHub Actions.")
    parser.add_argument("--bandit", required=True, help="Path to bandit.json")
    parser.add_argument("--output", help="Output markdown file (for PR comment)")
    parser.add_argument("--outputs", help="Path to GitHub outputs file")
    parser.add_argument(
        "--fail-on", default="none", help="Severity level to fail on (none, low, medium, high)"
    )
    parser.add_argument(
        "--check-exit", action="store_true", help="Exit 1 if issues >= fail-on severity"
    )
    args = parser.parse_args()

    main(args.bandit, args.output, args.outputs, args.fail_on, args.check_exit)


if __name__ == "__main__":
    cli()
