from __future__ import annotations

from .domain_error import DomainError


class RepositoryNotConfiguredError(DomainError):
    """Raised when a service is used without a configured repository."""

    def __init__(self, message: str | None = None) -> None:
        if message is None:
            message = "Repository not configured for this service"
        super().__init__(message)
