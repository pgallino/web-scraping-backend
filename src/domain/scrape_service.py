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

        # If no selectors were provided or any selector is 'hack', return a
        # broad set of extracted fields (title, meta description, headings,
        # links, images and the full body text) to give as much info as
        # possible.
        def _is_hack_mode(selectors: dict) -> bool:
            if not selectors:
                return True
            for name, sel in selectors.items():
                try:
                    if (str(name).strip().lower() == "hack") or (
                        str(sel).strip().lower() == "hack"
                    ):
                        return True
                except Exception:
                    continue
            return False

        if _is_hack_mode(request.selectors):
            logger.info("Hack mode: extracting full page data for %s", request.url)
            # title
            title = soup.title.string.strip() if soup.title and soup.title.string else ""
            if title:
                data.setdefault("title", []).append(title)

            # meta description
            desc = ""
            meta = soup.find("meta", attrs={"name": "description"})
            if meta and meta.get("content"):
                desc = meta.get("content").strip()
            if desc:
                data.setdefault("meta_description", []).append(desc)

            # headings
            for h in ("h1", "h2", "h3"):
                items = [el.get_text(strip=True) for el in soup.select(h)]
                if items:
                    data[h] = items

            # links (hrefs)
            links = []
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                text = a.get_text(strip=True)
                if text:
                    links.append(f"{text} -> {href}")
                else:
                    links.append(href)
            if links:
                data["links"] = links

            # images (src)
            imgs = []
            for img in soup.find_all("img", src=True):
                src = img.get("src").strip()
                alt = img.get("alt") or ""
                if alt:
                    imgs.append(f"{alt} -> {src}")
                else:
                    imgs.append(src)
            if imgs:
                data["images"] = imgs

            # full body text
            body = soup.body.get_text(separator="\n", strip=True) if soup.body else ""
            if body:
                # keep body as one big item to avoid huge arrays
                data.setdefault("body_text", []).append(body)

            return ScrapeResult(url=request.url, data=data)

        # Normal selector mode
        for name, selector in request.selectors.items():
            elements = soup.select(selector)
            items = [el.get_text(strip=True) for el in elements]
            data[name] = items

        return ScrapeResult(url=request.url, data=data)


__all__ = ["ScrapeService"]
