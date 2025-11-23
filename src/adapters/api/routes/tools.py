from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.adapters.api.security import get_api_key
from src.domain.exceptions import (
    ConflictError,
    DomainError,
    NotFoundError,
    RepositoryNotConfiguredError,
    ValidationError,
)
from src.log import logger

router = APIRouter(tags=["tools"])  # English path tag

# Protect tools endpoints with API key dependency (no-op if API_KEY not set)
router.dependencies = [Depends(get_api_key)]


class ToolCreateRequest(BaseModel):
    name: str
    description: str | None = None
    link: str | None = None


class ToolUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    link: str | None = None


@router.post("/tools", response_model=None, status_code=status.HTTP_201_CREATED)
async def create_tool_route(request: ToolCreateRequest):
    logger.info("API: create_tool request name=%s", request.name)
    # Import the facade from the application module at request-time
    from src.application.api_app import api_facade

    try:
        tool = await api_facade.create_tool(
            name=request.name,
            description=request.description or "",
            link=request.link or "",
        )
        return JSONResponse(content=asdict(tool), status_code=status.HTTP_201_CREATED)
    except ValidationError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)}
        )
    except ConflictError as exc:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
        )
    except RepositoryNotConfiguredError as exc:
        # Server misconfiguration
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)},
        )
    except DomainError as exc:
        # Fallback for other domain errors -> 400
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)}
        )


@router.get("/tools/{tool_id}", response_model=None, status_code=status.HTTP_200_OK)
async def get_tool_route(tool_id: int):
    logger.info("API: get_tool request id=%s", tool_id)
    from src.application.api_app import api_facade

    try:
        tool = await api_facade.get_tool(tool_id)
        return JSONResponse(content=asdict(tool), status_code=status.HTTP_200_OK)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found"
        )
    except RepositoryNotConfiguredError as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)},
        )
    except DomainError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)}
        )


@router.get("/tools", response_model=None, status_code=status.HTTP_200_OK)
async def list_tools_route():
    logger.info("API: list_tools request")
    from src.application.api_app import api_facade

    tools = await api_facade.list_tools()
    # tools is a list of dataclass Tool — convert to list of dicts
    content = [asdict(t) for t in tools]
    return JSONResponse(content=content, status_code=status.HTTP_200_OK)


@router.put("/tools/{tool_id}", response_model=None, status_code=status.HTTP_200_OK)
async def replace_tool_route(tool_id: int, request: ToolCreateRequest):
    """PUT: replace the tool resource with the provided representation.

    All required fields must be present (name required). This follows PUT
    semantics: the provided representation replaces the existing one.
    """
    logger.info("API: replace_tool request id=%s name=%s", tool_id, request.name)
    from src.application.api_app import api_facade

    try:
        # Call service inside try so domain exceptions are caught below.
        tool = await api_facade.update_tool(
            tool_id=tool_id,
            name=request.name,
            description=request.description,
            link=request.link,
        )
        # service may raise NotFoundError or Validation/Conflict errors
        return JSONResponse(content=asdict(tool), status_code=status.HTTP_200_OK)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found"
        )
    except ValidationError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)}
        )
    except ConflictError as exc:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
        )
    except RepositoryNotConfiguredError as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)},
        )
    except DomainError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)}
        )


@router.delete(
    "/tools/{tool_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_tool_route(tool_id: int):
    logger.info("API: delete_tool request id=%s", tool_id)
    from src.application.api_app import api_facade

    try:
        await api_facade.delete_tool(tool_id)
        return JSONResponse(content=None, status_code=status.HTTP_204_NO_CONTENT)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found"
        )
    except RepositoryNotConfiguredError as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)},
        )
    except DomainError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)}
        )
