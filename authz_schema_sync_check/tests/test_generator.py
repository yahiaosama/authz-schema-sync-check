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


def test_generate_types():
    """Test that the generator can generate type definitions from a schema."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    schema_parser = SchemaParser(schema_path)

    generator = TypeGenerator(schema_parser)
    generated_code = generator.generate_types()

    # Check that the generated code includes expected elements
    assert "class User" in generated_code
    assert "class Group" in generated_code
    assert "class Organization" in generated_code

    # Check for permission literals
    assert "GroupPermission = Literal" in generated_code
    assert "OrganizationPermission = Literal" in generated_code

    # Check for relation literals
    assert "GroupRelation = Literal" in generated_code
    assert "OrganizationRelation = Literal" in generated_code

    # Check for type variables
    assert "T = TypeVar" in generated_code


def test_write_types(tmp_path):
    """Test that the generator can write type definitions to a file."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    schema_parser = SchemaParser(schema_path)

    generator = TypeGenerator(schema_parser)

    # Write to a temporary file
    output_path = tmp_path / "models.py"
    generator.write_types(output_path)

    # Check that the file exists and contains the generated code
    assert output_path.exists()

    content = output_path.read_text()
    assert "GENERATED CODE - DO NOT EDIT MANUALLY" in content
    assert "class User" in content
    assert "class Group" in content
    assert "class Organization" in content


def test_generate_types_with_invalid_schema():
    """Test that the generator can handle an invalid schema."""
    schema_path = FIXTURES_DIR / "invalid_schema.zed"
    schema_parser = SchemaParser(schema_path)

    generator = TypeGenerator(schema_parser)
    generated_code = generator.generate_types()

    # Even with an invalid schema, we should get some output
    assert "GENERATED CODE - DO NOT EDIT MANUALLY" in generated_code

    # The invalid schema might not have all the expected elements,
    # but it should still generate something
    assert "from typing import" in generated_code
