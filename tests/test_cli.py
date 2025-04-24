"""
Tests for the CLI module.
"""

from pathlib import Path

from authz_schema_sync_check.cli import main


# Get the path to the fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_cli_valid_schema(mocker):
    """Test that the CLI returns 0 for a valid schema file."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    output_path = Path("models.py")
    
    # Mock sys.argv
    mocker.patch("sys.argv", ["check-schema", f"--schema={schema_path}", f"--output={output_path}"])
    
    # Mock Path through the cli module
    path_mock = mocker.patch("authz_schema_sync_check.cli.Path")
    path_instance = mocker.MagicMock()
    path_instance.exists.return_value = True
    path_mock.return_value = path_instance
    
    # Mock SchemaParser and TypeGenerator
    mocker.patch("authz_schema_sync_check.cli.SchemaParser")
    mocker.patch("authz_schema_sync_check.cli.TypeGenerator.generate_types", return_value="generated content")
    
    # Mock get_diff to return no diff
    mock_get_diff = mocker.patch("authz_schema_sync_check.cli.get_diff", return_value=(False, ""))
    
    # Mock stdout and stderr
    mock_stderr = mocker.patch("authz_schema_sync_check.cli.sys.stderr")
    mocker.patch("authz_schema_sync_check.cli.sys.stdout")
    
    # Run the test
    result = main()
    
    # Assertions
    assert result == 0
    mock_stderr.write.assert_not_called()
    mock_get_diff.assert_called_once_with(path_instance, "generated content")


def test_cli_nonexistent_schema(mocker):
    """Test that the CLI returns 1 for a nonexistent schema file."""
    schema_path = FIXTURES_DIR / "nonexistent.zed"
    output_path = Path("models.py")
    
    # Mock sys.argv
    mocker.patch("sys.argv", ["check-schema", f"--schema={schema_path}", f"--output={output_path}"])
    
    # Mock Path through the cli module
    path_mock = mocker.patch("authz_schema_sync_check.cli.Path")
    path_instance = mocker.MagicMock()
    path_instance.exists.return_value = False
    path_mock.return_value = path_instance
    
    # Mock stdout and stderr
    mock_stderr = mocker.patch("authz_schema_sync_check.cli.sys.stderr")
    mocker.patch("authz_schema_sync_check.cli.sys.stdout")
    
    # Run the test
    result = main()
    
    # Assertions
    assert result == 1
    mock_stderr.write.assert_called()


def test_cli_with_diff(mocker):
    """Test that the CLI returns 1 when there's a diff."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    output_path = Path("models.py")
    
    # Mock sys.argv
    mocker.patch("sys.argv", ["check-schema", f"--schema={schema_path}", f"--output={output_path}"])
    
    # Mock Path through the cli module
    path_mock = mocker.patch("authz_schema_sync_check.cli.Path")
    path_instance = mocker.MagicMock()
    path_instance.exists.return_value = True
    path_mock.return_value = path_instance
    
    # Mock SchemaParser and TypeGenerator
    mocker.patch("authz_schema_sync_check.cli.SchemaParser")
    mocker.patch("authz_schema_sync_check.cli.TypeGenerator.generate_types", return_value="generated content")
    
    # Mock get_diff to return a diff when called with the right arguments
    mock_get_diff = mocker.patch("authz_schema_sync_check.cli.get_diff", return_value=(True, "diff output"))
    
    # Mock stdout and stderr
    mock_stderr = mocker.patch("authz_schema_sync_check.cli.sys.stderr")
    mocker.patch("authz_schema_sync_check.cli.sys.stdout")
    
    # Run the test
    result = main()
    
    # Assertions
    assert result == 1
    mock_stderr.write.assert_called()
    mock_get_diff.assert_called_once_with(path_instance, "generated content")


def test_cli_with_auto_fix(mocker):
    """Test that the CLI returns 0 when there's a diff but --auto-fix is used."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    output_path = Path("models.py")
    
    # Mock sys.argv
    mocker.patch("sys.argv", ["check-schema", f"--schema={schema_path}", f"--output={output_path}", "--auto-fix"])
    
    # Mock Path through the cli module
    path_mock = mocker.patch("authz_schema_sync_check.cli.Path")
    path_instance = mocker.MagicMock()
    path_instance.exists.return_value = True
    path_mock.return_value = path_instance
    
    # Mock SchemaParser and TypeGenerator
    mocker.patch("authz_schema_sync_check.cli.SchemaParser")
    mocker.patch("authz_schema_sync_check.cli.TypeGenerator.generate_types", return_value="generated content")
    
    # Mock get_diff to return a diff
    mocker.patch("authz_schema_sync_check.cli.get_diff", return_value=(True, "diff output"))
    
    # Mock apply_changes
    mock_apply_changes = mocker.patch("authz_schema_sync_check.cli.apply_changes")
    
    # Mock stdout and stderr
    mocker.patch("authz_schema_sync_check.cli.sys.stderr")
    mocker.patch("authz_schema_sync_check.cli.sys.stdout")
    
    # Run the test
    result = main()
    
    # Assertions
    assert result == 0
    mock_apply_changes.assert_called_once_with(path_instance, "generated content")


def test_cli_verbose(mocker):
    """Test that the CLI prints a success message with --verbose."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    output_path = Path("models.py")
    
    # Mock sys.argv
    mocker.patch("sys.argv", ["check-schema", f"--schema={schema_path}", f"--output={output_path}", "--verbose"])
    
    # Mock Path through the cli module
    path_mock = mocker.patch("authz_schema_sync_check.cli.Path")
    path_instance = mocker.MagicMock()
    path_instance.exists.return_value = True
    path_mock.return_value = path_instance
    
    # Mock SchemaParser and TypeGenerator
    mocker.patch("authz_schema_sync_check.cli.SchemaParser")
    mocker.patch("authz_schema_sync_check.cli.TypeGenerator.generate_types", return_value="generated content")
    
    # Mock get_diff to return no diff
    mock_get_diff = mocker.patch("authz_schema_sync_check.cli.get_diff", return_value=(False, ""))
    
    # Mock stdout and stderr
    mocker.patch("authz_schema_sync_check.cli.sys.stderr")
    mock_stdout= mocker.patch("authz_schema_sync_check.cli.sys.stdout")
    
    # Run the test
    result = main()
    
    # Assertions
    assert result == 0
    mock_stdout.write.assert_called()
    mock_get_diff.assert_called_once_with(path_instance, "generated content")


def test_cli_exception(mocker):
    """Test that the CLI handles exceptions gracefully."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    output_path = Path("models.py")
    
    # Mock sys.argv
    mocker.patch("sys.argv", ["check-schema", f"--schema={schema_path}", f"--output={output_path}"])
    
    # Mock Path through the cli module
    path_mock = mocker.patch("authz_schema_sync_check.cli.Path")
    path_instance = mocker.MagicMock()
    path_instance.exists.return_value = True
    path_mock.return_value = path_instance
    
    # Mock SchemaParser to raise an exception
    mock_parser = mocker.patch("authz_schema_sync_check.cli.SchemaParser")
    mock_parser.side_effect = Exception("Test exception")
    
    # Mock stdout and stderr
    mock_stderr= mocker.patch("authz_schema_sync_check.cli.sys.stderr")
    mocker.patch("authz_schema_sync_check.cli.sys.stdout")
    
    # Run the test
    result = main()
    
    # Assertions
    assert result == 1
    mock_stderr.write.assert_called()


def test_cli_nonexistent_output_creates_file(mocker):
    """Test that the CLI creates a new file if the output file doesn't exist."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    output_path = Path("nonexistent.py")
    
    # Mock sys.argv
    mocker.patch("sys.argv", ["check-schema", f"--schema={schema_path}", f"--output={output_path}"])
    
    # Mock Path through the cli module with different behavior for schema_path and output_path
    path_mock = mocker.patch("authz_schema_sync_check.cli.Path")
    schema_instance = mocker.MagicMock()
    schema_instance.exists.return_value = True
    output_instance = mocker.MagicMock()
    output_instance.exists.return_value = False
    
    # Configure the Path mock to return different instances based on the argument
    def path_side_effect(path_arg):
        if str(path_arg) == str(schema_path):
            return schema_instance
        elif str(path_arg) == str(output_path):
            return output_instance
        return mocker.MagicMock()
    
    path_mock.side_effect = path_side_effect
    
    # Mock SchemaParser and TypeGenerator
    mocker.patch("authz_schema_sync_check.cli.SchemaParser")
    mocker.patch("authz_schema_sync_check.cli.TypeGenerator.generate_types", return_value="generated content")
    
    # Mock apply_changes
    mock_apply_changes = mocker.patch("authz_schema_sync_check.cli.apply_changes")
    
    # Mock stdout and stderr
    mocker.patch("authz_schema_sync_check.cli.sys.stderr")
    mocker.patch("authz_schema_sync_check.cli.sys.stdout")
    
    # Run the test
    result = main()
    
    # Assertions
    assert result == 0
    mock_apply_changes.assert_called_once_with(output_instance, "generated content")
