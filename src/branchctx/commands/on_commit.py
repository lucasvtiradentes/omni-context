from __future__ import annotations

import os

from branchctx.config import Config, config_exists
from branchctx.context_tags import update_context_tags
from branchctx.hooks import get_git_root


def cmd_on_commit(_args: list[str]) -> int:
    git_root = get_git_root()
    if not git_root:
        return 1

    if not config_exists(git_root):
        return 0

    config = Config.load(git_root)
    if not config.changed_files.enabled:
        return 0

    context_dir = os.path.join(git_root, config.symlink)
    if not os.path.exists(context_dir):
        return 0

    updates = update_context_tags(
        workspace=git_root,
        context_dir=context_dir,
        base_branch=config.changed_files.base_branch,
        show_stats=config.changed_files.show_stats,
    )

    if updates:
        print(f"Updated {len(updates)} tag(s) in context files:")
        for update in updates:
            rel_path = os.path.relpath(update.file, git_root)
            print(f"  {rel_path}: <{update.tag}>")

    return 0
