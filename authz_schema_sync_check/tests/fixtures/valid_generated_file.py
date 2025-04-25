"""
GENERATED CODE - DO NOT EDIT MANUALLY
This file is generated from schema.zed and should not be modified directly.
"""

from typing import Literal, TypeVar, Generic, Any, overload, NamedTuple
from abc import ABC


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
