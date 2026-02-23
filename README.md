# omnicontext

Git branch context manager - install post-checkout hooks to sync context across branches.

```
┌─────────────┐    post-checkout    ┌─────────────┐
│  branch A   │ ──────────────────> │  branch B   │
│  context    │                     │  context    │
└─────────────┘                     └─────────────┘
```

## Features

- post-checkout hook - runs on `git checkout` / `git switch`
- global install    - configure once, works on all repos
- custom callbacks  - run your own scripts on branch change

## Commands

```bash
omnicontext install                          # install hook in current repo
omnicontext install --global                 # configure global hooks path
omnicontext install --callback "my-script"   # custom callback command
omnicontext uninstall                        # remove hook from current repo
omnicontext uninstall --global               # remove global hooks config
omnicontext status                           # show hook status
omnicontext --help                           # show help
omnicontext --version                        # show version
```

## Install

```bash
pipx install omnicontext
# pip install omnicontext
```

## Update

```bash
pipx upgrade omnicontext
# pip install --upgrade omnicontext
```

## Uninstall

```bash
pipx uninstall omnicontext
# pip uninstall omnicontext
```

## How it works

### Hook mode (default)

Installs a `post-checkout` git hook that runs after every `git checkout` or `git switch`:

```bash
omnicontext install
git checkout feature-branch  # hook triggers automatically
```

The hook calls `omnicontext on-checkout <old_branch> <new_branch>`.

### Global mode

Configure once, works on all repos:

```bash
omnicontext install --global
```

Sets `git config --global core.hooksPath ~/.git-hooks`.

### Custom callbacks

Run your own script on branch change:

```bash
omnicontext install --callback "python my-sync-script.py"
```

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -v
```

```bash
# dev alias
ln -s $(pwd)/.venv/bin/omnicontext ~/.local/bin/omnicontextd   # install
rm ~/.local/bin/omnicontextd                                    # remove
```
