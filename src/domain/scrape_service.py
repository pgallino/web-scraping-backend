from __future__ import annotations

from typing import Dict

import httpx
from bs4 import BeautifulSoup

from src.domain.scrape import ScrapeRequest, ScrapeResult
from src.log import logger


class ScrapeService:
    """Domain service that fetches a URL and extracts items using CSS selectors.

    This service returns domain `ScrapeResult` objects so the application
    facade and adapters work with typed domain objects.
    """

    async def scrape(self, request: ScrapeRequest) -> ScrapeResult:
        logger.info(
            "Service: scraping %s selectors=%s",
            request.url,
            list(request.selectors.keys()),
        )

        async with httpx.AsyncClient(timeout=request.timeout) as client:
            resp = await client.get(request.url, headers=(request.headers or {}))
            resp.raise_for_status()
            content = resp.text

        soup = BeautifulSoup(content, "html.parser")
        data: Dict[str, list[str]] = {}
        for name, selector in request.selectors.items():
            elements = soup.select(selector)
            items = [el.get_text(strip=True) for el in elements]
            data[name] = items

        return ScrapeResult(url=request.url, data=data)


__all__ = ["ScrapeService"]
