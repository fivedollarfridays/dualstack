---
name: releasing-versions
description: Manages release preparation including validation, version bumping, documentation verification, and security checks.
skills: [releasing-versions]
agent-roles: [any]
---

# Releasing Versions

## When to Use

- Preparing a new release
- Version bumping
- Pre-release validation
- Documentation verification before release

## Release Workflow Overview

| Phase | Purpose | Blocking? |
|-------|---------|-----------|
| 1. Pre-Release Validation | Tests, security | Yes |
| 2. Version Bump | Update version strings | Yes |
| 3. Documentation | Verify/update docs | Warning |
| 4. Build Verification | Package builds | Yes |
| 5. Release Checklist | Final verification | Yes |
| 6. Git Operations | Commit and tag | Yes |

## Phase 1: Pre-Release Validation

### 1.1 Verify Sprint Tasks Complete

```bash
# Check for incomplete tasks
bpsai-pair task list --status in_progress
bpsai-pair task list --status blocked

# Check current state
bpsai-pair status
```

**BLOCKER**: All tasks must be complete or moved to next sprint.

### 1.2 Run Full Test Suite

```bash
# All tests must pass
pytest tests/ -v --tb=short

# Check coverage meets target (80%)
pytest tests/ --cov --cov-report=term-missing --cov-fail-under=80
```

**BLOCKER**: Release cannot proceed if tests fail.

### 1.3 Security Scans

```bash
# Scan for accidentally committed secrets
bpsai-pair security scan-secrets

# Scan dependencies for known vulnerabilities
bpsai-pair security scan-deps
```

**BLOCKER**: Secrets detected = cannot release.
**WARNING**: Dependency vulnerabilities should be reviewed but may not block.

## Phase 2: Version Bump

### Locate Version Files

```bash
grep -E "^version" pyproject.toml
```

### Update Version Files

| File | Format |
|------|--------|
| `pyproject.toml` | `version = "X.Y.Z"` |
| `pyproject.toml` description | Update CLI command count if changed |
| `capabilities.yaml` | `version: "X.Y.Z"` |
| `config.yaml` | `version: "X.Y.Z"` |

**Note**: `__init__.py` uses `importlib.metadata.version()` — no manual update needed.
**Note**: Version in files has NO 'v' prefix. Git tags use 'v' prefix.

## Phase 3: Documentation Verification

### 3.1 Required Documentation

```bash
# Check CHANGELOG has entry for this version
grep -A 20 "## \[X.Y.Z\]" CHANGELOG.md

# Check README mentions current features
head -100 README.md

```

### 3.2 Documentation Freshness

```bash
# Check modification dates
git log -1 --format="%ci" -- README.md
git log -1 --format="%ci" -- CHANGELOG.md
```

**WARNING** if any required doc older than 7 days - may need update.

### 3.3 CHANGELOG Entry Format

If missing, create entry following Keep a Changelog format:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- Feature 1
- Feature 2

### Changed
- Change 1

### Fixed
- Fix 1

### Removed
- (if applicable)
```

Generate content from archived tasks:
```bash
bpsai-pair task changelog-preview --since <last-version>
```

## Phase 4: Build Verification

```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info

# Build the package
pip install build && python -m build

# Verify clean install
pip install dist/*.whl --force-reinstall

# Verify version is correct
bpsai-pair --version
```

## Phase 5: Release Checklist

### Version & Build
- [ ] Version bumped in pyproject.toml
- [ ] Version bumped in capabilities.yaml
- [ ] Version bumped in config.yaml
- [ ] pyproject.toml description CLI command count updated
- [ ] Package builds successfully
- [ ] Package installs cleanly

### Tests & Security
- [ ] All sprint tasks complete
- [ ] Tests passing (100%)
- [ ] Coverage ≥ 80%
- [ ] No secrets in codebase

### Documentation
- [ ] CHANGELOG updated with version entry
- [ ] README version refs and command counts updated
- [ ] CLAUDE.md versioning table updated
- [ ] capabilities.yaml has feature entries for new modules

## Phase 6: Git Operations

```bash
# Stage all changes
git add -A

# Commit with release message
git commit -m "Release vX.Y.Z"

# Create annotated tag
git tag -a "vX.Y.Z" -m "Release vX.Y.Z"

# Show what will be pushed
git log --oneline -5
git tag -l | tail -5
```

**DO NOT push yet** - let user review and confirm.

## Phase 7: Report Summary

```
Release Prepared: vX.Y.Z

Pre-Release Checks:
- Tests: XXX passed
- Coverage: XX%
- Security: Clean

Documentation:
- CHANGELOG: Updated
- README: Current

Build:
- Package built successfully
- Installs cleanly
- Version verified

Ready to Release:
  git push origin main
  git push origin vX.Y.Z
  twine upload dist/*
```

## Error Recovery

### Tests Fail
1. Do not proceed with release
2. Fix failing tests
3. Re-run from Phase 1

### Secrets Detected
1. Do not proceed with release
2. Remove secrets from history (git filter-branch or BFG)
3. Rotate any exposed credentials
4. Re-run security scan

### Documentation Stale
1. WARNING, not blocker
2. User can choose to update or proceed
3. Log the decision

## Configuration Reference

Release configuration in `config.yaml`:

```yaml
release:
  version_source: pyproject.toml
  documentation:
    - CHANGELOG.md
    - README.md
  freshness_days: 7
```

## Version Format Reference

| Location | Format | Example |
|----------|--------|---------|
| pyproject.toml | X.Y.Z | 2.12.0 |
| capabilities.yaml | X.Y.Z | 2.12.0 |
| config.yaml | X.Y.Z | 2.12.0 |
| Git tags | vX.Y.Z | v2.12.0 |
| CHANGELOG | [X.Y.Z] | [2.12.0] |

**Note**: `__init__.py` uses dynamic `importlib.metadata.version()` — no update needed.
