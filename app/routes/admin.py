"""Admin endpoints for system management and configuration."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

def admin_auth_required():
    """Simple authentication middleware for admin endpoints."""
    if settings.DEBUG:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Admin authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )

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

@router.get("/config", response_model=List[ConfigItem])
async def get_config(authenticated: bool = Depends(admin_auth_required)):
    """Get current application configuration."""
    logger.info("Admin requested configuration")
    
    return [
        ConfigItem(key="APP_NAME", value=settings.APP_NAME, description="Application name", editable=False),
        ConfigItem(key="APP_VERSION", value=settings.APP_VERSION, description="Application version", editable=False),
        ConfigItem(key="DEBUG", value=settings.DEBUG, description="Debug mode", editable=True),
        ConfigItem(key="LOG_LEVEL", value=settings.LOG_LEVEL, description="Logging level", editable=True),
    ]

@router.get("/logs", response_model=List[LogEntry])
async def get_logs(
    authenticated: bool = Depends(admin_auth_required),
    limit: int = 100,
    level: Optional[str] = None,
):
    """Get recent application logs."""
    logger.info(f"Admin requested logs (limit={limit}, level={level})")
    
    # Sample logs for development/testing
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
    
    if level:
        logs = [log for log in logs if log.level == level.upper()]
    
    return logs[:limit]

@router.post("/restart", status_code=status.HTTP_202_ACCEPTED)
async def restart_service(authenticated: bool = Depends(admin_auth_required)):
    """Trigger a service restart."""
    logger.warning("Admin requested service restart")
    return {"message": "Restart initiated (mock - not actually restarting)"}