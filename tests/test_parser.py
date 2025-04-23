"""
Tests for the SchemaParser class.
"""

import os
import pytest
from pathlib import Path

from authz_schema_sync_check.parser import SchemaParser
from authz_schema_sync_check.errors import ValidationError


# Get the path to the fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_parser_initialization():
    """Test that the parser can be initialized with a valid schema file."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    parser = SchemaParser(schema_path)
    assert parser.schema_path == schema_path


def test_get_object_types():
    """Test that the parser can extract object types from a valid schema."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    parser = SchemaParser(schema_path)
    
    object_types = parser.get_object_types()
    
    assert "user" in object_types
    assert "group" in object_types
    assert "organization" in object_types
    assert len(object_types) == 3


def test_get_relations():
    """Test that the parser can extract relations from a valid schema."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    parser = SchemaParser(schema_path)
    
    relations = parser.get_relations()
    
    assert "group" in relations
    assert "organization" in relations
    assert "organization" in relations["group"]
    assert "member" in relations["group"]
    assert "admin" in relations["organization"]


def test_get_relations_for_object_type():
    """Test that the parser can extract relations for a specific object type."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    parser = SchemaParser(schema_path)
    
    group_relations = parser.get_relations("group")
    
    assert "organization" in group_relations
    assert "member" in group_relations
    assert len(group_relations) == 2


def test_get_permissions():
    """Test that the parser can extract permissions from a valid schema."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    parser = SchemaParser(schema_path)
    
    permissions = parser.get_permissions()
    
    assert "group" in permissions
    assert "organization" in permissions
    assert "edit_members" in permissions["group"]
    assert "administrate" in permissions["organization"]


def test_get_permissions_for_object_type():
    """Test that the parser can extract permissions for a specific object type."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    parser = SchemaParser(schema_path)
    
    group_permissions = parser.get_permissions("group")
    
    assert "edit_members" in group_permissions
    assert len(group_permissions) == 1


def test_parser_with_invalid_schema():
    """Test that the parser handles invalid schema files gracefully."""
    schema_path = FIXTURES_DIR / "invalid_schema.zed"
    parser = SchemaParser(schema_path)
    
    # The parser should still be able to extract some information
    object_types = parser.get_object_types()
    assert "user" in object_types
    assert "group" in object_types
    assert "organization" in object_types
    assert "invalid_definition" in object_types
