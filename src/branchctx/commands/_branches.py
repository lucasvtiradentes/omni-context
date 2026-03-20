from __future__ import annotations

from branchctx.core.sync import (
    list_branches,
    sanitize_branch_name,
)
from branchctx.utils.color import green, red
from branchctx.utils.git import git_list_branches, git_list_remote_branches


def collect_branch_info(git_root: str) -> dict[str, dict]:
    context_dirs = set(list_branches(git_root))
    local_branches = git_list_branches(git_root)
    remote_branches = set(git_list_remote_branches(git_root))

    local_to_sanitized = {b: sanitize_branch_name(b) for b in local_branches}
    sanitized_to_local = {v: k for k, v in local_to_sanitized.items()}

    all_names: dict[str, dict] = {}

    for ctx in context_dirs:
        original = sanitized_to_local.get(ctx, ctx)
        all_names[original] = {
            "context": True,
            "local": ctx in sanitized_to_local,
            "remote": original in remote_branches,
            "sanitized": ctx,
        }

    for branch in local_branches:
        if branch not in all_names:
            sanitized = sanitize_branch_name(branch)
            if sanitized not in context_dirs:
                all_names[branch] = {
                    "context": False,
                    "local": True,
                    "remote": branch in remote_branches,
                    "sanitized": sanitized,
                }

    return all_names


def print_table(all_names: dict[str, dict], current: str | None) -> None:
    if not all_names:
        return

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
