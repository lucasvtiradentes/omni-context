import os
import stat
import subprocess

from omnicontext.constants import DEFAULT_CALLBACK, HOOK_MARKER, HOOK_NAME, HOOK_TEMPLATE


def get_git_root(path=None):
    cwd = path or os.getcwd()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def get_hook_path(git_root):
    return os.path.join(git_root, ".git", "hooks", HOOK_NAME)


def is_hook_installed(git_root):
    hook_path = get_hook_path(git_root)
    if not os.path.exists(hook_path):
        return False
    with open(hook_path) as f:
        return HOOK_MARKER in f.read()


def install_hook(git_root, callback=None):
    hook_path = get_hook_path(git_root)
    hooks_dir = os.path.dirname(hook_path)

    if not os.path.exists(hooks_dir):
        os.makedirs(hooks_dir)

    if os.path.exists(hook_path):
        with open(hook_path) as f:
            existing = f.read()
        if HOOK_MARKER in existing:
            return "already_installed"
        return "hook_exists"

    callback_cmd = callback or DEFAULT_CALLBACK
    content = HOOK_TEMPLATE.format(marker=HOOK_MARKER, callback=callback_cmd)

    with open(hook_path, "w") as f:
        f.write(content)

    st = os.stat(hook_path)
    os.chmod(hook_path, st.st_mode | stat.S_IEXEC)

    return "installed"


def uninstall_hook(git_root):
    hook_path = get_hook_path(git_root)

    if not os.path.exists(hook_path):
        return "not_installed"

    with open(hook_path) as f:
        content = f.read()

    if HOOK_MARKER not in content:
        return "not_managed"

    os.remove(hook_path)
    return "uninstalled"


def get_current_branch(git_root=None):
    cwd = git_root or os.getcwd()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None
