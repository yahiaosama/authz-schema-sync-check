"""
GENERATED CODE - DO NOT EDIT MANUALLY
This file is generated from schema.zed and should not be modified directly.
"""

from typing import Any, Generic, Literal, NamedTuple, TypeVar

# Type aliases
ResourceId = str
Context = dict[str, Any] | None


class CheckRequest(NamedTuple):
    """A request to check a permission or relation."""

    subject_type: str
    subject_id: ResourceId
    subject_relation: str | None
    action: str
    resource_type: str
    resource_id: ResourceId
    context: Context = None


# Type variables for permissions
P = TypeVar("P")  # For resource permissions
S = TypeVar("S")  # For subject permissions


# Base resource class
class Resource(Generic[P]):
    """Base class for all resources with typed permissions."""

    def __init__(self, id: ResourceId, resource_type: str):
        self.id = id
        self.type = resource_type


# Resource classes with their specific permission types
class User(Resource[Literal["read", "update", "make_admin", "revoke_admin"]]):
    """User resource from schema.zed"""

    def __init__(self, id: ResourceId):
        super().__init__(id, "user")


class Group(Resource[Literal["edit_members"]]):
    """Group resource from schema.zed"""

    def __init__(self, id: ResourceId):
        super().__init__(id, "group")


class Organization(
    Resource[
        Literal[
            "administrate",
            "support",
            "read",
            "create_users",
            "view_articles",
            "edit_articles",
            "view_requests",
            "edit_requests",
            "view_suppliers",
            "edit_suppliers",
            "view_table_views",
            "edit_table_views",
        ]
    ]
):
    """Organization resource from schema.zed"""

    def __init__(self, id: ResourceId):
        super().__init__(id, "organization")


class Role(
    Resource[
        Literal[
            "edit",
            "view_articles",
            "edit_articles",
            "view_requests",
            "edit_requests",
            "view_suppliers",
            "edit_suppliers",
            "view_table_views",
            "edit_table_views",
        ]
    ]
):
    """Role resource from schema.zed"""

    def __init__(self, id: ResourceId):
        super().__init__(id, "role")


class Policy(
    Resource[
        Literal[
            "use",
            "view_articles",
            "edit_articles",
            "view_requests",
            "edit_requests",
            "view_suppliers",
            "edit_suppliers",
            "view_table_views",
            "edit_table_views",
        ]
    ]
):
    """Policy resource from schema.zed"""

    def __init__(self, id: ResourceId):
        super().__init__(id, "policy")


class Article(Resource[Literal["view", "edit"]]):
    """Article resource from schema.zed"""

    def __init__(self, id: ResourceId):
        super().__init__(id, "article")


class Request(Resource[Literal["view", "edit"]]):
    """Request resource from schema.zed"""

    def __init__(self, id: ResourceId):
        super().__init__(id, "request")


class Supplier(Resource[Literal["view", "edit"]]):
    """Supplier resource from schema.zed"""

    def __init__(self, id: ResourceId):
        super().__init__(id, "supplier")


class TableView(Resource[Literal["view", "edit"]]):
    """TableView resource from schema.zed"""

    def __init__(self, id: ResourceId):
        super().__init__(id, "table_view")


# DSL implementation
class ResourceCheck(Generic[P, S]):
    """First step in the permission check chain."""

    def __init__(self, resource: Resource[P]):
        self.resource = resource

    def check_that(
        self, subject: Resource[S], *, subject_relation: str | None = None
    ) -> "SubjectCheck[P, S]":
        """
        Check that the subject has permissions on the resource.

        Args:
            subject: The subject to check permissions for (another resource)
            subject_relation: The relation of the subject (keyword-only argument)

        Returns:
            A SubjectCheck object to continue the permission check chain
        """
        return SubjectCheck(self.resource, subject, subject_relation)


class SubjectCheck(Generic[P, S]):
    """Second step in the permission check chain."""

    def __init__(
        self, resource: Resource[P], subject: Resource[S], subject_relation: str | None
    ):
        self.resource = resource
        self.subject = subject
        self.subject_relation = subject_relation

    def can(self, permission: P, context: Context = None) -> CheckRequest:
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
            subject_relation=self.subject_relation,
            action=str(permission),  # Convert to string for the CheckRequest
            resource_type=self.resource.type,
            resource_id=self.resource.id,
            context=context,
        )


def on_resource(resource: Resource[P]) -> ResourceCheck[P, S]:
    """
    Start a permission check chain for the specified resource.

    Args:
        resource: The resource to check permissions on

    Returns:
        A ResourceCheck object to continue the permission check chain
    """
    return ResourceCheck(resource)
