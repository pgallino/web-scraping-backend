from __future__ import annotations

from .domain_error import DomainError


class ConflictError(DomainError):
    """Raised when an operation conflicts with existing state (e.g. unique constraint).

    Maps to HTTP 409 in the API layer.
    """

    def __init__(self, message: str | None = None) -> None:
        if message is None:
            message = "Conflict with existing resource state"
        super().__init__(message)
