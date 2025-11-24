from __future__ import annotations

from typing import Dict

import httpx
from bs4 import BeautifulSoup

from src.domain.exceptions import ScrapeError
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

        # Prepare headers (ensure we send a reasonable User-Agent by default).
        headers = dict(request.headers or {})
        if "User-Agent" not in {k.title(): v for k, v in headers.items()}:
            headers.setdefault(
                "User-Agent",
                (
                    "Mozilla/5.0 (compatible; web-scraping-backend/1.0; "
                    "+https://example.local)"
                ),
            )

        timeout_value = request.timeout or 10.0

        try:
            async with httpx.AsyncClient(timeout=timeout_value) as client:
                resp = await client.get(request.url, headers=headers)
                # raise_for_status will raise httpx.HTTPStatusError for 4xx/5xx
                resp.raise_for_status()
                content = resp.text
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code if exc.response is not None else None
            logger.error("HTTP error while fetching %s status=%s", request.url, status)
            raise ScrapeError(f"HTTP error: {exc}", status_code=status)
        except httpx.RequestError as exc:
            logger.error("Request error while fetching %s: %s", request.url, exc)
            raise ScrapeError(f"Request error: {exc}")

        soup = BeautifulSoup(content, "html.parser")
        data: Dict[str, list[str]] = {}
        for name, selector in request.selectors.items():
            elements = soup.select(selector)
            items = [el.get_text(strip=True) for el in elements]
            data[name] = items

        return ScrapeResult(url=request.url, data=data)


__all__ = ["ScrapeService"]
