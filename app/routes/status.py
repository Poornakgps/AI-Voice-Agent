"""
Status endpoints for health checking and monitoring.
"""
import time
from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from app.config import settings

router = APIRouter()

class HealthResponse(BaseModel):
    """Model for health check response."""
    status: str
    version: str
    environment: str

class MetricsResponse(BaseModel):
    """Model for metrics response."""
    uptime: float
    memory_usage: float
    cpu_usage: float
    active_connections: int

# Start time for uptime calculation
START_TIME = time.time()

@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint to verify service is operational.
    
    Returns:
        HealthResponse: Basic service information.
    """
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        environment=settings.APP_ENV
    )

@router.get("/readiness", status_code=status.HTTP_200_OK)
async def readiness_check():
    """
    Readiness check endpoint to verify service is ready to accept requests.
    
    This would typically check database connectivity, external services, etc.
    For now, it's a simple endpoint returning 200 OK.
    
    Returns:
        dict: Simple status message.
    """
    # In a real implementation, you'd check connections to databases,
    # external services, etc.
    # For simplicity, we just return a success response.
    return {"status": "ready"}

@router.get("/metrics", response_model=MetricsResponse)
async def metrics():
    """
    Metrics endpoint for monitoring.
    
    Returns:
        MetricsResponse: Current service metrics.
    """
    # In a real implementation, you'd gather actual metrics.
    # For now, we return mock data.
    
    # Calculate uptime in seconds
    uptime = time.time() - START_TIME
    
    # Mock metrics
    return MetricsResponse(
        uptime=uptime,
        memory_usage=123.45,  # MB
        cpu_usage=10.5,  # %
        active_connections=2
    )

@router.get("/test-openai", status_code=status.HTTP_200_OK)
async def test_openai():
    """
    Test if OpenAI API key is working.
    """
    if not settings.OPENAI_API_KEY:
        return {"status": "error", "message": "No OpenAI API key configured"}
    
    try:
        import openai
        # Initialize client without organization ID
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Make a simple API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        
        return {
            "status": "success", 
            "message": "OpenAI API is working",
            "response": response.choices[0].message.content
        }
    except Exception as e:
        return {"status": "error", "message": f"Error using OpenAI API: {str(e)}"}