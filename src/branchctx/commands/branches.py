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
from branchctx.utils.color import green, red, yellow
from branchctx.utils.git import git_delete_branch, git_list_branches, git_list_remote_branches
from branchctx.utils.prompt import multi_select


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


def _collect_branch_info(git_root: str) -> dict[str, dict]:
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
            "local": ctx in {sanitize_branch_name(b) for b in local_branches},
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


def _print_table(all_names: dict[str, dict], current: str | None) -> None:
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


def _cmd_list(git_root: str) -> int:
    all_names = _collect_branch_info(git_root)
    current = get_current_branch(git_root)

    if not all_names:
        print("No branch contexts yet")
        return 0

    print(f"Branch contexts ({len(all_names)}):\n")
    _print_table(all_names, current)

    archived = list_archived_branches(git_root)
    if archived:
        print(f"\nArchived: {len(archived)}")

    return 0


def _confirm(prompt: str) -> bool:
    try:
        answer = input(f"{prompt} [y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return answer in ("y", "yes")


def _cmd_prune(git_root: str) -> int:
    all_names = _collect_branch_info(git_root)
    current = get_current_branch(git_root)
    current_sanitized = sanitize_branch_name(current) if current else None

    no_local = [
        n for n, i in all_names.items() if i["context"] and not i["local"] and i["sanitized"] != current_sanitized
    ]
    no_remote = [
        n
        for n, i in all_names.items()
        if i["context"] and i["local"] and not i["remote"] and i["sanitized"] != current_sanitized
    ]

    if not no_local and not no_remote:
        print("Nothing to prune")
        return 0

    print(f"Branch contexts ({len(all_names)}):\n")
    _print_table(all_names, current)

    to_archive: list[str] = []

    if no_local:
        print(f"\n{len(no_local)} context(s) without {yellow('local branch')}:")
        for n in sorted(no_local):
            print(f"    {n}")
        if _confirm(f"\nArchive these {len(no_local)} context(s)?"):
            to_archive.extend(no_local)

    if no_remote:
        print(f"\n{len(no_remote)} context(s) without {yellow('remote branch')}:")
        for n in sorted(no_remote):
            print(f"    {n}")
        if _confirm(f"\nArchive these {len(no_remote)} context(s)?"):
            to_archive.extend(no_remote)

    deletable = [
        n
        for n, i in all_names.items()
        if i["local"] and i["sanitized"] != current_sanitized and n not in ("main", "master")
    ]

    to_delete: list[str] = []
    if deletable:
        print(f"\nSelect {yellow('local branches')} to delete:")
        labels = []
        for n in sorted(deletable):
            remote_status = green("remote: ✓") if all_names[n]["remote"] else red("remote: ✗")
            labels.append(f"{n}  {remote_status}")
        selected = multi_select(sorted(deletable), labels)
        to_delete = [sorted(deletable)[i] for i in selected]

    if not to_archive and not to_delete:
        print("\nNothing to do.")
        return 0

    if to_archive:
        print(f"\nArchiving {len(to_archive)} context(s):\n")
        for name in sorted(to_archive):
            sanitized = all_names[name]["sanitized"]
            if archive_branch(git_root, sanitized):
                print(f"  {name}")

    if to_delete:
        print(f"\nDeleting {len(to_delete)} local branch(es):\n")
        for name in sorted(to_delete):
            if git_delete_branch(git_root, name):
                print(f"  {name}")
            else:
                if git_delete_branch(git_root, name, force=True):
                    print(f"  {name} (force)")
                else:
                    print(f"  {name} (failed)")

    print(f"\nDone. Use '{CLI_NAME} branches list' to see current contexts.")
    return 0
