#!/usr/bin/env python3
# type: ignore
"""
Generate Ruff + MyPy markdown report for GitHub Actions.

- Default mode: parse ruff.json + mypy.txt, render Jinja2 template, write outputs.
- --check-exit mode: only evaluate thresholds (--fail-on) and exit accordingly.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

from jinja2 import Environment, FileSystemLoader

# ---------------------------
# Parsing
# ---------------------------


def load_ruff(path: str) -> list[dict]:
    """Load Ruff JSON results (list of issues)."""
    if not path or not pathlib.Path(path).exists():
        return []
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def load_mypy(path: str) -> list[str]:
    """Load MyPy text output (list of lines)."""
    if not path or not pathlib.Path(path).exists():
        return []
    return pathlib.Path(path).read_text(encoding="utf-8").splitlines()


# ---------------------------
# Status message
# ---------------------------


def build_status_message(ruff: list[dict], mypy: list[str], fail_on: str) -> str:
    """Return a global status message with emoji."""
    total = len(ruff) + len(mypy)
    if total == 0:
        return "✅ No lint/type issues found"

    if fail_on == "none":
        return f"⚠️ Found {len(ruff)} Ruff and {len(mypy)} MyPy issues, but allowed (fail-on=none)"

    return f"❌ Found {len(ruff)} Ruff and {len(mypy)} MyPy issues (blocking)"


# ---------------------------
# Rendering
# ---------------------------


def render(ruff: list[dict], mypy: list[str], template: str, output: str, status_msg: str) -> None:
    """Render report using Jinja2 template and write to output file."""
    tmpl_path = pathlib.Path(template)
    env = Environment(
        loader=FileSystemLoader(str(tmpl_path.parent)),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    t = env.get_template(tmpl_path.name)
    markdown = t.render(
        ruff=ruff,
        mypy=mypy,
        status_msg=status_msg,
        ruff_count=len(ruff),
        mypy_count=len(mypy),
    )
    pathlib.Path(output).write_text(markdown, encoding="utf-8")


# ---------------------------
# Outputs
# ---------------------------


def write_outputs(outputs_path: str | None, ruff: list[dict], mypy: list[str]) -> None:
    """Write GitHub Action outputs."""
    if not outputs_path:
        return
    with open(outputs_path, "a", encoding="utf-8") as f:
        f.write(f"ruff_issues={len(ruff)}\n")
        f.write(f"mypy_issues={len(mypy)}\n")


# ---------------------------
# CLI
# ---------------------------


def cli() -> None:
    parser = argparse.ArgumentParser(
        description="Build Ruff+MyPy markdown report for GitHub Actions."
    )
    parser.add_argument("--ruff", help="Path to Ruff JSON output")
    parser.add_argument("--mypy", help="Path to MyPy text output")
    parser.add_argument("--template", help="Path to Jinja2 template (report.md.j2)")
    parser.add_argument("--output", default="lint_report.md", help="Markdown output file")
    parser.add_argument("--outputs", help="Path to GitHub outputs file")
    parser.add_argument("--fail-on", default="any", choices=["none", "any"], help="When to fail")
    parser.add_argument(
        "--check-exit", action="store_true", help="Only evaluate fail/pass and exit"
    )
    args = parser.parse_args()

    ruff_issues = load_ruff(args.ruff)
    mypy_issues = load_mypy(args.mypy)

    if args.check - exit:
        if args.fail_on == "any" and (ruff_issues or mypy_issues):
            sys.exit(1)
        sys.exit(0)

    if not args.template:
        parser.error("--template is required unless --check-exit is set")

    status_msg = build_status_message(ruff_issues, mypy_issues, args.fail_on)
    render(ruff_issues, mypy_issues, args.template, args.output, status_msg)
    write_outputs(args.outputs, ruff_issues, mypy_issues)


if __name__ == "__main__":
    cli()
