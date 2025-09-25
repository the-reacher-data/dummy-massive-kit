from __future__ import annotations
import os, sys, tomllib
from datetime import datetime
from pathlib import Path
import shutil
from sphinx.util import logging

logger = logging.getLogger(__name__)

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


def on_build_finished(app, exception):
    build_static = os.path.join(app.outdir, "_static")
    if os.path.exists(build_static):
        for root, dirs, files in os.walk(build_static):
            for name in files:
                path = os.path.join(root, name)
                if os.path.islink(path):
                    target = os.readlink(path)
                    os.remove(path)
                    shutil.copy(target, path)
                    logger.info(f"Replaced symlink {path} with copy")

def setup(app):
    app.connect("build-finished", on_build_finished)
