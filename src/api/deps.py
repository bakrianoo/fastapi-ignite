"""
Shared dependencies for API routes
"""
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.db.session import get_db


async def get_api_key(x_api_key: str = Header(None)) -> str:
    """
    Validate API key from header if required
    Not used in this example but provided as a template for future auth
    """
    if settings.DEBUG:
        # Skip validation in debug mode
        return "debug"
    
    # Example API key validation logic
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key header is missing",
        )
        
    # Here you would validate the API key against your database or config
    return x_api_key


# Re-export the database session dependency for convenience
get_db_session = get_db
