import pytest

from src.domain.scrape_service import ScrapeService
from src.domain.scrape import ScrapeRequest


class FakeProvider:
    def __init__(self, text: str):
        self._text = text

    async def fetch(self, url: str, headers=None, timeout=None):
        return self._text


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

    svc = ScrapeService(provider=FakeProvider(html))
    req = ScrapeRequest(url="https://example.com", selectors={"title": "h1", "price": ".price", "links": "a"})

    result = await svc.scrape(req)

    assert result.url == req.url
    assert "title" in result.data and result.data["title"] == ["Title Example"]
    assert "price" in result.data and result.data["price"] == ["$9.99"]
    assert "links" in result.data and any("Link A" in s for s in result.data["links"]) 
