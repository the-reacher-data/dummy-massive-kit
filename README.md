# MassiveKit 🚀

[![CI](https://github.com/the-reacher-data/dummy-massive-kit/actions/workflows/devops-demo.yaml/badge.svg)](https://github.com/the-reacher-data//dummy-massive-kit/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/massivedatascope/dummy-massive-kit/branch/main/graph/badge.svg)](https://codecov.io/gh/dummy-massive-kit/massivekit)
[![PyPI](https://img.shields.io/pypi/v/dummy-massive-kit.svg)](https://pypi.org/project/dummy-massive-kit/)
[![Python Versions](https://img.shields.io/pypi/pyversions/dummy-massive-kit.svg)](https://pypi.org/project/massivekit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Lint: ruff](https://img.shields.io/badge/lint-ruff-46aef7.svg)](https://github.com/astral-sh/ruff)

---

**MassiveKit** is a modern, declarative framework for building **APIs** and **CLI tools**, designed with **Clean Code** and **SOLID** principles.

---

## ✨ Features (current focus)

- **API Framework** (based on FastAPI)
  - Declarative controllers, services, repositories, validators, orchestrators.
  - Project scaffolding from OpenAPI specs.
- **CLI** (`massivekit`)
  - `massivekit start-project` → bootstrap new projects.
  - `massivekit list` → explore available repositories/validators.

---

## 🚀 Installation

```bash
# Install core + dev tools
uv sync --extra dev

# Add API support
uv sync --extra api

# Add CLI
uv sync --extra cli
```

Or directly with pip:

```bash
pip install "massivekit[api,cli]"
```
