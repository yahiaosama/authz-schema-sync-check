"""
Generator for creating type definitions from schema.zed.
"""

from pathlib import Path
import jinja2
import subprocess
import tempfile

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

        # Add custom filters
        self.template_env.filters["to_camel_case"] = self._to_camel_case

    def _to_camel_case(self, s: str) -> str:
        """Convert snake_case to CamelCase."""
        return "".join(word.capitalize() for word in s.split("_"))

    def _format_with_ruff(self, code: str) -> str:
        """
        Format code using ruff via subprocess.

        Args:
            code: The code to format

        Returns:
            The formatted code
        """
        # Create a temporary file with the code
        with tempfile.NamedTemporaryFile(
            suffix=".py", mode="w+", delete=False
        ) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(code)
            temp_file.flush()

        try:
            # Run ruff format on the temporary file
            subprocess.run(
                ["ruff", "format", str(temp_path)],
                check=True,
                capture_output=True,
            )

            # Read the formatted code
            formatted_code = temp_path.read_text()
            return formatted_code
        except subprocess.CalledProcessError as e:
            # If formatting fails, return the original code
            print(f"Warning: Failed to format code with ruff: {e}")
            return code
        finally:
            # Clean up the temporary file
            temp_path.unlink(missing_ok=True)

    def generate_code(self, template_name: str) -> str:
        """
        Generate code based on the schema using the specified template.

        Args:
            template_name: Name of the template to use

        Returns:
            Generated code as a string
        """
        template = self.template_env.get_template(template_name)

        # Extract information from the schema
        object_types = self.schema_parser.get_object_types()
        relations = self.schema_parser.get_relations()
        permissions = self.schema_parser.get_permissions()

        # Render the template
        code = template.render(
            object_types=object_types,
            relations=relations,
            permissions=permissions,
        )

        # Format the code if it's a Python file
        if template_name.endswith(".py.jinja"):
            code = self._format_with_ruff(code)

        return code

    def write_code(self, output_path: Path, template_name: str) -> None:
        """
        Write generated code to a file.

        Args:
            output_path: Path to write the generated code to
            template_name: Template name to use
        """
        content = self.generate_code(template_name)

        # Create parent directories if they don't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the content
        output_path.write_text(content)
