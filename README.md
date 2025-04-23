# authz-schema-sync-check

A pre-commit hook for checking and syncing SpiceDB schema with Python models.

## Overview

This package provides a pre-commit hook that validates the synchronization between a SpiceDB schema file (`schema.zed`) and a Python models file (`models.py`). It ensures that the Python models correctly represent the relationships defined in the SpiceDB schema.

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

By default, the hook will look for `schema.zed` and `models.py` in the current directory. You can customize the paths using the `--schema` and `--models` options:

```yaml
repos:
  - repo: https://github.com/your-username/authz-schema-sync-check
    rev: v0.1.0
    hooks:
      - id: authz-schema-sync-check
        args: ["--schema", "path/to/schema.zed", "--models", "path/to/models.py"]
```

### As a Command-line Tool

You can also use the package as a command-line tool:

```bash
authz-schema-sync-check --schema path/to/schema.zed --models path/to/models.py
```

Options:
- `--schema`: Path to the schema.zed file (default: `schema.zed`)
- `--models`: Path to the models.py file (default: `models.py`)
- `--verbose`: Enable verbose output

## Validation Rules

The package performs the following validations:

1. **Object Types**: Verifies that all object types defined in `schema.zed` are available as `subject_type` and `object_type` in `models.py`.
2. **Relations**: Checks that all relations defined in `schema.zed` can be used in the `relation` field in `models.py`.
3. **Required Fields**: Ensures that the `Relation` class in `models.py` has all required fields (`subject_type`, `subject_id`, `relation`, `object_type`, `object_id`).

## Example

### schema.zed

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

### models.py

```python
from typing import Literal

from pydantic import BaseModel


class Relation(BaseModel):
    subject_type: Literal["user", "group", "organization"]
    subject_id: str
    subject_relation: Literal["member"] | None = None
    relation: Literal["member", "organization", "admin"]
    object_type: Literal["user", "group", "organization"]
    object_id: str
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
