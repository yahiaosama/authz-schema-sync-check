from typing import Literal

from pydantic import BaseModel


class Relation(BaseModel):
    """
    Invalid Relation class with missing fields and incorrect types.
    """

    # Missing subject_type field
    subject_id: str
    # Missing subject_relation field
    # Incorrect relation type - doesn't match schema.zed
    relation: Literal["invalid_relation", "nonexistent_relation"]
    # Incorrect object_type - doesn't include all types from schema.zed
    object_type: Literal["user", "group"]  # Missing "organization"
    object_id: str
