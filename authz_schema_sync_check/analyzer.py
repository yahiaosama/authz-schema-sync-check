"""
Models analyzer for extracting information about the Relation class.
"""

import importlib.util
from pathlib import Path
from typing import Dict, List, Set, Any, Optional


class ModelsAnalyzer:
    """
    Analyzer for models.py file to extract information about the Relation class.
    """

    def __init__(self, models_path: str | Path):
        """
        Initialize the analyzer with the path to the models file.

        Args:
            models_path: Path to the models.py file
        """
        self.models_path = Path(models_path)
        self.relation_class = None
        
    def analyze(self):
        """
        Analyze the models.py file and extract information about the Relation class.
        
        Returns:
            The Relation class
            
        Raises:
            ValueError: If no Relation class is found in the models file
        """
        # Load the module
        spec = importlib.util.spec_from_file_location("models", self.models_path)
        models_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(models_module)
        
        # Check if Relation class exists
        if not hasattr(models_module, "Relation"):
            raise ValueError(f"No Relation class found in {self.models_path}")
        
        self.relation_class = models_module.Relation
        return self.relation_class
    
    def get_available_types(self) -> Set[str]:
        """
        Return all types that can be used as subject_type or object_type.
        In a real implementation, this would analyze the actual constraints,
        but for now we'll assume any string is valid.
        
        Returns:
            A set of available types, or an empty set if any string is valid
        """
        # In a real implementation, we might analyze the field constraints
        # For now, we'll just return an empty set to indicate any string is valid
        return set()
    
    def get_available_relations(self) -> Set[str]:
        """
        Return all relations that can be used in the relation field.
        In a real implementation, this would analyze the actual constraints,
        but for now we'll assume any string is valid.
        
        Returns:
            A set of available relations, or an empty set if any string is valid
        """
        # In a real implementation, we might analyze the field constraints
        # For now, we'll just return an empty set to indicate any string is valid
        return set()
    
    def get_field_types(self) -> Dict[str, Any]:
        """
        Return the types of all fields in the Relation class.
        
        Returns:
            A dictionary mapping field names to their types
        """
        if not self.relation_class:
            self.analyze()  # Ensure the class is loaded
        
        field_types = {}
        for field_name, field in self.relation_class.__annotations__.items():
            field_types[field_name] = field
        
        return field_types
    
    def has_field(self, field_name: str) -> bool:
        """
        Check if the Relation class has a field with the given name.
        
        Args:
            field_name: The name of the field to check
            
        Returns:
            True if the field exists, False otherwise
        """
        if not self.relation_class:
            self.analyze()  # Ensure the class is loaded
        
        # Check both __annotations__ and direct attributes
        return field_name in self.relation_class.__annotations__ or hasattr(self.relation_class, field_name)
    
    def get_field_type(self, field_name: str) -> Optional[Any]:
        """
        Get the type of a field in the Relation class.
        
        Args:
            field_name: The name of the field
            
        Returns:
            The type of the field, or None if the field doesn't exist
        """
        if not self.relation_class:
            self.analyze()  # Ensure the class is loaded
        
        return self.relation_class.__annotations__.get(field_name)
