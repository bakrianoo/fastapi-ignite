"""
FastAPI application entry point
"""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.router import router as api_v1_router
from src.core.config import settings
from src.core.events import create_start_app_handler, create_stop_app_handler
from src.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan event handler for startup and shutdown events
    """
    # Setup logging
    setup_logging()
    
    # Override scheduler setting from environment variable (set by CLI)
    scheduler_env = os.environ.get("SCHEDULER_ENABLED")
    if scheduler_env is not None:
        from src.core.config import settings
        settings.scheduler.enabled = scheduler_env.lower() == "true"
    
    # Run startup event handlers
    start_handler = create_start_app_handler()
    await start_handler()
    
    # Yield control back to FastAPI
    yield
    
    # Run shutdown event handlers
    stop_handler = create_stop_app_handler()
    await stop_handler()


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application
    """
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        docs_url=f"{settings.API_PREFIX}/docs",
        redoc_url=f"{settings.API_PREFIX}/redoc",
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        lifespan=lifespan,
    )

    # Set up CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    application.include_router(api_v1_router, prefix=settings.API_PREFIX)

    return application


app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )
