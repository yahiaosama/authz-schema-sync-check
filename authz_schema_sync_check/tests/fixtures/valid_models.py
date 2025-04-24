from enum import Enum
from typing import Literal

from pydantic import BaseModel


class ObjectType(str, Enum):
    """Valid object types from schema.zed"""

    USER = "user"
    GROUP = "group"
    ORGANIZATION = "organization"


class RelationType(str, Enum):
    """Valid relation types from schema.zed"""

    MEMBER = "member"
    ORGANIZATION = "organization"
    ADMIN = "admin"


class Relation(BaseModel):
    """
    Represents a relationship between a subject and an object with a specific relation.

    Attributes:
        subject_type: The type of the subject (e.g. "user", "group")
        subject_id: The ID of the subject
        subject_relation: Optional relation for the subject (e.g. "member" for groups)
        relation: The relation between the subject and object (e.g. "member", "admin")
        object_type: The type of the object (e.g. "group", "organization")
        object_id: The ID of the object

    Example:
        ```python
        # User with ID "123" is a member of group with ID "456"
        relation = Relation(
            subject_type=ObjectType.USER,
            subject_id="123",
            relation=RelationType.MEMBER,
            object_type=ObjectType.GROUP,
            object_id="456",
        )

        # Group with ID "456" belongs to organization with ID "789"
        relation = Relation(
            subject_type=ObjectType.ORGANIZATION,
            subject_id="789",
            relation=RelationType.ORGANIZATION,
            object_type=ObjectType.GROUP,
            object_id="456",
        )
        ```
    """

    subject_type: Literal["user", "group", "organization"]
    subject_id: str
    subject_relation: Literal["member"] | None = None
    relation: Literal["member", "organization", "admin"]
    object_type: Literal["user", "group", "organization"]
    object_id: str
