from __future__ import annotations

import os
import re
import sys

from branchctx.cmd_registry import get_public_commands


def _get_prog_name() -> str:
    return os.path.basename(sys.argv[0])


def _safe_func_name(prog: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]", "_", prog)


def _get_zsh_completion(prog: str) -> str:
    commands = get_public_commands()
    cmd_lines = "\n        ".join(f"'{name}:{info['desc']}'" for name, info in commands.items())
    func = _safe_func_name(prog)

    return f"""#compdef {prog}

_{func}() {{
    local -a commands
    local git_root templates_dir

    commands=(
        {cmd_lines}
    )

    _get_templates() {{
        git_root="$(git rev-parse --show-toplevel 2>/dev/null)"
        if [[ -n "$git_root" ]]; then
            templates_dir="$git_root/.bctx/templates"
            if [[ -d "$templates_dir" ]]; then
                _values 'template' $(ls "$templates_dir" 2>/dev/null)
            fi
        fi
    }}

    case "$words[2]" in
        template)
            if (( CURRENT == 3 )); then
                _get_templates
            fi
            ;;
        completion)
            if (( CURRENT == 3 )); then
                _values 'shell' 'zsh' 'bash' 'fish'
            fi
            ;;
        *)
            if (( CURRENT == 2 )); then
                _describe -t commands 'command' commands
            fi
            ;;
    esac
}}

compdef _{func} {prog}
"""


def _get_bash_completion(prog: str) -> str:
    commands = get_public_commands()
    cmd_names = " ".join(commands.keys())
    func = _safe_func_name(prog)

    return f'''_{func}() {{
    local cur prev commands git_root templates_dir
    COMPREPLY=()
    cur="${{COMP_WORDS[COMP_CWORD]}}"
    prev="${{COMP_WORDS[COMP_CWORD-1]}}"
    commands="{cmd_names}"

    case "$prev" in
        template)
            git_root="$(git rev-parse --show-toplevel 2>/dev/null)"
            if [[ -n "$git_root" ]]; then
                templates_dir="$git_root/.bctx/templates"
                if [[ -d "$templates_dir" ]]; then
                    COMPREPLY=( $(compgen -W "$(ls "$templates_dir" 2>/dev/null)" -- "$cur") )
                fi
            fi
            return 0
            ;;
        completion)
            COMPREPLY=( $(compgen -W "zsh bash fish" -- "$cur") )
            return 0
            ;;
        {prog})
            COMPREPLY=( $(compgen -W "$commands" -- "$cur") )
            return 0
            ;;
    esac
}}

complete -F _{func} {prog}
'''


def _get_fish_completion(prog: str) -> str:
    commands = get_public_commands()

    cmd_lines = "\n".join(
        f'complete -c {prog} -n "__fish_use_subcommand" -a {name} -d "{info["desc"]}"'
        for name, info in commands.items()
    )

    completion_lines = f'complete -c {prog} -n "__fish_seen_subcommand_from completion" -a "zsh bash fish"'
    template_lines = f'complete -c {prog} -n "__fish_seen_subcommand_from template" -a "(__branchctx_templates)"'

    return f"""complete -c {prog} -f

{cmd_lines}

{completion_lines}

function __branchctx_templates
    set -l git_root (git rev-parse --show-toplevel 2>/dev/null)
    if test -n "$git_root"
        set -l templates_dir "$git_root/.bctx/templates"
        if test -d "$templates_dir"
            ls "$templates_dir" 2>/dev/null
        end
    end
end

{template_lines}
"""


def cmd_completion(args: list[str]) -> int:
    prog = _get_prog_name()

    if not args:
        print(f"usage: {prog} completion <shell>")
        print("shells: zsh, bash, fish")
        print()
        print("Add to your shell config:")
        print(f'  zsh:  eval "$({prog} completion zsh)"')
        print(f'  bash: eval "$({prog} completion bash)"')
        print(f"  fish: {prog} completion fish | source")
        return 1

    shell = args[0].lower()

    generators = {
        "zsh": _get_zsh_completion,
        "bash": _get_bash_completion,
        "fish": _get_fish_completion,
    }

    if shell not in generators:
        print(f"error: unknown shell '{shell}'")
        print("supported: zsh, bash, fish")
        return 1

    print(generators[shell](prog))
    return 0
