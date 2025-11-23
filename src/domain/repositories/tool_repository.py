from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from src.domain.tool import Tool


class ToolRepository(ABC):
    @abstractmethod
    async def get_by_id(self, tool_id: int) -> Optional[Tool]:
        raise NotImplementedError()

    @abstractmethod
    async def create(self, tool: Tool) -> Tool:
        raise NotImplementedError()

    @abstractmethod
    async def list_all(self) -> list[Tool]:
        """Return a list with all tools."""
        raise NotImplementedError()

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Tool]:
        """Return a single Tool matching the given name, or None if not found."""
        raise NotImplementedError()

    @abstractmethod
    async def update(self, tool: Tool) -> Tool | None:
        """Update an existing tool. Return the updated Tool or None if not found."""
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, tool_id: int) -> bool:
        """Delete a tool by id. Return True if deleted, False if not found."""
        raise NotImplementedError()
