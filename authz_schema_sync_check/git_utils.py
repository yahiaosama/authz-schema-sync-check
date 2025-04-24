"""
Git integration for comparing and updating files.
"""

import os
from pathlib import Path
from typing import Tuple, Optional
import difflib
import git  # GitPython library


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


def apply_changes(file_path: Path, content: str) -> bool:
    """
    Apply changes to the file and add it to git index if in a repository.

    Args:
        file_path: Path to the file to update
        content: New content to write

    Returns:
        True if the file was added to git index, False otherwise
    """
    # Create parent directories if they don't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the content
    file_path.write_text(content)

    # Add the file to git index if it's in a git repository
    try:
        # Find the git repository containing this file
        repo_path = find_git_repo(file_path)
        if repo_path:
            repo = git.Repo(repo_path)
            # Get relative path to the repository root
            rel_path = os.path.relpath(file_path, repo_path)
            # Add the file to the index
            repo.git.add(rel_path)
            return True
    except (git.InvalidGitRepositoryError, git.NoSuchPathError):
        # Not in a git repository or other git error
        pass

    return False


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
