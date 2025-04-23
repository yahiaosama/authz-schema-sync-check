from authzed.api.v1 import (
    ObjectReference,
    Relationship,
    RelationshipUpdate,
    SubjectReference,
)
from pydantic import BaseModel


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
            subject_type="user",
            subject_id="123",
            relation="member",
            object_type="group",
            object_id="456",
        )

        # Group with ID "456" belongs to organization with ID "789"
        relation = Relation(
            subject_type="organization",
            subject_id="789",
            relation="organization",
            object_type="group",
            object_id="456",
        )
        ```
    """

    subject_type: str
    subject_id: str
    subject_relation: str | None = None
    relation: str
    object_type: str
    object_id: str

    def to_proto(
        self, operation: RelationshipUpdate.Operation.ValueType
    ) -> RelationshipUpdate:
        """
        Convert this Relation to a protobuf RelationshipUpdate.

        Args:
            operation: The operation type (TOUCH, DELETE, etc.)

        Returns:
            A RelationshipUpdate protobuf object
        """
        subject = SubjectReference(
            object=ObjectReference(
                object_type=self.subject_type, object_id=self.subject_id
            )
        )
        if self.subject_relation:
            subject.optional_relation = self.subject_relation

        return RelationshipUpdate(
            operation=operation,
            relationship=Relationship(
                subject=subject,
                relation=self.relation,
                resource=ObjectReference(
                    object_type=self.object_type, object_id=self.object_id
                ),
            ),
        )
