# authz-schema-sync-check

A pre-commit hook for generating and syncing type definitions from SpiceDB schema.

## Overview

This package provides a pre-commit hook that generates type definitions from a SpiceDB schema file (`schema.zed`) and ensures they are in sync with a Python resources file (`resources.py`). It uses Git to compare the generated code with the existing code and can automatically apply changes.

## Installation

This package is built with Poetry and should be used with Poetry:

```bash
# Add to your project
poetry add --dev authz-schema-sync-check

# Or for development
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
    rev: v0.1.0
    hooks:
      - id: authz-schema-sync-check
        args: [
          "--schema", "backend/app/infra/authz/schema.zed",
          "--output", "backend/app/infra/authz/resources.py",
          "--verbose",
          "--colorized-diff=true",
          "--auto-fix"
        ]
        files: 'backend/app/infra/authz/schema\.zed$|backend/app/infra/authz/resources\.py$'
        pass_filenames: false
```

For local development with Poetry, use:

```yaml
repos:
  - repo: local
    hooks:
      - id: authz-schema-sync-check
        name: Check SpiceDB schema and models sync
        entry: poetry run authz-schema-sync-check
        language: system
        args: [
          "--schema", "path/to/schema.zed",
          "--output", "path/to/resources.py",
          "--verbose",
          "--colorized-diff=true",
          "--auto-fix"
        ]
        files: '\.zed$|resources\.py$'
        pass_filenames: false
```

Available options:
- `--schema`: Path to the schema.zed file (default: `schema.zed`)
- `--output`: Path to the output resources.py file (default: `resources.py`)
- `--auto-fix`: Automatically apply changes if out of sync
- `--verbose`: Enable verbose output
- `--colorized-diff`: Enable or disable colorized diff output (true/false, default: true)

The `files` pattern determines when the hook runs. In the example above, it will run whenever:
- The schema.zed file is modified
- The resources.py file is modified

**Important Note**: The hook will fail if the output file doesn't exist, even with `--auto-fix` enabled. With `--auto-fix`, it will create the file but still fail, requiring you to review and commit the newly created file in a separate step. This ensures that generated files are always explicitly committed.

### As a Command-line Tool

You can also use the package as a command-line tool:

```bash
# Check if files are in sync
poetry run authz-schema-sync-check --schema path/to/schema.zed --output path/to/resources.py

# Automatically apply changes
poetry run authz-schema-sync-check --schema path/to/schema.zed --output path/to/resources.py --auto-fix

# Check with colorized diff disabled
poetry run authz-schema-sync-check --schema path/to/schema.zed --output path/to/resources.py --colorized-diff=false
```

Options:
- `--schema`: Path to the schema.zed file (default: `schema.zed`)
- `--output`: Path to the output resources.py file (default: `resources.py`)
- `--auto-fix`: Automatically apply changes if out of sync
- `--verbose`: Enable verbose output
- `--colorized-diff`: Enable or disable colorized diff output (true/false, default: true)

## Generated Type Definitions

The package generates the following type definitions based on the schema:

1. **Resource Classes**: Classes for each object type defined in the schema.
2. **Permission Literals**: Type literals for permissions specific to each resource type.
3. **Relation Literals**: Type literals for relations specific to each resource type.
4. **CheckRequest Class**: A NamedTuple for representing permission check requests.
5. **DSL Implementation**: Classes for building a fluent permission checking API.

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

#### Generated resources.py

```python
"""
GENERATED CODE - DO NOT EDIT MANUALLY
This file is generated from schema.zed and should not be modified directly.
"""

from abc import ABC
from typing import Any, Generic, Literal, NamedTuple, TypeVar, overload


class CheckRequest(NamedTuple):
    """A request to check a permission or relation."""

    subject_type: str
    subject_id: str
    subject_relation: str | None
    action: str  # The permission or relation name
    resource_type: str
    resource_id: str
    context: dict[str, Any] | None = None


# Permission literals for each resource type
UserPermission = Literal["read", "update", "make_admin", "revoke_admin"]
GroupPermission = Literal["edit_members"]
OrganizationPermission = Literal["administrate", "read"]

# Relation literals for each resource type
UserRelation = Literal["organization", "self"]
GroupRelation = Literal["organization", "member"]
OrganizationRelation = Literal["admin", "member"]


# Abstract base class for all resources
class Resource(ABC):
    """Abstract base class for all resources."""

    def __init__(self, id: str, subject_relation: str | None = None):
        self.id = id
        self.type = ""  # Will be overridden by subclasses
        self.subject_relation = subject_relation


# Resource types from schema
class User(Resource):
    """User resource from schema.zed"""

    def __init__(self, id: str, subject_relation: str | None = None):
        super().__init__(id, subject_relation)
        self.type = "user"


class Group(Resource):
    """Group resource from schema.zed"""

    def __init__(self, id: str, subject_relation: str | None = None):
        super().__init__(id, subject_relation)
        self.type = "group"


class Organization(Resource):
    """Organization resource from schema.zed"""

    def __init__(self, id: str, subject_relation: str | None = None):
        super().__init__(id, subject_relation)
        self.type = "organization"


# Type variable for resources
T = TypeVar("T", bound=Resource)  # Constrain T to be a subclass of Resource


# DSL implementation
class ResourceCheck(Generic[T]):
    """First step in the permission check chain."""

    def __init__(self, resource: T):
        self.resource = resource

    def check_that(self, subject: Resource) -> "SubjectCheck[T]":
        """
        Check that the subject has permissions on the resource.

        Args:
            subject: The subject to check permissions for (another resource)

        Returns:
            A SubjectCheck object to continue the permission check chain
        """
        return SubjectCheck(self.resource, subject)


class SubjectCheck(Generic[T]):
    """Second step in the permission check chain."""

    def __init__(self, resource: T, subject: Resource):
        self.resource = resource
        self.subject = subject

    @overload
    def can(
        self: "SubjectCheck[User]",
        permission: UserPermission,
        context: dict[str, Any] | None = None,
    ) -> CheckRequest: ...
    @overload
    def can(
        self: "SubjectCheck[Group]",
        permission: GroupPermission,
        context: dict[str, Any] | None = None,
    ) -> CheckRequest: ...
    @overload
    def can(
        self: "SubjectCheck[Organization]",
        permission: OrganizationPermission,
        context: dict[str, Any] | None = None,
    ) -> CheckRequest: ...

    def can(
        self, permission: str, context: dict[str, Any] | None = None
    ) -> CheckRequest:
        """
        Create a permission check request.

        Args:
            permission: The permission to check
            context: Additional context for the permission check (optional)

        Returns:
            A CheckRequest object
        """
        return CheckRequest(
            subject_type=self.subject.type,
            subject_id=self.subject.id,
            subject_relation=self.subject.subject_relation,
            action=permission,
            resource_type=self.resource.type,
            resource_id=self.resource.id,
            context=context,
        )

    @overload
    def is_(
        self: "SubjectCheck[User]",
        relation: UserRelation,
        context: dict[str, Any] | None = None,
    ) -> CheckRequest: ...
    @overload
    def is_(
        self: "SubjectCheck[Group]",
        relation: GroupRelation,
        context: dict[str, Any] | None = None,
    ) -> CheckRequest: ...
    @overload
    def is_(
        self: "SubjectCheck[Organization]",
        relation: OrganizationRelation,
        context: dict[str, Any] | None = None,
    ) -> CheckRequest: ...

    def is_(self, relation: str, context: dict[str, Any] | None = None) -> CheckRequest:
        """
        Create a relation check request.

        Args:
            relation: The relation to check
            context: Additional context for the relation check (optional)

        Returns:
            A CheckRequest object
        """
        return CheckRequest(
            subject_type=self.subject.type,
            subject_id=self.subject.id,
            subject_relation=self.subject.subject_relation,
            action=relation,
            resource_type=self.resource.type,
            resource_id=self.resource.id,
            context=context,
        )


def on_resource(resource: T) -> ResourceCheck[T]:
    """
    Start a permission check chain for the specified resource.

    Args:
        resource: The resource to check permissions on

    Returns:
        A ResourceCheck object to continue the permission check chain
    """
    return ResourceCheck(resource)
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

### Building the Package

```bash
poetry build
```

## Troubleshooting

### Missing Output File

If you see an error like:

```
Error: Output file 'path/to/resources.py' does not exist
```

This means the resources.py file doesn't exist yet. Run the hook with `--auto-fix` to create it:

```bash
poetry run authz-schema-sync-check --schema path/to/schema.zed --output path/to/resources.py --auto-fix
```

Then review the generated file and commit it.

### Files Out of Sync

If you see an error like:

```
Error: resources.py is out of sync with schema.zed
```

This means you've modified the schema.zed file but haven't updated resources.py. Run the hook with `--auto-fix` to update it:

```bash
poetry run authz-schema-sync-check --schema path/to/schema.zed --output path/to/resources.py --auto-fix
```

Then review the changes and commit them.

## License

MIT
