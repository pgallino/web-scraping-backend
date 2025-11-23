import pytest

import src.adapters.db.session as session_module
from src.adapters.db.models.models import Base as ORMBase
from src.adapters.db.repositories.tool_repository import SqlAlchemyToolRepository
from src.domain.tool import Tool


@pytest.mark.asyncio
async def test_tool_repository_integration(monkeypatch, async_session_factory):
    """Integration test for SqlAlchemyToolRepository using a real async SQLite engine.

    This test creates an in-memory `aiosqlite` engine, initializes the schema,
    patches the repository session factory to use the test session, and performs
    full CRUD operations to ensure the repository works end-to-end with SQLAlchemy.
    """

    # Use the shared async_session_factory fixture (provided by tests/integration/conftest.py)
    monkeypatch.setattr(session_module, "AsyncSessionLocal", async_session_factory)

    repo = SqlAlchemyToolRepository()

    # Create
    new_tool = Tool(id=None, name="integration-tool", description="desc", link="http://example")
    created = await repo.create(new_tool)
    assert created.id is not None

    # Read
    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.name == new_tool.name

    # List
    all_tools = await repo.list_all()
    assert any(t.id == created.id for t in all_tools)

    # Update
    created.name = "integration-updated"
    updated = await repo.update(created)
    assert updated is not None and updated.name == "integration-updated"

    # Delete
    deleted = await repo.delete(created.id)
    assert deleted is True
    fetched_after = await repo.get_by_id(created.id)
    assert fetched_after is None

    # engine disposed by the shared fixture


@pytest.mark.asyncio
async def test_delete_nonexistent_and_edge_cases(monkeypatch, async_session_factory):
    """Edge cases for delete(): nonexistent id, negative id, zero id, delete twice."""

    # Use the shared async_session_factory fixture (provided by tests/integration/conftest.py)
    monkeypatch.setattr(session_module, "AsyncSessionLocal", async_session_factory)

    repo = SqlAlchemyToolRepository()

    # Deleting an id that was never created should return False
    assert await repo.delete(9999) is False

    # Negative id should be handled and return False (no-op)
    assert await repo.delete(-1) is False

    # Zero id (unlikely valid PK) should return False
    assert await repo.delete(0) is False

    # Create a tool, delete it, then deleting again should return False
    new_tool = Tool(id=None, name="to-delete-twice", description=None, link=None)
    created = await repo.create(new_tool)
    assert created.id is not None

    first_delete = await repo.delete(created.id)
    assert first_delete is True

    second_delete = await repo.delete(created.id)
    assert second_delete is False

    # engine disposed by the shared fixture
