from __future__ import annotations

import os

from branchctx.constants import CLI_NAME
from branchctx.core.hooks import get_current_branch, get_git_root
from branchctx.core.sync import get_branch_dir
from branchctx.data.branch_base import get_base_branch, save_base_branch
from branchctx.data.config import config_exists


def cmd_base(args: list[str]) -> int:
    git_root = get_git_root()
    if not git_root:
        print("error: not a git repository")
        return 1

    if not config_exists(git_root):
        print(f"error: not initialized. Run '{CLI_NAME} init' first")
        return 1

    branch = get_current_branch(git_root)
    if not branch:
        print("error: could not determine current branch")
        return 1

    branch_dir = get_branch_dir(git_root, branch)

    if not os.path.exists(branch_dir):
        print(f"error: no context for '{branch}'. Run '{CLI_NAME} sync' first")
        return 1

    if not args:
        base = get_base_branch(git_root, branch_dir)
        print(base)
        return 0

    new_base = args[0]
    save_base_branch(branch_dir, new_base)
    print(f"Base branch set to '{new_base}' for '{branch}'")
    return 0
