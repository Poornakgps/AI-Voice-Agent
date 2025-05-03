"""
Admin endpoints for system management and configuration.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from app.config import settings

# Set up logger
logger = logging.getLogger(__name__)

router = APIRouter()

# Simple mock authentication for admin routes
def admin_auth_required():
    """
    Mock authentication middleware for admin endpoints.
    
    In a real implementation, this would validate tokens, API keys, etc.
    For now, it just checks if DEBUG mode is enabled.
    
    Returns:
        bool: Always True in debug mode, otherwise raises an exception.
    """
    if settings.DEBUG:
        return True
    
    # In production, this would check for a valid token/credentials
    # For now, we just deny access in non-debug mode
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Admin authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )

# Models
class ConfigItem(BaseModel):
    """Model for configuration items."""
    key: str
    value: Any
    description: Optional[str] = None
    editable: bool = False

class LogEntry(BaseModel):
    """Model for log entries."""
    timestamp: str
    level: str
    message: str
    context: Optional[Dict[str, Any]] = None

# Admin endpoints
@router.get("/config", response_model=List[ConfigItem])
async def get_config(authenticated: bool = Depends(admin_auth_required)):
    """
    Get current application configuration.
    
    Args:
        authenticated: Dependency injection for authentication.
        
    Returns:
        List[ConfigItem]: List of configuration items.
    """
    # In a real implementation, you'd get this from a database or config service
    # For now, we return a subset of settings
    logger.info("Admin requested configuration")
    
    config_items = [
        ConfigItem(
            key="APP_NAME",
            value=settings.APP_NAME,
            description="Application name",
            editable=False,
        ),
        ConfigItem(
            key="APP_VERSION", 
            value=settings.APP_VERSION,
            description="Application version",
            editable=False,
        ),
        ConfigItem(
            key="DEBUG",
            value=settings.DEBUG,
            description="Debug mode",
            editable=True,
        ),
        ConfigItem(
            key="LOG_LEVEL",
            value=settings.LOG_LEVEL,
            description="Logging level",
            editable=True,
        ),
    ]
    
    return config_items

@router.get("/logs", response_model=List[LogEntry])
async def get_logs(
    authenticated: bool = Depends(admin_auth_required),
    limit: int = 100,
    level: Optional[str] = None,
):
    """
    Get recent application logs.
    
    Args:
        authenticated: Dependency injection for authentication.
        limit: Maximum number of log entries to return.
        level: Filter logs by level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        
    Returns:
        List[LogEntry]: List of log entries.
    """
    # In a real implementation, you'd get this from a log store
    # For now, we return mock data
    logger.info(f"Admin requested logs (limit={limit}, level={level})")
    
    # Mock log entries
    logs = [
        LogEntry(
            timestamp="2025-05-03T12:00:00Z",
            level="INFO",
            message="Application started",
            context={"pid": 1234},
        ),
        LogEntry(
            timestamp="2025-05-03T12:01:00Z",
            level="INFO",
            message="Incoming call received",
            context={"call_id": "CA123456789"},
        ),
        LogEntry(
            timestamp="2025-05-03T12:02:00Z",
            level="WARNING",
            message="Slow API response",
            context={"latency_ms": 2500, "endpoint": "/webhook/voice"},
        ),
    ]
    
    # Filter by level if specified
    if level:
        logs = [log for log in logs if log.level == level.upper()]
    
    # Limit results
    logs = logs[:limit]
    
    return logs

@router.post("/restart", status_code=status.HTTP_202_ACCEPTED)
async def restart_service(authenticated: bool = Depends(admin_auth_required)):
    """
    Trigger a service restart.
    
    Args:
        authenticated: Dependency injection for authentication.
        
    Returns:
        dict: Confirmation message.
    """
    # In a real implementation, this would trigger an actual restart
    # For now, we just log the request
    logger.warning("Admin requested service restart")
    
    return {"message": "Restart initiated (mock - not actually restarting)"}