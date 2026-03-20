import os
import subprocess
import tempfile

import pytest

from branchctx.commands._branches import collect_branch_info
from branchctx.commands.prune import cmd_prune
from branchctx.commands.status import cmd_status
from branchctx.core.sync import sync_branch
from branchctx.data.config import Config, get_branches_dir, get_template_dir
from branchctx.utils.git import git_add, git_checkout, git_commit, git_config, git_init


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

        original_cwd = os.getcwd()
        os.chdir(tmpdir)
        yield tmpdir
        os.chdir(original_cwd)


def test_status_shows_branches(git_repo, capsys):
    sync_branch(git_repo, "main")
    git_checkout(git_repo, "feature/test", create=True)
    sync_branch(git_repo, "feature/test")

    cmd_status([])
    captured = capsys.readouterr()
    assert "main" in captured.out
    assert "feature" in captured.out


def test_status_shows_current_marker(git_repo, capsys):
    sync_branch(git_repo, "main")

    cmd_status([])
    captured = capsys.readouterr()
    assert "* main" in captured.out


def test_status_shows_orphan_warning(git_repo, capsys):
    sync_branch(git_repo, "main")
    git_checkout(git_repo, "feature/old", create=True)
    sync_branch(git_repo, "feature/old")
    git_checkout(git_repo, "main")
    subprocess.run(["git", "branch", "-D", "feature/old"], cwd=git_repo, capture_output=True)

    cmd_status([])
    captured = capsys.readouterr()
    assert "orphan" in captured.out


def test_prune_no_orphans(git_repo, capsys):
    sync_branch(git_repo, "main")

    result = cmd_prune([])
    assert result == 0
    captured = capsys.readouterr()
    assert "Nothing to prune" in captured.out


def test_prune_archives_orphans(git_repo, capsys, monkeypatch):
    sync_branch(git_repo, "main")
    git_checkout(git_repo, "feature/old", create=True)
    sync_branch(git_repo, "feature/old")
    git_checkout(git_repo, "main")
    subprocess.run(["git", "branch", "-D", "feature/old"], cwd=git_repo, capture_output=True)

    inputs = iter(["y", "n"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    result = cmd_prune([])
    assert result == 0
    captured = capsys.readouterr()
    assert "Archiving" in captured.out
    assert "feature" in captured.out


def test_collect_branch_info_basic(git_repo):
    sync_branch(git_repo, "main")
    info = collect_branch_info(git_repo)
    assert "main" in info
    assert info["main"]["context"] is True
    assert info["main"]["local"] is True


def test_collect_branch_info_orphan(git_repo):
    sync_branch(git_repo, "main")
    git_checkout(git_repo, "feature/test", create=True)
    sync_branch(git_repo, "feature/test")
    git_checkout(git_repo, "main")
    subprocess.run(["git", "branch", "-D", "feature/test"], cwd=git_repo, capture_output=True)

    info = collect_branch_info(git_repo)
    orphans = [n for n, i in info.items() if i["context"] and not i["local"]]
    assert len(orphans) == 1
