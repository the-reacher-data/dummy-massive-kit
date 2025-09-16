# Contributing to MassiveKit 🚀

## Branch naming

Branches must follow:

- `feature/<scope>-<desc>` → new features  
- `fix/<scope>-<desc>` → bug fixes  
- `hotfix/<scope>-<desc>` → urgent patch  
- `chore/<scope>-<desc>` → infra/docs/tests  
- `release/x.y` → release branches  

Examples:

- `feature/core-add-cache`
- `fix/api-handle-404`
- `hotfix/core-credentials`
- `chore/docs-update`

⚠️ Invalid branches will be blocked by pre-commit.

---

## Pull Requests

### PRs to `master`

- Must be **Squash & Merge** ✅.  
- The **PR title** is used as the final Conventional Commit message.  
- Example:
  - Branch: `feature/api-add-auth`  
  - PR title: `Add authentication middleware`  
  - Final commit: `feat(api): Add authentication middleware`  
- This ensures the CHANGELOG shows a single entry per feature/hotfix.

### PRs to `release/x.y`

- Must be **Merge commit (no squash)** ✅.  
- Each feature/hotfix branch merged into the release branch must use Squash & Merge.  
- When merging the release branch into `master`, all those commits will appear in the CHANGELOG for that version.

---

## Commit messages

- Developers don’t need to write Conventional Commits manually.  
- Final Conventional Commit is auto-generated from:
  - The branch type (`feature`, `fix`, `hotfix`, `chore`) → commit type.  
  - The branch scope → commit scope.  
  - The PR title → commit subject.  

Example:

- Branch: `feature/core-add-cache`
- PR title: `Add cache support`
- Final commit in master:  `feat(core): Add cache support`

---

## Tests & Quality

All PRs must pass:

- `ruff` (lint)
- `mypy` (type checks)
- `pytest` (unit tests + coverage)
- `snyk` (dependency security scan)

---

## Releases

- **Pre-releases** published to **TestPyPI** from feature/fix/hotfix/release branches.  
- **Official releases** happen when merging into `master`, handled by **semantic-release**.  
- Changelog and versioning follow [Semantic Versioning](https://semver.org).  

---

## Breaking changes

- Add `!` in the branch name or PR title (e.g., `feature/core-breaking-change`)  
- Or write `BREAKING CHANGE:` in the PR description.
