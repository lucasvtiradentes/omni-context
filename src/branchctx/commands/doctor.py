from __future__ import annotations

import os

from branchctx.config import Config, config_exists, get_templates_dir, list_templates
from branchctx.constants import CLI_NAME, DEFAULT_TEMPLATE, HOOK_POST_CHECKOUT, HOOK_POST_COMMIT
from branchctx.git import git_list_branches
from branchctx.hooks import get_git_root, is_hook_installed
from branchctx.sync import list_branches, sanitize_branch_name

STATUS_OK = "[ok]"
STATUS_ERROR = "[!!]"
STATUS_WARN = "[--]"


def cmd_doctor(_args: list[str]) -> int:
    git_root = get_git_root()
    if not git_root:
        print("error: not a git repository")
        return 1

    if not config_exists(git_root):
        print(f"error: {CLI_NAME} not initialized")
        print(f"run: {CLI_NAME} init")
        return 1

    issues = []
    warnings = []

    print("Running diagnostics...\n")

    if is_hook_installed(git_root, HOOK_POST_CHECKOUT):
        print(f"{STATUS_OK} {HOOK_POST_CHECKOUT} hook installed")
    else:
        issues.append(f"{HOOK_POST_CHECKOUT} hook not installed")
        print(f"{STATUS_ERROR} {HOOK_POST_CHECKOUT} hook not installed")

    config = Config.load(git_root)
    if config.changed_files.enabled:
        if is_hook_installed(git_root, HOOK_POST_COMMIT):
            print(f"{STATUS_OK} {HOOK_POST_COMMIT} hook installed")
        else:
            warnings.append(f"{HOOK_POST_COMMIT} hook not installed (changed_files enabled)")
            print(f"{STATUS_WARN} {HOOK_POST_COMMIT} hook not installed")

    templates_dir = get_templates_dir(git_root)
    if os.path.exists(templates_dir):
        print(f"{STATUS_OK} templates/ exists")
    else:
        issues.append("templates/ missing")
        print(f"{STATUS_ERROR} templates/ missing")

    templates = list_templates(git_root)
    if DEFAULT_TEMPLATE in templates:
        print(f"{STATUS_OK} {DEFAULT_TEMPLATE} template exists")
    else:
        issues.append(f"{DEFAULT_TEMPLATE} template missing")
        print(f"{STATUS_ERROR} {DEFAULT_TEMPLATE} template missing")

    symlink_path = os.path.join(git_root, config.symlink)
    if os.path.islink(symlink_path):
        target = os.readlink(symlink_path)
        if os.path.exists(os.path.join(git_root, target)):
            print(f"{STATUS_OK} symlink valid -> {target}")
        else:
            issues.append("symlink points to non-existent target")
            print(f"{STATUS_ERROR} symlink broken -> {target}")
    elif os.path.exists(symlink_path):
        issues.append("symlink path exists but is not a symlink")
        print(f"{STATUS_ERROR} {config.symlink} is not a symlink")
    else:
        warnings.append(f"symlink not set (run '{CLI_NAME} sync')")
        print(f"{STATUS_WARN} symlink not set")

    git_branches = git_list_branches(git_root)
    git_branches_sanitized = {sanitize_branch_name(b) for b in git_branches}
    context_branches = set(list_branches(git_root))

    orphans = context_branches - git_branches_sanitized
    if orphans:
        warnings.append(f"orphan contexts: {', '.join(sorted(orphans))}")
        print(f"{STATUS_WARN} orphan contexts: {', '.join(sorted(orphans))}")
    else:
        print(f"{STATUS_OK} no orphan contexts")

    print()
    if issues:
        print(f"Issues: {len(issues)}")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    elif warnings:
        print(f"Warnings: {len(warnings)}")
        for warning in warnings:
            print(f"  - {warning}")
        return 0
    else:
        print("All checks passed")
        return 0
