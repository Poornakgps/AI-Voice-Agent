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
from app.utils.twilio_client import create_twilio_client
import base64
from sqlalchemy.orm import Session

from app.config import settings
from app.core.agent import RestaurantAgent
from app.voice.twiml_generator import TwiMLGenerator
from app.voice.stt import transcribe_audio
from database import get_db_dependency

logger = logging.getLogger(__name__)

router = APIRouter()

twiml_generator = TwiMLGenerator()

active_sessions = {}

def validate_twilio_request(request: Request, form_data) -> bool:
    """Validate that the request is coming from Twilio."""
    if settings.DEBUG or not settings.TWILIO_API_SECRET:
        return True
    
    twilio_signature = request.headers.get("X-Twilio-Signature")
    if not twilio_signature:
        return False
    
    # Convert to dict for validation
    form_dict = dict(form_data)
    
    # Use Twilio's validator
    from twilio.request_validator import RequestValidator
    validator = RequestValidator(settings.TWILIO_API_SECRET)
    
    return validator.validate(
        str(request.url),
        form_dict,
        twilio_signature
    )

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
    form_data = await request.form()
    
    if not settings.DEBUG and not validate_twilio_request(request, form_data):
        logger.warning("Invalid Twilio signature")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature")
    
    call_sid = form_data.get("CallSid", "unknown")
    caller = form_data.get("From", "unknown")
    logger.info(f"Incoming call received: {call_sid} from {caller}")
    
    client = create_twilio_client()
    if not client:
        logger.error("Failed to create Twilio client")
        return PlainTextResponse(
            content=twiml_generator.error_response("System error. Please try again later."),
            media_type="application/xml"
        )
    
    get_or_create_agent(call_sid, db)
    
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
    form_data = await request.form()
    
    if not settings.DEBUG and not validate_twilio_request(request, form_data):
        logger.warning("Invalid Twilio signature")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature")
    
    call_sid = form_data.get("CallSid", "unknown")
    recording_url = form_data.get("RecordingUrl")
    recording_sid = form_data.get("RecordingSid", "unknown")
    
    logger.info(f"Recording received: {recording_sid} from call {call_sid}")

    # Check if transcript was directly provided (for testing)
    transcript = form_data.get("Transcript")
    
    # Debug DB connection
    try:
        category_count = db.query(MenuCategory).count()
        logger.info(f"DB check: Found {category_count} menu categories")
    except Exception as e:
        logger.error(f"DB connection error: {str(e)}")
    
    client = create_twilio_client()
    if not client:
        logger.error("Failed to create Twilio client")
        return PlainTextResponse(
            content=twiml_generator.error_response("System error. Please try again later."),
            media_type="application/xml"
        )
    agent = get_or_create_agent(call_sid, db)
    
    try:
        # If transcript is directly provided (for testing), use it
        if transcript:
            logger.info(f"Using provided transcript: '{transcript}'")
        # Otherwise try to transcribe from the recording URL
        elif recording_url:
            transcript = await transcribe_audio(recording_url)
        else:
            logger.warning(f"No recording URL or transcript for call {call_sid}")
            return PlainTextResponse(
                content=twiml_generator.fallback_response(),
                media_type="application/xml"
            )
        
        logger.info(f"Processing transcript: '{transcript}'")
        
        # Process the transcript with the agent
        agent_response = agent.process_message(transcript)
        
        logger.info(f"Agent response: '{agent_response}'")
        
        return PlainTextResponse(
            content=twiml_generator.agent_response(agent_response),
            media_type="application/xml"
        )
    except Exception as e:
        logger.error(f"Error processing recording: {str(e)}", exc_info=True)
        return PlainTextResponse(
            content=twiml_generator.error_response("I'm sorry, I couldn't understand that. Could you try again?"),
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
    if not settings.DEBUG and not validate_twilio_request(request):
        logger.warning("Invalid Twilio signature")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature")
    
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    call_status = form_data.get("CallStatus", "unknown")
    
    logger.info(f"Call status update: {call_sid} is now {call_status}")

    client = create_twilio_client()
    if not client:
        logger.error("Failed to create Twilio client")
        return PlainTextResponse(
            content=twiml_generator.error_response("System error. Please try again later."),
            media_type="application/xml"
        )
        
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
    if not settings.DEBUG and not validate_twilio_request(request):
        logger.warning("Invalid Twilio signature")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature")
    
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    error_code = form_data.get("ErrorCode", "unknown")
    error_msg = form_data.get("ErrorMessage", "unknown")
    
    logger.error(f"Twilio error in call {call_sid}: {error_code} - {error_msg}")
    
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
    if not settings.DEBUG and not validate_twilio_request(request):
        logger.warning("Invalid Twilio signature")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature")
    
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    digits = form_data.get("Digits", "")
    
    logger.info(f"DTMF input received: {digits} from call {call_sid}")

    client = create_twilio_client()
    if not client:
        logger.error("Failed to create Twilio client")
        return PlainTextResponse(
            content=twiml_generator.error_response("System error. Please try again later."),
            media_type="application/xml"
        )
    agent = get_or_create_agent(call_sid, db)
    
    agent_response = agent.process_message(f"I pressed {digits}")
    
    return PlainTextResponse(
        content=twiml_generator.agent_response(agent_response),
        media_type="application/xml"
    )