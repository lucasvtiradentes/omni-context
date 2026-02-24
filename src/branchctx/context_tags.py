from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass

TAG_COMMITS = "bctx:commits"
TAG_FILES = "bctx:files"
TAG_PATTERN = re.compile(r"<(bctx:(?:commits|files))>(.*?)</\1>", re.DOTALL)
CONTEXT_FILE_EXTENSIONS = (".md", ".txt")
SYNC_MESSAGE_TEMPLATE = "N/A - in sync with {base_branch}"


@dataclass
class TagUpdate:
    file: str
    tag: str
    old_content: str
    new_content: str


def git_commits_since_base(path: str, base_branch: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "log", f"{base_branch}..HEAD", "--oneline"],
            cwd=path,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def git_changed_files(path: str, base_branch: str) -> str | None:
    try:
        status_result = subprocess.run(
            ["git", "diff", "--name-status", f"{base_branch}...HEAD"],
            cwd=path,
            capture_output=True,
            text=True,
            check=True,
        )

        numstat_result = subprocess.run(
            ["git", "diff", "--numstat", f"{base_branch}...HEAD"],
            cwd=path,
            capture_output=True,
            text=True,
            check=True,
        )

        status_lines = status_result.stdout.strip().split("\n")
        numstat_lines = numstat_result.stdout.strip().split("\n")

        if not status_lines or status_lines == [""]:
            return None

        file_stats: dict[str, tuple[str, str]] = {}
        for line in numstat_lines:
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) >= 3:
                added, removed, filepath = parts[0], parts[1], parts[2]
                file_stats[filepath] = (added, removed)

        files: list[tuple[str, str, str, str]] = []
        for line in status_lines:
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                status = parts[0][0]
                filepath = parts[-1]
                added, removed = file_stats.get(filepath, ("0", "0"))
                files.append((status, filepath, added, removed))

        if not files:
            return None

        max_path_len = max(len(f[1]) for f in files)

        result_lines = []
        for status, filepath, added, removed in files:
            padding = " " * (max_path_len - len(filepath))
            result_lines.append(f"{status}  {filepath}{padding}  (+{added} -{removed})")

        return "\n".join(result_lines)
    except subprocess.CalledProcessError:
        return None


def find_context_files(context_dir: str) -> list[str]:
    if not os.path.isdir(context_dir):
        return []

    files = []
    for root, _, filenames in os.walk(context_dir):
        for filename in filenames:
            if filename.endswith(CONTEXT_FILE_EXTENSIONS):
                files.append(os.path.join(root, filename))
    return files


def find_tags_in_file(filepath: str) -> list[tuple[str, str]]:
    try:
        with open(filepath, "r") as f:
            content = f.read()
    except (OSError, IOError):
        return []

    return [(match.group(1), match.group(2)) for match in TAG_PATTERN.finditer(content)]


def update_tag_content(content: str, tag: str, new_value: str) -> str:
    pattern = re.compile(rf"<({re.escape(tag)})>(.*?)</\1>", re.DOTALL)
    return pattern.sub(rf"<\1>{new_value}</\1>", content)


def update_context_tags(
    workspace: str,
    context_dir: str,
    base_branch: str,
) -> list[TagUpdate]:
    updates: list[TagUpdate] = []

    commits_content = git_commits_since_base(workspace, base_branch)
    files_content = git_changed_files(workspace, base_branch)

    sync_message = SYNC_MESSAGE_TEMPLATE.format(base_branch=base_branch)

    if not commits_content:
        commits_content = sync_message

    if not files_content:
        files_content = sync_message

    context_files = find_context_files(context_dir)

    for filepath in context_files:
        try:
            with open(filepath, "r") as f:
                original_content = f.read()
        except (OSError, IOError):
            continue

        tags = find_tags_in_file(filepath)
        if not tags:
            continue

        new_content = original_content
        file_updates = []

        tag_content_map = {
            TAG_COMMITS: commits_content,
            TAG_FILES: files_content,
        }

        for tag, old_value in tags:
            if tag not in tag_content_map:
                continue

            content_value = tag_content_map[tag]
            new_value = f"\n{content_value}\n"
            new_content = update_tag_content(new_content, tag, new_value)
            file_updates.append(
                TagUpdate(
                    file=filepath,
                    tag=tag,
                    old_content=old_value.strip(),
                    new_content=content_value,
                )
            )

        if new_content != original_content:
            with open(filepath, "w") as f:
                f.write(new_content)
            updates.extend(file_updates)

    return updates
