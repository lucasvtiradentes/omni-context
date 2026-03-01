---
title: Local Setup
description: How to set up the development environment
related_docs:
  - docs/repo/tooling.md: development tools overview
  - docs/testing.md:      running tests
required_docs: []
sources:
  - Makefile:                 installation targets
  - pyproject.toml:           dev dependencies
---

# Local Setup

## Prerequisites

- Python 3.9+
- Git

## Installation

```bash
make install
```

This command:
1. Creates virtualenv at `.venv/`
2. Installs package in editable mode with dev dependencies
3. Installs pre-commit hooks

## Manual Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pre-commit install
```

## Dev Dependencies

Installed via `[dev]` extra:

| Package      | Purpose              |
|--------------|----------------------|
| pytest       | Test runner          |
| ruff         | Linting + formatting |
| towncrier    | Changelog generation |
| bump2version | Version management   |
| pre-commit   | Git hook management  |

## Running Commands

### Format Code

```bash
make format
```

Runs `ruff check --fix` + `ruff format`

### Check Code

```bash
make check
```

Runs `ruff check` + `ruff format --check`

### Run Tests

```bash
make test
```

Runs `pytest -v`

### Test CLI

```bash
.venv/bin/bctx status
.venv/bin/bctx --help
```

## Project Structure After Setup

```
branch-context/
├── .venv/           Virtual environment
├── src/branchctx/   Editable install
└── ...
```
