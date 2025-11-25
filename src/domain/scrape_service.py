from __future__ import annotations

from typing import Dict

from bs4 import BeautifulSoup

from src.domain.exceptions import ScrapeError
from src.domain.ports.scrape_provider import ScrapeProvider
from src.domain.scrape import ScrapeRequest, ScrapeResult
from src.log import logger


class ScrapeService:
    """Domain service that parses HTML obtained from a ScrapeProvider.

    The domain service focuses on parsing and transformation. Network IO is
    delegated to the `ScrapeProvider` outbound port so the domain remains
    independent of httpx or other HTTP clients.
    """

    def __init__(self, provider: ScrapeProvider):
        self.provider = provider

    async def scrape(self, request: ScrapeRequest) -> ScrapeResult:
        logger.info(
            "Service: scraping %s selectors=%s",
            request.url,
            list(request.selectors.keys()),
        )

        # Delegate network fetching to the provider (outbound port).
        try:
            content = await self.provider.fetch(
                request.url,
                headers=request.headers,
                timeout=request.timeout,
                respect_robots=(
                    request.respect_robots
                    if request.respect_robots is not None
                    else True
                ),
            )
        except ScrapeError:
            # propagate domain scraping/network errors
            raise

        soup = BeautifulSoup(content, "html.parser")
        data: Dict[str, list[str]] = {}
        for name, selector in request.selectors.items():
            elements = soup.select(selector)
            items = [el.get_text(strip=True) for el in elements]
            data[name] = items

        return ScrapeResult(url=request.url, data=data)


__all__ = ["ScrapeService"]
