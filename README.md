# authz-schema-sync-check

A pre-commit hook for generating and syncing type definitions from SpiceDB schema.

## Overview

This package provides a pre-commit hook that generates type definitions from a SpiceDB schema file (`schema.zed`) and ensures they are in sync with output files. It supports generating both Python and TypeScript type definitions, and can be extended to support other languages through custom templates. It uses Git to compare the generated code with the existing code and can automatically apply changes.

## Installation

This package is built with Poetry and should be used with Poetry:

```bash
# For development
git clone https://github.com/yahiaosama/authz-schema-sync-check.git
cd authz-schema-sync-check
poetry install
```

## Usage

### As a Pre-commit Hook

Add the following to your `.pre-commit-config.yaml` file to use it exactly as in the backend repository:

```yaml
repos:
  - repo: https://github.com/yahiaosama/authz-schema-sync-check
    rev: v0.2.0
    hooks:
      - id: authz-schema-sync-check
        args: [
          "--schema", "backend/app/infra/authz/schema.zed",
          "--outputs", 
            "backend/app/infra/authz/resources.py", 
            "frontend-apps/packages/shared/src/authz/resources.ts",
          "--verbose",
          "--colorized-diff=true",
          "--auto-fix"
        ]
        files: 'backend/app/infra/authz/schema\.zed$|backend/app/infra/authz/resources\.py$|frontend-apps/packages/shared/src/authz/resources\.ts$'
        pass_filenames: false
```

Available options:
- `--schema`: Path to the schema.zed file (default: `schema.zed`)
- `--outputs`: Output paths, optionally with template names in format 'output_path[:template_name]' (required)
  - For `.py` files, the default template is `default_types.py.jinja`
  - For `.ts` files, the default template is `default_types.ts.jinja`
  - For other file types, you must specify the template explicitly
- `--auto-fix`: Automatically apply changes if out of sync
- `--verbose`: Enable verbose output
- `--colorized-diff`: Enable or disable colorized diff output (true/false, default: true)

The `files` pattern determines when the hook runs. In the example above, it will run whenever:
- The `schema.zed` file is modified
- The `resources.py` file is modified
- The `resources.ts` file is modified

**Important Note**: The hook will fail if any output file doesn't exist, even with `--auto-fix` enabled. With `--auto-fix`, it will create the file but still fail, requiring you to review and commit the newly created file in a separate step. This is an intentional security feature to ensure that generated files are always explicitly committed by the user, preventing accidental inclusion of unreviewed generated code.

### As a Command-line Tool

You can also use the package as a command-line tool:

```bash
# Generate a single output with default template (inferred from file extension)
poetry run authz-schema-sync-check --schema path/to/schema.zed --outputs "path/to/resources.py"

# Generate multiple outputs with default templates
poetry run authz-schema-sync-check --schema path/to/schema.zed --outputs \
  "path/to/resources.py" \
  "path/to/resources.ts"

# Generate outputs with explicit templates
poetry run authz-schema-sync-check --schema path/to/schema.zed --outputs \
  "path/to/resources.py:default_types.py.jinja" \
  "path/to/resources.ts:default_types.ts.jinja"

# Automatically apply changes
poetry run authz-schema-sync-check --schema path/to/schema.zed --outputs \
  "path/to/resources.py" \
  --auto-fix

# Check with colorized diff disabled
poetry run authz-schema-sync-check --schema path/to/schema.zed --outputs \
  "path/to/resources.py" \
  --colorized-diff=false
```

Options:
- `--schema`: Path to the schema.zed file (default: `schema.zed`)
- `--outputs`: Output paths, optionally with template names in format 'output_path[:template_name]' (required)
  - For `.py` files, the default template is `default_types.py.jinja`
  - For `.ts` files, the default template is `default_types.ts.jinja`
  - For other file types, you must specify the template explicitly
- `--auto-fix`: Automatically apply changes if out of sync
- `--verbose`: Enable verbose output
- `--colorized-diff`: Enable or disable colorized diff output (true/false, default: true)

## Generated Type Definitions

The package can generate type definitions in multiple languages based on the schema. The available templates are:

- `default_types.py.jinja`: Generates Python type definitions
- `default_types.ts.jinja`: Generates TypeScript type definitions

You can also create your own templates in the `templates` directory.

### Python Type Definitions

The Python template generates the following:

1. **Permission Type Aliases**: Type literals for permissions specific to each resource type.
2. **Resource Base Class**: A generic base class for all resources.
3. **Resource Classes**: Classes for each object type defined in the schema, with a `permission_type` class variable.

### Example

#### schema.zed

```
definition user {
    relation organization: organization
    relation self: user

    permission read = self
    permission update = self
    permission make_admin = organization->administrate
    permission revoke_admin = organization->administrate
}

definition group {
    relation organization: organization
    relation member: user | group#member

    permission edit_members = organization->administrate
}

definition organization {
    relation admin: user
    relation member: user | group#member

    permission administrate = admin
    permission read = member
}
```

#### Generated Python Output (resources.py)

```python
"""
GENERATED CODE - DO NOT EDIT MANUALLY
This file is generated from schema.zed and should not be modified directly.
"""

from typing import Generic, Literal, TypeVar

# Permission type aliases for each resource type
UserPermission = Literal["read", "update", "make_admin", "revoke_admin"]
GroupPermission = Literal["edit_members"]
OrganizationPermission = Literal["administrate", "read"]

# Type variable for permission literals
P = TypeVar("P", bound=str)

# Base resource class
class Resource(Generic[P]):
    """Base class for all resources with typed permissions."""

    def __init__(self, id: str, resource_type: str):
        self.id = id
        self.type = resource_type

# Resource classes with their specific permission types
class User(Resource[UserPermission]):
    """User resource from schema.zed"""

    # Set the permission type for this resource
    permission_type = UserPermission

    def __init__(self, id: str):
        super().__init__(id, "user")

class Group(Resource[GroupPermission]):
    """Group resource from schema.zed"""

    # Set the permission type for this resource
    permission_type = GroupPermission

    def __init__(self, id: str):
        super().__init__(id, "group")

class Organization(Resource[OrganizationPermission]):
    """Organization resource from schema.zed"""

    # Set the permission type for this resource
    permission_type = OrganizationPermission

    def __init__(self, id: str):
        super().__init__(id, "organization")

# Note: snake_case resource names are converted to CamelCase
# For example, table_view would become TableView
```

## Development

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yahiaosama/authz-schema-sync-check.git
   cd authz-schema-sync-check
   ```

2. Install dependencies with Poetry:
   ```bash
   poetry install
   ```

### Running Tests

```bash
poetry run pytest
```

### TypeScript Type Definitions

The TypeScript template generates a discriminated union type that represents all valid resource-permission combinations from the schema.

#### Generated TypeScript Output (resources.ts)

```typescript
/**
 * GENERATED CODE - DO NOT EDIT MANUALLY
 * This file is generated from schema.zed and should not be modified directly.
 */

/**
 * Type representing all valid resource-permission combinations
 * from the SpiceDB schema.
 */
export type ResourcePermission = 
  | { resource: "user"; permission: "read" | "update" | "make_admin" | "revoke_admin"; resourceId: string | number }
  | { resource: "group"; permission: "edit_members"; resourceId: string | number }
  | { resource: "organization"; permission: "administrate" | "read"; resourceId: string | number };
```

This TypeScript type ensures that only valid resource-permission combinations can be used at compile time. For example:

```typescript
// Valid combinations
const valid1: ResourcePermission = { resource: "user", permission: "read", resourceId: "user-123" };
const valid2: ResourcePermission = { resource: "organization", permission: "administrate", resourceId: 456 };

// Invalid combinations - TypeScript error
const invalid1: ResourcePermission = { resource: "user", permission: "administrate", resourceId: "user-123" }; // Error
const invalid2: ResourcePermission = { resource: "invalid", permission: "read", resourceId: 789 }; // Error
```

## Troubleshooting

### Missing Output File

If you see an error like:

```
Error processing path/to/resources.py: Output file does not exist
```

This means the output file doesn't exist yet. Run the hook with `--auto-fix` to create it:

```bash
poetry run authz-schema-sync-check --schema path/to/schema.zed --outputs "path/to/resources.py" --auto-fix
```

The hook will create the file but still fail with an error like:

```
Error processing path/to/resources.py: Output file did not exist but has been created
Please review and commit the newly created file: path/to/resources.py
```

This is intentional - you need to review the generated file and commit it manually. This ensures that generated files are always explicitly reviewed before being committed.

### Files Out of Sync

If you see an error like:

```
Error processing path/to/resources.py: File is out of sync with schema
```

This means you've modified the schema.zed file but haven't updated the output file. Run the hook with `--auto-fix` to update it:

```bash
poetry run authz-schema-sync-check --schema path/to/schema.zed --outputs "path/to/resources.py" --auto-fix
```

Then review the changes and commit them.

### Template Not Found

If you see an error like:

```
Error processing path/to/resources.py: Template 'nonexistent.jinja' not found
```

This means the specified template doesn't exist. Make sure the template exists in the `templates` directory.

## License

MIT
