# type: ignore

import json
import pathlib
import xml.etree.ElementTree as ET

import jinja2


def parse_junit(path: str) -> tuple[int, int, int, int, list[dict[str, str]]]:
    """Parse JUnit XML and return counts and failed test details."""
    root = ET.parse(path).getroot()
    passed = failed = skipped = total = 0
    failures = []

    for tc in root.iter("testcase"):
        total += 1
        name = tc.get("name", "")
        classname = tc.get("classname", "").replace("_", ".")
        nodeid = f"{classname}.{name}"

        if tc.find("failure") is not None or tc.find("error") is not None:
            failed += 1
            msg = (tc.find("failure") or tc.find("error")).get("message", "")
            failures.append({"nodeid": nodeid, "message": msg.split("\n")[0]})
        elif tc.find("skipped") is not None:
            skipped += 1
        else:
            passed += 1

    return passed, failed, skipped, total, failures


def parse_coverage(path: str, threshold: int) -> tuple[int, list[tuple[str, int]]]:
    """Parse coverage JSON and return percent + files under threshold."""
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    percent = int(data["totals"]["percent_covered"])
    under_files = [
        (f, int(info["summary"]["percent_covered"]))
        for f, info in data["files"].items()
        if int(info["summary"]["percent_covered"]) < threshold
    ]
    return percent, sorted(under_files, key=lambda x: x[1])


def render(template_path: str, context: dict) -> str:
    """Render Jinja2 template."""
    template_dir = pathlib.Path(template_path).parent
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
    template = env.get_template(pathlib.Path(template_path).name)
    return template.render(**context)
