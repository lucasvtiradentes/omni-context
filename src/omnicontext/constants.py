CLI_NAME = "omnicontext"
PACKAGE_NAME = "omnicontext"
ENV_BRANCH = "OMNICONTEXT_BRANCH"

GIT_DIR = ".git"
HOOK_NAME = "post-checkout"
HOOK_MARKER = "# omnicontext-managed"
GLOBAL_HOOKS_DIR = "~/.git-hooks"
DEFAULT_SOUND_FILE = "notification.oga"
DEFAULT_SYNC_PROVIDER = "local"

CONFIG_DIR = ".omnicontext"
CONFIG_FILE = "config.json"
TEMPLATE_DIR = "template"
BRANCHES_DIR = "branches"
DEFAULT_SYMLINK = ".branch-context"

DEFAULT_TEMPLATE_CONTEXT = """# Branch Context

## Objective

N/A

## Notes

N/A

## Tasks

- [ ] TODO
"""

GITIGNORE_BRANCHES = """# Ignore all branch contexts (local only)
*
!.gitignore
"""

GITIGNORE_ROOT = """branches/
"""

HOOK_TEMPLATE = """#!/bin/bash
{marker}

PREV_HEAD="$1"
NEW_HEAD="$2"
CHECKOUT_TYPE="$3"

if [ "$CHECKOUT_TYPE" == "1" ]; then
    OLD_BRANCH=$(git rev-parse --abbrev-ref @{{-1}} 2>/dev/null || echo "unknown")
    NEW_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    {callback} "$OLD_BRANCH" "$NEW_BRANCH" "$PREV_HEAD" "$NEW_HEAD"
fi
"""
