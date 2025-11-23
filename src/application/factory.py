from typing import Optional

from src.adapters.db.repositories.tool_repository import SqlAlchemyToolRepository
from src.application.facade import ApplicationFacade


def create_facade(
    project_name: str, environment: str, tool_repository: Optional[object] = None
) -> ApplicationFacade:
    """Create an ApplicationFacade with sensible defaults.

    The factory lets other adapters (CLI, tests) create a facade with a
    different repository implementation if desired.
    """
    repo = tool_repository or SqlAlchemyToolRepository()
    return ApplicationFacade(
        project_name=project_name, environment=environment, tool_repository=repo
    )
