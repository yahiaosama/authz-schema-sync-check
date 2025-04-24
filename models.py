"""
GENERATED CODE - DO NOT EDIT MANUALLY
This file is generated from schema.zed and should not be modified directly.
"""

from typing import Literal, TypeVar, Generic, Any, overload

# Permission literals for each resource type
GroupPermission = Literal["edit_members"]
OrganizationPermission = Literal["administrate"]

# Relation literals for each resource type
GroupRelation = Literal["organization", "member"]
OrganizationRelation = Literal["admin"]

# Resource types from schema
class User:
    """User resource from schema.zed"""
    def __init__(self, id: str):
        self.id = id
        self.type = "user"
        self._relation: str | None = None
    
    
    @property
    def relation(self) -> str | None:
        return self._relation
class Group:
    """Group resource from schema.zed"""
    def __init__(self, id: str):
        self.id = id
        self.type = "group"
        self._relation: str | None = None
    
    def organization(self) -> "Group":
        """Set the relation to 'organization'."""
        self._relation = "organization"
        return self
    def member(self) -> "Group":
        """Set the relation to 'member'."""
        self._relation = "member"
        return self
    
    @property
    def relation(self) -> str | None:
        return self._relation
class Organization:
    """Organization resource from schema.zed"""
    def __init__(self, id: str):
        self.id = id
        self.type = "organization"
        self._relation: str | None = None
    
    def admin(self) -> "Organization":
        """Set the relation to 'admin'."""
        self._relation = "admin"
        return self
    
    @property
    def relation(self) -> str | None:
        return self._relation

# Type variable for resources
T = TypeVar('T')

# DSL implementation
class ResourceCheck(Generic[T]):
    """First step in the permission check chain."""
    def __init__(self, resource: T):
        self.resource = resource
    
    def check_that(self, subject: Any) -> "SubjectCheck[T]":
        """
        Check that the subject has permissions on the resource.
        
        Args:
            subject: The subject to check permissions for
            
        Returns:
            A SubjectCheck object to continue the permission check chain
        """
        return SubjectCheck(self.resource, subject)

class SubjectCheck(Generic[T]):
    """Second step in the permission check chain."""
    def __init__(self, resource: T, subject: Any):
        self.resource = resource
        self.subject = subject
    
    @overload
    def can(self: "SubjectCheck[Group]", permission: GroupPermission) -> bool: ...
    @overload
    def can(self: "SubjectCheck[Organization]", permission: OrganizationPermission) -> bool: ...
    
    def can(self, permission: str) -> bool:
        """
        Check if the subject has the specified permission on the resource.
        
        Args:
            permission: The permission to check
            
        Returns:
            True if the subject has the permission, False otherwise
        """
        resource_type = getattr(self.resource, "type", None)
        resource_id = getattr(self.resource, "id", None)
        subject_type = getattr(self.subject, "type", None)
        subject_id = getattr(self.subject, "id", None)
        subject_relation = getattr(self.subject, "relation", None)
        
        # Placeholder for SpiceDB integration
        print(f"Checking permission: {subject_type}:{subject_id}{f'#{subject_relation}' if subject_relation else ''} -> {permission} -> {resource_type}:{resource_id}")
        
        # For now, just return True as a placeholder
        return True

def on_resource(resource: T) -> ResourceCheck[T]:
    """
    Start a permission check chain for the specified resource.
    
    Args:
        resource: The resource to check permissions on
        
    Returns:
        A ResourceCheck object to continue the permission check chain
    """
    return ResourceCheck(resource)