from __future__ import annotations

import httpx

from src.domain.exceptions import ScrapeError
from src.domain.ports.scrape_provider import ScrapeProvider
from src.log import logger


class HttpxScrapeProvider:
    """Httpx-based implementation of the `ScrapeProvider` port.

    Keeps network concerns (headers, timeouts, error mapping) out of the domain.
    """

    async def fetch(
        self, url: str, headers: dict | None = None, timeout: float | None = 10.0
    ) -> str:
        hdrs = dict(headers or {})
        # ensure a reasonable User-Agent if the caller didn't supply one
        if "User-Agent" not in {k.title(): v for k, v in hdrs.items()}:
            hdrs.setdefault(
                "User-Agent",
                "Mozilla/5.0 (compatible; web-scraping-backend/1.0; +https://example.local)",
            )

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.get(url, headers=hdrs)
                resp.raise_for_status()
                return resp.text
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code if exc.response is not None else None
            logger.error("HTTP error while fetching %s status=%s", url, status)
            raise ScrapeError(f"HTTP error: {exc}", status_code=status)
        except httpx.RequestError as exc:
            logger.error("Request error while fetching %s: %s", url, exc)
            raise ScrapeError(f"Request error: {exc}")


__all__ = ["HttpxScrapeProvider"]
