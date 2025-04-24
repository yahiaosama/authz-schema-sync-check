"""
Tests for the CLI module.
"""

from pathlib import Path

from authz_schema_sync_check.cli import main


# Get the path to the fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def setup_cli_test(
    mocker,
    args=None,
    path_exists=True,
    has_diff=False,
    schema_path=None,
    output_path=None,
):
    """Set up common test environment for CLI tests."""
    # Default paths if none provided
    if schema_path is None:
        schema_path = FIXTURES_DIR / "valid_schema.zed"
    if output_path is None:
        output_path = Path("models.py")

    # Default args if none provided
    if args is None:
        args = ["check-schema", f"--schema={schema_path}", f"--output={output_path}"]

    # Mock sys.argv
    mocker.patch("sys.argv", args)

    # Mock Path through the cli module
    path_mock = mocker.patch("authz_schema_sync_check.cli.Path")

    # Configure path_mock based on the test needs
    if isinstance(path_exists, bool):
        # Simple case: all paths have the same exists() result
        path_instance = mocker.MagicMock()
        path_instance.exists.return_value = path_exists
        path_mock.return_value = path_instance
    else:
        # Complex case: different paths have different exists() results
        # path_exists should be a dict mapping path strings to booleans
        def path_side_effect(path_arg):
            path_str = str(path_arg)
            instance = mocker.MagicMock()
            instance.exists.return_value = path_exists.get(path_str, False)
            return instance

        path_mock.side_effect = path_side_effect

    # Mock SchemaParser and TypeGenerator
    mocker.patch("authz_schema_sync_check.cli.SchemaParser")
    mocker.patch(
        "authz_schema_sync_check.cli.TypeGenerator.generate_types",
        return_value="generated content",
    )

    # Mock get_diff
    diff_output = "diff output" if has_diff else ""
    mock_get_diff = mocker.patch(
        "authz_schema_sync_check.cli.get_diff", return_value=(has_diff, diff_output)
    )

    # Mock stdout and stderr
    mock_stderr = mocker.patch("authz_schema_sync_check.cli.sys.stderr")
    mock_stdout = mocker.patch("authz_schema_sync_check.cli.sys.stdout")

    return {
        "schema_path": schema_path,
        "output_path": output_path,
        "path_mock": path_mock,
        "mock_get_diff": mock_get_diff,
        "mock_stderr": mock_stderr,
        "mock_stdout": mock_stdout,
    }


def test_cli_valid_schema(mocker):
    """Test that the CLI returns 0 for a valid schema file."""
    # Setup test environment
    mocks = setup_cli_test(mocker, has_diff=False)

    # Run the test
    result = main()

    # Assertions
    assert result == 0
    mocks["mock_stderr"].write.assert_not_called()


def test_cli_nonexistent_schema(mocker):
    """Test that the CLI returns 1 for a nonexistent schema file."""
    # Setup test environment with nonexistent schema file
    schema_path = FIXTURES_DIR / "nonexistent.zed"
    mocks = setup_cli_test(mocker, schema_path=schema_path, path_exists=False)

    # Run the test
    result = main()

    # Assertions
    assert result == 1
    mocks["mock_stderr"].write.assert_called()


def test_cli_with_diff(mocker):
    """Test that the CLI returns 1 when there's a diff."""
    # Setup test environment with a diff
    mocks = setup_cli_test(mocker, has_diff=True)

    # Run the test
    result = main()

    # Assertions
    assert result == 1
    mocks["mock_stderr"].write.assert_called()


def test_cli_with_auto_fix(mocker):
    """Test that the CLI returns 0 when there's a diff but --auto-fix is used."""
    # Setup test environment with a diff and auto-fix
    args = [
        "check-schema",
        f"--schema={FIXTURES_DIR / 'valid_schema.zed'}",
        "--output=models.py",
        "--auto-fix",
    ]
    setup_cli_test(mocker, args=args, has_diff=True)

    # Mock apply_changes
    mock_apply_changes = mocker.patch("authz_schema_sync_check.cli.apply_changes")

    # Run the test
    result = main()

    # Assertions
    assert result == 0
    # The path_instance is now in mocks, not directly accessible
    mock_apply_changes.assert_called_once()


def test_cli_verbose(mocker):
    """Test that the CLI prints a success message with --verbose."""
    # Setup test environment with verbose flag
    args = [
        "check-schema",
        f"--schema={FIXTURES_DIR / 'valid_schema.zed'}",
        "--output=models.py",
        "--verbose",
    ]
    mocks = setup_cli_test(mocker, args=args, has_diff=False)

    # Run the test
    result = main()

    # Assertions
    assert result == 0
    mocks["mock_stdout"].write.assert_called()


def test_cli_exception(mocker):
    """Test that the CLI handles exceptions gracefully."""
    # Setup test environment
    mocks = setup_cli_test(mocker)

    # Mock SchemaParser to raise an exception
    mock_parser = mocker.patch("authz_schema_sync_check.cli.SchemaParser")
    mock_parser.side_effect = Exception("Test exception")

    # Run the test
    result = main()

    # Assertions
    assert result == 1
    mocks["mock_stderr"].write.assert_called()


def test_cli_with_colorized_diff_enabled(mocker):
    """Test that the CLI uses colorized diff when --colorized-diff=True."""
    # Setup test environment with colorized-diff=True
    args = [
        "check-schema",
        f"--schema={FIXTURES_DIR / 'valid_schema.zed'}",
        "--output=models.py",
        "--colorized-diff=True",
    ]
    mocks = setup_cli_test(mocker, args=args, has_diff=True)

    # Mock colorize_diff to track if it's called
    mock_colorize_diff = mocker.patch(
        "authz_schema_sync_check.cli.colorize_diff", return_value="colorized diff"
    )

    # Run the test
    result = main()

    # Assertions
    assert result == 1
    mocks["mock_stderr"].write.assert_called()
    mock_colorize_diff.assert_called_once_with("diff output")


def test_cli_with_colorized_diff_disabled(mocker):
    """Test that the CLI doesn't use colorized diff when --colorized-diff=False."""
    # Setup test environment with colorized-diff=False
    args = [
        "check-schema",
        f"--schema={FIXTURES_DIR / 'valid_schema.zed'}",
        "--output=models.py",
        "--colorized-diff=False",
    ]
    mocks = setup_cli_test(mocker, args=args, has_diff=True)

    # Mock colorize_diff to track if it's called
    mock_colorize_diff = mocker.patch("authz_schema_sync_check.cli.colorize_diff")

    # Run the test
    result = main()

    # Assertions
    assert result == 1
    mocks["mock_stderr"].write.assert_called()
    mock_colorize_diff.assert_not_called()


def test_cli_nonexistent_output_creates_file(mocker):
    """Test that the CLI creates a new file if the output file doesn't exist."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    output_path = Path("nonexistent.py")

    # Setup test environment with schema exists but output doesn't
    path_exists = {str(schema_path): True, str(output_path): False}
    setup_cli_test(
        mocker,
        schema_path=schema_path,
        output_path=output_path,
        path_exists=path_exists,
    )

    # Mock apply_changes
    mock_apply_changes = mocker.patch("authz_schema_sync_check.cli.apply_changes")

    # Run the test
    result = main()

    # Assertions
    assert result == 0
    mock_apply_changes.assert_called_once()
