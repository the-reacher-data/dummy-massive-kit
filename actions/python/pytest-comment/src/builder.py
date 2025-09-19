#!/usr/bin/env python3
# type: ignore
"""
Builder script for pytest report comments in GitHub Actions.

- Parses pytest junit.xml results
- Parses coverage.json results
- Renders a Markdown report via Jinja2 template
- Exits with code 1 if tests failed or coverage is below threshold (when --check-exit is used)
"""

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET
from typing import Any

from jinja2 import Environment, FileSystemLoader

# -----------------------------
# Helpers for parsing test results and coverage
# -----------------------------


def parse_coverage(path: str) -> tuple[float, list[tuple[str, float]]]:
    """Parse coverage.json and return global coverage and per-file coverages."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    totals = data.get("totals", {})
    global_cov = round(totals.get("percent_covered", 0.0), 2)

    files = []
    for file, info in data.get("files", {}).items():
        pct = round(info["summary"]["percent_covered"], 2)
        files.append((file, pct))

    return global_cov, files


def parse_junit(path: str) -> dict[str, Any]:
    """Parse junit.xml and return tests summary and failed tests details."""
    tree = ET.parse(path)
    root = tree.getroot()

    tests = int(root.attrib.get("tests", 0))
    failures = int(root.attrib.get("failures", 0))
    errors = int(root.attrib.get("errors", 0))
    skipped = int(root.attrib.get("skipped", 0))

    failed = failures + errors
    passed = tests - failed - skipped

    failed_tests = []
    for case in root.iter("testcase"):
        for fail in case.findall("failure") + case.findall("error"):
            nodeid = f"{case.attrib.get('classname', '')}::{case.attrib.get('name', '')}"
            message = fail.attrib.get("message", "").strip() or (
                fail.text.strip() if fail.text else ""
            )
            failed_tests.append({"nodeid": nodeid, "message": message})

    return {
        "tests": tests,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "failures": failed_tests,
    }


# -----------------------------
# Core functionality
# -----------------------------


def render_report(
    junit_data: dict[str, Any],
    coverage: float,
    file_cov: list[tuple[str, float]],
    threshold: int,
) -> str:
    """Render the markdown report using Jinja2 template."""
    under_files = [(f, pct) for f, pct in file_cov if pct < threshold]

    base_dir = os.path.dirname(__file__)
    template_dir = os.path.join(base_dir, "templates")

    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("report.md.j2")

    return template.render(
        coverage=coverage,
        threshold=threshold,
        under_files=under_files,
        **junit_data,
    )


def main(
    junit_path: str, cov_json_path: str, threshold: int, output_path: str, outputs_path: str
) -> None:
    """Generate the comment and write GitHub outputs."""
    coverage, file_cov = parse_coverage(cov_json_path)
    junit_data = parse_junit(junit_path)

    body = render_report(junit_data, coverage, file_cov, threshold)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(body)

    # Export outputs for GitHub Actions
    if outputs_path:
        with open(outputs_path, "a", encoding="utf-8") as f:
            f.write(f"coverage={coverage}\n")
            f.write(f"failed={junit_data['failed']}\n")


def check_exit(junit_path: str, cov_json_path: str, threshold: int) -> None:
    """Exit with code 1 if coverage is below threshold or tests failed."""
    coverage, _ = parse_coverage(cov_json_path)
    junit_data = parse_junit(junit_path)

    if junit_data["failed"] > 0 or coverage < threshold:
        sys.exit(1)


# -----------------------------
# CLI
# -----------------------------


def cli() -> None:
    parser = argparse.ArgumentParser(description="Build pytest markdown report for GitHub Actions.")
    parser.add_argument("--junit", required=True, help="Path to junit.xml")
    parser.add_argument("--cov", required=True, help="Path to coverage.json")
    parser.add_argument("--threshold", type=int, required=True, help="Coverage threshold")
    parser.add_argument("--output", help="Output markdown file (for PR comment)")
    parser.add_argument("--outputs", help="Path to GitHub outputs file")
    parser.add_argument(
        "--check-exit",
        action="store_true",
        help="Exit with 1 if tests failed or coverage < threshold",
    )

    args = parser.parse_args()

    if args.check_exit:
        check_exit(args.junit, args.cov, args.threshold)
    else:
        if not args.output or not args.outputs:
            parser.error("--output and --outputs are required unless --check-exit is set")
        main(args.junit, args.cov, args.threshold, args.output, args.outputs)


if __name__ == "__main__":
    cli()
