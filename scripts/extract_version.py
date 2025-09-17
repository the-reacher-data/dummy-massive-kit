import re
import sys
from pathlib import Path

pyproject = Path("pyproject.toml")
content = pyproject.read_text('utf-8')

match = re.search(r'version\s*=\s*"([^"]+)"', content)
if not match:
    sys.exit(1)

print(match.group(1))
