import pytest

import httpx

from src.adapters.http.scrape_provider_http import HttpxScrapeProvider
from src.domain.exceptions import ScrapeError


def _make_factory(handler):
    # Capture the original AsyncClient class so the factory doesn't recurse
    OriginalAsyncClient = httpx.AsyncClient

    def factory(*a, **kw):
        # ensure we construct AsyncClient with our MockTransport using the
        # original AsyncClient implementation captured above (avoids recursion
        # when the module-level symbol is monkeypatched).
        return OriginalAsyncClient(transport=httpx.MockTransport(handler), **kw)

    return factory


@pytest.mark.asyncio
async def test_fetch_respects_robots_allow(monkeypatch):
    # robots.txt allows everything, target returns 200
    async def handler(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        return httpx.Response(200, text="<html><h1>OK</h1></html>")

    monkeypatch.setattr(
        "src.adapters.http.scrape_provider_http.httpx.AsyncClient",
        _make_factory(handler),
    )

    provider = HttpxScrapeProvider()
    text = await provider.fetch("https://example.com/page")
    assert "OK" in text


@pytest.mark.asyncio
async def test_fetch_respects_robots_disallow(monkeypatch):
    async def handler(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nDisallow: /")
        return httpx.Response(200, text="<html></html>")

    monkeypatch.setattr(
        "src.adapters.http.scrape_provider_http.httpx.AsyncClient",
        _make_factory(handler),
    )

    provider = HttpxScrapeProvider()
    with pytest.raises(ScrapeError) as excinfo:
        await provider.fetch("https://example.com/page")
    assert getattr(excinfo.value, "status_code", None) == 403


@pytest.mark.asyncio
async def test_fetch_robots_404_then_fetch_page(monkeypatch):
    async def handler(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(404, text="")
        return httpx.Response(200, text="<html><p>content</p></html>")

    monkeypatch.setattr(
        "src.adapters.http.scrape_provider_http.httpx.AsyncClient",
        _make_factory(handler),
    )

    provider = HttpxScrapeProvider()
    text = await provider.fetch("https://example.com/page")
    assert "content" in text


@pytest.mark.asyncio
async def test_fetch_target_403_maps_error(monkeypatch):
    async def handler(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        return httpx.Response(403, text="Forbidden")

    monkeypatch.setattr(
        "src.adapters.http.scrape_provider_http.httpx.AsyncClient",
        _make_factory(handler),
    )

    provider = HttpxScrapeProvider()
    with pytest.raises(ScrapeError) as excinfo:
        await provider.fetch("https://example.com/page")
    assert getattr(excinfo.value, "status_code", None) == 403


@pytest.mark.asyncio
async def test_fetch_robots_network_error_proceeds(monkeypatch):
    # simulate network error when fetching robots.txt -> should proceed
    async def handler(request):
        if request.url.path == "/robots.txt":
            raise httpx.RequestError("network error")
        return httpx.Response(200, text="<html><p>ok</p></html>")

    monkeypatch.setattr(
        "src.adapters.http.scrape_provider_http.httpx.AsyncClient",
        _make_factory(handler),
    )

    provider = HttpxScrapeProvider()
    text = await provider.fetch("https://example.com/page")
    assert "ok" in text
