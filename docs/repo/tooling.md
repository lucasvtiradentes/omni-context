---
title: Tooling
description: Development tools, linting, testing, and build configuration
related_docs:
  - docs/repo/local-setup.md: how to set up locally
  - docs/repo/cicd.md:        CI pipeline details
required_docs: []
sources:
  - pyproject.toml:           package and tool config
  - Makefile:                 dev command shortcuts
  - .pre-commit-config.yaml:  pre-commit hooks
---

# Tooling

## Build System

| Tool      | Purpose                 | Config Location |
|-----------|-------------------------|-----------------|
| hatchling | Package build backend   | pyproject.toml  |
| pip       | Dependency installation | pyproject.toml  |

## Code Quality

| Tool       | Purpose              | Config Location         |
|------------|----------------------|-------------------------|
| ruff       | Linting + formatting | pyproject.toml          |
| pre-commit | Git hook runner      | .pre-commit-config.yaml |

### Ruff Configuration

```toml
[tool.ruff]
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "I"]
```

Rules enabled:
- E: pycodestyle errors
- F: pyflakes
- I: isort (import sorting)

## Testing

| Tool   | Purpose     | Config Location |
|--------|-------------|-----------------|
| pytest | Test runner | pyproject.toml  |

Test paths configured: `tests/`

## Version Management

| Tool         | Purpose              | Config Location  |
|--------------|----------------------|------------------|
| bump2version | Version bumping      | .bumpversion.cfg |
| towncrier    | Changelog generation | pyproject.toml   |

### Towncrier Configuration

Changelog entries stored in `.changelog/` directory:

```
.changelog/
├── feature/
│   └── 123.md
├── bugfix/
│   └── 456.md
└── misc/
    └── 789.md
```

## Python Support

Supported versions: 3.9, 3.10, 3.11, 3.12, 3.13, 3.14

## Makefile Targets

| Target         | Command                           |
|----------------|-----------------------------------|
| make install   | Create venv, install deps + hooks |
| make check     | Run ruff check + format check     |
| make format    | Run ruff fix + format             |
| make test      | Run pytest                        |
| make build     | Build package with hatch          |
| make changelog | Generate changelog with towncrier |
| make clean     | Remove build artifacts            |
