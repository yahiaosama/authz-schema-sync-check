"""
Command-line interface for the pre-commit hook.
"""

import argparse
import sys
from pathlib import Path

from .validator import SchemaModelValidator


def main():
    """
    Main entry point for the CLI.
    
    Returns:
        Exit code: 0 for success, 1 for validation errors
    """
    parser = argparse.ArgumentParser(
        description="Check that models.py is in sync with schema.zed"
    )
    parser.add_argument(
        "--schema", 
        type=str, 
        default="schema.zed", 
        help="Path to the schema.zed file"
    )
    parser.add_argument(
        "--models", 
        type=str, 
        default="models.py", 
        help="Path to the models.py file"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Check that the files exist
    schema_path = Path(args.schema)
    models_path = Path(args.models)
    
    if not schema_path.exists():
        print(f"Error: Schema file '{schema_path}' does not exist", file=sys.stderr)
        return 1
    
    if not models_path.exists():
        print(f"Error: Models file '{models_path}' does not exist", file=sys.stderr)
        return 1
    
    # Validate the schema and models
    try:
        validator = SchemaModelValidator(schema_path, models_path)
        errors = validator.validate()
        
        # Print errors and exit with appropriate code
        if errors:
            for error in errors:
                print(f"Error: {error}", file=sys.stderr)
            return 1
        
        if args.verbose:
            print("Schema and models are in sync!")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
