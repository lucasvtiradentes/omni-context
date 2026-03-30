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


def _is_interactive() -> bool:
    return hasattr(sys.stdin, "isatty") and sys.stdin.isatty()


def _read_key() -> str:
    try:
        import termios
        import tty
    except ImportError:
        return input() or "enter"

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


def _multi_select_fallback(items: list[str], labels: list[str] | None = None) -> list[int]:
    display = labels if labels else items
    print()
    for i, label in enumerate(display):
        print(f"  {i + 1}. {label}")
    print()
    try:
        raw = input("Enter numbers to select (comma-separated, empty to skip): ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return []
    if not raw:
        return []
    selected = []
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < len(items):
                selected.append(idx)
    return sorted(set(selected))


def _get_terminal_height() -> int:
    try:
        import shutil

        return shutil.get_terminal_size().lines
    except Exception:
        return 24


def multi_select(items: list[str], labels: list[str] | None = None) -> list[int]:
    if not items:
        return []

    if not _is_interactive():
        return _multi_select_fallback(items, labels)

    try:
        import termios  # noqa: F401
    except ImportError:
        return _multi_select_fallback(items, labels)

    display = labels if labels else items
    selected: set[int] = set()
    cursor = 0
    total = len(items)

    max_visible = min(total, _get_terminal_height() - 4)
    viewport_start = 0

    hint = dim("(↑↓ move, space select, a toggle all, enter confirm)")

    def _viewport_range() -> range:
        return range(viewport_start, min(viewport_start + max_visible, total))

    def _adjust_viewport():
        nonlocal viewport_start
        if cursor < viewport_start:
            viewport_start = cursor
        elif cursor >= viewport_start + max_visible:
            viewport_start = cursor - max_visible + 1

    def render():
        vr = _viewport_range()
        lines = len(vr) + 1
        sys.stdout.write(f"\r\x1b[{lines}A")
        sys.stdout.write(f"\x1b[K{hint}\n")
        for i in vr:
            check = green("✓") if i in selected else " "
            arrow = "›" if i == cursor else " "
            prefix = ""
            if total > max_visible:
                if i == vr[0] and viewport_start > 0:
                    prefix = "↑ "
                elif i == vr[-1] and viewport_start + max_visible < total:
                    prefix = "↓ "
                else:
                    prefix = "  "
            sys.stdout.write(f"\x1b[K  {arrow} [{check}] {prefix}{display[i]}\n")
        sys.stdout.flush()

    sys.stdout.write(f"{hint}\n")
    for i in _viewport_range():
        arrow = "›" if i == cursor else " "
        prefix = "  " if total > max_visible else ""
        sys.stdout.write(f"  {arrow} [ ] {prefix}{display[i]}\n")
    sys.stdout.flush()

    try:
        while True:
            key = _read_key()
            if key == "up" and cursor > 0:
                cursor -= 1
                _adjust_viewport()
            elif key == "down" and cursor < total - 1:
                cursor += 1
                _adjust_viewport()
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
            else:
                continue
            render()
    except (EOFError, KeyboardInterrupt):
        return []
