import sys, pathlib, re

pr = sys.argv[1]
sha = sys.argv[2][:7]

p = pathlib.Path("pyproject.toml")
s = p.read_text(encoding="utf-8")

def repl(m):
    ver = m.group(1)
    suffix = f".devPR{pr}.sha{sha}"
    if ".dev" in ver:
        ver = re.sub(r"\.dev[^\"']*", suffix, ver)
    else:
        ver = ver + suffix
    print("New prerelease version:", ver)
    return f'version = "{ver}"'

s2 = re.sub(r'(?m)^\s*version\s*=\s*"([^"]+)"\s*$', repl, s)
p.write_text(s2, encoding="utf-8")
