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
    return {"status": "ready"}

@router.get("/metrics", response_model=MetricsResponse)
async def metrics():
    """
    Metrics endpoint for monitoring.
    
    Returns:
        MetricsResponse: Current service metrics.
    """
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

        client = openai.OpenAI(
            api_key=settings.OPENAI_API_KEY, 
            organization=settings.OPENAIORG_ID
        )
        print(settings.OPENAI_API_KEY, settings.OPENAIORG_ID)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
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
    
    
@router.get("/test-twilio", status_code=status.HTTP_200_OK)
async def test_twilio():
    """
    Test if Twilio API credentials are working properly.
    
    Returns:
        dict: Status of the Twilio API connection test with diagnostic information
    """
    import datetime
    from app.utils.twilio_client import create_twilio_client
    
    if not settings.TWILIO_API_KEY or not settings.TWILIO_API_SECRET:
        return {
            "status": "error",
            "message": "Twilio API credentials not configured",
            "help": "Please set TWILIO_API_KEY and TWILIO_API_SECRET in your .env file"
        }
    
    try:
        client = create_twilio_client()
        if not client:
            return {
                "status": "error",
                "message": "Failed to initialize Twilio client",
                "help": "Check your API credentials in the .env file"
            }
        
        numbers = client.incoming_phone_numbers.list(limit=1)
        
        return {
            "status": "success",
            "message": "Twilio API authentication successful",
            "test_time": str(datetime.datetime.now()),
            "phone_numbers_found": len(numbers),
            "api_key_verified": True
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Twilio API test failed: {str(e)}",
            "type": str(type(e).__name__),
            "test_time": str(datetime.datetime.now()),
            "troubleshooting": [
                "Verify your Twilio API credentials are correct",
                "Check that your Twilio account is active",
                "Ensure your API key has the necessary permissions",
                "Try creating a new API key in the Twilio Console"
            ]
        }