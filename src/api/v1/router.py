"""
API v1 router configuration
"""
from fastapi import APIRouter

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
