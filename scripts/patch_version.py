import pathlib
import re
import sys
from re import Match

pr: str = sys.argv[1]
sha: str = sys.argv[2][:7]

p: pathlib.Path = pathlib.Path("pyproject.toml")
s: str = p.read_text(encoding="utf-8")


def repl(m: Match[str]) -> str:
    """Replace version string with prerelease version."""
    ver: str = m.group(1)
    suffix: str = f".devPR{pr}.sha{sha}"
    if ".dev" in ver:
        ver = re.sub(r"\.dev[^\"']*", suffix, ver)
    else:
        ver = ver + suffix
    print("New prerelease version:", ver)
    return f'version = "{ver}"'


s2: str = re.sub(r'(?m)^\s*version\s*=\s*"([^"]+)"\s*$', repl, s)
p.write_text(s2, encoding="utf-8")
