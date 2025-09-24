from __future__ import annotations

import argparse
import json
import pathlib
import sys
from dataclasses import dataclass

from jinja2 import Environment, FileSystemLoader

# Severity ranking for thresholds
SEVERITY_ORDER = {"none": 0, "low": 1, "medium": 2, "high": 3}


@dataclass
class BanditIssue:
    filename: str
    line_number: int
    severity: str
    confidence: str
    test_id: str
    test_name: str
    issue_text: str


# ---------------------------
# Parsing
# ---------------------------


def load_bandit(path: str) -> list[BanditIssue]:
    """Load bandit.json and return list of BanditIssue objects."""
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    issues: list[BanditIssue] = []
    for i in data.get("results", []):
        issues.append(
            BanditIssue(
                filename=i.get("filename", ""),
                line_number=int(i.get("line_number", 0) or 0),
                severity=str(i.get("issue_severity", "LOW")),
                confidence=str(i.get("issue_confidence", "LOW")),
                test_id=i.get("test_id", ""),
                test_name=i.get("test_name", ""),
                issue_text=(i.get("issue_text", "") or "").strip(),
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

def build_status_message(issues: list[BanditIssue], fail_on: str) -> str:
    """Return a human-readable status message for the PR comment."""
    total = len(issues)
    if total == 0:
        return "✅ No Bandit issues found"

    blocking = filter_failures(issues, fail_on)
    if blocking:
        return f"❌ Found {total} Bandit issues, including issues >= {fail_on.upper()} (blocking)"
    else:
        return f"⚠️ Found {total} Bandit issues, but all are below the '{fail_on.upper()}' threshold"

# ---------------------------
# Rendering
# ---------------------------


def render(issues: list[BanditIssue], template_path: str, output: str, status_msg: str) -> None:
    """Render report from Jinja2 template and write markdown file."""
    tmpl_path = pathlib.Path(template_path)
    env = Environment(
        loader=FileSystemLoader(str(tmpl_path.parent)),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(tmpl_path.name)
    markdown = template.render(count=len(issues), issues=issues, status_msg=status_msg)
    pathlib.Path(output).write_text(markdown, encoding="utf-8")


# ---------------------------
# Outputs
# ---------------------------


def write_outputs(outputs_path: str | None, issues: list[BanditIssue]) -> None:
    """Write GitHub Actions outputs (issue count)."""
    if not outputs_path:
        return
    with open(outputs_path, "a", encoding="utf-8") as f:
        f.write(f"bandit_issues={len(issues)}\n")


# ---------------------------
# CLI
# ---------------------------


def cli() -> None:
    parser = argparse.ArgumentParser(description="Build Bandit markdown report for GitHub Actions.")
    parser.add_argument("--input", default="bandit.json", help="Bandit JSON input file")
    parser.add_argument("--template", help="Path to Jinja2 template")
    parser.add_argument("--output", default="bandit_report.md", help="Markdown output file")
    parser.add_argument("--outputs", help="Path to GitHub outputs file")
    parser.add_argument(
        "--fail-on",
        default="none",
        choices=["none", "low", "medium", "high"],
        help="Severity level to fail on",
    )
    parser.add_argument(
        "--check-exit",
        action="store_true",
        help="Exit 1 if issues >= fail-on (no rendering, no outputs).",
    )
    args = parser.parse_args()

    issues = load_bandit(args.input)

    if args.check_exit:
        # Only threshold evaluation
        if filter_failures(issues, args.fail_on):
            print(f"❌ Bandit found issues >= {args.fail_on.upper()}")
            sys.exit(1)
        sys.exit(0)

    # Default: render report + write outputs
    if not args.template:
        parser.error("--template is required unless --check-exit is set")
    status_msg = build_status_message(issues, args.fail_on)
    render(issues, args.template, args.output, status_msg)
    write_outputs(args.outputs, issues)


if __name__ == "__main__":
    cli()
