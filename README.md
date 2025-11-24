# Web Scraping API

A minimal web-scraping API built with FastAPI. This repository exposes a
single HTTP endpoint that fetches an HTML page and extracts text items using
CSS selectors. The project follows Hexagonal (Ports & Adapters) principles so
the domain parsing logic is decoupled from HTTP/network concerns.

This README explains how to run the service, the endpoint contract and
examples to get started.

## Features

- Single POST endpoint: `/scrape` to fetch a page and extract selector results.
- Domain/adapters separation: network I/O is implemented in an adapter that
  implements the `ScrapeProvider` outbound port.
- Returns structured JSON: keys mapped to lists of extracted text values.
- Clear error mapping for upstream HTTP failures (403 -> 403, other upstream
  errors -> 502) and timeouts.

## Quickstart (development)

1. Copy environment variables example:

```bash
cp .env.example .env
```

2. Build and start the development compose stack:

```bash
docker compose -f docker-compose.dev.yml up -d --build
```

3. Open the interactive API docs and try the endpoint:

```
http://localhost:8000/docs
```

## Endpoint: POST /scrape

Request body (JSON):

- `url` (string): page URL to fetch
- `selectors` (object): mapping of key -> CSS selector
- `headers` (object, optional): HTTP headers to include in the request
- `timeout` (number, optional): seconds to wait for the upstream request

Example request body:

```json
{
  "url": "https://example.com/page",
  "selectors": {
    "title": "h1",
    "summary": ".intro > p"
  },
  "headers": { "User-Agent": "Mozilla/5.0 (compatible)" },
  "timeout": 10
}
```

Example curl:

```bash
curl -s -X POST 'http://localhost:8000/scrape' \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com","selectors":{"title":"h1"}}' | jq .
```

Response (200):

```json
{
  "url": "https://example.com",
  "data": {
    "title": ["Page title here"]
  }
}
```

Errors:

- `403` — returned if the remote site responded with HTTP 403 (Forbidden).
- `502` — returned for other upstream HTTP/network failures.
- `500` — unexpected server error.

## Architecture note

The repository follows a Ports & Adapters layout:

- `src/domain`: domain models and `ScrapeService` (parsing logic)
- `src/domain/ports`: `ScrapeProvider` port (protocol)
- `src/adapters/http`: HTTP adapter `HttpxScrapeProvider` (implements the port)
- `src/adapters/api`: FastAPI HTTP routes

This keeps network details (httpx, retries, headers) inside the HTTP adapter
and allows unit testing the domain by injecting fake providers.

## Testing

- Unit tests: `make test-unit`
- Acceptance tests (BDD): `make test-acceptance`

## Development tips

- If the page returns empty data, verify your CSS selectors match the
  elements in the page or add appropriate selectors in the request body.
- The default HTTP adapter adds a reasonable `User-Agent` header when not
  provided; you can override it using the `headers` parameter.

## Next steps / enhancements

- Add attribute extraction (`href`, `src`) per selector.
- Add retries/backoff, proxy support, and rate-limiting in the HTTP adapter.
- Add integration tests for `HttpxScrapeProvider` using `httpx.MockTransport`.

If you want, I can add examples for extracting attributes or add tests for the
HTTP adapter.
