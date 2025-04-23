"""
Validator for checking that models.py is in sync with schema.zed.
"""

from pathlib import Path
from typing import List, Dict, Any

from .parser import SchemaParser
from .analyzer import ModelsAnalyzer
from .errors import ValidationError, ObjectTypeError, RelationError


class SchemaModelValidator:
    """
    Validator for checking that models.py is in sync with schema.zed.
    """

    def __init__(self, schema_path: str | Path, models_path: str | Path):
        """
        Initialize the validator with paths to the schema and models files.

        Args:
            schema_path: Path to the schema.zed file
            models_path: Path to the models.py file
        """
        self.schema_parser = SchemaParser(schema_path)
        self.models_analyzer = ModelsAnalyzer(models_path)

    def validate(self) -> List[ValidationError]:
        """
        Perform validation and return a list of validation errors.

        Returns:
            A list of validation errors, or an empty list if validation passes
        """
        errors = []

        # Validate object types
        object_type_errors = self.validate_object_types()
        errors.extend(object_type_errors)

        # Validate relations
        relation_errors = self.validate_relations()
        errors.extend(relation_errors)

        # Validate required fields
        required_field_errors = self.validate_required_fields()
        errors.extend(required_field_errors)

        return errors

    def validate_object_types(self) -> List[ObjectTypeError]:
        """
        Check that all object types in schema.zed are available in models.py.

        Returns:
            A list of object type errors, or an empty list if validation passes
        """
        errors = []

        # Get all object types from the schema
        schema_object_types = self.schema_parser.get_object_types()

        # Get available types from models.py
        models_types = self.models_analyzer.get_available_types()

        # If models_types is empty, we assume any string is valid
        if not models_types:
            return []

        # Check that all schema object types are available in models.py
        for object_type in schema_object_types:
            if object_type not in models_types:
                errors.append(
                    ObjectTypeError(
                        f"Object type '{object_type}' defined in schema.zed is not available in models.py"
                    )
                )

        return errors

    def validate_relations(self) -> List[RelationError]:
        """
        Check that all relations in schema.zed can be used in models.py.

        Returns:
            A list of relation errors, or an empty list if validation passes
        """
        errors = []

        # Get all relations from the schema
        schema_relations = self.schema_parser.get_relations()

        # Get available relations from models.py
        models_relations = self.models_analyzer.get_available_relations()

        # If models_relations is empty, we assume any string is valid
        if not models_relations:
            return []

        # Check that all schema relations are available in models.py
        for object_type, relations in schema_relations.items():
            for relation in relations:
                if relation not in models_relations:
                    errors.append(
                        RelationError(
                            f"Relation '{relation}' for object type '{object_type}' defined in schema.zed is not available in models.py"
                        )
                    )

        return errors

    def validate_required_fields(self) -> List[ValidationError]:
        """
        Check that the Relation class has all required fields.

        Returns:
            A list of validation errors, or an empty list if validation passes
        """
        errors = []

        # Required fields for the Relation class
        required_fields = [
            "subject_type",
            "subject_id",
            "relation",
            "object_type",
            "object_id",
        ]

        # Check that all required fields exist
        for field in required_fields:
            if not self.models_analyzer.has_field(field):
                errors.append(
                    ValidationError(
                        f"Required field '{field}' is missing from the Relation class in models.py"
                    )
                )

        return errors
