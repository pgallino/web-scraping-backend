from __future__ import annotations

import urllib.robotparser as robotparser
from urllib.parse import urlparse

import httpx

from src.domain.exceptions import ScrapeError
from src.domain.ports.scrape_provider import ScrapeProvider
from src.log import logger


class HttpxScrapeProvider:
    """Httpx-based implementation of the `ScrapeProvider` port.

    Keeps network concerns (headers, timeouts, error mapping) out of the domain.
    """

    async def fetch(
        self,
        url: str,
        headers: dict | None = None,
        timeout: float | None = 10.0,
        respect_robots: bool = True,
    ) -> str:
        DEFAULT_HEADERS = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }

        # normalize keys to Title-Case (e.g. "user-agent" -> "User-Agent") and
        # merge defaults with user-provided headers (user values take precedence).
        def _normalize(h: dict) -> dict:
            return {str(k).title(): v for k, v in (h or {}).items()}

        hdrs = {**_normalize(DEFAULT_HEADERS), **_normalize(headers or {})}
        logger.debug("Fetch headers for %s: %s", url, hdrs)

        # Respect robots.txt before requesting the target page (unless caller opts out)
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                # optionally fetch robots.txt; if it fails (network), we log and proceed
                r = None
                if respect_robots:
                    try:
                        r = await client.get(robots_url, headers=hdrs)
                    except httpx.RequestError as exc:
                        logger.debug(
                            "Could not fetch robots.txt %s: %s", robots_url, exc
                        )
                else:
                    logger.debug(
                        "Skipping robots.txt check for %s (respect_robots=False)", url
                    )

                if r is not None and r.status_code == 200:
                    rp = robotparser.RobotFileParser()
                    rp.parse(r.text.splitlines())
                    # prefer X-Agent if present (middleware or client can set it),
                    # otherwise use User-Agent.
                    ua = hdrs.get("X-Agent") or hdrs.get("User-Agent") or "*"
                    try:
                        allowed = rp.can_fetch(ua, url)
                    except Exception:
                        allowed = True

                    if not allowed:
                        logger.info("Disallowed by robots.txt %s ua=%s", url, ua)
                        raise ScrapeError("Disallowed by robots.txt", status_code=403)
                elif r is not None and r.status_code in (401, 403):
                    # treat explicit forbidden for robots.txt as disallow
                    logger.info(
                        "robots.txt returned %s for %s; treating as disallow",
                        r.status_code,
                        robots_url,
                    )
                    raise ScrapeError("Disallowed by robots.txt", status_code=403)

                # fetch the target page
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
