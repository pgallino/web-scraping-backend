from __future__ import annotations


class DomainError(Exception):
    """Base class for domain-level exceptions.

    Accepts an optional message. If none provided, a generic message is used.
    """

    def __init__(self, message: str | None = None) -> None:
        if message is None:
            message = "An unspecified domain error occurred"
        super().__init__(message)
