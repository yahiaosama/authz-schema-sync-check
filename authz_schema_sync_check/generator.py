"""
Generator for creating type definitions from schema.zed.
"""

from pathlib import Path
import jinja2

from .parser import SchemaParser


class TypeGenerator:
    """
    Generator for creating type definitions from schema.zed.
    """

    def __init__(self, schema_parser: SchemaParser):
        """
        Initialize the generator with a schema parser.

        Args:
            schema_parser: Parser for the schema.zed file
        """
        self.schema_parser = schema_parser

        # Set up Jinja environment
        template_dir = Path(__file__).parent / "templates"
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate_types(self) -> str:
        """
        Generate Python type definitions based on the schema.

        Returns:
            Generated Python code as a string
        """
        template = self.template_env.get_template("types.py.jinja")

        # Extract information from the schema
        object_types = self.schema_parser.get_object_types()
        relations = self.schema_parser.get_relations()
        permissions = self.schema_parser.get_permissions()

        # Render the template
        return template.render(
            object_types=object_types,
            relations=relations,
            permissions=permissions,
        )

    def write_types(self, output_path: Path) -> None:
        """
        Write generated types to a file.

        Args:
            output_path: Path to write the generated code to
        """
        content = self.generate_types()

        # Create parent directories if they don't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the content
        output_path.write_text(content)
