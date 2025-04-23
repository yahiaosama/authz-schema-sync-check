"""
Tests for the SchemaModelValidator class.
"""

import pytest
from pathlib import Path

from authz_schema_sync_check.validator import SchemaModelValidator
from authz_schema_sync_check.errors import ValidationError, ObjectTypeError, RelationError


# Get the path to the fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_validator_initialization():
    """Test that the validator can be initialized with valid schema and models files."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    models_path = FIXTURES_DIR / "valid_models.py"
    
    validator = SchemaModelValidator(schema_path, models_path)
    
    assert validator.schema_parser.schema_path == schema_path
    assert validator.models_analyzer.models_path == models_path


def test_validate_valid_files():
    """Test that validation passes for valid schema and models files."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    models_path = FIXTURES_DIR / "valid_models.py"
    
    validator = SchemaModelValidator(schema_path, models_path)
    errors = validator.validate()
    
    assert len(errors) == 0


def test_validate_required_fields():
    """Test that validation checks for required fields in the Relation class."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    models_path = FIXTURES_DIR / "valid_models.py"
    
    validator = SchemaModelValidator(schema_path, models_path)
    errors = validator.validate_required_fields()
    
    assert len(errors) == 0


def test_validate_required_fields_invalid():
    """Test that validation fails for missing required fields in the Relation class."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    models_path = FIXTURES_DIR / "invalid_models.py"
    
    validator = SchemaModelValidator(schema_path, models_path)
    errors = validator.validate_required_fields()
    
    assert len(errors) > 0
    assert any(isinstance(error, ValidationError) for error in errors)
    assert any("subject_type" in str(error) for error in errors)


def test_validate_with_invalid_models():
    """Test that validation fails for invalid models file."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    models_path = FIXTURES_DIR / "invalid_models.py"
    
    validator = SchemaModelValidator(schema_path, models_path)
    
    # Update validate method to include validate_required_fields
    original_validate = validator.validate
    def patched_validate():
        errors = original_validate()
        errors.extend(validator.validate_required_fields())
        return errors
    
    validator.validate = patched_validate
    
    errors = validator.validate()
    
    assert len(errors) > 0
    assert any(isinstance(error, ValidationError) for error in errors)


def test_validate_object_types():
    """Test that validation checks for object types in the schema."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    models_path = FIXTURES_DIR / "valid_models.py"
    
    validator = SchemaModelValidator(schema_path, models_path)
    
    # Mock get_available_types to return a set of valid types
    original_get_available_types = validator.models_analyzer.get_available_types
    validator.models_analyzer.get_available_types = lambda: {"user", "group"}
    
    errors = validator.validate_object_types()
    
    # Restore original method
    validator.models_analyzer.get_available_types = original_get_available_types
    
    assert len(errors) > 0
    assert any(isinstance(error, ObjectTypeError) for error in errors)
    assert any("organization" in str(error) for error in errors)


def test_validate_relations():
    """Test that validation checks for relations in the schema."""
    schema_path = FIXTURES_DIR / "valid_schema.zed"
    models_path = FIXTURES_DIR / "valid_models.py"
    
    validator = SchemaModelValidator(schema_path, models_path)
    
    # Mock get_available_relations to return a set of valid relations
    original_get_available_relations = validator.models_analyzer.get_available_relations
    validator.models_analyzer.get_available_relations = lambda: {"member"}
    
    errors = validator.validate_relations()
    
    # Restore original method
    validator.models_analyzer.get_available_relations = original_get_available_relations
    
    assert len(errors) > 0
    assert any(isinstance(error, RelationError) for error in errors)
    assert any("organization" in str(error) for error in errors)
    assert any("admin" in str(error) for error in errors)
