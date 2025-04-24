"""
Schema parser using tree-sitter with the tree-sitter-spicedb grammar.
"""

from pathlib import Path
from typing import Any
from tree_sitter import Parser, Language, Node

# Global variable to cache the language
_SPICEDB_LANGUAGE = None


def get_spicedb_language() -> Language:
    """
    Get the SpiceDB language.

    Returns:
        The SpiceDB language object
    """
    global _SPICEDB_LANGUAGE

    if _SPICEDB_LANGUAGE is not None:
        return _SPICEDB_LANGUAGE

    # Path to the compiled grammar library
    library_path = Path(__file__).parent / "build" / "spicedb.so"

    # Path to the tree-sitter-spicedb directory
    spicedb_dir = Path(__file__).parent.parent / "tree-sitter-spicedb"

    if not spicedb_dir.exists():
        raise ValueError(f"SpiceDB grammar directory not found at {spicedb_dir}")

    # Create the build directory if it doesn't exist
    build_dir = Path(__file__).parent / "build"
    build_dir.mkdir(exist_ok=True, parents=True)

    # Build the library
    try:
        Language.build_library(str(library_path), [str(spicedb_dir)])
    except Exception as e:
        raise ValueError(f"Failed to build SpiceDB grammar: {e}")

    # Load the language
    try:
        _SPICEDB_LANGUAGE = Language(str(library_path), "spicedb")
    except Exception as e:
        raise ValueError(f"Failed to load SpiceDB language: {e}")

    return _SPICEDB_LANGUAGE


class SchemaParser:
    """
    Parser for SpiceDB schema files using tree-sitter.
    """

    def __init__(self, schema_path: str | Path):
        """
        Initialize the parser with the path to the schema file.

        Args:
            schema_path: Path to the schema.zed file
        """
        self.schema_path = Path(schema_path)

        # Initialize the parser with the SpiceDB language
        self.parser = Parser()
        try:
            self.language = get_spicedb_language()  # Store the language separately
            self.parser.set_language(self.language)
        except ValueError as e:
            raise ValueError(f"Failed to initialize parser: {e}")

    def parse(self) -> Any:
        """
        Parse the schema file and return the syntax tree.

        Returns:
            The parsed syntax tree
        """
        with open(self.schema_path, "rb") as f:
            schema_content = f.read()

        tree = self.parser.parse(schema_content)
        return tree

    def get_object_types(self) -> list[str]:
        """
        Extract all object types (definitions) from the schema.

        Returns:
            A list of object type names
        """
        tree = self.parse()
        object_types = []

        # Query for object_definition nodes with type_identifier children
        query_string = "(object_definition (type_identifier) @name)"
        query = self.language.query(query_string)

        captures = query.captures(tree.root_node)
        for capture in captures:
            if capture[1] == "name":
                object_types.append(capture[0].text.decode("utf-8"))

        return object_types

    def get_relations(
        self, object_type: str | None = None
    ) -> dict[str, list[str]] | list[str]:
        """
        Extract all relations from the schema.
        If object_type is provided, only return relations for that object type.

        Args:
            object_type: Optional object type to filter relations

        Returns:
            A dictionary mapping object types to lists of relation names,
            or a list of relation names if object_type is provided
        """
        tree = self.parse()
        relations: dict[str, list[str]] = {}

        # Query for relation nodes within object_definitions
        query_string = """
        (object_definition
          (type_identifier) @def_name
          (relation
            (field_identifier) @rel_name))
        """
        query = self.language.query(query_string)

        captures = query.captures(tree.root_node)
        current_def = None

        for i, capture in enumerate(captures):
            node, name = capture

            if name == "def_name":
                current_def = node.text.decode("utf-8")
                if current_def is not None and current_def not in relations:
                    relations[current_def] = []

            elif (
                name == "rel_name"
                and current_def is not None
                and (object_type is None or current_def == object_type)
            ):
                rel_name = node.text.decode("utf-8")
                relations[current_def].append(rel_name)

        if object_type:
            return relations.get(object_type, [])
        return relations

    def get_permissions(
        self, object_type: str | None = None
    ) -> dict[str, list[str]] | list[str]:
        """
        Extract all permissions from the schema.
        If object_type is provided, only return permissions for that object type.

        Args:
            object_type: Optional object type to filter permissions

        Returns:
            A dictionary mapping object types to lists of permission names,
            or a list of permission names if object_type is provided
        """
        tree = self.parse()
        permissions: dict[str, list[str]] = {}

        # Query for permission nodes within object_definitions
        query_string = """
        (object_definition
          (type_identifier) @def_name
          (permission
            (method_identifier) @perm_name))
        """
        query = self.language.query(query_string)

        captures = query.captures(tree.root_node)
        current_def = None

        for capture in captures:
            node, name = capture

            if name == "def_name":
                current_def = node.text.decode("utf-8")
                if current_def is not None and current_def not in permissions:
                    permissions[current_def] = []

            elif (
                name == "perm_name"
                and current_def is not None
                and (object_type is None or current_def == object_type)
            ):
                perm_name = node.text.decode("utf-8")
                permissions[current_def].append(perm_name)

        if object_type:
            return permissions.get(object_type, [])
        return permissions

    def debug_print_tree(self) -> None:
        """Print the entire syntax tree for debugging."""
        tree = self.parse()
        self._print_tree_structure(tree.root_node)

    def _print_tree_structure(self, node: Node, indent: int = 0) -> None:
        """Print the structure of a syntax tree."""
        node_type = node.type
        node_text = node.text.decode("utf-8") if hasattr(node, "text") else ""
        print("  " * indent + f"{node_type}: '{node_text}'")

        for child in node.children:
            self._print_tree_structure(child, indent + 1)
