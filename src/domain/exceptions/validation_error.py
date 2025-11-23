from __future__ import annotations

from .domain_error import DomainError


class ValidationError(DomainError):
    """Raised when business/data validation fails.

    Maps to HTTP 400 in the API layer.
    """

    def __init__(self, message: str | None = None) -> None:
        if message is None:
            message = "Validation failed for the provided data"
        super().__init__(message)
