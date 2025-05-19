"""
GENERATED CODE - DO NOT EDIT MANUALLY
This file is generated from schema.zed and should not be modified directly.
"""

from typing import Any, Generic, Literal, TypeVar

# Type aliases
ResourceId = int | str
Context = dict[str, Any] | None

# Permission type aliases for each resource type
UserPermission = Literal["read", "update", "make_admin", "revoke_admin"]
GroupPermission = Literal["edit_members"]
OrganizationPermission = Literal["administrate", "read"]
TableViewPermission = Literal["view", "edit"]

# Type variable for permission literals
P = TypeVar("P", bound=str)


# Base resource class
class Resource(Generic[P]):
    """Base class for all resources with typed permissions."""

    def __init__(self, id: ResourceId, resource_type: str):
        self.id = id
        self.type = resource_type


# Resource classes with their specific permission types
class User(Resource[UserPermission]):
    """User resource from schema.zed"""

    # Set the permission type for this resource
    permission_type = UserPermission

    def __init__(self, id: ResourceId):
        super().__init__(id, "user")


class Group(Resource[GroupPermission]):
    """Group resource from schema.zed"""

    # Set the permission type for this resource
    permission_type = GroupPermission

    def __init__(self, id: ResourceId):
        super().__init__(id, "group")


class Organization(Resource[OrganizationPermission]):
    """Organization resource from schema.zed"""

    # Set the permission type for this resource
    permission_type = OrganizationPermission

    def __init__(self, id: ResourceId):
        super().__init__(id, "organization")


class TableView(Resource[TableViewPermission]):
    """TableView resource from schema.zed"""

    # Set the permission type for this resource
    permission_type = TableViewPermission

    def __init__(self, id: ResourceId):
        super().__init__(id, "table_view")
