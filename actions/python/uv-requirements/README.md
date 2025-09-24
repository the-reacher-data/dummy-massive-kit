# UV Requirements Action

Installs Python dependencies from a `requirements.txt` using [uv](https://github.com/astral-sh/uv).

👉 This action **does not run `checkout` or `setup-python` / `setup-uv`**.  
Make sure your workflow sets up Python and uv before using it.

## Usage

```yaml
jobs:
  deps:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - uses: astral-sh/setup-uv@v3

      - uses: ./actions/devops/uv-requirements
        with:
          requirements: ./actions/devops/versioning-branch-semantic/requirements.txt
```

## Inputs

| Name          | Required | Description                                           |
|---------------|----------|-------------------------------------------------------|
| requirements  | ✅       | Path to `requirements.txt` file with the dependencies |

## Notes

- Designed to be minimal and reusable across all your DevOps actions.  
- Each action can maintain its own `requirements.txt` to grow independently.  
- Keeps environment setup (`checkout`, `setup-python`, `setup-uv`) at the workflow level for speed and consistency.

