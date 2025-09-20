# type: ignore

import argparse
import json
import pathlib
import sys

from jinja2 import Environment, FileSystemLoader

SEVERITY_ORDER = {"low": 1, "medium": 2, "high": 3}


def load_bandit(path: str):
    data = json.loads(pathlib.Path(path).read_text())
    return data.get("results", [])


def filter_failures(issues, fail_on: str):
    """Return True if any issue meets or exceeds fail_on severity."""
    if fail_on == "none":
        return False
    threshold = SEVERITY_ORDER[fail_on]
    for i in issues:
        sev = i.get("issue_severity", "low").lower()
        if SEVERITY_ORDER.get(sev, 0) >= threshold:
            return True
    return False


def render(issues, template_dir, template_name, output):
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    tmpl = env.get_template(template_name)
    markdown = tmpl.render(count=len(issues), issues=issues)
    pathlib.Path(output).write_text(markdown)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="bandit.json")
    parser.add_argument("--template", required=True)
    parser.add_argument("--output", default="security_comment.md")
    parser.add_argument("--fail-on", default="none")
    args = parser.parse_args()

    issues = load_bandit(args.input)
    render(
        issues, pathlib.Path(args.template).parent, pathlib.Path(args.template).name, args.output
    )

    # If severity threshold met, exit with 1
    if filter_failures(issues, args.fail_on):
        print(f"❌ Bandit found issues >= {args.fail_on}")
        sys.exit(1)


if __name__ == "__main__":
    main()
