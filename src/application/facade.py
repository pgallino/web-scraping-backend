from typing import Optional, final

from src.domain.scrape import ScrapeRequest, ScrapeResult
from src.domain.scrape_service import ScrapeService
from src.log import logger


@final
class ApplicationFacade:
    """
    Application Facade.
    Exposes `health_check` and `scrape` application operations.
    """

    def __init__(
        self,
        project_name: str,
        environment: str,
        scrape_service: Optional[ScrapeService] = None,
    ):
        self.project_name = project_name
        self.environment = environment
        # use provided service or build a default one using the HTTP adapter
        if scrape_service is None:
            from src.adapters.http.scrape_provider_http import HttpxScrapeProvider

            provider = HttpxScrapeProvider()
            scrape_service = ScrapeService(provider=provider)

        # single annotated assignment to keep mypy happy
        self.scrape_service: ScrapeService = scrape_service

    def health_check(self):
        logger.info("Facade: health_check called")
        return self.project_name, self.environment

    async def scrape(self, request: ScrapeRequest) -> ScrapeResult:
        """Delegate scraping work to the domain service."""
        logger.debug("Facade: scrape url=%s", request.url)
        return await self.scrape_service.scrape(request)
