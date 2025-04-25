"""
Git integration for comparing and updating files.
"""

from pathlib import Path
from typing import Tuple, Optional
import difflib


def get_diff(file_path: Path, content: str) -> Tuple[bool, str]:
    """
    Compare content with existing file using GitPython.

    Args:
        file_path: Path to the existing file
        content: New content to compare with

    Returns:
        Tuple of (has_diff, diff_output)
    """
    if not file_path.exists():
        return True, f"File {file_path} does not exist"

    # Read existing content
    existing_content = file_path.read_text()

    # Compare content
    if existing_content == content:
        return False, ""

    # Generate unified diff
    existing_lines = existing_content.splitlines(keepends=True)
    new_lines = content.splitlines(keepends=True)

    diff = difflib.unified_diff(
        existing_lines,
        new_lines,
        fromfile=str(file_path),
        tofile=str(file_path) + " (generated)",
        n=3,  # Context lines
    )

    diff_text = "".join(diff)
    return bool(diff_text), diff_text


def apply_changes(file_path: Path, content: str) -> None:
    """
    Apply changes to the file without staging in git.

    Args:
        file_path: Path to the file to update
        content: New content to write
    """
    # Create parent directories if they don't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the content
    file_path.write_text(content)


def find_git_repo(path: Path) -> Optional[str]:
    """
    Find the git repository containing the given path.

    Args:
        path: Path to search from

    Returns:
        Path to the git repository root, or None if not in a repository
    """
    current = path.absolute()

    # Walk up the directory tree
    while current != current.parent:
        git_dir = current / ".git"
        if git_dir.exists() and git_dir.is_dir():
            return str(current)
        current = current.parent

    return None
