from __future__ import annotations

from branchctx.commands._branches import collect_branch_info, print_table
from branchctx.constants import CLI_NAME
from branchctx.core.hooks import get_current_branch, get_git_root
from branchctx.core.sync import (
    archive_branch,
    list_archived_branches,
    sanitize_branch_name,
)
from branchctx.data.config import config_exists
from branchctx.utils.color import green, red, yellow
from branchctx.utils.git import git_delete_branch
from branchctx.utils.prompt import confirm, multi_select


def cmd_prune(_args: list[str]) -> int:
    git_root = get_git_root()
    if not git_root:
        print("error: not a git repository")
        return 1

    if not config_exists(git_root):
        print(f"error: not initialized. Run '{CLI_NAME} init' first")
        return 1

    all_names = collect_branch_info(git_root)
    current = get_current_branch(git_root)
    current_sanitized = sanitize_branch_name(current) if current else None

    no_local = [n for n, i in all_names.items() if i.context and not i.local and i.sanitized != current_sanitized]

    deletable = [
        n for n, i in all_names.items() if i.local and i.sanitized != current_sanitized and n not in ("main", "master")
    ]

    if not no_local and not deletable:
        print("Nothing to prune")
        return 0

    print(f"Branch contexts ({len(all_names)}):\n")
    print_table(all_names, current)

    archived = list_archived_branches(git_root)
    if archived:
        print(f"\nArchived: {len(archived)}")

    to_delete: list[str] = []
    if deletable:
        deletable_sorted = sorted(deletable)
        print(f"\nSelect {yellow('local branches')} to delete:")
        labels = []
        for n in deletable_sorted:
            remote_status = green("remote: ✓") if all_names[n].remote else red("remote: ✗")
            labels.append(f"{n}  {remote_status}")
        selected = multi_select(deletable_sorted, labels)
        to_delete = [deletable_sorted[i] for i in selected]

    deleted: list[str] = []
    if to_delete:
        print(f"\nDeleting {len(to_delete)} local branch(es):\n")
        for name in sorted(to_delete):
            if git_delete_branch(git_root, name):
                print(f"  {name}")
                deleted.append(name)
            else:
                print(f"  {name} (not fully merged, skipped)")

    for name in deleted:
        info = all_names[name]
        if info.context and name not in no_local:
            no_local.append(name)

    to_archive: list[str] = []
    if no_local:
        print(f"\n{len(no_local)} context(s) without {yellow('local branch')}:")
        for n in sorted(no_local):
            print(f"    {n}")
        if confirm(f"\nArchive these {len(no_local)} context(s)?"):
            to_archive.extend(no_local)

    if not to_archive and not deleted:
        print("\nNothing to do.")
        return 0

    if to_archive:
        print(f"\nArchiving {len(to_archive)} context(s):\n")
        for name in sorted(to_archive):
            sanitized = all_names[name].sanitized
            if archive_branch(git_root, sanitized):
                print(f"  {name}")

    print(f"\nDone. Use '{CLI_NAME} status' to see current contexts.")
    return 0
