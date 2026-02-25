import os
import tempfile

import pytest

from branchctx.config import Config, get_branches_dir, get_template_dir
from branchctx.git import git_add, git_checkout, git_commit, git_config, git_init
from branchctx.meta import (
    archive_branch_meta,
    create_branch_meta,
    delete_branch_meta,
    get_branch_meta,
    load_archived_meta,
    load_branch_meta,
    update_branch_meta,
)
from branchctx.sync import sanitize_branch_name, sync_branch


@pytest.fixture
def git_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        git_init(tmpdir, "main")
        git_config(tmpdir, "user.email", "test@test.com")
        git_config(tmpdir, "user.name", "Test User")

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
            f.write("# Context")

        yield tmpdir


def test_create_branch_meta(git_repo):
    branch_key = "feature-test"
    create_branch_meta(git_repo, branch_key, "feature/test")

    meta = get_branch_meta(git_repo, branch_key)
    assert meta is not None
    assert meta["branch"] == "feature/test"
    assert meta["author"] == "Test User"
    assert "created_at" in meta
    assert "updated_at" in meta


def test_create_branch_meta_does_not_overwrite(git_repo):
    branch_key = "feature-test"
    create_branch_meta(git_repo, branch_key, "feature/test")

    original_created = get_branch_meta(git_repo, branch_key)["created_at"]

    create_branch_meta(git_repo, branch_key, "feature/test")

    meta = get_branch_meta(git_repo, branch_key)
    assert meta["created_at"] == original_created


def test_update_branch_meta(git_repo):
    sync_branch(git_repo, "main")
    git_checkout(git_repo, "feature/test", create=True)

    branch_key = sanitize_branch_name("feature/test")
    create_branch_meta(git_repo, branch_key, "feature/test")

    test_file = os.path.join(git_repo, "new_file.py")
    with open(test_file, "w") as f:
        f.write("print('hello')")

    git_add(git_repo)
    git_commit(git_repo, "feat: add new file")

    update_branch_meta(git_repo, branch_key, "main")

    meta = get_branch_meta(git_repo, branch_key)
    assert meta["last_commit"] is not None
    assert meta["last_commit"]["message"] == "feat: add new file"
    assert "feat: add new file" in meta["commits"]
    assert "new_file.py" in meta["changed_files"]


def test_archive_branch_meta(git_repo):
    branch_key = "feature-old"
    create_branch_meta(git_repo, branch_key, "feature/old")

    archive_branch_meta(git_repo, branch_key)

    assert get_branch_meta(git_repo, branch_key) is None

    archived = load_archived_meta(git_repo)
    assert branch_key in archived
    assert archived[branch_key]["branch"] == "feature/old"


def test_delete_branch_meta(git_repo):
    branch_key = "feature-temp"
    create_branch_meta(git_repo, branch_key, "feature/temp")

    assert get_branch_meta(git_repo, branch_key) is not None

    delete_branch_meta(git_repo, branch_key)

    assert get_branch_meta(git_repo, branch_key) is None


def test_load_branch_meta_empty(git_repo):
    meta = load_branch_meta(git_repo)
    assert meta == {}


def test_multiple_branches_in_meta(git_repo):
    create_branch_meta(git_repo, "main", "main")
    create_branch_meta(git_repo, "feature-a", "feature/a")
    create_branch_meta(git_repo, "feature-b", "feature/b")

    meta = load_branch_meta(git_repo)
    assert len(meta) == 3
    assert "main" in meta
    assert "feature-a" in meta
    assert "feature-b" in meta
