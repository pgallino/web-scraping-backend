from typing import Any, Dict

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl

from src.domain.scrape import ScrapeRequest as DomainScrapeRequest
from src.log import logger

router = APIRouter(tags=["scrape"])


class ScrapeRequest(BaseModel):
    url: HttpUrl
    # selectors: mapping of name -> CSS selector
    selectors: Dict[str, str]
    # optional headers to send with the request
    headers: Dict[str, str] | None = None
    timeout: float | None = 10.0


@router.post("/scrape", response_model=None, status_code=status.HTTP_200_OK)
@router.post("/scrap", response_model=None, status_code=status.HTTP_200_OK)
async def scrape_route(request: ScrapeRequest):
    logger.info(
        "API: scrape request url=%s selectors=%s",
        request.url,
        list(request.selectors.keys()),
    )

    # Import facade at request-time to avoid circular imports
    from src.application.api_app import api_facade

    # Build domain request and delegate to the application facade
    domain_req = DomainScrapeRequest(
        url=str(request.url),
        selectors=request.selectors,
        headers=request.headers,
        timeout=request.timeout,
    )
    try:
        result = await api_facade.scrape(domain_req)
    except Exception as exc:
        logger.exception("Facade error during scrape %s", request.url)
        raise HTTPException(status_code=500, detail=str(exc))

    # `result` is a domain ScrapeResult; convert to JSON-friendly structure
    return JSONResponse(
        content={"url": result.url, "data": result.data}, status_code=status.HTTP_200_OK
    )
