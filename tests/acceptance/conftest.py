import logging
import os
import pytest
from sqlalchemy import create_engine, text
from fastapi.testclient import TestClient
from src.application.api_app import app
from src.adapters.db.models.models import Base

logger = logging.getLogger(__name__)


# Session-scoped engine: create once per test session (faster than recreating per test)
@pytest.fixture(scope="session")
def engine():
    """Create a SQLAlchemy engine for tests.

    Uses a single `dev.db` SQLite file for the test session.
    """
    db_url = f"sqlite:///dev.db"
    engine = create_engine(db_url)

    # Ensure tables exist once per session (helps running tests without Alembic)
    try:
        Base.metadata.create_all(engine)
    except Exception as exc:
        logger.exception("Error creating tables in test setup: %s", exc)

    yield engine

    try:
        engine.dispose()
    except Exception:
        pass


@pytest.fixture(autouse=True)
def clean_db(engine):
    """Clean DB state before each test (function scope).

    Uses the session-scoped `engine` to delete rows from all tables declared in
    `Base.metadata`. For sqlite it also resets sqlite_sequence so autoincrements
    start from 1. Runs inside a transaction which is committed after cleaning.
    """
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            for table in reversed(Base.metadata.sorted_tables):
                name = table.name
                if name == "alembic_version":
                    continue
                try:
                    conn.execute(text(f"DELETE FROM {name}"))
                except Exception as exc:
                    # Log unexpected errors but continue trying to clean other tables
                    logger.debug("Could not DELETE from %s: %s", name, exc)

            # Reset SQLite autoincrement sequences so IDs start from 1 in tests
            try:
                if engine.dialect.name == "sqlite":
                    for table in Base.metadata.sorted_tables:
                        tname = table.name
                        if tname == "alembic_version":
                            continue
                        try:
                            conn.execute(text(f"DELETE FROM sqlite_sequence WHERE name='{tname}'"))
                        except Exception:
                            # ignore per-table reset errors
                            pass
            except Exception:
                # If dialect introspection fails or not sqlite, ignore
                pass

            trans.commit()
        except Exception:
            trans.rollback()
            raise


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def context():
    return {}


@pytest.fixture
def api_headers():
    """Return headers including X-API-Key when API_KEY is set in the environment.

    Keeps header logic centralized for acceptance tests.
    """
    key = os.getenv("API_KEY")
    return {"X-API-Key": key} if key else {}
