# GitHub Repository Setup Guide

## 🔒 Branch Protection Rules

### For `main` branch:

1. Go to: **Settings** → **Branches** → **Add branch protection rule**

2. Configure the following:

#### Branch name pattern
```
main
```

#### Protection settings to enable:

**Require a pull request before merging:**
- ✅ Require approvals: **1** (if working with others; disable if solo)
- ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require review from Code Owners (optional, need CODEOWNERS file)

**Require status checks to pass before merging:**
- ✅ Require branches to be up to date before merging
- ✅ Status checks that are required:
  - `lint-and-test (3.10)`
  - `lint-and-test (3.11)`
  - `lint-and-test (3.12)`
  - `security-scan`
  - `streamlit-health-check`

**Other protections:**
- ✅ Require conversation resolution before merging
- ✅ Require signed commits (optional, recommended)
- ✅ Require linear history (keeps history clean)
- ✅ Include administrators (even you must follow rules)

**Rules applied to everyone:**
- ✅ Allow force pushes: **NO**
- ✅ Allow deletions: **NO**

---

## 🏷️ Repository Topics/Tags

Add these topics to make your repo discoverable:

**Settings** → **About** → **Topics**

```
streamlit
finance
stock-analysis
fundamental-analysis
investment
python
data-visualization
yfinance
plotly
financial-data
portfolio-management
streamlit-app
stock-market
investment-analysis
```

---

## 📋 Repository Settings

### General Settings

**Settings** → **General**

#### Features to enable:
- ✅ Issues
- ✅ Projects
- ✅ Preserve this repository (important data)
- ✅ Discussions (optional - for Q&A)
- ✅ Wikis (optional - for extended docs)

#### Pull Requests:
- ✅ Allow squash merging (clean history)
- ✅ Allow auto-merge
- ✅ Automatically delete head branches (cleanup)
- ✅ Default to PR title for squash commits

#### Archives:
- ✅ Include Git LFS objects in archives

---

## 📄 Create GitHub Templates

### 1. Pull Request Template

Create: `.github/PULL_REQUEST_TEMPLATE.md`

```markdown
## Description
<!-- Describe your changes in detail -->

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Performance improvement
- [ ] Configuration/infrastructure change

## How Has This Been Tested?
<!-- Describe the tests you ran to verify your changes -->
- [ ] Unit tests pass (`uv run pytest`)
- [ ] Linting passes (`uv run ruff check .`)
- [ ] Type checking passes (`uv run mypy dashboard.py`)
- [ ] Manual testing (describe scenarios)

## Screenshots (if applicable)
<!-- Add screenshots to help explain your changes -->

## Checklist
- [ ] My code follows the style guidelines (runs through pre-commit)
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Related Issues
Closes #(issue number)
```

### 2. Bug Report Template

Create: `.github/ISSUE_TEMPLATE/bug_report.md`

```markdown
---
name: Bug Report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

## Bug Description
A clear and concise description of what the bug is.

## Steps To Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
A clear and concise description of what you expected to happen.

## Actual Behavior
What actually happened.

## Screenshots
If applicable, add screenshots to help explain your problem.

## Environment
- OS: [e.g. macOS 14.0, Ubuntu 22.04]
- Python Version: [e.g. 3.10.6]
- Browser (if relevant): [e.g. Chrome 120, Safari 17]

## Additional Context
Add any other context about the problem here.

## Possible Solution
If you have ideas on how to fix this, please share.
```

### 3. Feature Request Template

Create: `.github/ISSUE_TEMPLATE/feature_request.md`

```markdown
---
name: Feature Request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

## Is your feature request related to a problem?
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

## Describe the solution you'd like
A clear and concise description of what you want to happen.

## Describe alternatives you've considered
A clear and concise description of any alternative solutions or features you've considered.

## Additional context
Add any other context or screenshots about the feature request here.

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3
```

---

## 🏷️ Labels Setup

**Issues** → **Labels** → Create these labels:

| Label | Color | Description |
|-------|-------|-------------|
| `bug` | `#d73a4a` | Something isn't working |
| `documentation` | `#0075ca` | Improvements or additions to documentation |
| `enhancement` | `#a2eeef` | New feature or request |
| `good first issue` | `#7057ff` | Good for newcomers |
| `help wanted` | `#008672` | Extra attention is needed |
| `priority: high` | `#e11d21` | High priority |
| `priority: medium` | `#eb6420` | Medium priority |
| `priority: low` | `#fbca04` | Low priority |
| `wontfix` | `#ffffff` | This will not be worked on |
| `duplicate` | `#cfd3d7` | This issue or pull request already exists |
| `dependencies` | `#0366d6` | Pull requests that update a dependency |
| `security` | `#ee0701` | Security-related issues |
| `performance` | `#5319e7` | Performance improvements |
| `refactor` | `#1d76db` | Code refactoring |
| `tests` | `#d4c5f9` | Related to testing |
| `ci/cd` | `#bfdadc` | CI/CD pipeline changes |

---

## 🔐 Secrets Management

### For GitHub Actions:

**Settings** → **Secrets and variables** → **Actions**

Add these secrets if needed:

```
STREAMLIT_CLOUD_API_KEY    # For automated deployments
CODECOV_TOKEN              # For coverage reporting
TOGETHER_API_KEY           # For LLM features (when implemented)
```

### For Dependabot:

**Settings** → **Security** → **Dependabot**

Enable:
- ✅ Dependabot alerts
- ✅ Dependabot security updates
- ✅ Dependabot version updates

Create `.github/dependabot.yml`:

```yaml
version: 2
updates:
  # Python dependencies
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    reviewers:
      - "akhilkarra"
    labels:
      - "dependencies"
      - "python"

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    reviewers:
      - "akhilkarra"
    labels:
      - "dependencies"
      - "ci/cd"
```

---

## 📊 Code Quality Badges

Add to your README.md (already has CI/CD badge):

```markdown
[![codecov](https://codecov.io/gh/akhilkarra/investilearn/branch/main/graph/badge.svg)](https://codecov.io/gh/akhilkarra/investilearn)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
```

---

## 👥 CODEOWNERS File

Create `.github/CODEOWNERS`:

```
# Global code owners
* @akhilkarra

# Python code
*.py @akhilkarra

# CI/CD
/.github/ @akhilkarra

# Documentation
*.md @akhilkarra
/docs/ @akhilkarra

# Configuration
pyproject.toml @akhilkarra
.pre-commit-config.yaml @akhilkarra
```

---

## 🔗 GitHub Pages (Optional)

If you want to host documentation:

**Settings** → **Pages**
- Source: Deploy from a branch
- Branch: `gh-pages` (create this branch for docs)
- Or use GitHub Actions for deployment

---

## 🎯 Project Boards

**Projects** → **New project**

Create boards like:
- **Development Roadmap** (Kanban board)
- **Bug Tracking**
- **Feature Requests**

Columns:
- 📋 Backlog
- 🔄 In Progress
- 👀 In Review
- ✅ Done

---

## 🔔 Notification Settings

Personal GitHub settings:

**Settings** → **Notifications**
- Configure email/web notifications
- Watch your repository
- Subscribe to releases

---

## 📦 Release Management

### Create Release Workflow

`.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Create Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          draft: false
          prerelease: false
```

---

## ✅ Quick Setup Checklist

- [ ] Configure branch protection for `main`
- [ ] Add repository topics/tags
- [ ] Create PR template
- [ ] Create issue templates (bug, feature)
- [ ] Set up labels
- [ ] Add CODEOWNERS file
- [ ] Configure Dependabot
- [ ] Add secrets (when needed)
- [ ] Enable security features
- [ ] Configure pull request settings
- [ ] Set up project boards (optional)
- [ ] Add additional badges to README

---

## 🚀 After Setup

Your repository will have:
- Protected main branch
- Automated dependency updates
- Clear contribution process
- Organized issue tracking
- Professional appearance
- Security scanning
- Quality enforcement

This is the setup used by top open-source projects! 🎉
