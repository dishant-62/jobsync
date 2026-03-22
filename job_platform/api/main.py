"""FastAPI application entrypoint."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from job_platform.api.routes import jobs as jobs_routes
from job_platform.config import get_settings
from job_platform.db.session import engine
from job_platform.utils.logging import configure_logging, get_logger


def _bootstrap_logging() -> None:
    """
    Configure logging as soon as this module is imported.

    Uvicorn imports the app (``config.load()``) before it logs
    "Started server process" / "Waiting for application startup."; doing this
    here keeps those lines on the same structlog format as the rest.
    """
    settings = get_settings()
    configure_logging(log_level=settings.log_level, json_logs=settings.json_logs)


_bootstrap_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan hooks (startup / shutdown)."""
    settings = get_settings()
    logger.info("application_starting", environment=settings.environment)
    yield
    await engine.dispose()
    logger.info("application_stopping")


def create_app() -> FastAPI:
    """Build the FastAPI app (factory pattern for tests and ASGI servers)."""
    application = FastAPI(
        title="Job Platform",
        version="0.1.0",
        lifespan=lifespan,
    )

    application.include_router(jobs_routes.router)

    @application.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        """Liveness/readiness style health check."""
        return {"status": "ok"}

    return application


app = create_app()
