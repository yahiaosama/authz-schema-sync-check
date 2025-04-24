"""
Custom error classes for validation errors.
"""


class ValidationError(Exception):
    """Base class for validation errors."""

    pass


class ObjectTypeError(ValidationError):
    """Error for missing object types."""

    pass


class RelationError(ValidationError):
    """Error for missing relations."""

    pass
