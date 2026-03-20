from __future__ import annotations

import sys

from branchctx.utils.color import dim, green


def confirm(prompt: str) -> bool:
    try:
        answer = input(f"{prompt} [y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return answer in ("y", "yes")


def _read_key() -> str:
    import termios
    import tty

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            ch2 = sys.stdin.read(1)
            if ch2 == "[":
                ch3 = sys.stdin.read(1)
                if ch3 == "A":
                    return "up"
                if ch3 == "B":
                    return "down"
            return "esc"
        if ch == " ":
            return "space"
        if ch in ("\r", "\n"):
            return "enter"
        if ch == "\x03":
            return "ctrl-c"
        if ch == "a":
            return "a"
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def multi_select(items: list[str], labels: list[str] | None = None) -> list[int]:
    if not items:
        return []

    display = labels if labels else items
    selected: set[int] = set()
    cursor = 0
    total = len(items)

    hint = dim("(↑↓ move, space select, a toggle all, enter confirm)")

    def render():
        sys.stdout.write(f"\r\x1b[{total + 1}A")
        sys.stdout.write(f"\x1b[K{hint}\n")
        for i, label in enumerate(display):
            check = green("✓") if i in selected else " "
            arrow = "›" if i == cursor else " "
            sys.stdout.write(f"\x1b[K  {arrow} [{check}] {label}\n")
        sys.stdout.flush()

    sys.stdout.write(f"{hint}\n")
    for i, label in enumerate(display):
        arrow = "›" if i == cursor else " "
        sys.stdout.write(f"  {arrow} [ ] {label}\n")
    sys.stdout.flush()

    try:
        while True:
            key = _read_key()
            if key == "up" and cursor > 0:
                cursor -= 1
            elif key == "down" and cursor < total - 1:
                cursor += 1
            elif key == "space":
                if cursor in selected:
                    selected.discard(cursor)
                else:
                    selected.add(cursor)
            elif key == "a":
                if len(selected) == total:
                    selected.clear()
                else:
                    selected = set(range(total))
            elif key == "enter":
                render()
                return sorted(selected)
            elif key in ("ctrl-c", "esc"):
                render()
                return []
            render()
    except (EOFError, KeyboardInterrupt):
        return []
