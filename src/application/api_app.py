import json
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.adapters.api.middleware import add_middlewares
from src.adapters.api.routes import health, tools
from src.application.factory import create_facade
from src.config import api_settings, ensure_api_required_env_vars
from src.log import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        f"La aplicación se está iniciando en ambiente: {api_settings.ENVIRONMENT}"
    )
    yield
    logger.info("La aplicación se ha apagado.")


# Instantiate facade for the API adapter
# Ensure API-specific environment variables (like API_KEY) are present before
# creating API resources. This prevents the application from starting with a
# missing API secret while keeping CLI imports unaffected.
ensure_api_required_env_vars()

api_facade = create_facade(
    project_name=api_settings.PROJECT_NAME, environment=api_settings.ENVIRONMENT
)


app = FastAPI(
    title=f"{api_settings.PROJECT_NAME} ({api_settings.ENVIRONMENT})",
    description="Aplicación Backend con Arquitectura Hexagonal.",
    lifespan=lifespan,
)

# Configure middleware (CORS + request-id)
add_middlewares(app, api_settings)

# Include routers
app.include_router(health.router)  # type: ignore
app.include_router(tools.router)  # type: ignore
