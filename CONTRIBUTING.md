# Contributing to MassiveKit 🚀

## Overview

MassiveKit follows a professional development methodology with **Clean Architecture**, **SOLID principles**, and **Conventional Commits**. This guide explains our CI/CD workflow and contribution standards.

## Project Structure

```text
src/
├── dummy_massivekit/
│   ├── __init__.py
│   ├── api/           # API endpoints and controllers
│   ├── core/          # Core business logic
│   ├── domain/        # Entities and value objects
│   └── infrastructure/ # Repositories and adapters
└── tests/             # Unit and integration tests
```

## Branch Naming Convention

### Required Format

```text
<type>/<description>
```

### Branch Types (Enforced by Pre-commit)

- `feat/<description>` → New features
- `feature/<description>` → New features (alternative)
- `multifeature/<description>` → Multiple related features
- `fix/<description>` → Bug fixes
- `hotfix/<description>` → Production critical fixes
- `chore/<description>` → Infrastructure, docs, tests
- `docs/<description>` → Documentation improvements

### Examples

```bash
# Valid branches ✅
git checkout -b feat/user-authentication
git checkout -b fix/api-validation-error
git checkout -b hotfix/security-vulnerability
git checkout -b feature/database-migration
git checkout -b multifeature/core-refactor
git checkout -b chore/dependency-update
git checkout -b docs/readme-enhancement
```

### Branch Validation

- **Pre-commit hook** (`validate-branch-name`) enforces this format during `git push`
- Invalid branches are **blocked** with clear error messages
- Allowed prefixes: `feat/`, `feature/`, `multifeature/`, `fix/`, `hotfix/`

## Git Workflow

### 1. Create Feature Branch

```bash
# Start from latest main
git checkout main
git pull origin main

# Create new branch
git checkout -b feat/your-feature-description
```

### 2. Local Development

```bash
# Install development dependencies
uv sync --dev

# Pre-commit hooks are automatically active
pre-commit run --all-files  # Optional: run all checks

# Make atomic commits with Conventional Commits format in BODY
git add .
git commit                    # Interactive commit to add body
# or
git commit -m "Initial commit" -m "feat(api): add user authentication endpoint"
```

### 3. Push and CI

```bash
# Push triggers CI for specific branches
git push origin feat/your-feature

# Pre-push hooks:
# - Validate branch name
# - Run all tests
# - Block if validation fails
```

### 4. Pull Request Process

- **Target**: Always merge to `main` (protected branch)
- **Merge Strategy**: **Squash & Merge ONLY** (branch protection rule)
- **PR Requirements**: All CI checks must pass
- **CI Triggers**: PRs to main execute full quality pipeline

**Important**: The `main` branch is protected and only allows squash merges. This ensures clean commit history while preserving Conventional Commit bodies for semantic-release analysis.

### 5. Code Review

- Reviewers verify code quality, tests, and documentation
- CI results are automatically commented on the PR
- Merge only when all checks pass and review is approved

### 6. Automated Release

- **Trigger**: Push to `main` (squashed merge)
- **Semantic Release**: Analyzes **commit bodies** containing Conventional Commits to determine version
- **Actions**: Version bump, changelog generation, PyPI publish

## Conventional Commits (Required in Commit Body)

### Manual Conventional Commits in Body

Developers **must** write commits following the [Conventional Commits](https://www.conventionalcommits.org/) specification in the **commit body** (second line):

```text
<subject line>

<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Why Body Instead of Subject?

- **Squash Merges**: Preserve Conventional Commit format through protected main branch
- **Semantic Release**: Analyzes commit bodies to determine release versions
- **Clean History**: Subject line remains descriptive for humans, body provides machine-readable format

### Commit Types

| Type     | Description                                                | Release Impact |
|----------|------------------------------------------------------------|----------------|
| `feat`   | New feature                                                | Minor version  |
| `fix`    | Bug fix                                                    | Patch version  |
| `docs`   | Documentation                                              | No impact      |
| `style`  | Formatting, missing semicolons                             | No impact      |
| `refactor` | Code change that neither fixes a bug nor adds a feature | No impact      |
| `perf`   | Performance improvement                                    | Patch version  |
| `test`   | Adding missing tests or correcting broken tests            | No impact      |
| `build`  | Changes that affect the build system                       | No impact      |
| `ci`     | Changes to CI configuration                                | No impact      |
| `chore`  | Other changes that don't modify source or test files       | No impact      |
| `revert` | Reverts a previous commit                                  | No impact      |

### Examples

```bash
# Good commits with Conventional Commits in BODY ✅

# Method 1: Interactive commit (recommended)
git commit
# Git UI/editor opens:
# Subject: Add user authentication endpoint
#
# feat(api): implement JWT authentication with refresh tokens
#
# This adds complete authentication flow including:
# - Registration endpoint
# - Login with JWT tokens
# - Token refresh mechanism
# - Protected route middleware

# Method 2: Command line with body
git commit -m "Add user authentication endpoint" -m "feat(api): implement JWT authentication with refresh tokens"

# Method 3: Multiple lines
git commit -m "Add user authentication endpoint" -m "feat(api): implement JWT authentication with refresh tokens
This adds complete authentication flow including:
- Registration endpoint
- Login with JWT tokens
- Token refresh mechanism
- Protected route middleware"

# Breaking changes
git commit -m "Migrate authentication system" -m "feat(auth): migrate from session-based to JWT!
BREAKING CHANGE: Session-based auth deprecated
Migration guide: docs/migration/auth-jwt.md"
```

### Commit Validation

- **Commitizen pre-commit hook** validates Conventional Commits format in the **body** during `git commit`
- Invalid formats are **rejected** with helpful error messages
- Use `git commit` without `-m` for interactive guidance (recommended)

### Squash Merge Behavior

When squashing PR commits to `main`:

1. **Subject**: Becomes the squashed commit message (human-readable)
2. **Body**: Include the Conventional Commit format for semantic-release
3. **Preservation**: Main protection ensures body is maintained for analysis

**Example PR squash:**

```text
PR Title: Add user authentication system

Squashed commit:
Subject: Add user authentication system

Body: feat(auth): implement complete JWT authentication flow
Includes registration, login, token refresh, and protected routes
```

## Main Branch Protection

### Protected Branch Rules

The `main` branch has strict protection rules enforced by GitHub:

| Rule | Status | Description |
|------|--------|-------------|
| **Require pull request reviews** | ✅ Enabled | At least 1 approving review required |
| **Require status checks to pass** | ✅ Enabled | All CI jobs must pass before merge |
| **Restrict pushes that are not from pull requests** | ✅ Enabled | No direct pushes to main allowed |
| **Require linear history** | ❌ Disabled | Allows merge commits if needed |
| **Require signed commits** | ❌ Disabled | GPG signing optional |
| **Do not allow bypassing the above settings** | ✅ Enabled | Admins cannot bypass rules |

### Squash Merge Only

- **Only squash merges** are allowed to main
- **No rebase merges** or **merge commits** permitted
- **Reason**: Ensures clean, linear history with preserved commit bodies
- **Impact**: Semantic-release can reliably analyze commit bodies for versioning

### Branch Protection Workflow

```bash
# 1. Work on feature branch
git checkout -b feat/new-feature
# ... development with Conventional Commits in bodies ...

# 2. Push feature branch
git push origin feat/new-feature

# 3. Create PR to main
# GitHub UI shows: "This branch has no conflicts with the base branch"

# 4. PR Requirements (automatically checked):
# - [ ] 1+ approving review
# - [ ] All CI checks pass (Ruff, MyPy, pytest, Bandit, Snyk)
# - [ ] No conflicts
# - [ ] Linear history maintained

# 5. Merge Options (only one available):
# - [x] Squash and merge (only option)
# - [ ] Create a merge commit (disabled)
# - [ ] Rebase and merge (disabled)

# 6. After squash merge:
# - Single commit on main with preserved body
# - Semantic-release analyzes body for version determination
# - Automatic release to PyPI if applicable
```

## CI/CD Pipeline Details

### Continuous Integration (`.github/workflows/ci.yaml`)

**Triggers:**

- Push to: `feature/**`, `multifeature/**`, `fix/**`, `hotfix/**`, `chore/**`, `docs/**`
- Pull Requests targeting `main`

**Quality Checks:**

| Check | Tool | Standard |
|-------|------|----------|
| **Linting** | Ruff | Zero errors |
| **Formatting** | Ruff | Consistent style |
| **Type Checking** | MyPy | Strict mode, no errors |
| **Unit Tests** | Pytest | All tests pass |
| **Coverage** | pytest-cov | ≥85% branch coverage |
| **Security** | Bandit | No critical issues |
| **Dependencies** | Snyk | No high/critical vulnerabilities |

**PR Automation:**

- **CI Summary Comment**: Automatic status report on PR with test results, coverage, and predicted version from body analysis
- **Code Coverage**: Badge and detailed report via Codecov
- **Artifacts**: Logs uploaded for debugging (pytest.log, coverage.xml, lint.log, etc.)
- **Pre-release Analysis**: Dry-run semantic-release predicts next version from **commit bodies** containing Conventional Commits

### Release Pipeline (`.github/workflows/release.yaml`)

**Trigger:** Push to `main` only (protected branch, squash merges)

**Body-Based Semantic Release Analysis:**

- **Key Feature**: Semantic-release specifically analyzes **commit bodies** for Conventional Commits format
- **Preservation**: Squash merges ensure that the Conventional Commit from the body is preserved in the final main commit
- **Analysis Process**:
  1. Scans all commits since last release tag
  2. Extracts Conventional Commits from **body sections** only
  3. Ignores subject lines for version determination
  4. Determines version bump: `feat` → minor, `fix` → patch, breaking changes → major

**Automated Steps:**

1. **Security Scan**: Final Snyk dependency check
2. **Semantic Release Analysis**:
   - **Scans commit bodies** for Conventional Commits since last release
   - **Body parsing**: Extracts `feat(module): description`, `fix(...)`, etc. from commit bodies
   - Determines version bump based on body content: `feat` (minor), `fix` (patch), breaking changes (major)
   - **Preserves body format** from squash merges for accurate analysis
3. **Version Management**:
   - Updates `pyproject.toml` `[project]` version field automatically
   - Creates Git tag with semantic version (e.g., `v0.2.1`)
   - Commits version changes back to main with proper body format
4. **Changelog Generation**:
   - Creates/updates `CHANGELOG.md` from **commit body** analysis
   - Groups by type: Features (`feat`), Bug Fixes (`fix`), etc.
   - Uses body content for detailed descriptions
5. **PyPI Publishing**:
   - Builds package with `python -m build`
   - Uploads wheel and sdist to official PyPI using twine
   - Verifies successful upload and creates GitHub release
6. **Documentation Deployment**:
   - Builds MkDocs documentation with `mkdocs build --strict`
   - Deploys to GitHub Pages (`gh-pages` branch, `/docs` folder)
7. **CodeQL Analysis**: Security scan for public repository

### Body Analysis Example

**Commit on main after squash merge:**

```text
Subject: Add comprehensive user authentication

Body:
feat(auth): implement JWT authentication system with role-based access control

This implementation includes:
- User registration with email verification
- JWT token generation and validation
- Role-based access control middleware
- Token refresh and revocation mechanisms
- Comprehensive audit logging
```

**Semantic-release processing:**

- **Type**: `feat` → Minor version bump
- **Scope**: `auth` → Groups in changelog under Authentication
- **Description**: Uses body content for changelog entry
- **Result**: `0.1.0` → `0.2.0`, changelog entry created

### Pre-release Analysis (Feature Branches)

- **Dry-run Semantic Release**: Predicts version from current branch's **commit bodies**
- **TestPyPI**: Pre-releases available for testing new features (rcN, bN suffixes)
- **Version Preview**: Shows predicted version in CI comments based on body analysis
- **Body Validation**: Ensures Conventional Commits format is correct before main merge

## Deployment and Releases

### Version Management

- **Semantic Versioning**: MAJOR.MINOR.PATCH format
- **Automatic Determination**: Based on Conventional Commits in **commit bodies**
- **Configuration**: `pyproject.toml` `[project]` section automatically updated
- **History**: All versions published to PyPI with changelogs

### Release Types

| Scenario | Trigger | Version Impact | PyPI Target | Analysis Source |
|----------|---------|----------------|-------------|-----------------|
| New feature | `feat` in body to main | Minor (x.y.z → x.y+1.z) | Official PyPI | Commit body |
| Bug fix | `fix` in body to main | Patch (x.y.z → x.y.z+1) | Official PyPI | Commit body |
| Breaking change | `!` in body to main | Major (x.y.z → x+1.0.0) | Official PyPI | Commit body |
| Pre-release | Feature branch push | RC/Beta to TestPyPI | TestPyPI | Dry-run body analysis |

### What NOT to Do

- ❌ **Don't** put Conventional Commits in subject line (use body for semantic-release)
- ❌ **Don't** push branches without proper prefix (blocked by pre-push hook)
- ❌ **Don't** commit large changes in single commits (keep atomic)
- ❌ **Don't** hardcode secrets or credentials (blocked by detect-secrets)
- ❌ **Don't** skip tests for new functionality (blocked by pre-push)
- ❌ **Don't** modify generated files (`.egg-info/`, `build/`, `dist/`)
- ❌ **Don't** use relative imports in production code (blocked by pre-commit)
- ❌ **Don't** leave TODO/FIXME comments in committed code (blocked by pre-commit)
- ❌ **Don't** attempt direct pushes to main (protected branch)

## Troubleshooting

### Common Pre-commit Issues

#### Invalid branch name

```bash
# Solution: Rename branch with proper prefix
git branch -m old-name feat/new-feature-name
git push origin -u feat/new-feature-name
```

#### Commit body does not follow Conventional Commits

```bash
# Solution: Use interactive commit or proper body format
git commit                    # Opens editor for subject + body
# Ensure body starts with: feat(module): description
```

#### Tests failed in pre-push

```bash
# Solution: Run tests locally first
pytest src/tests/ --cov=src/ --cov-report=term-missing
# Fix failing tests before pushing
```

### CI Failures

#### Linting Errors

```bash
ruff check src/ --fix  # Auto-fix where possible
ruff format src/       # Format code
```

#### Type Errors

```bash
mypy src/  # See specific errors
# Add type hints or fix logic
```

#### Coverage Below 85%

```bash
pytest src/tests/ --cov=src/ --cov-report=html
# Open htmlcov/index.html to see uncovered lines
# Add missing tests
```

#### Semantic-release cannot determine version

```bash
# Solution: Ensure commit bodies contain Conventional Commits
# Check recent commits: git log --oneline -10
# Verify body format in full log: git log -10
# Look for: feat(module): description in commit bodies
```

### Main Branch Protection Issues

#### Cannot push to main directly

```bash
# Solution: Create PR from feature branch
git push origin feat/your-feature
# Create PR to main through GitHub UI
```

#### Merge conflicts on squash

```bash
# Solution: Rebase before PR
git fetch origin
git rebase origin/main
git push --force-with-lease origin feat/your-feature
```

#### Squash merge rejected by branch protection

```bash
# Solution: Ensure all status checks pass
# Check CI summary comment on PR for failing jobs
# Fix issues and push new commits to trigger re-check
```

### Semantic Release Body Analysis Issues

#### No version bump detected

```bash
# Check if Conventional Commits are in bodies:
git log --oneline -5  # See commit subjects
git log -5            # See full commits with bodies

# Ensure body format:
# feat(api): add endpoint
# Not in subject line
```

#### Wrong version bump (patch instead of minor)

```bash
# Verify commit bodies contain 'feat' type:
git log --grep="feat" -p -5  # Search for feat in commit history

# Body must start with: feat(module): description
```

#### Changelog missing features

```bash
# Semantic-release uses body content for changelog
# Ensure descriptive bodies after Conventional Commit line:
# feat(auth): add JWT support
#
# This adds complete authentication including login, registration,
# token refresh, and role-based access control.
```

### Commit Body Best Practices

#### For Interactive Commits (`git commit` without `-m`)

1. **Subject line**: Short, descriptive summary (50-72 characters)
2. **Blank line**: Separate subject from body
3. **Conventional Commit**: First line of body: `feat(module): description`
4. **Additional details**: Explain what, why, how below
5. **Breaking changes**: Use `!` after type: `feat(module)!: breaking change`

#### For Command Line (`git commit -m`)

```bash
# Single line body
git commit -m "Add auth endpoint" -m "feat(api): implement JWT authentication"

# Multi-line body
git commit -m "Add auth endpoint" -m "feat(api): implement JWT authentication
This adds complete flow with:
- Registration and login endpoints
- Token validation middleware
- Role-based access control"
```

## Thank You! 🎉

Your contributions help make MassiveKit a robust framework for building scalable APIs and microservices. By following these standards—especially proper Conventional Commits in commit bodies—we maintain professional, maintainable, and automatically releasable code.

*Last updated: September 18, 2025*
