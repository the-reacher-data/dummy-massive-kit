# 🚀 CI/CD Flow Documentation

## 📋 Overview

This project uses a sophisticated automated CI/CD pipeline with:
- 🤖 **Conventional commits** generated from branch names + PR titles
- 🧪 **TestPyPI prereleases** for all branches/PRs (PEP 440 compliant)
- 🚀 **PyPI releases** only on master merges
- 📝 **Automatic changelog** generation with semantic versioning
- 📊 **Comprehensive quality reporting** with coverage, linting, and security

## 🏗️ Architecture

### Jobs Overview:
1. **🔄 Setup**: Shared configuration and base setup
2. **🧪 Test & Quality**: Comprehensive testing, linting, type checking, security
3. **📝 Conventional Commit**: Generates conventional commits (non-release branches only)
4. **📋 Changelog Preview**: Shows changelog preview in PRs with quality summary
5. **🧪 Prerelease**: TestPyPI uploads for all non-master branches/PRs
6. **🚀 Release**: PyPI releases for master merges only
7. **📊 Summary**: Final comprehensive summary of all results

## 🌿 Branch Naming Convention

### Format: `type/scope-description`

**Examples:**
- `feature/api-new-endpoint` → `feat(api): New endpoint`
- `fix/auth-login-bug` → `fix(auth): Login bug`
- `hotfix/security-patch` → `fix(security): Patch`
- `chore/deps-update` → `chore(deps): Update`

### Supported Types:
- `feature/feat` → `feat`
- `fix/bugfix` → `fix`
- `hotfix/patch` → `fix`
- `chore` → `chore`
- `docs` → `docs`
- `style` → `style`
- `refactor` → `refactor`
- `perf` → `perf`
- `test` → `test`
- `ci` → `ci`

## 🔄 CI/CD Workflow

### 1. 🧪 Feature Development (Push to Feature Branch)

```bash
git checkout -b feature/api-user-management
git push origin feature/api-user-management
```

**Triggers:**
- ✅ `test-and-quality` job (lint, type check, tests)
- ✅ `prerelease` job (TestPyPI upload with branch-specific version)

**Version Generated:** `0.1.0.dev1705328400+feature-api-user`

### 2. 📝 Pull Request (PR to Master/Release)

```bash
# Create PR: "Add comprehensive user management API"
```

**Triggers:**
- ✅ `test-and-quality` job
- ✅ `changelog-preview` job (shows preview in PR comment)
- ✅ `prerelease` job (TestPyPI upload with PR-specific version)

**Changelog Preview in PR:**
```
## 📝 Changelog Preview

If this PR is merged, the following will be added to the changelog:

### feat(api): Add comprehensive user management API

- **Branch**: `feature/api-user-management`
- **PR**: #123 - Add comprehensive user management API
```

**Version Generated:** `0.1.0.dev1705328500+pr123`

### 3. 🎯 Release Branch (release/v1.2.0)

```bash
git checkout -b release/v1.2.0
git push origin release/v1.2.0
```

**Triggers:**
- ✅ `test-and-quality` job
- ✅ `release` job with `--prerelease` flag
- 🔄 Generates conventional commits from merged PR history
- 📝 Creates release candidate: `v1.2.0-rc.1`

### 4. 🚀 Master Merge (Final Release)

```bash
git checkout master
git merge release/v1.2.0
git push origin master
```

**Triggers:**
- ✅ `test-and-quality` job
- ✅ `release` job (final release)
- 📦 PyPI upload
- 📚 Documentation deployment
- 🏷️ Git tag creation
- 📝 GitHub Release creation
- ✨ CHANGELOG.md update

## 📊 Generated Changelog Example

```markdown
# Changelog

## [1.2.0] - 2024-01-15

### ✨ Features
- **api**: Add comprehensive user management API (#123)
- **auth**: Implement OAuth2 integration (#124)

### 🐛 Bug Fixes
- **auth**: Fix login validation issue (#125)
- **api**: Resolve rate limiting edge case (#126)

### 📚 Documentation
- **readme**: Update installation instructions (#127)
```

## 🎛️ Manual Override

If your PR title is already a conventional commit, it will be used as-is:

**Branch:** `feature/api-endpoints`
**PR Title:** `feat(api): add user management endpoints with validation`
**Result:** `feat(api): add user management endpoints with validation`

## 🔧 Configuration Files

- **`.releaserc.json`**: Semantic-release configuration
- **`scripts/generate_conventional_commit.py`**: Branch name → conventional commit logic
- **`.github/workflows/ci.yaml`**: Complete CI/CD pipeline

## 📈 Benefits

1. **🤖 Automated**: No manual changelog maintenance
2. **📝 Consistent**: Standardized conventional commits
3. **🔍 Transparent**: Preview changelog in PRs
4. **⚡ Fast**: Parallel jobs with UV-based dependency management
5. **🛡️ Reliable**: Comprehensive testing and quality checks
6. **📦 Complete**: From feature branch to PyPI automatically
