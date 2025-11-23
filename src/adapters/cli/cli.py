import asyncio
from typing import Optional

import typer

from src.application.cli_app import app, cli_facade

# The Typer `app` is created in `src.application.cli_app` (the application
# entrypoint). This module only registers commands on that app.


@app.command()
def list_tools():
    """List all tools."""

    facade = cli_facade

    async def _inner():
        tools = await facade.list_tools()
        for t in tools:
            typer.echo(f"{t.id}: {t.name} - {t.description} ({t.link})")

    asyncio.run(_inner())


@app.command()
def get_tool(tool_id: int):
    """Get a single tool by id."""

    facade = cli_facade

    async def _inner():
        t = await facade.get_tool(tool_id)
        if t is None:
            typer.secho("Tool not found", fg=typer.colors.RED)
        else:
            typer.echo(f"{t.id}: {t.name} - {t.description} ({t.link})")

    asyncio.run(_inner())


@app.command()
def create(name: str, description: Optional[str] = "", link: Optional[str] = ""):
    """Create a new tool."""

    facade = cli_facade

    async def _inner():
        t = await facade.create_tool(
            name=name, description=description or "", link=link or ""
        )
        typer.secho(f"Created tool {t.id}", fg=typer.colors.GREEN)

    asyncio.run(_inner())


@app.command()
def delete(tool_id: int):
    """Delete a tool by id."""

    facade = cli_facade

    async def _inner():
        ok = await facade.delete_tool(tool_id)
        if ok:
            typer.secho("Deleted", fg=typer.colors.GREEN)
        else:
            typer.secho("Tool not found", fg=typer.colors.RED)

    asyncio.run(_inner())


def main() -> None:
    app()


if __name__ == "__main__":
    main()
