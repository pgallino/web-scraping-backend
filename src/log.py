import contextvars
import logging
import sys
from uuid import uuid4

from src.config import core_settings as settings

# Formato de log legible para desarrollo. Incluimos request_id para trazar
# peticiones a través de capas. Nivel por defecto: DEBUG (desarrollo).
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] [%(request_id)s] [%(module)s:%(lineno)d] - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Context var para propagar el request id entre corutinas
request_id_ctx_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default="-"
)


class RequestIdFormatter(logging.Formatter):
    def format(self, record):
        # Ensure record has request_id attribute for formatting
        try:
            record.request_id = request_id_ctx_var.get()
        except Exception:
            record.request_id = "-"
        return super().format(record)


def setup_logging():
    """Configura el sistema de logging para la aplicación."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(RequestIdFormatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    root = logging.getLogger()
    # Clear default handlers to avoid duplicate logs
    for h in list(root.handlers):
        root.removeHandler(h)
    root.addHandler(handler)
    # Read the configured log level from central settings (core_settings.LOG_LEVEL).
    # This keeps logging configuration in sync with application settings.
    level_name = getattr(settings, "LOG_LEVEL", "DEBUG")
    try:
        level = getattr(logging, str(level_name).upper())
    except Exception:
        # Fallback to INFO if the configured value is invalid
        level = logging.INFO
    root.setLevel(level)

    # Reduce noise from very chatty third-party libraries unless debugging
    if level > logging.DEBUG:
        logging.getLogger("aiosqlite").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("asyncio").setLevel(logging.WARNING)
        logging.getLogger("uvicorn").setLevel(logging.WARNING)


# Inicializa el logging al cargar el módulo
setup_logging()
logger = logging.getLogger("fastapi_backend")


# Helper to generate a new request id
def new_request_id() -> str:
    return uuid4().hex
