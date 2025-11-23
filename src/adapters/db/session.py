import ssl
from typing import Any, Dict, Union
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Read DB URL from central core settings (only needs DB / SQL flags)
from src.config import core_settings as settings

DB_URL = settings.DB_URL_ASYNC


def _sanitize_async_url_and_connect_args(db_url: str):
    """Remove any ``sslmode`` query param from the URL and return
    (sanitized_url, connect_args).

    asyncpg's connect() does not accept the ``sslmode`` keyword argument
    (that's used by sync drivers like psycopg2). If a connection string
    includes ``?sslmode=require`` (for example from Neon), we translate
    that into a proper ``ssl`` argument for asyncpg (an SSLContext).
    """
    try:
        parsed = urlparse(db_url)
    except Exception:
        return db_url, {}

    if not parsed.query:
        return db_url, {}

    qs = dict(parse_qsl(parsed.query, keep_blank_values=True))

    # Remove known unsupported keys for asyncpg connect
    # asyncpg.connect does not accept 'channel_binding' nor 'sslmode'
    sslmode = None
    for key in ("sslmode", "SSL_MODE", "ssl_mode"):
        if key in qs:
            sslmode = qs.pop(key)
            break

    # Remove channel_binding if present (e.g. channel_binding=prefer)
    for cb_key in (
        "channel_binding",
        "channel-binding",
        "channelBinding",
        "CHANNEL_BINDING",
    ):
        if cb_key in qs:
            qs.pop(cb_key, None)

    # rebuild URL without the removed keys
    new_query = urlencode(qs, doseq=True)
    sanitized = urlunparse(parsed._replace(query=new_query))

    # Map sslmode values to an SSLContext (asyncpg expects 'ssl')
    ssl_arg: Union[bool, ssl.SSLContext, None] = None
    # sslmode may be None; only call .lower() when it's a str
    if isinstance(sslmode, str):
        if sslmode.lower() == "disable":
            ssl_arg = False
        else:
            # create a default SSL context which enforces cert verification
            ctx = ssl.create_default_context()
            ssl_arg = ctx

    # If ssl_arg is None we return an empty connect_args dict
    connect_args: Dict[str, Any] = {"ssl": ssl_arg} if ssl_arg is not None else {}

    return sanitized, connect_args


sanitized_url, _connect_args = _sanitize_async_url_and_connect_args(DB_URL)

engine = create_async_engine(
    sanitized_url,
    connect_args=_connect_args,
    echo=bool(settings.SQL_ECHO),
    future=True,
)
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
