import pytest

from src.domain.scrape_service import ScrapeService
from src.domain.scrape import ScrapeRequest


class FakeResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


class FakeAsyncClient:
    def __init__(self, text, status_code=200, *a, **kw):
        self._resp = FakeResponse(text, status_code)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url, headers=None):
        return self._resp


@pytest.mark.asyncio
async def test_scrape_service_extracts_selectors(monkeypatch):
    html = """
    <html>
      <body>
        <h1>Title Example</h1>
        <div class="price">$9.99</div>
        <a href="/a">Link A</a>
      </body>
    </html>
    """

    # patch httpx.AsyncClient constructor inside the domain service module
    monkeypatch.setattr("src.domain.scrape_service.httpx.AsyncClient", lambda *a, **k: FakeAsyncClient(html))

    svc = ScrapeService()
    req = ScrapeRequest(url="https://example.com", selectors={"title": "h1", "price": ".price", "links": "a"})

    result = await svc.scrape(req)

    assert result.url == req.url
    assert "title" in result.data and result.data["title"] == ["Title Example"]
    assert "price" in result.data and result.data["price"] == ["$9.99"]
    assert "links" in result.data and any("Link A" in s for s in result.data["links"]) 
