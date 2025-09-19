"""
Massive DevOps - Pytest Comment Builder

Responsibility:
- Parse JUnit XML and coverage JSON
- Build an enterprise-style HTML comment with logo, badges and details
- Emit outputs (coverage, failed tests)
"""

# mypy: ignore-errors
# ruff: noqa

from __future__ import annotations

import html
import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path

# External logo
PYTEST_LOGO_URL = "https://docs.pytest.org/en/latest/_static/pytest1.png"


def parse_junit(path: str) -> tuple[int, int, int, int, list[dict[str, str]]]:
    """Parse JUnit XML and return counts and failed test details."""
    root = ET.parse(path).getroot()
    passed = failed = skipped = total = 0
    failures: list[dict[str, str]] = []

    for tc in root.iter("testcase"):
        total += 1
        classname = tc.get("classname", "")
        name = tc.get("name", "")
        nodeid = f"{classname}.{name}".strip(".")

        if tc.find("failure") is not None or tc.find("error") is not None:
            failed += 1
            el = tc.find("failure") or tc.find("error")
            msg = el.get("message", "").splitlines()[0] if el else ""
            failures.append({"nodeid": nodeid, "message": msg})
        elif tc.find("skipped") is not None:
            skipped += 1
        else:
            passed += 1

    return passed, failed, skipped, total, failures


def parse_coverage_json(path: str) -> tuple[int, list[tuple[str, int]]]:
    """Parse coverage.json and return global % and per-file %."""
    data = json.loads(Path(path).read_text())
    total_pct = int(round(float(data.get("totals", {}).get("percent_covered", 0.0))))

    file_pcts: list[tuple[str, int]] = []
    for file, info in data.get("files", {}).items():
        pct = int(round(float(info.get("summary", {}).get("percent_covered", 0.0))))
        file_pcts.append((file, pct))

    return total_pct, file_pcts


def coverage_badge(coverage: int) -> str:
    """Return shields.io badge URL depending on coverage %."""
    if coverage >= 90:
        color = "brightgreen"
    elif coverage >= 75:
        color = "yellow"
    else:
        color = "red"
    return f"https://img.shields.io/badge/coverage-{coverage}%25-{color}"


def build_comment_html(
    passed: int,
    failed: int,
    skipped: int,
    total: int,
    coverage_pct: int,
    under_files: list[tuple[str, int]],
    threshold: int,
) -> str:
    """Build HTML comment body."""
    logo = f'<img src="{PYTEST_LOGO_URL}" width="50" style="vertical-align:middle;"/>'
    badge = f'<img src="{coverage_badge(coverage_pct)}" style="vertical-align:middle;"/>'
    summary = (
        f"✅ <b>{passed}</b> passed ❌ <b>{failed}</b> failed "
        f"⏭ <b>{skipped}</b> skipped — <b>{total}</b> total"
    )

    under_section = ""
    if under_files:
        rows = "\n".join(
            f"| `{html.escape(path)}` | {pct}% |"
            for path, pct in sorted(under_files, key=lambda x: x[1])[:20]
        )
        more = "" if len(under_files) <= 20 else f"\n… and {len(under_files)-20} more"
        under_section = f"""
<details>
<summary>⚠ Files under {threshold}% coverage ({len(under_files)})</summary>

| File | Coverage |
|------|----------|
{rows}
{more}
</details>
"""

    return f"""## {logo} Pytest Report

{badge}
{summary}

{under_section}
""".strip()


def main(
    junit_path: str,
    cov_json_path: str,
    threshold: int,
    output_path: str,
    outputs_path: str,
) -> None:
    """Main entry: parse, build, write HTML and outputs."""
    passed, failed, skipped, total, _ = parse_junit(junit_path)
    total_pct, file_pcts = parse_coverage_json(cov_json_path)
    under = [(f, pct) for f, pct in file_pcts if pct < threshold]

    html = build_comment_html(passed, failed, skipped, total, total_pct, under, threshold)
    Path(output_path).write_text(html, encoding="utf-8")

    with open(outputs_path, "a", encoding="utf-8") as f:
        f.write(f"coverage={total_pct}\n")
        f.write(f"failed={failed}\n")
