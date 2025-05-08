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
    output_mappings=None,
):
    """Set up common test environment for CLI tests."""
    # Default paths if none provided
    if schema_path is None:
        schema_path = FIXTURES_DIR / "valid_schema.zed"
    if output_mappings is None:
        output_mappings = [("resources.py", "types.py.jinja")]

    # Default args if none provided
    if args is None:
        outputs_args = [f"{path}:{template}" for path, template in output_mappings]
        args = ["check-schema", f"--schema={schema_path}", "--outputs"] + outputs_args

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
        "authz_schema_sync_check.cli.TypeGenerator.generate_code",
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
        "output_mappings": output_mappings,
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
    # The file exists but has a diff
    args = [
        "check-schema",
        f"--schema={FIXTURES_DIR / 'valid_schema.zed'}",
        "--outputs",
        "resources.py:types.py.jinja",
        "--auto-fix",
    ]
    setup_cli_test(mocker, args=args, has_diff=True, path_exists=True)

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
        "--outputs",
        "resources.py:types.py.jinja",
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
        "--outputs",
        "resources.py:types.py.jinja",
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
        "--outputs",
        "resources.py:types.py.jinja",
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


def test_cli_nonexistent_output_fails(mocker):
    """Test that the CLI fails if the output file doesn't exist."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    output_mappings = [("nonexistent.py", "types.py.jinja")]

    # Setup test environment with schema exists but output doesn't
    path_exists = {str(schema_path): True, "nonexistent.py": False}
    mocks = setup_cli_test(
        mocker,
        schema_path=schema_path,
        output_mappings=output_mappings,
        path_exists=path_exists,
    )

    # Mock apply_changes
    mock_apply_changes = mocker.patch("authz_schema_sync_check.cli.apply_changes")

    # Run the test
    result = main()

    # Assertions
    assert result == 1  # Should fail
    mock_apply_changes.assert_not_called()  # Should not create file without --auto-fix
    mocks["mock_stderr"].write.assert_called()  # Should write error message


def test_cli_nonexistent_output_with_auto_fix(mocker):
    """Test that the CLI creates a new file but still fails if the output file doesn't exist and --auto-fix is used."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    output_mappings = [("nonexistent.py", "types.py.jinja")]

    # Setup test environment with schema exists but output doesn't, and --auto-fix
    args = [
        "check-schema",
        f"--schema={schema_path}",
        "--outputs",
        "nonexistent.py:types.py.jinja",
        "--auto-fix",
    ]
    path_exists = {str(schema_path): True, "nonexistent.py": False}
    mocks = setup_cli_test(
        mocker,
        args=args,
        schema_path=schema_path,
        output_mappings=output_mappings,
        path_exists=path_exists,
    )

    # Mock apply_changes
    mock_apply_changes = mocker.patch("authz_schema_sync_check.cli.apply_changes")

    # Run the test
    result = main()

    # Assertions
    assert result == 1  # Should fail even with --auto-fix when creating a new file
    mock_apply_changes.assert_called_once()  # Should create file with --auto-fix
    mocks["mock_stderr"].write.assert_called()  # Should write error message


def test_cli_multiple_outputs(mocker):
    """Test that the CLI handles multiple outputs correctly."""
    # Setup test environment with multiple outputs
    output_mappings = [
        ("resources.py", "types.py.jinja"),
        ("resources.ts", "types.ts.jinja"),
    ]
    mocks = setup_cli_test(mocker, output_mappings=output_mappings, has_diff=False)

    # Run the test
    result = main()

    # Assertions
    assert result == 0
    mocks["mock_stderr"].write.assert_not_called()


def test_cli_invalid_output_mapping(mocker):
    """Test that the CLI handles invalid output mappings correctly."""
    # Setup test environment with invalid output mapping
    args = [
        "check-schema",
        f"--schema={FIXTURES_DIR / 'valid_schema.zed'}",
        "--outputs",
        "invalid_mapping",
    ]
    mocks = setup_cli_test(mocker, args=args)

    # Run the test
    result = main()

    # Assertions
    assert result == 1
    mocks["mock_stderr"].write.assert_called()


def test_cli_template_not_found(mocker):
    """Test that the CLI handles template not found correctly."""
    # Setup test environment with nonexistent template
    output_mappings = [("resources.py", "nonexistent.jinja")]
    mocks = setup_cli_test(mocker, output_mappings=output_mappings)

    # Mock generate_code to raise TemplateNotFound
    import jinja2

    mock_generate_code = mocker.patch(
        "authz_schema_sync_check.cli.TypeGenerator.generate_code"
    )
    mock_generate_code.side_effect = jinja2.exceptions.TemplateNotFound(
        "nonexistent.jinja"
    )

    # Run the test
    result = main()

    # Assertions
    assert result == 1
    mocks["mock_stderr"].write.assert_called()
