from __future__ import annotations

import os
import shutil
import stat
import sys
from typing import Literal

from branchctx.assets import get_post_checkout_hook_template, get_post_commit_hook_template
from branchctx.constants import CLI_NAME, GIT_DIR, HOOK_MARKER, HOOK_POST_CHECKOUT
from branchctx.git import git_current_branch, git_root

HookType = Literal["post-checkout", "post-commit"]
HookInstallResult = Literal["installed", "already_installed", "hook_exists"]
HookUninstallResult = Literal["uninstalled", "not_installed", "not_managed"]


def get_branchctx_path() -> str:
    script_name = CLI_NAME

    if getattr(sys, "frozen", False):
        return sys.executable

    bin_dir = os.path.dirname(sys.executable)
    candidate = os.path.join(bin_dir, script_name)
    if os.path.exists(candidate):
        return candidate

    found = shutil.which(script_name)
    if found:
        return found

    return script_name


def get_callback(hook_type: HookType) -> str:
    branchctx_path = get_branchctx_path()
    if hook_type == HOOK_POST_CHECKOUT:
        return f'"{branchctx_path}" on-checkout'
    return f'"{branchctx_path}" on-commit'


def get_git_root(path: str | None = None) -> str | None:
    return git_root(path or os.getcwd())


def get_hook_path(git_root: str, hook_type: HookType = HOOK_POST_CHECKOUT) -> str:
    return os.path.join(git_root, GIT_DIR, "hooks", hook_type)


def is_hook_installed(git_root: str, hook_type: HookType = HOOK_POST_CHECKOUT) -> bool:
    hook_path = get_hook_path(git_root, hook_type)
    if not os.path.exists(hook_path):
        return False
    with open(hook_path) as f:
        return HOOK_MARKER in f.read()


def _get_hook_template(hook_type: HookType) -> str:
    if hook_type == HOOK_POST_CHECKOUT:
        return get_post_checkout_hook_template()
    return get_post_commit_hook_template()


def install_hook(git_root: str, hook_type: HookType = HOOK_POST_CHECKOUT) -> HookInstallResult:
    hook_path = get_hook_path(git_root, hook_type)
    hooks_dir = os.path.dirname(hook_path)

    if not os.path.exists(hooks_dir):
        os.makedirs(hooks_dir)

    if os.path.exists(hook_path):
        with open(hook_path) as f:
            existing = f.read()
        if HOOK_MARKER in existing:
            return "already_installed"
        return "hook_exists"

    template = _get_hook_template(hook_type)
    content = template.format(marker=HOOK_MARKER, callback=get_callback(hook_type))

    with open(hook_path, "w") as f:
        f.write(content)

    st = os.stat(hook_path)
    os.chmod(hook_path, st.st_mode | stat.S_IEXEC)

    return "installed"


def uninstall_hook(git_root: str, hook_type: HookType = HOOK_POST_CHECKOUT) -> HookUninstallResult:
    hook_path = get_hook_path(git_root, hook_type)

    if not os.path.exists(hook_path):
        return "not_installed"

    with open(hook_path) as f:
        content = f.read()

    if HOOK_MARKER not in content:
        return "not_managed"

    os.remove(hook_path)
    return "uninstalled"


def get_current_branch(path: str | None = None) -> str | None:
    return git_current_branch(path or os.getcwd())
