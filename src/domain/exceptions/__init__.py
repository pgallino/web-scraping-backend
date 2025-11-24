"""Domain exceptions package.

This project removed the separate exception modules; keep a small set of
domain exception classes here so imports like
`from src.domain.exceptions import ValidationError` continue to work and
type checking (mypy) does not fail.

If you prefer to reintroduce separate files for each exception, move these
classes back into their own modules and restore imports.
"""


class DomainError(Exception):
    """Base class for domain-level errors."""


class RepositoryNotConfiguredError(DomainError):
    """Raised when a repository dependency was not configured."""


class ValidationError(DomainError):
    """Raised when a domain validation fails."""


class NotFoundError(DomainError):
    """Raised when an entity is not found in the domain."""


class ConflictError(DomainError):
    """Raised when a domain-level conflict occurs (e.g. duplicate)."""


class ScrapeError(DomainError):
    """Raised when a scraping operation fails (network / HTTP / parsing).

    `status_code` may contain the remote HTTP status code (e.g. 403)
    when the error originated from an HTTP response.
    """

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


__all__ = [
    "DomainError",
    "RepositoryNotConfiguredError",
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    "ScrapeError",
]
