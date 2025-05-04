"""
Twilio webhook handlers for voice interactions.
"""
from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import PlainTextResponse
import logging
from typing import Dict, Any, Optional
import json
import hashlib
import hmac
import base64
from sqlalchemy.orm import Session

from app.config import settings
from app.core.agent import RestaurantAgent
from app.voice.twiml_generator import TwiMLGenerator
from app.voice.stt import transcribe_audio
from database import get_db_dependency

# Set up logger
logger = logging.getLogger(__name__)

router = APIRouter()

# Create TwiML generator
twiml_generator = TwiMLGenerator()

# Active call sessions (in-memory storage for development)
# In production, this would be stored in a database or Redis
active_sessions = {}

def validate_twilio_request(request: Request) -> bool:
    """Validate that the request is coming from Twilio."""
    # Skip validation in debug mode or without auth token
    if settings.DEBUG or not settings.TWILIO_AUTH_TOKEN:
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
    
    # Create the validation string
    validation_string = url
    for k, v in sorted_form_data:
        validation_string += k + v
    
    # Compute the HMAC-SHA1 signature
    auth_token = settings.TWILIO_AUTH_TOKEN
    expected_signature = base64.b64encode(
        hmac.new(
            auth_token.encode("utf-8"),
            validation_string.encode("utf-8"),
            hashlib.sha1
        ).digest()
    ).decode("utf-8")
    
    # Compare signatures
    return hmac.compare_digest(expected_signature, twilio_signature)

def get_or_create_agent(call_sid: str, db: Session) -> RestaurantAgent:
    """
    Get or create an agent for a call.
    
    Args:
        call_sid: Twilio call SID
        db: Database session
        
    Returns:
        RestaurantAgent: Agent instance
    """
    if call_sid not in active_sessions:
        agent = RestaurantAgent(db)
        active_sessions[call_sid] = agent
        logger.info(f"Created new agent for call {call_sid}")
    
    return active_sessions[call_sid]

@router.post("/voice", response_class=PlainTextResponse)
async def voice_webhook(request: Request, db: Session = Depends(get_db_dependency)):
    """
    Handle incoming voice calls from Twilio.
    
    Args:
        request: The incoming FastAPI request.
        db: Database session
        
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
    
    # Create agent for the call
    get_or_create_agent(call_sid, db)
    
    # Return welcome TwiML
    return PlainTextResponse(content=twiml_generator.welcome_response(), media_type="application/xml")

@router.post("/transcribe", response_class=PlainTextResponse)
async def transcribe_webhook(request: Request, db: Session = Depends(get_db_dependency)):
    """
    Handle transcription of voice recordings from Twilio.
    
    Args:
        request: The incoming FastAPI request.
        db: Database session
        
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
    
    # Get agent for the call
    agent = get_or_create_agent(call_sid, db)
    
    # Transcribe the recording
    if recording_url:
        try:
            transcript = await transcribe_audio(recording_url)
            logger.info(f"Transcription: {transcript}")
            
            # Process the transcript with the agent
            agent_response = agent.process_message(transcript)
            
            # Generate TwiML response
            return PlainTextResponse(
                content=twiml_generator.agent_response(agent_response),
                media_type="application/xml"
            )
        except Exception as e:
            logger.error(f"Error processing recording: {str(e)}")
            return PlainTextResponse(
                content=twiml_generator.error_response("I'm sorry, I couldn't understand that. Could you try again?"),
                media_type="application/xml"
            )
    else:
        logger.warning(f"No recording URL for call {call_sid}")
        return PlainTextResponse(
            content=twiml_generator.fallback_response(),
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
    
    # Clean up resources if call is completed or failed
    if call_status in ["completed", "failed", "busy", "no-answer"]:
        if call_sid in active_sessions:
            del active_sessions[call_sid]
            logger.info(f"Removed agent for completed call {call_sid}")
    
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
    return PlainTextResponse(content=twiml_generator.error_response(), media_type="application/xml")

@router.post("/dtmf", response_class=PlainTextResponse)
async def dtmf_webhook(request: Request, db: Session = Depends(get_db_dependency)):
    """
    Handle DTMF (touch-tone) input from Twilio.
    
    Args:
        request: The incoming FastAPI request.
        db: Database session
        
    Returns:
        PlainTextResponse: TwiML response.
    """
    # Validate the request (in production)
    if not settings.DEBUG and not validate_twilio_request(request):
        logger.warning("Invalid Twilio signature")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature")
    
    # Process the DTMF input
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    digits = form_data.get("Digits", "")
    
    logger.info(f"DTMF input received: {digits} from call {call_sid}")
    
    # Get agent for the call
    agent = get_or_create_agent(call_sid, db)
    
    # Process the DTMF input with the agent
    agent_response = agent.process_message(f"I pressed {digits}")
    
    # Generate TwiML response
    return PlainTextResponse(
        content=twiml_generator.agent_response(agent_response),
        media_type="application/xml"
    )