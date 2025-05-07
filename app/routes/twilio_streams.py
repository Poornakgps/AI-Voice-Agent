from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Request
from sqlalchemy.orm import Session
import json
import logging

from app.voice.twilio_streams import TwilioMediaStreamHandler
from app.voice.streaming import stream_manager
from app.core.streaming_agent import StreamingAgent
from database import get_db_dependency

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize handler
media_handler = TwilioMediaStreamHandler(stream_manager)

@router.websocket("/streams/{call_sid}")
async def twilio_media_stream(
    websocket: WebSocket, 
    call_sid: str,
    db: Session = Depends(get_db_dependency)
):
    """
    WebSocket endpoint for Twilio Media Streams.
    
    Args:
        websocket: WebSocket connection
        call_sid: Twilio call SID
        db: Database session
    """
    agent = StreamingAgent(db)
    
    try:
        await media_handler.handle_connection(websocket, call_sid, agent)
        
        # Main receive loop
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("event") == "media":
                await media_handler.handle_media(call_sid, message)
            elif message.get("event") == "mark":
                await media_handler.handle_mark(call_sid, message)
            elif message.get("event") == "close":
                logger.info(f"Stream closed for call {call_sid}")
                break
                
    except WebSocketDisconnect:
        logger.info(f"Media Stream disconnected for call {call_sid}")
    except Exception as e:
        logger.error(f"Error in Media Stream handler: {str(e)}")
    finally:
        stream_manager.disconnect(call_sid)
        if call_sid in media_handler.active_calls:
            await media_handler.active_calls[call_sid].close()
            del media_handler.active_calls[call_sid]