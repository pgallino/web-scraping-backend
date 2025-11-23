from __future__ import annotations

from typing import Optional, final

from src.log import logger

from .exceptions import (
    ConflictError,
    NotFoundError,
    RepositoryNotConfiguredError,
    ValidationError,
)
from .repositories.tool_repository import ToolRepository
from .tool import Tool


@final
class ToolService:
    """Servicio de dominio para la entidad Tool (herramientas).

    Esta clase actúa como capa de aplicación/servicio que orquesta la lógica
    básica sobre `Tool` usando un `ToolRepository` inyectado. El servicio
    asume que el repositorio implementa la interfaz definida en
    `src.domain.repositories.tool_repository.ToolRepository`.
    """

    def __init__(self, tool_repository: Optional[ToolRepository] = None) -> None:
        self.tool_repository = tool_repository

    def _repo(self) -> ToolRepository:
        """Return the configured repository or raise a clear RuntimeError.

        Centraliza la verificación para evitar repetir comprobaciones en cada
        método público.
        """
        if self.tool_repository is None:
            raise RepositoryNotConfiguredError("No hay repositorio de tool configurado")
        return self.tool_repository

    async def get_tool(self, tool_id: int) -> Tool:
        """Obtener una herramienta por id.

        Si no existe, lanzar `NotFoundError`.
        """
        logger.info("Service: get_tool id=%s", tool_id)
        existing = await self._repo().get_by_id(tool_id)
        if existing is None:
            from .exceptions import NotFoundError

            raise NotFoundError(f"Tool id={tool_id} not found")
        return existing

    async def create_tool(self, name: str, description: str, link: str) -> Tool:
        """Crear una nueva herramienta a partir de los datos proporcionados."""
        # Basic validation: name must be present and non-empty
        if not (isinstance(name, str) and name.strip()):
            raise ValidationError("'name' is required and cannot be empty")

        tool = Tool.from_input(name=name, description=description, link=link)

        # Business rule: tool name must be unique — use repository lookup by name
        existing = await self._repo().get_by_name(tool.name)
        if existing is not None:
            raise ConflictError(f"Tool with name '{tool.name}' already exists")

        logger.info("Service: create_tool name=%s", name)
        return await self._repo().create(tool)

    async def list_tools(self) -> list[Tool]:
        """Listar todas las herramientas."""
        logger.info("Service: list_tools")
        return await self._repo().list_all()

    async def update_tool(
        self,
        tool_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        link: Optional[str] = None,
    ) -> Optional[Tool]:
        """Actualizar campos de una herramienta existente.

        Cuando un campo es `None` se conserva el valor anterior.
        Devuelve la herramienta actualizada, o `None` si no se encontró.
        """
        logger.info("Service: update_tool id=%s", tool_id)
        existing = await self._repo().get_by_id(tool_id)
        if existing is None:
            # Explicitly surface not-found as a domain exception so callers
            # (controllers) can map it to HTTP 404.
            raise NotFoundError(f"Tool id={tool_id} not found")

        updated = Tool(
            id=existing.id,
            name=name if name is not None else existing.name,
            description=(
                description if description is not None else existing.description
            ),
            link=link if link is not None else existing.link,
        )
        return await self._repo().update(updated)

    async def delete_tool(self, tool_id: int) -> bool:
        """Eliminar una herramienta por id. Devuelve True si se borró."""
        logger.info("Service: delete_tool id=%s", tool_id)
        deleted = await self._repo().delete(tool_id)
        if not deleted:
            raise NotFoundError(f"Tool id={tool_id} not found")
        return True
