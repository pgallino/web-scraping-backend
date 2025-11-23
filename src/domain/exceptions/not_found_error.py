from __future__ import annotations

from .domain_error import DomainError


class NotFoundError(DomainError):
    """Raised when a requested resource is not found.

    Maps to HTTP 404 in the API layer.
    """

    def __init__(self, message: str | None = None) -> None:
        if message is None:
            message = "Requested resource not found"
        super().__init__(message)
