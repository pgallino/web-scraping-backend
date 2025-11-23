"""Domain exceptions package.

This package exposes domain-level exceptions so other modules can import
from `src.domain.exceptions` (same API as the previous single-file module).
"""

from .conflict_error import ConflictError
from .domain_error import DomainError
from .not_found_error import NotFoundError
from .repository_not_configured_error import RepositoryNotConfiguredError
from .validation_error import ValidationError

__all__ = [
    "DomainError",
    "RepositoryNotConfiguredError",
    "ValidationError",
    "NotFoundError",
    "ConflictError",
]
