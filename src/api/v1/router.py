"""
API v1 router configuration
"""
from fastapi import APIRouter
from src.core.config import settings

from src.api.v1.endpoints import items

# Create the v1 router
router = APIRouter()

# Include all endpoint routers
router.include_router(items.router)

# Add health check endpoint directly to v1 router
@router.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint
    
    Returns a simple message to confirm the API is running
    """
    return {"status": "ok", "version": "1"}

@router.get("/app-info", tags=["info"])
async def app_info():
    """
    Application information endpoint
    
    Returns basic information about the application
    """
    return {
        "name": settings.PROJECT_NAME,
        "description": settings.PROJECT_DESCRIPTION,
        "version": settings.VERSION
    }
