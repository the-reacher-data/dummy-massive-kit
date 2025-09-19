# type: ignore
import json
import sys
import xml.etree.ElementTree as ET

from jinja2 import Environment, FileSystemLoader


def parse_coverage(path: str):
    with open(path) as f:
        data = json.load(f)

    totals = data["totals"]
    global_cov = round(totals["percent_covered"], 2)

    files = []
    for file, info in data["files"].items():
        pct = round(info["summary"]["percent_covered"], 2)
        files.append((file, pct))

    return global_cov, files


def parse_junit(path: str):
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
            failed_tests.append(
                {
                    "nodeid": case.attrib.get("classname", "") + "::" + case.attrib.get("name", ""),
                    "message": fail.attrib.get("message", "").strip() or fail.text.strip()
                    if fail.text
                    else "",
                }
            )

    return {
        "tests": tests,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "failures": failed_tests,
    }


def main(junit_path, cov_json_path, threshold, output_path, outputs_path):
    coverage, file_cov = parse_coverage(cov_json_path)
    junit_data = parse_junit(junit_path)

    under_files = [(f, pct) for f, pct in file_cov if pct < threshold]

    env = Environment(loader=FileSystemLoader("src/templates"))
    template = env.get_template("pytest_comment.md.j2")

    body = template.render(
        coverage=coverage, threshold=threshold, under_files=under_files, **junit_data
    )

    with open(output_path, "w") as f:
        f.write(body)

    # Set GitHub outputs
    with open(outputs_path, "a") as f:
        f.write(f"coverage={coverage}\n")
        f.write(f"failed={junit_data['failed']}\n")


def check_exit(junit_path, cov_json_path, threshold):
    coverage, file_cov = parse_coverage(cov_json_path)
    junit_data = parse_junit(junit_path)

    if junit_data["failed"] > 0 or coverage < threshold:
        sys.exit(1)
