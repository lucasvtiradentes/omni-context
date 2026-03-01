---
title: Repository Status
description: Health checks and status reporting
related_docs:
  - docs/features/branch-context-management.md: context management
  - docs/features/shell-integration.md:         hook installation
required_docs: []
sources:
  - src/branchctx/commands/status.py:           status command
---

# Repository Status

## Status Command

```bash
bctx status
```

### Output Example

```
Repository:  /path/to/repo
Branch:      feature/auth
Symlink:     _branch -> .bctx/branches/feature-auth
Hooks:       post-checkout, post-commit
Templates:   _default, feature, fix
Contexts:    5 branches
Base:        main

Health:
  [ok] post-checkout hook installed
  [ok] post-commit hook installed
  [ok] templates/ exists
  [ok] _default template exists
  [ok] symlink valid
  [ok] no orphan contexts
```

### Status Indicators

| Indicator | Meaning                 |
|-----------|-------------------------|
| [ok]      | Check passed            |
| [!!]      | Error - needs fix       |
| [--]      | Warning - informational |

## Health Checks

### Hook Installation

```
┌─────────────────────────────────────────────────────┐
│  Check: post-checkout hook installed?               │
│         post-commit hook installed?                 │
├─────────────────────────────────────────────────────┤
│  [ok] if bctx marker found in hook file             │
│  [!!] if hook missing or not managed by bctx        │
└─────────────────────────────────────────────────────┘
```

### Templates Directory

```
┌─────────────────────────────────────────────────────┐
│  Check: .bctx/templates/ exists?                    │
│         _default template exists?                   │
├─────────────────────────────────────────────────────┤
│  [ok] if directory and _default present             │
│  [!!] if missing                                    │
└─────────────────────────────────────────────────────┘
```

### Symlink Validity

```
┌─────────────────────────────────────────────────────┐
│  Check: _branch/ is symlink?                        │
│         symlink target exists?                      │
├─────────────────────────────────────────────────────┤
│  [ok] if valid symlink pointing to existing dir     │
│  [!!] if broken symlink or not a symlink            │
│  [--] if symlink not set yet                        │
└─────────────────────────────────────────────────────┘
```

### Orphan Contexts

```
┌─────────────────────────────────────────────────────┐
│  Check: all contexts have matching git branches?    │
├─────────────────────────────────────────────────────┤
│  [ok] if no orphans                                 │
│  [--] if orphan contexts exist (can prune)          │
└─────────────────────────────────────────────────────┘
```

## Exit Codes

| Code | Meaning                   |
|------|---------------------------|
| 0    | All checks passed         |
| 1    | One or more errors ([!!]) |

Warnings ([--]) do not affect exit code.

## Global Hooks Path

If `core.hooksPath` is set globally, status shows:

```
Global:      /path/to/global/hooks
```

This helps diagnose hook conflicts.
