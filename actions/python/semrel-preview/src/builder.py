#!/usr/bin/env python3
# type: ignore
"""
Format semantic-release changelog preview into an enterprise PR comment.
"""

import argparse
import pathlib
from jinja2 import Environment, FileSystemLoader


def load_file(path: str) -> str:
    p = pathlib.Path(path)
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8").strip()


def render(changelog: str, version: str, template: str, output: str) -> None:
    env = Environment(
        loader=FileSystemLoader(str(pathlib.Path(template).parent)),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    t = env.get_template(pathlib.Path(template).name)
    markdown = t.render(changelog=changelog, version=version)
    pathlib.Path(output).write_text(markdown, encoding="utf-8")


def cli():
    parser = argparse.ArgumentParser(description="Build semantic-release changelog preview.")
    parser.add_argument("--input", required=True, help="Path to raw changelog.md")
    parser.add_argument("--template", required=True, help="Path to Jinja2 template")
    parser.add_argument("--output", required=True, help="Markdown output file")
    parser.add_argument("--version-file", help="File with next version (from semantic-release)")
    args = parser.parse_args()

    changelog = load_file(args.input)
    version = load_file(args.version_file) if args.version_file else ""

    render(changelog, version, args.template, args.output)


if __name__ == "__main__":
    cli()
