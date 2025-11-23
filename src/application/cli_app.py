from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typer import Typer

import typer

from src.application.factory import create_facade
from src.config import cli_settings, ensure_common_required_env_vars

# Ensure common environment variables are present for CLI runs.
ensure_common_required_env_vars()

# Instantiate facade for the CLI adapter
cli_facade = create_facade(
    project_name=cli_settings.PROJECT_NAME, environment=cli_settings.ENVIRONMENT
)

# Create the Typer app here (application entrypoint owns the app object).
# Adapters should import `app` and register commands on it.
app: "Typer" = typer.Typer(help="CLI for the backend application (tools)")


def main() -> None:
    """Entry point for running the CLI as a module: python -m src.application.cli_app"""
    app()


if __name__ == "__main__":
    main()
