import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)

from src.adapters.db.models.models import Base as ORMBase


@pytest_asyncio.fixture(scope="module")
async def async_engine() -> AsyncEngine:
    """Create a single in-memory async engine per test module.

    Using `module` scope avoids creating multiple engines across tests
    in the same module and keeps setup/teardown cheap.
    """
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(ORMBase.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
def async_session_factory(async_engine):
    """Return an `async_sessionmaker` bound to the shared engine."""
    return async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
