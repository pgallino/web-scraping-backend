from fastapi.testclient import TestClient


def test_scrape_route_calls_facade(monkeypatch):
    # Import app only inside the test to ensure patched facade is used
    from src.application import api_app as api_app_module
    from src.domain.scrape import ScrapeResult

    # Fake scrape result returned by facade
    fake_result = ScrapeResult(url="https://example.com", data={"title": ["X"]})

    async def fake_scrape(req):
        return fake_result

    # Patch the facade instance used by the app
    monkeypatch.setattr(api_app_module, "api_facade", api_app_module.api_facade)
    monkeypatch.setattr(api_app_module.api_facade, "scrape", fake_scrape)

    client = TestClient(api_app_module.app)

    payload = {"url": "https://example.com", "selectors": {"title": "h1"}}
    resp = client.post("/scrape", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["url"] == "https://example.com"
    assert body["data"]["title"] == ["X"]
