# authz-schema-sync-check

A pre-commit hook for generating and syncing type definitions from SpiceDB schema.

## Overview

This package provides a pre-commit hook that generates type definitions from a SpiceDB schema file (`schema.zed`) and ensures they are in sync with a Python models file (`models.py`). It uses Git to compare the generated code with the existing code and can automatically apply changes.

## Installation

```bash
pip install authz-schema-sync-check
```

## Usage

### As a Pre-commit Hook

Add the following to your `.pre-commit-config.yaml` file:

```yaml
repos:
  - repo: https://github.com/your-username/authz-schema-sync-check
    rev: v0.1.0
    hooks:
      - id: authz-schema-sync-check
```

By default, the hook will look for `schema.zed` and generate/update `models.py` in the current directory. You can customize the paths and behavior using the following options:

```yaml
repos:
  - repo: https://github.com/your-username/authz-schema-sync-check
    rev: v0.1.0
    hooks:
      - id: authz-schema-sync-check
        args: ["--schema", "path/to/schema.zed", "--output", "path/to/models.py", "--auto-fix"]
```

Available options:
- `--schema`: Path to the schema.zed file (default: `schema.zed`)
- `--output`: Path to the output models.py file (default: `models.py`)
- `--auto-fix`: Automatically apply changes if out of sync
- `--verbose`: Enable verbose output

For projects with multiple schema files, you can add multiple instances of the hook:

```yaml
repos:
  - repo: https://github.com/your-username/authz-schema-sync-check
    rev: v0.1.0
    hooks:
      - id: authz-schema-sync-check
        name: Check user schema
        args: ["--schema", "schemas/user.zed", "--output", "models/user_models.py"]
      - id: authz-schema-sync-check
        name: Check product schema
        args: ["--schema", "schemas/product.zed", "--output", "models/product_models.py"]
```

### As a Command-line Tool

You can also use the package as a command-line tool:

```bash
# Check if files are in sync
authz-schema-sync-check --schema path/to/schema.zed --output path/to/models.py

# Automatically apply changes
authz-schema-sync-check --schema path/to/schema.zed --output path/to/models.py --auto-fix
```

Options:
- `--schema`: Path to the schema.zed file (default: `schema.zed`)
- `--output`: Path to the output models.py file (default: `models.py`)
- `--auto-fix`: Automatically apply changes if out of sync
- `--verbose`: Enable verbose output

## Generated Type Definitions

The package generates the following type definitions based on the schema:

1. **Resource Classes**: Classes for each object type defined in the schema.
2. **Permission Literals**: Type literals for permissions specific to each resource type.
3. **Relation Literals**: Type literals for relations specific to each resource type.
4. **Type Variables**: Type variables for future DSL implementation.

### Example

#### schema.zed

```
definition user {}

definition group {
    relation organization: organization
    relation member: user | group#member

    permission edit_members = organization->administrate
}

definition organization {
    relation admin: user | group#member

    permission administrate = admin
}
```

#### Generated models.py

```python
"""
GENERATED CODE - DO NOT EDIT MANUALLY
This file is generated from schema.zed and should not be modified directly.
"""

from typing import Literal, TypeVar, Generic, overload, Union
from pydantic import BaseModel

# Resource types from schema
class User:
    """User resource from schema.zed"""
    def __init__(self, id: str):
        self.id = id
        self.type = "user"

class Group:
    """Group resource from schema.zed"""
    def __init__(self, id: str):
        self.id = id
        self.type = "group"

class Organization:
    """Organization resource from schema.zed"""
    def __init__(self, id: str):
        self.id = id
        self.type = "organization"

# Permission literals for each resource type
GroupPermission = Literal["edit_members"]
OrganizationPermission = Literal["administrate"]

# Relation literals for each resource type
GroupRelation = Literal["organization", "member"]
OrganizationRelation = Literal["admin"]

# Type variables for future DSL implementation
T = TypeVar('T')
S = TypeVar('S')

# Placeholder for future DSL implementation
# This will be implemented separately
```

## Development

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/authz-schema-sync-check.git
   cd authz-schema-sync-check
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .
   ```

### Running Tests

```bash
pytest
```

## License

MIT
