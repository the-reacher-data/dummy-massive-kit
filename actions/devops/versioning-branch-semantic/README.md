# Versioning Branch Semantic Action

Calculates the next version number based on the branch name and rules defined in a TOML config file (by default `pyproject.toml`).

Supports both **release** and **pre-release** modes, and can decide automatically if a deploy should be triggered.

---

## Configuration (`pyproject.toml` or custom TOML)

Example configuration:

```toml
[tool.semantic-branch]
release = ["main", "master"]     # branches that trigger final releases
prerelease = ["develop", "hotfix/.*", "feature/.*"]  # branches that trigger prereleases (.devN)
patch = ["hotfix/.*"]            # bump patch version
minor = ["feature/.*"]           # bump minor version
major = ["breaking/.*"]          # bump major version
prerelease-ignore = ["docs/.*"]  # branches ignored for prerelease
release-ignore = ["wip/.*"]      # branches ignored for release
```
## Inputs

| Name         | Required | Default          | Description                                                                 |
|--------------|----------|------------------|-----------------------------------------------------------------------------|
| `branch`     | ✅       | —                | Branch name                                                                 |
| `prerelease` | ❌       | `false`          | `true` to generate pre-release (`.devN`) versions                           |
| `config-file`| ❌       | `pyproject.toml` | Path to the TOML config file (must contain `[tool.semantic-branch]` section)|

## Outputs

| Name     | Description                                                     |
|----------|-----------------------------------------------------------------|
| `version`| Calculated version string (e.g. `1.3.0` or `1.3.0.dev12`)       |
| `deploy` | Whether this branch should trigger a deploy (`true` or `false`) |

## Behavior

- **Pre-release mode** (`prerelease=true`):  
  - Bumps version based on branch rules and appends `.devN` (commit count).  
  - Does **not** modify `pyproject.toml`.  
  - Sets `deploy=true` only if branch matches `prerelease` rules.  

- **Release mode** (`prerelease=false`):  
  - Bumps version based on branch rules (patch, minor, major).  
  - Updates `pyproject.toml` with the new version.  
  - Sets `deploy=true` only if branch matches `release` rules.  

- **Ignore rules**:  
  - If branch matches `prerelease-ignore` or `release-ignore`, no version bump is applied and `deploy=false`.  

## Example usage

### Pre-release in PRs

```yaml
jobs:
  prerelease:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - uses: astral-sh/setup-uv@v3

      - uses: ./actions/devops/versioning-branch-semantic
        id: version
        with:
          branch: ${{ github.head_ref }}
          prerelease: "true"

      - run: echo "Pre-release version ${{ steps.version.outputs.version }} (deploy=${{ steps.version.outputs.deploy }})"
```

## Notes

- `pyproject.toml` is updated **only** in release mode, not in prerelease mode.  
- For prereleases, the suffix `.devN` is based on the number of commits (`git rev-list --count HEAD`).  
- Regex patterns in the config must use Python regex syntax and match the **entire** branch name.  
