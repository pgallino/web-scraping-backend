import json
from typing import Any, Iterable, List

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.log import logger, new_request_id, request_id_ctx_var


def _parse_allowed_origins(raw: str, allow_all: bool, env: str) -> List[str]:
    """Return a list of origins from the raw ALLOWED_ORIGINS string.

    Accepts both JSON arrays (e.g. "[\"https://a\", \"https://b\"]")
    or comma-separated strings. If allow_all is True returns ["*"]. If no
    origins are provided and we're in development, return local origins.
    """
    if allow_all:
        return ["*"]

    if not raw:
        raw = ""

    ra = raw.strip()
    origins: List[str] = []
    if ra.startswith("["):
        try:
            origins = list(json.loads(ra))
        except Exception:
            origins = [o.strip() for o in ra.strip("[]").split(",") if o.strip()]
    else:
        origins = [o.strip() for o in ra.split(",") if o.strip()]

    if not origins and env in ("dev", "development"):
        origins = ["http://localhost:5173", "http://127.0.0.1:5173"]

    return origins


def _default_allow_headers() -> Iterable[str]:
    """Headers that we allow for CORS preflight responses.

    Keep this centralized so it's easy to extend in the future.
    """
    return [
        "Authorization",
        "Content-Type",
        "Accept",
        "X-API-Key",
        "X-Requested-With",
        "X-Request-ID",
        # Allow a custom agent header if clients want to supply one
        "X-Agent",
    ]


def add_middlewares(app: FastAPI, settings: Any) -> None:
    """Configure CORS (if requested) and add the request-id middleware.

    This centralizes the middleware configuration so `src/app.py` stays small.
    """
    raw = getattr(settings, "ALLOWED_ORIGINS", None) or ""
    allow_all = getattr(settings, "ALLOW_ALL_ORIGINS", False)
    env = getattr(settings, "ENVIRONMENT", "")

    origins = _parse_allowed_origins(raw, allow_all, env)

    if origins:
        allow_credentials = not (len(origins) == 1 and origins[0] == "*")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=allow_credentials,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=list(_default_allow_headers()),
            max_age=3600,
        )
        logger.debug(
            "CORS configured origins=%s allow_credentials=%s",
            origins,
            allow_credentials,
        )

    @app.middleware("http")
    async def add_request_id_middleware(request: Request, call_next):
        """Ensure a request id exists for every request and populate the log context."""
        rid = request.headers.get("X-Request-ID") or new_request_id()
        # capture client agent (may be absent for some clients)
        client_agent = request.headers.get("User-Agent") or request.headers.get("X-Agent")
        request_id_ctx_var.set(rid)
        logger.debug(
            "HTTP request start %s %s request_id=%s agent=%s",
            request.method,
            request.url.path,
            rid,
            client_agent,
        )
        try:
            response = await call_next(request)
        finally:
            request_id_ctx_var.set("-")
        response.headers["X-Request-ID"] = rid
        logger.debug(
            "HTTP request end %s %s request_id=%s status=%s agent=%s",
            request.method,
            request.url.path,
            rid,
            getattr(response, "status_code", "-"),
            client_agent,
        )
        return response
