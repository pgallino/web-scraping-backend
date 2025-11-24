from __future__ import annotations

from typing import Protocol


class ScrapeProvider(Protocol):
    """Domain port (outbound) for fetching HTML content from a URL.

    Implementations live in adapters (infrastructure) and the domain depends
    on this protocol to obtain raw HTML for parsing.
    """

    async def fetch(
        self, url: str, headers: dict | None = None, timeout: float | None = None
    ) -> str:
        """Fetch the raw HTML content for `url`.

        Raises `src.domain.exceptions.ScrapeError` on failures.
        """
        ...


__all__ = ["ScrapeProvider"]
