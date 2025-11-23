from typing import Any, Optional

from src.application.facade import ApplicationFacade


def create_facade(
    project_name: str, environment: str, **kwargs: Any
) -> ApplicationFacade:
    """Create an ApplicationFacade with sensible defaults.

    Accepts optional keyword args (e.g. `scrape_service`) to inject domain
    dependencies for testing or alternate implementations.
    """
    scrape_service = kwargs.get("scrape_service")
    return ApplicationFacade(
        project_name=project_name,
        environment=environment,
        scrape_service=scrape_service,
    )
