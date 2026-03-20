## 0.3.1 (2026-03-20)

### Bug Fixes

- Fix prune requiring two runs to fully clean up: reorder to delete branches before archiving orphans, and fix remote branch detection for orphan contexts.


## 0.3.0 (2026-03-20)

### Features

- Interactive multi-step `bctx prune` workflow: archive contexts without local/remote branch, then select local branches to delete via arrow-key multi-select.
- Shell completion now derives function name from binary name (sys.argv[0]), so `bctx`, `bctxd`, and `branch-ctx` each get independent completions without conflicts.
- Show branch status table (context/local/remote) in `bctx status` with color-coded indicators and grouping by availability level.

### Bug Fixes

- Add fallback numbered-list selector when `termios` is unavailable (Windows) or stdin is not a TTY.

### Misc

- Remove `bctx branches` subcommand. Branch list merged into `bctx status`. Prune promoted to top-level `bctx prune`.
- Update default templates to "Guidelines" format. Add missing template_rules (bugfix/, refactor/) to default config. Untrack .bctx/ from git.


## 0.2.4 (2026-03-18)

### Features

- Added `bctx base` command to show or set the base branch for the current context.

### Bug Fixes

- Fixed `bctx template` destroying extra files and folders in the branch context directory.

### Misc

- Improved all templates with YAML frontmatter, HTML comment guide, consistent sections (Description, Key Paths, References, Tasks), and added fix/chore bundled templates. Sound enabled by default on init. Removed auto-creation of base_branch file.


## 0.2.3 (2026-03-02)

No significant changes.


## 0.2.2 (2026-03-01)

### Bug Fixes

- fix: expose sync command in shell completions


## 0.2.1 (2026-03-01)

### Features

- Auto-create base_branch file on branch context creation
- Enhanced `bctx sync` command now updates meta and context tags

### Misc

- Reorganize branchctx module into core/, data/, utils/ subpackages


## 0.2.0 (2026-03-01)

### Features

- Per-branch base_branch override via `_branch/base_branch` file
- Shell completion for `branches` subcommands (list, prune)

### Misc

- Remove `symlink`/`default_template` from config, use constants directly
- Remove unused `on_switch` feature
- Rename symlink from `_context` to `_branch`


## 0.1.10 (2026-02-27)

No significant changes.


## 0.1.9 (2026-02-27)

No significant changes.


## 0.1.8 (2026-02-25)

No significant changes.


## 0.1.7 (2026-02-25)

No significant changes.


## 0.1.6 (2026-02-24)

No significant changes.


## 0.1.5 (2026-02-24)

No significant changes.


## 0.1.4 (2026-02-24)

No significant changes.


## 0.1.3 (2026-02-24)

No significant changes.


## 0.1.2 (2026-02-24)

No significant changes.


## 0.1.1 (2026-02-24)

No significant changes.


## 0.1.0 (2026-02-24)

No significant changes.


# Changelog

All notable changes to this project will be documented in this file.
