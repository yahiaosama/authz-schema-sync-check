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
    py_code = generator.generate_code("default_types.py.jinja")

    # Check that the generated code includes expected elements
    assert "class User" in py_code
    assert "class Group" in py_code
    assert "class Organization" in py_code

    # Check for the new structure
    assert "P = TypeVar" in py_code
    assert "class Resource(Generic[P])" in py_code
    assert "def __init__(self, id: ResourceId, resource_type: str)" in py_code
    assert "ResourceId = int | str" in py_code
    assert "class CheckRequest" not in py_code

    # Check for the simplified class definitions
    assert "class User(Resource[" in py_code
    assert "class Group(Resource[" in py_code
    assert "class Organization(Resource[" in py_code

    # Check for the permission type aliases
    assert "UserPermission = Literal" in py_code
    assert "GroupPermission = Literal" in py_code
    assert "OrganizationPermission = Literal" in py_code
    assert "TableViewPermission = Literal" in py_code

    # Check that classes use these aliases and have permission_type
    assert "class User(Resource[UserPermission])" in py_code
    assert "class Group(Resource[GroupPermission])" in py_code
    assert "class Organization(Resource[OrganizationPermission])" in py_code
    assert "class TableView(Resource[TableViewPermission])" in py_code
    assert "permission_type = UserPermission" in py_code
    assert "permission_type = GroupPermission" in py_code
    assert "permission_type = OrganizationPermission" in py_code
    assert "permission_type = TableViewPermission" in py_code

    # Check for the camel case conversion of snake_case resource names
    assert "class TableView" in py_code
    assert "class Table_view" not in py_code  # Make sure it's not using capitalize
    assert 'Literal["view", "edit"]' in py_code
    # Ensure the resource_type is still snake_case
    assert 'super().__init__(id, "table_view")' in py_code


def test_generate_code_typescript():
    """Test that the generator can generate TypeScript code from a template."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    schema_parser = SchemaParser(schema_path)

    generator = TypeGenerator(schema_parser)

    # Test TypeScript template
    ts_code = generator.generate_code("default_types.ts.jinja")

    # Check that the generated code includes expected elements
    assert "export type ResourcePermission =" in ts_code

    # Check that each resource type has the correct permissions
    assert (
        'resource: "user"; permission: "read" | "update" | "make_admin" | "revoke_admin"'
        in ts_code
    )
    assert 'resource: "group"; permission: "edit_members"' in ts_code
    assert 'resource: "organization"; permission: "administrate" | "read"' in ts_code

    assert "resourceId: string | number" in ts_code


def test_write_code(tmp_path):
    """Test that the generator can write code to a file using a specific template."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    schema_parser = SchemaParser(schema_path)

    generator = TypeGenerator(schema_parser)

    # Write Python code to a temporary file
    py_output_path = tmp_path / "resources.py"
    generator.write_code(py_output_path, "default_types.py.jinja")

    # Check that the file exists and contains the generated code
    assert py_output_path.exists()
    py_content = py_output_path.read_text()
    assert "GENERATED CODE - DO NOT EDIT MANUALLY" in py_content
    assert "class User" in py_content

    # Check for the new structure
    assert "P = TypeVar" in py_content
    assert "class Resource(Generic[P])" in py_content
    assert "def __init__(self, id: ResourceId, resource_type: str)" in py_content
    assert "ResourceId = int | str" in py_content

    # Check for the simplified class definitions
    assert "class User(Resource[" in py_content
    assert "class Group(Resource[" in py_content
    assert "class Organization(Resource[" in py_content

    # Check for the camel case conversion of snake_case resource names
    assert "class TableView" in py_content
    assert "class Table_view" not in py_content
    # Ensure the resource_type is still snake_case
    assert 'super().__init__(id, "table_view")' in py_content
    # Check for permission_type
    assert "permission_type = UserPermission" in py_content
    assert "permission_type = GroupPermission" in py_content
    assert "permission_type = OrganizationPermission" in py_content
    assert "permission_type = TableViewPermission" in py_content

    # Write TypeScript code to a temporary file
    ts_output_path = tmp_path / "resources.ts"
    generator.write_code(ts_output_path, "default_types.ts.jinja")

    # Check that the file exists and contains the generated code
    assert ts_output_path.exists()
    ts_content = ts_output_path.read_text()
    assert "GENERATED CODE - DO NOT EDIT MANUALLY" in ts_content
    assert "export type ResourcePermission =" in ts_content

    # Check that each resource type has the correct permissions
    assert (
        'resource: "user"; permission: "read" | "update" | "make_admin" | "revoke_admin"'
        in ts_content
    )
    assert 'resource: "group"; permission: "edit_members"' in ts_content
    assert 'resource: "organization"; permission: "administrate" | "read"' in ts_content

    assert "resourceId: string | number" in ts_content


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
    generator.generate_code("default_types.py.jinja")

    # Verify formatting was applied
    assert format_called

    # Reset mock
    format_called = False

    # Generate TypeScript code (should not be formatted)
    generator.generate_code("default_types.ts.jinja")

    # Verify formatting was not applied
    assert not format_called
