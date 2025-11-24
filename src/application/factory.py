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
    if scrape_service is None:
        # Lazy import adapter and domain types to avoid import cycles at module
        # import time for CLI/test runners that may not need HTTP adapters.
        from src.adapters.http.scrape_provider_http import HttpxScrapeProvider
        from src.domain.scrape_service import ScrapeService

        provider = HttpxScrapeProvider()
        scrape_service = ScrapeService(provider=provider)

    return ApplicationFacade(
        project_name=project_name,
        environment=environment,
        scrape_service=scrape_service,
    )
