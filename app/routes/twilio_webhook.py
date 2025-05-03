"""
Twilio webhook handlers for voice interactions.
"""
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import PlainTextResponse
import logging
from typing import Dict, Any, Optional
import json
import hashlib
import hmac
import base64
from app.config import settings

# Set up logger
logger = logging.getLogger(__name__)

router = APIRouter()

# TwiML templates (would typically be in a template file)
TWIML_WELCOME = """
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Welcome to our restaurant AI assistant. How may I help you today?</Say>
    <Record action="/webhook/transcribe" maxLength="60" playBeep="true" />
</Response>
"""

TWIML_RESPONSE = """
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>{message}</Say>
    <Record action="/webhook/transcribe" maxLength="60" playBeep="true" />
</Response>
"""

TWIML_GOODBYE = """
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Thank you for calling. Goodbye!</Say>
    <Hangup />
</Response>
"""

TWIML_ERROR = """
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>I'm sorry, we're experiencing technical difficulties. Please try again later.</Say>
    <Hangup />
</Response>
"""

def validate_twilio_request(request: Request) -> bool:
    """
    Validate that the request is coming from Twilio.
    
    Args:
        request: The incoming FastAPI request.
        
    Returns:
        bool: True if the request is valid, False otherwise.
    """
    # Skip validation in debug mode
    if settings.DEBUG:
        return True
    
    # Get the Twilio signature from the headers
    twilio_signature = request.headers.get("X-Twilio-Signature")
    if not twilio_signature:
        return False
    
    # Get the request URL and form data
    url = str(request.url)
    form_data = request.form()
    
    # Sort the form data parameters
    sorted_form_data = sorted(form_data.items())
    
    # Create the validation string (url + sorted form params)
    validation_string = url
    for k, v in sorted_form_data:
        validation_string += k + v
    
    # Compute the HMAC-SHA1 signature
    # In a real implementation, this would be the actual auth token
    auth_token = settings.TWILIO_AUTH_TOKEN or "dummy_token"
    expected_signature = base64.b64encode(
        hmac.new(
            auth_token.encode("utf-8"),
            validation_string.encode("utf-8"),
            hashlib.sha1
        ).digest()
    ).decode("utf-8")
    
    # Compare signatures
    return hmac.compare_digest(expected_signature, twilio_signature)

@router.post("/voice", response_class=PlainTextResponse)
async def voice_webhook(request: Request):
    """
    Handle incoming voice calls from Twilio.
    
    Args:
        request: The incoming FastAPI request.
        
    Returns:
        PlainTextResponse: TwiML response.
    """
    # Validate the request (in production)
    if not settings.DEBUG and not validate_twilio_request(request):
        logger.warning("Invalid Twilio signature")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature")
    
    # Log the incoming call
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    caller = form_data.get("From", "unknown")
    logger.info(f"Incoming call received: {call_sid} from {caller}")
    
    # Return welcome TwiML
    return PlainTextResponse(content=TWIML_WELCOME, media_type="application/xml")

@router.post("/transcribe", response_class=PlainTextResponse)
async def transcribe_webhook(request: Request):
    """
    Handle transcription of voice recordings from Twilio.
    
    Args:
        request: The incoming FastAPI request.
        
    Returns:
        PlainTextResponse: TwiML response.
    """
    # Validate the request (in production)
    if not settings.DEBUG and not validate_twilio_request(request):
        logger.warning("Invalid Twilio signature")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature")
    
    # Process the recording
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    recording_url = form_data.get("RecordingUrl")
    recording_sid = form_data.get("RecordingSid", "unknown")
    
    logger.info(f"Recording received: {recording_sid} from call {call_sid}")
    
    # In a real implementation, you would:
    # 1. Download the recording
    # 2. Transcribe it using a speech-to-text service
    # 3. Process the transcription with your agent
    # 4. Generate a response
    
    # For now, we just return a mock response
    message = "I understand you're asking about our menu. We have a variety of dishes including pasta, pizza, and salads. Is there something specific you'd like to know?"
    
    # Mock "goodbye" detection - in a real implementation, this would be based on NLU
    if "goodbye" in recording_url or "bye" in recording_url or "thank you" in recording_url:
        return PlainTextResponse(content=TWIML_GOODBYE, media_type="application/xml")
    
    # Return response TwiML
    return PlainTextResponse(
        content=TWIML_RESPONSE.format(message=message),
        media_type="application/xml"
    )

@router.post("/status", status_code=status.HTTP_200_OK)
async def status_webhook(request: Request):
    """
    Handle call status callbacks from Twilio.
    
    Args:
        request: The incoming FastAPI request.
        
    Returns:
        dict: Acknowledgement response.
    """
    # Validate the request (in production)
    if not settings.DEBUG and not validate_twilio_request(request):
        logger.warning("Invalid Twilio signature")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature")
    
    # Process the status update
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    call_status = form_data.get("CallStatus", "unknown")
    
    logger.info(f"Call status update: {call_sid} is now {call_status}")
    
    # In a real implementation, you would update your database with the call status
    
    return {"status": "received"}

@router.post("/fallback", response_class=PlainTextResponse)
async def fallback_webhook(request: Request):
    """
    Handle fallback requests when errors occur in Twilio.
    
    Args:
        request: The incoming FastAPI request.
        
    Returns:
        PlainTextResponse: TwiML response.
    """
    # Validate the request (in production)
    if not settings.DEBUG and not validate_twilio_request(request):
        logger.warning("Invalid Twilio signature")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature")
    
    # Log the error
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    error_code = form_data.get("ErrorCode", "unknown")
    error_msg = form_data.get("ErrorMessage", "unknown")
    
    logger.error(f"Twilio error in call {call_sid}: {error_code} - {error_msg}")
    
    # Return error TwiML
    return PlainTextResponse(content=TWIML_ERROR, media_type="application/xml")