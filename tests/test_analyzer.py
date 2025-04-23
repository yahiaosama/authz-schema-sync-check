"""
Tests for the ModelsAnalyzer class.
"""

import pytest
from pathlib import Path

from authz_schema_sync_check.analyzer import ModelsAnalyzer


# Get the path to the fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_analyzer_initialization():
    """Test that the analyzer can be initialized with a valid models file."""
    models_path = FIXTURES_DIR / "valid_models.py"
    analyzer = ModelsAnalyzer(models_path)
    assert analyzer.models_path == models_path


def test_analyze_valid_models():
    """Test that the analyzer can analyze a valid models file."""
    models_path = FIXTURES_DIR / "valid_models.py"
    analyzer = ModelsAnalyzer(models_path)
    
    relation_class = analyzer.analyze()
    
    assert relation_class.__name__ == "Relation"
    assert "subject_type" in relation_class.__annotations__
    assert "subject_id" in relation_class.__annotations__
    assert "subject_relation" in relation_class.__annotations__
    assert "relation" in relation_class.__annotations__
    assert "object_type" in relation_class.__annotations__
    assert "object_id" in relation_class.__annotations__


def test_get_field_types():
    """Test that the analyzer can extract field types from a valid models file."""
    models_path = FIXTURES_DIR / "valid_models.py"
    analyzer = ModelsAnalyzer(models_path)
    
    field_types = analyzer.get_field_types()
    
    assert "subject_type" in field_types
    assert "subject_id" in field_types
    assert "subject_relation" in field_types
    assert "relation" in field_types
    assert "object_type" in field_types
    assert "object_id" in field_types


def test_has_field():
    """Test that the analyzer can check if a field exists in the Relation class."""
    models_path = FIXTURES_DIR / "valid_models.py"
    analyzer = ModelsAnalyzer(models_path)
    
    assert analyzer.has_field("subject_type") is True
    assert analyzer.has_field("subject_id") is True
    assert analyzer.has_field("nonexistent_field") is False


def test_get_field_type():
    """Test that the analyzer can get the type of a field in the Relation class."""
    models_path = FIXTURES_DIR / "valid_models.py"
    analyzer = ModelsAnalyzer(models_path)
    
    subject_type = analyzer.get_field_type("subject_type")
    assert subject_type is not None
    
    nonexistent_field = analyzer.get_field_type("nonexistent_field")
    assert nonexistent_field is None


def test_analyze_invalid_models():
    """Test that the analyzer can analyze an invalid models file."""
    models_path = FIXTURES_DIR / "invalid_models.py"
    analyzer = ModelsAnalyzer(models_path)
    
    relation_class = analyzer.analyze()
    
    assert relation_class.__name__ == "Relation"
    assert "subject_type" not in relation_class.__annotations__  # Missing field
    assert "subject_id" in relation_class.__annotations__
    assert "subject_relation" not in relation_class.__annotations__  # Missing field
    assert "relation" in relation_class.__annotations__
    assert "object_type" in relation_class.__annotations__
    assert "object_id" in relation_class.__annotations__


def test_has_field_invalid_models():
    """Test that the analyzer correctly identifies missing fields in an invalid models file."""
    models_path = FIXTURES_DIR / "invalid_models.py"
    analyzer = ModelsAnalyzer(models_path)
    
    assert analyzer.has_field("subject_type") is False  # Missing field
    assert analyzer.has_field("subject_id") is True
    assert analyzer.has_field("subject_relation") is False  # Missing field
    assert analyzer.has_field("relation") is True
    assert analyzer.has_field("object_type") is True
    assert analyzer.has_field("object_id") is True
