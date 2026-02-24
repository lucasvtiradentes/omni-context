import os
import tempfile

import pytest

from branchctx.config import Config, get_branches_dir, get_template_dir
from branchctx.constants import HOOK_POST_CHECKOUT, HOOK_POST_COMMIT
from branchctx.context_tags import update_context_tags
from branchctx.git import git_add, git_checkout, git_commit, git_config, git_init
from branchctx.hooks import install_hook
from branchctx.sync import sync_branch


@pytest.fixture
def git_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        git_init(tmpdir, "main")
        git_config(tmpdir, "user.email", "test@test.com")
        git_config(tmpdir, "user.name", "Test")

        readme = os.path.join(tmpdir, "README.md")
        with open(readme, "w") as f:
            f.write("# Test")

        git_add(tmpdir)
        git_commit(tmpdir, "init")

        template_dir = get_template_dir(tmpdir)
        branches_dir = get_branches_dir(tmpdir)

        os.makedirs(template_dir)
        os.makedirs(branches_dir)

        config = Config()
        config.save(tmpdir)

        with open(os.path.join(template_dir, "context.md"), "w") as f:
            f.write("# Context\n<bctx:commits></bctx:commits>\n<bctx:files></bctx:files>")

        install_hook(tmpdir, HOOK_POST_CHECKOUT)
        install_hook(tmpdir, HOOK_POST_COMMIT)

        yield tmpdir


def test_update_tags_on_feature_branch(git_repo):
    sync_branch(git_repo, "main")

    git_checkout(git_repo, "feature/test", create=True)
    sync_branch(git_repo, "feature/test")

    test_file = os.path.join(git_repo, "new_file.py")
    with open(test_file, "w") as f:
        f.write("print('hello')")

    git_add(git_repo)
    git_commit(git_repo, "feat: add new file")

    config = Config.load(git_repo)
    context_dir = os.path.join(git_repo, config.symlink)

    updates = update_context_tags(
        workspace=git_repo,
        context_dir=context_dir,
        base_branch="main",
    )

    assert len(updates) == 2

    context_file = os.path.join(context_dir, "context.md")
    with open(context_file) as f:
        content = f.read()

    assert "feat: add new file" in content
    assert "new_file.py" in content


def test_update_tags_shows_sync_message_on_main(git_repo):
    sync_branch(git_repo, "main")

    config = Config.load(git_repo)
    context_dir = os.path.join(git_repo, config.symlink)

    updates = update_context_tags(
        workspace=git_repo,
        context_dir=context_dir,
        base_branch="main",
    )

    assert len(updates) == 2

    context_file = os.path.join(context_dir, "context.md")
    with open(context_file) as f:
        content = f.read()

    assert "N/A - in sync with main" in content


def test_update_tags_multiple_commits(git_repo):
    sync_branch(git_repo, "main")

    git_checkout(git_repo, "feature/multi", create=True)
    sync_branch(git_repo, "feature/multi")

    for i in range(3):
        test_file = os.path.join(git_repo, f"file{i}.py")
        with open(test_file, "w") as f:
            f.write(f"# file {i}")
        git_add(git_repo)
        git_commit(git_repo, f"feat: add file {i}")

    config = Config.load(git_repo)
    context_dir = os.path.join(git_repo, config.symlink)

    update_context_tags(
        workspace=git_repo,
        context_dir=context_dir,
        base_branch="main",
    )

    context_file = os.path.join(context_dir, "context.md")
    with open(context_file) as f:
        content = f.read()

    assert "feat: add file 0" in content
    assert "feat: add file 1" in content
    assert "feat: add file 2" in content


def test_update_tags_shows_stats(git_repo):
    sync_branch(git_repo, "main")

    git_checkout(git_repo, "feature/stats", create=True)
    sync_branch(git_repo, "feature/stats")

    test_file = os.path.join(git_repo, "test.py")
    with open(test_file, "w") as f:
        f.write("print('test')")

    git_add(git_repo)
    git_commit(git_repo, "feat: test")

    config = Config.load(git_repo)
    context_dir = os.path.join(git_repo, config.symlink)

    update_context_tags(
        workspace=git_repo,
        context_dir=context_dir,
        base_branch="main",
    )

    context_file = os.path.join(context_dir, "context.md")
    with open(context_file) as f:
        content = f.read()

    assert "test.py" in content
    assert "(+" in content
    assert "-" in content


def test_no_tags_in_file_skips_silently(git_repo):
    sync_branch(git_repo, "main")

    config = Config.load(git_repo)
    context_dir = os.path.join(git_repo, config.symlink)
    context_file = os.path.join(context_dir, "context.md")

    with open(context_file, "w") as f:
        f.write("# No tags here")

    updates = update_context_tags(
        workspace=git_repo,
        context_dir=context_dir,
        base_branch="main",
    )

    assert len(updates) == 0
