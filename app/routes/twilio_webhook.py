"""
Twilio webhook handlers for voice interactions with support for both 
traditional TwiML and Media Streams approaches.
"""
from fastapi import APIRouter, Request, HTTPException, status, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
import logging
import json
import asyncio
from typing import Dict, Any, Optional
import base64
from sqlalchemy.orm import Session

from app.config import settings
from app.core.agent import RestaurantAgent
from app.core.streaming_agent import StreamingAgent
from app.voice.twiml_generator import TwiMLGenerator
from app.voice.stt import transcribe_audio_stream
from app.voice.vad import InterruptionDetector
from app.utils.twilio_client import create_twilio_client
from app.voice.streaming import stream_manager
from database import get_db_dependency

logger = logging.getLogger(__name__)
router = APIRouter()

twiml_generator = TwiMLGenerator()
active_sessions = {}
streaming_agents = {}

# Choose which approach to use (can be set in .env)
USE_MEDIA_STREAMS = settings.USE_MEDIA_STREAMS if hasattr(settings, 'USE_MEDIA_STREAMS') else False

def validate_twilio_request(request: Request, form_data) -> bool:
    """Validate that the request is coming from Twilio."""
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

def get_or_create_agent(call_sid: str, db: Session) -> RestaurantAgent:
    """Get or create a traditional agent for a call."""
    if call_sid not in active_sessions:
        agent = RestaurantAgent(db)
        active_sessions[call_sid] = agent
    
    return active_sessions[call_sid]

# ----- Traditional TwiML Approach -----

@router.post("/voice/traditional", response_class=PlainTextResponse)
async def voice_traditional_webhook(request: Request, db: Session = Depends(get_db_dependency)):
    """Traditional TwiML approach for voice calls."""
    form_data = await request.form()
    
    if not validate_twilio_request(request, form_data):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature")
    
    call_sid = form_data.get("CallSid", "unknown")
    caller = form_data.get("From", "unknown")
    logger.info(f"Incoming call received (traditional): {call_sid} from {caller}")
    
    get_or_create_agent(call_sid, db)
    
    return PlainTextResponse(content=twiml_generator.welcome_response(), media_type="application/xml")

@router.post("/transcribe", response_class=PlainTextResponse)
async def transcribe_webhook(request: Request, db: Session = Depends(get_db_dependency)):
    """Handle transcription of voice recordings from Twilio."""
    form_data = await request.form()
    
    if not validate_twilio_request(request, form_data):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature")
    
    call_sid = form_data.get("CallSid", "unknown")
    recording_url = form_data.get("RecordingUrl")
    transcript = form_data.get("Transcript")
    
    agent = get_or_create_agent(call_sid, db)
    
    try:
        if transcript:
            logger.info(f"Using provided transcript: '{transcript}'")
        elif recording_url:
            transcript = await transcribe_audio_stream(recording_url)
        else:
            return PlainTextResponse(content=twiml_generator.fallback_response(), media_type="application/xml")
        
        agent_response = agent.process_message(transcript)
        
        return PlainTextResponse(
            content=twiml_generator.agent_response(agent_response),
            media_type="application/xml"
        )
    except Exception as e:
        logger.error(f"Error processing recording: {str(e)}", exc_info=True)
        return PlainTextResponse(
            content=twiml_generator.error_response("I couldn't understand that. Could you try again?"),
            media_type="application/xml"
        )

@router.post("/status", status_code=status.HTTP_200_OK)
async def status_webhook(request: Request):
    """Handle call status callbacks from Twilio."""
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    call_status = form_data.get("CallStatus", "unknown")
    
    if call_status in ["completed", "failed", "busy", "no-answer"]:
        if call_sid in active_sessions:
            del active_sessions[call_sid]
        if call_sid in streaming_agents:
            await streaming_agents[call_sid].close()
            del streaming_agents[call_sid]
    
    return {"status": "received"}

@router.post("/fallback", response_class=PlainTextResponse)
async def fallback_webhook(request: Request):
    """Handle fallback requests when errors occur in Twilio."""
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "unknown")
    error_code = form_data.get("ErrorCode", "unknown")
    
    logger.error(f"Twilio error in call {call_sid}: {error_code}")
    
    return PlainTextResponse(content=twiml_generator.error_response(), media_type="application/xml")

# ----- Media Streams Approach -----

@router.post("/voice", response_class=PlainTextResponse)
async def voice_webhook(request: Request):
    """Main entry point - decides which approach to use based on settings."""
    if USE_MEDIA_STREAMS:
        return await voice_streams_webhook(request)
    else:
        return await voice_traditional_webhook(request)

@router.post("/voice/streams", response_class=PlainTextResponse)
async def voice_streams_webhook(request: Request):
    """Setup Twilio call with Media Streams."""
    form_data = await request.form()
    
    if not validate_twilio_request(request, form_data):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature")
    
    call_sid = form_data.get("CallSid", "unknown")
    caller = form_data.get("From", "unknown")
    logger.info(f"Incoming call received (streams): {call_sid} from {caller}")
    
    # Generate TwiML to establish Media Streams connection
    stream_url = f"{settings.SERVER_URL}/streams/{call_sid}"
    
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

@router.websocket("/streams/{call_sid}")
async def media_stream_endpoint(
    websocket: WebSocket, 
    call_sid: str,
    db: Session = Depends(get_db_dependency)
):
    """WebSocket endpoint for Twilio Media Streams."""
    await websocket.accept()
    logger.info(f"Media Stream established for call {call_sid}")
    
    # Initialize streaming agent
    agent = StreamingAgent(db)
    streaming_agents[call_sid] = agent
    
    # Create interruption detector
    vad = InterruptionDetector()
    
    # Connect to stream manager
    await stream_manager.connect(websocket, call_sid)
    
    # Send welcome message
    welcome_text = twiml_generator.welcome_response()
    # Extract just the text content from the TwiML
    import re
    welcome_text = re.search(r"<Say[^>]*>(.*?)</Say>", welcome_text)
    welcome_text = welcome_text.group(1) if welcome_text else "Welcome to Taste of India. How may I help you?"
    
    # Process welcome message
    asyncio.create_task(agent.stream_response(welcome_text))
    response_task = asyncio.create_task(handle_agent_responses(call_sid, agent, stream_manager))
    
    audio_buffer = bytearray()
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("event") == "media":
                # Process media payload
                if message.get("track") == "inbound":
                    try:
                        payload = message.get("payload", "")
                        audio_data = base64.b64decode(payload)
                        
                        # Process with VAD for interruption detection
                        is_speech, is_interruption = vad.process_frame(audio_data)
                        
                        if is_interruption and agent.is_speaking:
                            await agent.handle_interruption()
                        
                        # Accumulate audio
                        audio_buffer.extend(audio_data)
                        
                        # Process when we have enough data (~1 second)
                        if len(audio_buffer) >= 16000:
                            await agent.process_audio(bytes(audio_buffer))
                            audio_buffer = bytearray()
                            
                    except Exception as e:
                        logger.error(f"Error processing media: {str(e)}")
                        
            elif message.get("event") == "stop":
                logger.info(f"Media Stream closed for call {call_sid}")
                break
    
    except WebSocketDisconnect:
        logger.info(f"Media Stream disconnected for call {call_sid}")
    except Exception as e:
        logger.error(f"Error in Media Stream handler: {str(e)}")
    finally:
        # Clean up
        if call_sid in streaming_agents:
            await streaming_agents[call_sid].close()
            del streaming_agents[call_sid]
        
        if not response_task.done():
            response_task.cancel()
            
        stream_manager.disconnect(call_sid)

async def handle_agent_responses(call_sid: str, agent: StreamingAgent, manager: Any):
    """Stream agent responses back to Twilio."""
    try:
        async for audio_chunk in agent.get_response_stream():
            if audio_chunk:
                await manager.send_audio(call_sid, audio_chunk)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Error streaming response: {str(e)}")