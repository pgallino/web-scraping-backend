import pytest


@pytest.fixture
def async_engine():
    """Persistence has been removed from the app; DB fixtures are disabled.

    Any test that depended on an async DB fixture will be skipped when
    requesting this fixture.
    """
    pytest.skip("Database persistence disabled for this project")


@pytest.fixture
def async_session_factory(async_engine):
    pytest.skip("Database persistence disabled for this project")
