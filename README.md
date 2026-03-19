<a name="TOC"></a>

<h1 align="center">branch-context</h1>

<p align="center">
  <a href="#-overview">Overview</a> •
  <a href="#-features">Features</a> •
  <a href="#-motivation">Motivation</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-commands">Commands</a> •
  <a href="#-configuration">Configuration</a> •
  <a href="#-contributing">Contributing</a> •
  <a href="#-license">License</a>
</p>

<div width="100%" align="center">
  <img src="https://cdn.jsdelivr.net/gh/lucasvtiradentes/branch-context@main/.github/images/divider.png" />
</div>

## 🎺 Overview<a href="#TOC"><img align="right" src="https://cdn.jsdelivr.net/gh/lucasvtiradentes/branch-context@main/.github/images/up_arrow.png" width="22"></a>

Git branch context manager that automatically syncs context folders across branches. Each branch gets an isolated context directory containing notes, metadata, and files that follow the branch lifecycle.

<div align="center">
  <img src="https://cdn.jsdelivr.net/gh/lucasvtiradentes/branch-context@main/.github/images/demo.gif" width="650" />
</div>

<div align="center">
<details>
<summary>How it works</summary>
<div align="left">

```
  git checkout feature/login
              │
              ▼
      ┌────────────────┐
      │  post-checkout │
      │    git hook    │
      └───────┬────────┘
              │
              ▼
    context exists? ──NO──▶ copy template (by prefix rules)
              │                     │
             YES                    │
              │◀────────────────────┘
              ▼
    ┌───────────────────────────────────────────┐
    │ _branch/ → .bctx/branches/feature-login   │
    └───────────────────────────────────────────┘
              │
              ▼
    ┌─────────────────────────────────┐
    │ • update meta.json (commits)    │
    │ • update <bctx:*> tags          │
    │ • play sound (if enabled)       │
    └─────────────────────────────────┘
```

</div>
</details>
</div>

## ⭐ Features<a href="#TOC"><img align="right" src="https://cdn.jsdelivr.net/gh/lucasvtiradentes/branch-context@main/.github/images/up_arrow.png" width="22"></a>

- Isolated contexts - per-branch folder, `_branch/` symlink to current
- Auto-sync         - git hook triggers on checkout
- Templates         - per-prefix rules (feature/, bugfix/, etc.)
- Meta tracking     - commits, changed files, timestamps
- Context tags      - `<bctx:commits>` and `<bctx:files>` auto-updated

## ❓ Motivation<a href="#TOC"><img align="right" src="https://cdn.jsdelivr.net/gh/lucasvtiradentes/branch-context@main/.github/images/up_arrow.png" width="22"></a>

When working on multiple branches, it's easy to lose track of what you were doing. This tool helps you:

- Keep notes, TODOs, and context organized per branch
- Provide context to AI coding assistants (Claude Code, Codex, Cursor, etc.) via `_branch/context.md`
- Track commits and changed files automatically with `<bctx:*>` tags

The `_branch/` symlink gives AI tools a stable path to read your current branch context, helping them understand what you're working on.

## 🚀 Quick Start<a href="#TOC"><img align="right" src="https://cdn.jsdelivr.net/gh/lucasvtiradentes/branch-context@main/.github/images/up_arrow.png" width="22"></a>

Install:

```bash
brew install pipx         # if not installed (macOS/linux)
pipx install branch-ctx   # or: pip install branch-ctx
```

Setup in your repo:

```bash
cd your-repo
bctx init                        # creates .bctx/ + installs hook

git checkout -b feature/new      # auto-creates context from template
cat _branch/context.md
```

## 📖 Commands<a href="#TOC"><img align="right" src="https://cdn.jsdelivr.net/gh/lucasvtiradentes/branch-context@main/.github/images/up_arrow.png" width="22"></a>

```bash
bctx init                          # initialize + install hook
bctx sync                          # sync context + update meta/tags
bctx status                        # show status and health
bctx branches list                 # list all branch contexts
bctx branches prune                # archive orphan contexts
bctx template                      # select template interactively
bctx base                          # show current base branch
bctx base origin/develop           # set base branch
bctx template feature              # apply feature template
bctx completion zsh                # generate shell completion
bctx uninstall                     # remove hook
```

Alias: `branch-ctx` works too.

## ⚙️ Configuration<a href="#TOC"><img align="right" src="https://cdn.jsdelivr.net/gh/lucasvtiradentes/branch-context@main/.github/images/up_arrow.png" width="22"></a>

<div align="center">
<details>
<summary>Structure</summary>
<div align="left">

```
.bctx/
├── config.json
├── templates/
│   ├── _default/            # fallback template
│   │   └── context.md
│   └── feature/             # template for feature/* branches
│       └── context.md
└── branches/                # gitignored
    ├── meta.json            # branch metadata (commits, files, timestamps)
    ├── main/
    │   └── context.md
    └── feature-login/
        ├── context.md
        └── base_branch      # optional per-branch base override

_branch -> .bctx/branches/main/   # symlink to current
```

</div>
</details>
</div>

<div align="center">
<details>
<summary>Config file</summary>
<div align="left">

`.bctx/config.json`:

```json
{
  "default_base_branch": "origin/main",
  "sound": true,
  "sound_file": "/path/to/custom.wav",
  "template_rules": [
    {"prefix": "feature/", "template": "feature"},
    {"prefix": "fix/", "template": "fix"},
    {"prefix": "bugfix/", "template": "fix"},
    {"prefix": "chore/", "template": "chore"},
    {"prefix": "refactor/", "template": "chore"}
  ]
}
```

| Key                   | Description                                           |
|-----------------------|-------------------------------------------------------|
| `default_base_branch` | base branch for diff/commits (default: `origin/main`) |
| `sound`               | play sound on sync (default: `true`)                  |
| `sound_file`          | custom sound file (default: bundled sound)            |
| `template_rules`      | per-prefix template mapping (fallback: _default)      |

Per-branch base override: `bctx base <branch-name>`

</div>
</details>
</div>

<div align="center">
<details>
<summary>Shell Completion</summary>
<div align="left">

```bash
# zsh - add to ~/.zshrc
eval "$(bctx completion zsh)"

# bash - add to ~/.bashrc
eval "$(bctx completion bash)"

# fish
bctx completion fish | source
```

</div>
</details>
</div>

## 🤝 Contributing<a href="#TOC"><img align="right" src="https://cdn.jsdelivr.net/gh/lucasvtiradentes/branch-context@main/.github/images/up_arrow.png" width="22"></a>

```bash
make install    # venv + deps + pre-commit
make test       # run tests
make format     # ruff fix + format
make check      # validate ruff rules
make build      # build package
make clean      # remove venv + dist
```

Dev alias:

```bash
ln -sf $(pwd)/.venv/bin/bctx ~/.local/bin/bctxd   # install
rm ~/.local/bin/bctxd                             # remove
```

## 📜 License<a href="#TOC"><img align="right" src="https://cdn.jsdelivr.net/gh/lucasvtiradentes/branch-context@main/.github/images/up_arrow.png" width="22"></a>

This project is licensed under the [MIT License](LICENSE).

<div width="100%" align="center">
  <img src="https://cdn.jsdelivr.net/gh/lucasvtiradentes/branch-context@main/.github/images/divider.png" />
</div>

<br />

<div align="center">
  <a target="_blank" href="https://www.linkedin.com/in/lucasvtiradentes/"><img src="https://img.shields.io/badge/-linkedin-blue?logo=Linkedin&logoColor=white" alt="LinkedIn"></a>
  <a target="_blank" href="mailto:lucasvtiradentes@gmail.com"><img src="https://img.shields.io/badge/-email-red?logo=Gmail&logoColor=white" alt="Email"></a>
  <a target="_blank" href="https://github.com/lucasvtiradentes"><img src="https://img.shields.io/badge/-github-gray?logo=Github&logoColor=white" alt="GitHub"></a>
</div>
