from typing import Optional

from sqlalchemy.future import select

from src.adapters.db.models.models import ToolModel
from src.adapters.db.session import AsyncSessionLocal
from src.domain.repositories.tool_repository import ToolRepository
from src.domain.tool import Tool

# repository should be agnostic about business rules like uniqueness;
# ConflictError will be raised by the service when appropriate
from src.log import logger


class SqlAlchemyToolRepository(ToolRepository):
    async def get_by_id(self, tool_id: int) -> Optional[Tool]:
        async with AsyncSessionLocal() as session:
            logger.debug("DB: get_by_id %s", tool_id)
            result = await session.execute(
                select(ToolModel).where(ToolModel.id == tool_id)
            )
            row = result.scalar_one_or_none()
            if row:
                logger.info(
                    "DB: found tool id=%s name=%s",
                    getattr(row, "id"),
                    getattr(row, "name"),
                )
                return Tool(
                    id=getattr(row, "id"),
                    name=getattr(row, "name"),
                    description=getattr(row, "description"),
                    link=getattr(row, "link"),
                )
            logger.info("DB: tool id=%s not found", tool_id)
            return None

    async def get_by_name(self, name: str) -> Optional[Tool]:
        async with AsyncSessionLocal() as session:
            logger.debug("DB: get_by_name %s", name)
            result = await session.execute(
                select(ToolModel).where(ToolModel.name == name)
            )
            row = result.scalar_one_or_none()
            if row:
                return Tool(
                    id=getattr(row, "id"),
                    name=getattr(row, "name"),
                    description=getattr(row, "description"),
                    link=getattr(row, "link"),
                )
            return None

    async def create(self, tool: Tool) -> Tool:
        async with AsyncSessionLocal() as session:
            logger.info("DB: creating tool name=%s", tool.name)
            model = ToolModel(
                name=tool.name, description=tool.description, link=tool.link
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            logger.info("DB: created tool id=%s", getattr(model, "id"))
            return Tool(
                id=getattr(model, "id"),
                name=getattr(model, "name"),
                description=getattr(model, "description"),
                link=getattr(model, "link"),
            )

    async def list_all(self) -> list[Tool]:
        async with AsyncSessionLocal() as session:
            logger.debug("DB: listing all tools")
            result = await session.execute(select(ToolModel))
            rows = result.scalars().all()
            tools: list[Tool] = []
            for row in rows:
                tools.append(
                    Tool(
                        id=getattr(row, "id"),
                        name=getattr(row, "name"),
                        description=getattr(row, "description"),
                        link=getattr(row, "link"),
                    )
                )
            logger.info("DB: returning %s tools", len(tools))
            return tools

    async def update(self, tool: Tool) -> Tool | None:
        async with AsyncSessionLocal() as session:
            logger.info("DB: update tool id=%s", tool.id)
            result = await session.execute(
                select(ToolModel).where(ToolModel.id == tool.id)
            )
            model = result.scalar_one_or_none()
            if model is None:
                logger.warning("DB: tool id=%s not found for update", tool.id)
                return None
            # update fields (use setattr to avoid static typing issues with SQLAlchemy
            # Column descriptors in some type-checking environments)
            setattr(model, "name", tool.name)
            setattr(model, "description", tool.description)
            setattr(model, "link", tool.link)
            session.add(model)
            await session.commit()
            await session.refresh(model)
            logger.info("DB: updated tool id=%s", getattr(model, "id"))
            return Tool(
                id=getattr(model, "id"),
                name=getattr(model, "name"),
                description=getattr(model, "description"),
                link=getattr(model, "link"),
            )

    async def delete(self, tool_id: int) -> bool:
        async with AsyncSessionLocal() as session:
            logger.info("DB: delete tool id=%s", tool_id)
            result = await session.execute(
                select(ToolModel).where(ToolModel.id == tool_id)
            )
            model = result.scalar_one_or_none()
            if model is None:
                logger.warning("DB: tool id=%s not found for delete", tool_id)
                return False
            await session.delete(model)
            await session.commit()
            logger.info("DB: deleted tool id=%s", tool_id)
            return True
