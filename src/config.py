import os
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class CommonSettings(BaseSettings):
    """Settings shared by both CLI and API applications.

    This class contains values that both adapters may need (project name,
    environment, DB urls, CORS flags). We intentionally avoid including API
    specific secrets here so that the CLI can use a settings object without an
    API key field.
    """

    model_config = SettingsConfigDict(extra="ignore")

    PROJECT_NAME: str
    ENVIRONMENT: str
    # Note: CORS (allowed origins) is API-specific and defined on APISettings.

    DB_URL_ASYNC: str
    DB_URL_SYNC: Optional[str] = None
    SQL_ECHO: bool = False
    # Global log level for the application. Can be overridden per-environment.
    # Expected values: DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_LEVEL: str = "INFO"


class APISettings(CommonSettings):
    """Settings used by the HTTP API application (includes API_KEY)."""

    API_KEY: Optional[str] = None
    # CORS configuration (optional):
    # - If ALLOW_ALL_ORIGINS is true, the app will allow requests from any origin
    #   (useful for public APIs or temporary testing). Do NOT enable in sensitive
    #   production environments unless you understand the risks.
    # - Otherwise, set ALLOWED_ORIGINS to a comma-separated list of origins.
    ALLOWED_ORIGINS: Optional[str] = None
    ALLOW_ALL_ORIGINS: bool = False


class CLISettings(CommonSettings):
    """Settings used by CLI application. Intentionally does not expose
    API_KEY so CLI code cannot accidentally rely on API-only configuration.
    """

    pass


# Developer convenience: if a local .env file exists in the repo root, load it
# into the process environment before instantiating Settings. This allows
# developers to keep a local `.env` (ignored by git) for convenience while
# keeping the application code free of defaults.
env_path = Path(".env")
if env_path.exists():
    # load_dotenv does not override existing environment variables by default
    load_dotenv(env_path)


# Recreate settings now that .env may have been loaded
class MissingEnvironmentVariables(RuntimeError):
    """Raised when required environment variables are not present.

    This is raised early (during import) so the application fails fast
    with a clear, actionable message instead of a cryptic validation
    error later on.
    """


def _ensure_required_env_vars(required: List[str]) -> None:
    missing = [v for v in required if not os.environ.get(v)]
    if missing:
        msg_lines = [
            "Missing required environment variables:",
            ", ".join(missing),
            "",
            "To fix locally: copy .env.example -> .env and set the values, or",
            "export the variables in your shell. In CI/production inject the",
            "variables via your secrets manager (GitHub Actions, Render, etc.).",
        ]
        raise MissingEnvironmentVariables("\n".join(msg_lines))


# List the settings names we expect to find in the environment. Keep this in
# sync with the fields defined on `Settings` above.
# Only require the core settings for the app to run; keep CORS optional to
# avoid requiring ALLOWED_ORIGINS configuration during CI and simple dev runs.
_required_env_vars = [
    "PROJECT_NAME",
    "ENVIRONMENT",
    "DB_URL_ASYNC",
]

# Fail fast with a clear message if any required env var is missing.
_ensure_required_env_vars(_required_env_vars)


# API-specific required environment variables. Keep the check out of module
# import-time for CLI use; the API application should call
# `ensure_api_required_env_vars()` before starting to enforce these.
_api_required_env_vars = _required_env_vars + ["API_KEY"]


def ensure_api_required_env_vars() -> None:
    """Ensure environment variables required by the API are present.

    This function should be called by API entrypoints (for example in
    `src/application/api_app.py`) before instantiating or using API-only
    settings. We intentionally avoid enforcing API secrets at module import
    time so CLI runs don't fail when API-only env vars are absent.
    """
    _ensure_required_env_vars(_api_required_env_vars)


def ensure_common_required_env_vars() -> None:
    """Ensure the common/core environment variables are present.

    This is a thin wrapper around the internal helper so callers (CLI startup)
    can ask for the same enforcement in an explicit and readable way.
    """
    _ensure_required_env_vars(_required_env_vars)


# Instantiate settings now that we've ensured the environment contains the
# required values. Mypy may still complain about missing constructor args
# because the class declares required attributes, but at runtime the values
# are supplied from the environment; use an inline ignore for the call site.
# Backwards-compatible single `settings` instance: keep this pointing to the
# API-focused settings so existing imports (`from src.config import settings`)
# continue to work. New code should import `api_settings` or `cli_settings`
# explicitly to make its intent clear.
api_settings = APISettings()  # type: ignore[call-arg]
cli_settings = CLISettings()  # type: ignore[call-arg]

# Minimal/common settings object for adapters that only need core values
# (DB urls, SQL_ECHO, PROJECT_NAME, ENVIRONMENT). Use this from modules
# like `src.adapters.db.session` to avoid importing API-only or CLI-only
# settings objects.
core_settings = CommonSettings()  # type: ignore[call-arg]
