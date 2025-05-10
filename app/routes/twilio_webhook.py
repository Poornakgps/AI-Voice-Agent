"""
Twilio webhook handlers for voice interactions using Media Streams.
"""
from fastapi import APIRouter, Request, HTTPException, status, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
import logging
import json
import asyncio
import base64
import re
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.config import settings
from app.core.streaming_agent import StreamingAgent
from app.voice.twiml_generator import TwiMLGenerator
from app.voice.vad import InterruptionDetector
from app.voice.streaming import stream_manager
from database import get_db_dependency

logger = logging.getLogger(__name__)
router = APIRouter()

twiml_generator = TwiMLGenerator()
streaming_agents = {}

# Always use Media Streams approach
USE_MEDIA_STREAMS = True

def validate_twilio_request(request: Request, form_data) -> bool:
    if settings.DEBUG or not settings.TWILIO_API_SECRET:
        return True
    
    twilio_signature = request.headers.get("X-Twilio-Signature")
    if not twilio_signature:
        return False
    
    form_dict = dict(form_data)
    
    from twilio.request_validator import RequestValidator
    validator = RequestValidator(settings.TWILIO_API_SECRET)
    
    return validator.validate(
        str(request.url),
        form_dict,
        twilio_signature
    )

@router.post("/status", status_code=status.HTTP_200_OK)
async def status_webhook(request: Request):

    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    call_status = form_data.get("CallStatus", "unknown")
    
    if call_status in ["completed", "failed", "busy", "no-answer"]:
        if call_sid in streaming_agents:
            await streaming_agents[call_sid].close()
            del streaming_agents[call_sid]
    
    return {"status": "received"}

@router.post("/fallback", response_class=PlainTextResponse)
async def fallback_webhook(request: Request):

    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    error_code = form_data.get("ErrorCode", "unknown")
    
    logger.error(f"Twilio error in call {call_sid}: {error_code}")
    
    # Generate TwiML that will reset the call using Media Streams
    stream_url = f"{settings.WEBHOOKBASE_URL}/streams/{call_sid}"
    
    twiml = f"""
    <?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say>We're experiencing technical difficulties. Reconnecting you now.</Say>
        <Connect>
            <Stream url="{stream_url}" track="both_tracks">
                <Parameter name="callSid" value="{call_sid}" />
            </Stream>
        </Connect>
        <Pause length="60" />
    </Response>
    """
    
    return PlainTextResponse(content=twiml, media_type="application/xml")

@router.post("/voice", response_class=PlainTextResponse)
async def voice_webhook(request: Request):

    form_data = await request.form()
    
    if not validate_twilio_request(request, form_data):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature")
    
    call_sid = form_data.get("CallSid", "unknown")
    caller = form_data.get("From", "unknown")
    logger.info(f"Incoming call received: {call_sid} from {caller}")
    
    # Generate TwiML to establish Media Streams connection
    stream_url = f"{settings.WEBHOOKBASE_URL}/streams/{call_sid}"
    
    twiml = f"""
    <?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Connect>
            <Stream url="{stream_url}" track="both_tracks">
                <Parameter name="callSid" value="{call_sid}" />
            </Stream>
        </Connect>
        <Pause length="600" /> <!-- Keep connection alive for 10 minutes -->
    </Response>
    """
    
    return PlainTextResponse(content=twiml, media_type="application/xml")

