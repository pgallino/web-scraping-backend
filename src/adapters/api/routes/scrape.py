from typing import Any, Dict

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl

from src.domain.exceptions import ScrapeError
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
    # If provided and false, the server will skip robots.txt checks (useful for dev)
    respect_robots: bool | None = True


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
        respect_robots=(
            request.respect_robots if request.respect_robots is not None else True
        ),
    )
    try:
        result = await api_facade.scrape(domain_req)
    except ScrapeError as exc:
        # Remote site responded with an error or network problem occurred.
        logger.exception("Facade error during scrape %s", request.url)
        # If the remote returned a known HTTP status (e.g. 403), surface it.
        if getattr(exc, "status_code", None) == 403:
            raise HTTPException(
                status_code=403,
                detail=(
                    "Remote site returned 403 Forbidden. "
                    "Try adding request headers (User-Agent) or using a different URL."
                ),
            )
        # Otherwise return a 502 Bad Gateway to indicate upstream failure.
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected facade error during scrape %s", request.url)
        raise HTTPException(status_code=500, detail="internal server error")

    # `result` is a domain ScrapeResult; convert to JSON-friendly structure
    return JSONResponse(
        content={"url": result.url, "data": result.data}, status_code=status.HTTP_200_OK
    )
