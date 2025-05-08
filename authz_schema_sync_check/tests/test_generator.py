"""
Tests for the TypeGenerator class.
"""

from pathlib import Path

from authz_schema_sync_check.parser import SchemaParser
from authz_schema_sync_check.generator import TypeGenerator


# Get the path to the fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_generator_initialization():
    """Test that the generator can be initialized with a schema parser."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    schema_parser = SchemaParser(schema_path)

    generator = TypeGenerator(schema_parser)

    assert generator.schema_parser == schema_parser


def test_generate_code_python():
    """Test that the generator can generate Python code from a template."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    schema_parser = SchemaParser(schema_path)

    generator = TypeGenerator(schema_parser)

    # Test Python template
    py_code = generator.generate_code("types.py.jinja")

    # Check that the generated code includes expected elements
    assert "class User" in py_code
    assert "class Group" in py_code
    assert "class Organization" in py_code
    assert "GroupPermission = Literal" in py_code
    assert "OrganizationPermission = Literal" in py_code
    assert "GroupRelation = Literal" in py_code
    assert "OrganizationRelation = Literal" in py_code
    assert "T = TypeVar" in py_code


def test_generate_code_typescript():
    """Test that the generator can generate TypeScript code from a template."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    schema_parser = SchemaParser(schema_path)

    generator = TypeGenerator(schema_parser)

    # Test TypeScript template
    ts_code = generator.generate_code("types.ts.jinja")

    # Check that the generated code includes expected elements
    assert "export type ResourceId = string | number;" in ts_code
    assert "export type ResourcePermission =" in ts_code
    assert "resourceId: ResourceId" in ts_code
    assert "export type UserPermission =" in ts_code
    assert "export type GroupPermission =" in ts_code
    assert "export type OrganizationPermission =" in ts_code
    assert "export type ResourceType =" in ts_code


def test_write_code(tmp_path):
    """Test that the generator can write code to a file using a specific template."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    schema_parser = SchemaParser(schema_path)

    generator = TypeGenerator(schema_parser)

    # Write Python code to a temporary file
    py_output_path = tmp_path / "resources.py"
    generator.write_code(py_output_path, "types.py.jinja")

    # Check that the file exists and contains the generated code
    assert py_output_path.exists()
    py_content = py_output_path.read_text()
    assert "GENERATED CODE - DO NOT EDIT MANUALLY" in py_content
    assert "class User" in py_content

    # Write TypeScript code to a temporary file
    ts_output_path = tmp_path / "resources.ts"
    generator.write_code(ts_output_path, "types.ts.jinja")

    # Check that the file exists and contains the generated code
    assert ts_output_path.exists()
    ts_content = ts_output_path.read_text()
    assert "GENERATED CODE - DO NOT EDIT MANUALLY" in ts_content
    assert "export type ResourceId = string | number;" in ts_content
    assert "export type ResourcePermission =" in ts_content
    assert "resourceId: ResourceId" in ts_content


def test_format_with_ruff():
    """Test that the generator formats Python code with ruff but not TypeScript code."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    schema_parser = SchemaParser(schema_path)

    generator = TypeGenerator(schema_parser)

    # Mock the _format_with_ruff method to verify it's called
    original_format = generator._format_with_ruff
    format_called = False

    def mock_format(code):
        nonlocal format_called
        format_called = True
        return original_format(code)

    generator._format_with_ruff = mock_format

    # Generate Python code
    generator.generate_code("types.py.jinja")

    # Verify formatting was applied
    assert format_called

    # Reset mock
    format_called = False

    # Generate TypeScript code (should not be formatted)
    generator.generate_code("types.ts.jinja")

    # Verify formatting was not applied
    assert not format_called
