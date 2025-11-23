from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from src.adapters.api.security import get_api_key

# Creamos un router específico para rutas de salud/sistema
router = APIRouter(tags=["health"])

# Protect health endpoint with API key dependency (no-op if API_KEY not set)
router.dependencies = [Depends(get_api_key)]


@router.get("/", status_code=status.HTTP_200_OK)
async def health_check():
    """Endpoint básico para verificar que el servicio está funcionando."""
    # Import the facade at request-time to avoid circular imports during module
    # import (the application entrypoint creates the facade and includes
    # routers). Importing here ensures the module import chain completes.
    from src.application.api_app import api_facade

    project_name, environment = api_facade.health_check()
    return JSONResponse(
        content={"project_name": project_name, "environment": environment},
        status_code=status.HTTP_200_OK,
    )
