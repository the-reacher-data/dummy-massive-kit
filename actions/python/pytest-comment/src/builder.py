#!/usr/bin/env python3
# type: ignore
"""
Genera el comentario de pytest en Markdown para GitHub Actions.

- Lee junit.xml (tests, fallos, skipped + mensajes)
- Lee coverage.json (cobertura global y por fichero + líneas ausentes)
- Renderiza una plantilla Jinja2 (pytest_comment.md.j2)
- --check-exit: sale con 1 si hay fallos o la cobertura global < threshold
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any

from jinja2 import Environment, FileSystemLoader

# ---------------------------
# Modelos
# ---------------------------


@dataclass
class FailedTest:
    nodeid: str
    message: str


@dataclass
class FileCoverage:
    path: str
    percent: float
    missing_lines: list[int]


# ---------------------------
# Parsing
# ---------------------------


def parse_junit(junit_path: str) -> dict[str, Any]:
    """Soporta junit con raíz <testsuites> o <testsuite>."""
    tree = ET.parse(junit_path)
    root = tree.getroot()

    # Normaliza a una lista de <testsuite>
    suites = _get_test_suites(root)

    test_stats, failed_tests = _parse_test_suites(suites)

    failed = test_stats["failures"] + test_stats["errors"]
    passed = test_stats["tests"] - failed - test_stats["skipped"]

    return {
        "tests": test_stats["tests"],
        "passed": max(passed, 0),
        "failed": failed,
        "skipped": test_stats["skipped"],
        "failures": failed_tests,
    }


def _get_test_suites(root: ET.Element) -> list[ET.Element]:
    """Extrae lista de suites desde la raíz del XML."""
    if root.tag == "testsuite":
        return [root]
    else:
        return list(root.findall("testsuite"))


def _parse_test_suites(suites: list[ET.Element]) -> tuple[dict[str, int], list[FailedTest]]:
    """Parsea estadísticas y testcases fallidos de todas las suites."""
    tests = failures = errors = skipped = 0
    failed_tests: list[FailedTest] = []

    for suite in suites:
        suite_stats = _parse_suite_stats(suite)
        tests += suite_stats["tests"]
        failures += suite_stats["failures"]
        errors += suite_stats["errors"]
        skipped += suite_stats["skipped"]

        suite_failures = _parse_suite_testcases(suite)
        failed_tests.extend(suite_failures)

    return {
        "tests": tests,
        "failures": failures,
        "errors": errors,
        "skipped": skipped,
    }, failed_tests


def _parse_suite_stats(suite: ET.Element) -> dict[str, int]:
    """Extrae estadísticas de una suite individual."""
    return {
        "tests": int(suite.attrib.get("tests", 0)),
        "failures": int(suite.attrib.get("failures", 0)),
        "errors": int(suite.attrib.get("errors", 0)),
        "skipped": int(suite.attrib.get("skipped", 0)),
    }


def _parse_suite_testcases(suite: ET.Element) -> list[FailedTest]:
    """Extrae testcases fallidos de una suite."""
    failed_tests: list[FailedTest] = []

    for case in suite.iter("testcase"):
        failures = _extract_test_failures(case)
        failed_tests.extend(failures)

    return failed_tests


def _extract_test_failures(case: ET.Element) -> list[FailedTest]:
    """Extrae fallos de un testcase individual."""
    failures: list[FailedTest] = []

    for node in list(case.findall("failure")) + list(case.findall("error")):
        file_ = case.attrib.get("file") or ""
        classname = case.attrib.get("classname") or ""
        name = case.attrib.get("name") or ""
        nodeid = f"{file_}::{name}" if file_ else f"{classname}::{name}"
        message = _extract_failure_message(node)

        failures.append(FailedTest(nodeid=nodeid, message=message))

    return failures


def _extract_failure_message(node: ET.Element) -> str:
    """Extrae el mensaje de error de un nodo de fallo."""
    message = (node.attrib.get("message") or "").strip()
    if not message and node.text:
        message = node.text.strip()
    return message


def parse_coverage_json(cov_json_path: str) -> tuple[float, list[FileCoverage]]:
    """Lee coverage.json de coverage.py (format v3)."""
    with open(cov_json_path, encoding="utf-8") as f:
        data = json.load(f)

    totals = data.get("totals", {})
    global_cov = float(totals.get("percent_covered", 0.0))

    files_cov: list[FileCoverage] = []
    for path, info in data.get("files", {}).items():
        summary = info.get("summary", {})
        pct = float(summary.get("percent_covered", 0.0))
        missing = info.get("missing_lines", []) or []
        files_cov.append(FileCoverage(path=path, percent=pct, missing_lines=missing))

    return round(global_cov, 2), files_cov


# ---------------------------
# Render
# ---------------------------


def render_report(
    junit_data: dict[str, Any],
    coverage: float,
    files_cov: list[FileCoverage],
    threshold: float,
) -> str:
    base_dir = os.path.dirname(__file__)
    template_dir = os.path.join(base_dir, "templates")
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    under_files = sorted(
        [fc for fc in files_cov if fc.percent < threshold], key=lambda fc: fc.percent
    )

    template = env.get_template("report.md.j2")
    return template.render(
        coverage=round(coverage, 2),
        threshold=float(threshold),
        under_files=under_files,
        failures=junit_data["failures"],  # lista[FailedTest]
        tests=junit_data["tests"],
        passed=junit_data["passed"],
        failed=junit_data["failed"],
        skipped=junit_data["skipped"],
    )


# ---------------------------
# Entradas/Salidas GH Actions
# ---------------------------


def write_outputs(outputs_path: str, coverage: float, failed: int) -> None:
    if not outputs_path:
        return
    with open(outputs_path, "a", encoding="utf-8") as f:
        f.write(f"coverage={coverage}\n")
        f.write(f"failed={failed}\n")


def main(
    junit_path: str, cov_json_path: str, threshold: float, output_path: str, outputs_path: str
) -> None:
    coverage, files_cov = parse_coverage_json(cov_json_path)
    junit_data = parse_junit(junit_path)

    body = render_report(junit_data, coverage, files_cov, threshold)

    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(body)

    write_outputs(outputs_path, coverage, junit_data["failed"])


def check_exit(junit_path: str, cov_json_path: str, threshold: float) -> None:
    coverage, _ = parse_coverage_json(cov_json_path)
    junit_data = parse_junit(junit_path)
    if junit_data["failed"] > 0 or coverage < float(threshold):
        sys.exit(1)


# ---------------------------
# CLI
# ---------------------------


def cli() -> None:
    parser = argparse.ArgumentParser(description="Build pytest markdown report for GitHub Actions.")
    parser.add_argument("--junit", required=True, help="Path to junit.xml")
    parser.add_argument("--cov", required=True, help="Path to coverage.json")
    parser.add_argument(
        "--threshold", type=float, required=True, help="Coverage threshold (e.g. 85)"
    )
    parser.add_argument("--output", help="Output markdown file (for PR comment)")
    parser.add_argument("--outputs", help="Path to GitHub outputs file")
    parser.add_argument(
        "--check-exit", action="store_true", help="Exit 1 if tests failed or coverage < threshold"
    )
    args = parser.parse_args()

    if args.check_exit:
        check_exit(args.junit, args.cov, args.threshold)
        return

    if not args.output or not args.outputs:
        parser.error("--output and --outputs are required unless --check-exit is set")

    main(args.junit, args.cov, args.threshold, args.output, args.outputs)


if __name__ == "__main__":
    cli()
