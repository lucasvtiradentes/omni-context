from __future__ import annotations

from branchctx.constants import CLI_NAME
from branchctx.core.hooks import get_current_branch, get_git_root
from branchctx.core.sync import (
    archive_branch,
    list_archived_branches,
    list_branches,
    sanitize_branch_name,
)
from branchctx.data.config import config_exists
from branchctx.utils.color import green, red
from branchctx.utils.git import git_list_branches, git_list_remote_branches


def _print_help():
    print("""usage: bctx branches <command>

Commands:
  list    List all branch contexts
  prune   Archive orphan contexts""")


def cmd_branches(args: list[str]) -> int:
    if not args:
        _print_help()
        return 1

    subcommand = args[0]

    if subcommand in ("-h", "--help"):
        _print_help()
        return 0

    git_root = get_git_root()
    if not git_root:
        print("error: not a git repository")
        return 1

    if not config_exists(git_root):
        print(f"error: not initialized. Run '{CLI_NAME} init' first")
        return 1

    if subcommand == "list":
        return _cmd_list(git_root)
    elif subcommand == "prune":
        return _cmd_prune(git_root)
    else:
        print(f"error: unknown subcommand '{subcommand}'")
        _print_help()
        return 1


def _cmd_list(git_root: str) -> int:
    context_dirs = set(list_branches(git_root))
    local_branches = git_list_branches(git_root)
    remote_branches = set(git_list_remote_branches(git_root))
    current = get_current_branch(git_root)

    local_to_sanitized = {b: sanitize_branch_name(b) for b in local_branches}
    sanitized_to_local = {v: k for k, v in local_to_sanitized.items()}

    all_names: dict[str, dict[str, bool]] = {}

    for ctx in context_dirs:
        original = sanitized_to_local.get(ctx, ctx)
        all_names[original] = {
            "context": True,
            "local": ctx in {sanitize_branch_name(b) for b in local_branches},
            "remote": original in remote_branches,
        }

    for branch in local_branches:
        if branch not in all_names:
            sanitized = sanitize_branch_name(branch)
            if sanitized not in context_dirs:
                all_names[branch] = {
                    "context": False,
                    "local": True,
                    "remote": branch in remote_branches,
                }

    if not all_names:
        print("No branch contexts yet")
        return 0

    group_all = []
    group_ctx_local = []
    group_ctx_only = []

    for name, info in all_names.items():
        if info["context"] and info["local"] and info["remote"]:
            group_all.append(name)
        elif info["context"] and info["local"]:
            group_ctx_local.append(name)
        else:
            group_ctx_only.append(name)

    group_all.sort()
    group_ctx_local.sort()
    group_ctx_only.sort()

    groups = [g for g in [group_all, group_ctx_local, group_ctx_only] if g]

    max_len = max(len(n) for n in all_names)
    col_w = max(max_len, 6)

    yes = green("✓")
    no = red("✗")

    print(f"Branch contexts ({len(all_names)}):\n")
    print(f"    {'Branch':<{col_w}}  Context  Local  Remote")
    print(f"    {'─' * col_w}  ───────  ─────  ──────")

    for i, group in enumerate(groups):
        if i > 0:
            print(f"    {'─' * col_w}  ───────  ─────  ──────")
        for name in group:
            info = all_names[name]
            marker = "*" if current and name == current else " "
            ctx = yes if info["context"] else no
            local = yes if info["local"] else no
            remote = yes if info["remote"] else no
            print(f"  {marker} {name:<{col_w}}     {ctx}       {local}      {remote}")

    archived = list_archived_branches(git_root)
    if archived:
        print(f"\nArchived: {len(archived)}")

    return 0


def _cmd_prune(git_root: str) -> int:
    branches = list_branches(git_root)
    git_branches = git_list_branches(git_root)
    git_branches_sanitized = {sanitize_branch_name(b) for b in git_branches}

    orphans = set(branches) - git_branches_sanitized

    if not orphans:
        print("No orphan contexts to prune")
        return 0

    print(f"Archiving {len(orphans)} orphan contexts:\n")
    for orphan in sorted(orphans):
        if archive_branch(git_root, orphan):
            print(f"  {orphan}")

    print(f"\nDone. Use '{CLI_NAME} branches list' to see current contexts.")
    return 0
