from typing import final

from src.adapters.db.repositories.tool_repository import SqlAlchemyToolRepository
from src.domain.tool_service import ToolService
from src.log import logger


@final
class ApplicationFacade:
    """
    Application Facade.
    Entry point for input adapters (HTTP, CLI, etc.).
    Orchestrates calls to the domain layer and other adapters (e.g. DB).
    """

    def __init__(self, project_name, environment, tool_repository=None):
        self.project_name = project_name
        self.environment = environment
        self.tool_service = ToolService(tool_repository or SqlAlchemyToolRepository())

    def health_check(self):
        # Return raw values, not a dict or JSON
        logger.info("Facade: health_check called")
        return self.project_name, self.environment

    # tool operations

    async def get_tool(self, tool_id: int):
        """Get a tool by id delegating to ToolService."""
        logger.debug("Facade: get_tool id=%s", tool_id)
        return await self.tool_service.get_tool(tool_id)

    async def create_tool(self, name: str, description: str, link: str):
        """Create a tool delegating to the domain service."""
        logger.debug("Facade: create_tool name=%s", name)
        return await self.tool_service.create_tool(name, description, link)

    async def list_tools(self):
        """Return all tools."""
        logger.debug("Facade: list_tools")
        return await self.tool_service.list_tools()

    async def update_tool(
        self,
        tool_id: int,
        name: str | None = None,
        description: str | None = None,
        link: str | None = None,
    ):
        """Update a tool delegating to the domain service."""
        logger.debug("Facade: update_tool id=%s", tool_id)
        return await self.tool_service.update_tool(
            tool_id=tool_id, name=name, description=description, link=link
        )

    async def delete_tool(self, tool_id: int) -> bool:
        """Delete a tool delegating to the domain service."""
        logger.debug("Facade: delete_tool id=%s", tool_id)
        return await self.tool_service.delete_tool(tool_id)
