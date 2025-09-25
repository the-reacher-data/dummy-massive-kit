from __future__ import annotations
import os, sys, tomllib
from datetime import datetime
from pathlib import Path

# --- Path setup (src/ layout) ---
sys.path.insert(0, os.path.abspath(os.path.join("..", "src/mkit")))

# --- Read pyproject.toml ---
pyproject = Path(__file__).parent.parent / "pyproject.toml"
with pyproject.open("rb") as f:
    data = tomllib.load(f)

proj = data.get("project", {})

# --- Project info ---
project = proj.get("name", "Unknown Project")
author = ", ".join(a.get("name", "") for a in proj.get("authors", []))
copyright = f"{datetime.now().year}, {author}"
release = proj.get("version", "0.0.0")

# --- Extensions ---
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "myst_parser",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

html_theme = "furo"

autodoc_typehints = "description"
add_module_names = False 
