"""
Tests for the CLI module.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

from authz_schema_sync_check.cli import main


# Get the path to the fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_cli_valid_schema():
    """Test that the CLI returns 0 for a valid schema file."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    output_path = Path("models.py")
    
    with patch("sys.argv", ["check-schema", f"--schema={schema_path}", f"--output={output_path}"]):
        with patch("authz_schema_sync_check.git.get_diff") as mock_get_diff:
            # Mock that there's no diff
            mock_get_diff.return_value = (False, "")
            with patch("sys.stderr") as mock_stderr:
                with patch("sys.stdout") as mock_stdout:
                    result = main()
    
    assert result == 0
    mock_stderr.write.assert_not_called()


def test_cli_nonexistent_schema():
    """Test that the CLI returns 1 for a nonexistent schema file."""
    schema_path = FIXTURES_DIR / "nonexistent.zed"
    output_path = Path("models.py")
    
    with patch("sys.argv", ["check-schema", f"--schema={schema_path}", f"--output={output_path}"]):
        with patch("sys.stderr") as mock_stderr:
            with patch("sys.stdout") as mock_stdout:
                result = main()
    
    assert result == 1
    mock_stderr.write.assert_called()


def test_cli_with_diff():
    """Test that the CLI returns 1 when there's a diff."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    output_path = Path("models.py")
    
    with patch("sys.argv", ["check-schema", f"--schema={schema_path}", f"--output={output_path}"]):
        with patch("authz_schema_sync_check.git.get_diff") as mock_get_diff:
            # Mock that there's a diff
            mock_get_diff.return_value = (True, "diff output")
            with patch("sys.stderr") as mock_stderr:
                with patch("sys.stdout") as mock_stdout:
                    result = main()
    
    assert result == 1
    mock_stderr.write.assert_called()


def test_cli_with_auto_fix():
    """Test that the CLI returns 0 when there's a diff but --auto-fix is used."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    output_path = Path("models.py")
    
    with patch("sys.argv", ["check-schema", f"--schema={schema_path}", f"--output={output_path}", "--auto-fix"]):
        with patch("authz_schema_sync_check.git.get_diff") as mock_get_diff:
            # Mock that there's a diff
            mock_get_diff.return_value = (True, "diff output")
            with patch("authz_schema_sync_check.git.apply_changes") as mock_apply_changes:
                with patch("sys.stderr") as mock_stderr:
                    with patch("sys.stdout") as mock_stdout:
                        result = main()
    
    assert result == 0
    mock_apply_changes.assert_called()


def test_cli_verbose():
    """Test that the CLI prints a success message with --verbose."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    output_path = Path("models.py")
    
    with patch("sys.argv", ["check-schema", f"--schema={schema_path}", f"--output={output_path}", "--verbose"]):
        with patch("authz_schema_sync_check.git.get_diff") as mock_get_diff:
            # Mock that there's no diff
            mock_get_diff.return_value = (False, "")
            with patch("sys.stderr") as mock_stderr:
                with patch("sys.stdout") as mock_stdout:
                    result = main()
    
    assert result == 0
    mock_stdout.write.assert_called()


def test_cli_exception():
    """Test that the CLI handles exceptions gracefully."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    output_path = Path("models.py")
    
    with patch("sys.argv", ["check-schema", f"--schema={schema_path}", f"--output={output_path}"]):
        with patch("authz_schema_sync_check.parser.SchemaParser") as mock_parser:
            # Mock that the parser raises an exception
            mock_parser.side_effect = Exception("Test exception")
            with patch("sys.stderr") as mock_stderr:
                with patch("sys.stdout") as mock_stdout:
                    result = main()
    
    assert result == 1
    mock_stderr.write.assert_called()


def test_cli_nonexistent_output_creates_file():
    """Test that the CLI creates a new file if the output file doesn't exist."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    output_path = Path("nonexistent.py")
    
    with patch("sys.argv", ["check-schema", f"--schema={schema_path}", f"--output={output_path}"]):
        with patch("pathlib.Path.exists") as mock_exists:
            # Mock that the output file doesn't exist
            mock_exists.return_value = False
            with patch("authz_schema_sync_check.git.apply_changes") as mock_apply_changes:
                with patch("sys.stderr") as mock_stderr:
                    with patch("sys.stdout") as mock_stdout:
                        result = main()
    
    assert result == 0
    mock_apply_changes.assert_called()
