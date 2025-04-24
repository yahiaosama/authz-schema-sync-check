"""
Tests for the Git integration module.
"""

from pathlib import Path

from authz_schema_sync_check.git_utils import get_diff, apply_changes, find_git_repo


def test_get_diff_nonexistent_file(tmp_path):
    """Test that get_diff returns True for a nonexistent file."""
    file_path = tmp_path / "nonexistent.py"
    content = "test content"

    has_diff, diff_output = get_diff(file_path, content)

    assert has_diff is True
    assert "does not exist" in diff_output


def test_get_diff_identical_content(tmp_path):
    """Test that get_diff returns False for identical content."""
    file_path = tmp_path / "test.py"
    content = "test content"

    # Create the file with the content
    file_path.write_text(content)

    has_diff, diff_output = get_diff(file_path, content)

    assert has_diff is False
    assert diff_output == ""


def test_get_diff_different_content(tmp_path):
    """Test that get_diff returns True for different content."""
    file_path = tmp_path / "test.py"
    original_content = "original content"
    new_content = "new content"

    # Create the file with the original content
    file_path.write_text(original_content)

    has_diff, diff_output = get_diff(file_path, new_content)

    assert has_diff is True
    assert "original content" in diff_output
    assert "new content" in diff_output


def test_apply_changes(tmp_path):
    """Test that apply_changes writes content to a file."""
    file_path = tmp_path / "test.py"
    content = "test content"

    apply_changes(file_path, content)

    assert file_path.exists()
    assert file_path.read_text() == content


def test_apply_changes_creates_directories(tmp_path):
    """Test that apply_changes creates parent directories if they don't exist."""
    file_path = tmp_path / "subdir" / "test.py"
    content = "test content"

    apply_changes(file_path, content)

    assert file_path.exists()
    assert file_path.read_text() == content


def test_find_git_repo():
    """Test that find_git_repo returns None for a non-git directory."""
    # This test assumes that the temporary directory is not a git repository
    repo_path = find_git_repo(Path("/tmp"))
    assert repo_path is None
