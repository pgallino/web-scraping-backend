from typing import Optional

from fastapi import HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader

from src.config import api_settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_api_key(api_key: Optional[str] = Security(api_key_header)) -> None:
    """Dependency that validates X-API-Key header against api_settings.API_KEY.

    If `api_settings.API_KEY` is not set, the dependency is a no-op (allows requests).
    Otherwise it raises HTTP 403 if the header is missing or does not match.
    """
    expected = getattr(api_settings, "API_KEY", None)
    if not expected:
        # API key protection disabled
        return None

    if not api_key or api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key",
        )

    return None
