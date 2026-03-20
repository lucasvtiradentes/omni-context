from branchctx.commands.completion import (
    _get_bash_completion,
    _get_fish_completion,
    _get_zsh_completion,
    _safe_func_name,
)


def test_safe_func_name_simple():
    assert _safe_func_name("bctx") == "bctx"


def test_safe_func_name_with_hyphen():
    assert _safe_func_name("branch-ctx") == "branch_ctx"


def test_safe_func_name_with_dots():
    assert _safe_func_name("my.tool") == "my_tool"


def test_zsh_uses_prog_name():
    output = _get_zsh_completion("bctx")
    assert "#compdef bctx" in output
    assert "_bctx()" in output
    assert "compdef _bctx bctx" in output


def test_zsh_different_prog():
    output = _get_zsh_completion("bctxd")
    assert "#compdef bctxd" in output
    assert "_bctxd()" in output
    assert "compdef _bctxd bctxd" in output


def test_zsh_hyphenated_prog():
    output = _get_zsh_completion("branch-ctx")
    assert "#compdef branch-ctx" in output
    assert "_branch_ctx()" in output
    assert "compdef _branch_ctx branch-ctx" in output


def test_bash_uses_prog_name():
    output = _get_bash_completion("bctx")
    assert "_bctx()" in output
    assert "complete -F _bctx bctx" in output


def test_bash_different_prog():
    output = _get_bash_completion("bctxd")
    assert "_bctxd()" in output
    assert "complete -F _bctxd bctxd" in output


def test_fish_uses_prog_name():
    output = _get_fish_completion("bctx")
    assert "complete -c bctx" in output


def test_fish_different_prog():
    output = _get_fish_completion("bctxd")
    assert "complete -c bctxd" in output
    assert "complete -c bctx " not in output


def test_zsh_includes_all_commands():
    output = _get_zsh_completion("bctx")
    for cmd in ["init", "sync", "status", "prune", "base", "template", "completion", "uninstall"]:
        assert cmd in output


def test_bash_includes_all_commands():
    output = _get_bash_completion("bctx")
    for cmd in ["init", "sync", "status", "prune", "base", "template", "completion", "uninstall"]:
        assert cmd in output
