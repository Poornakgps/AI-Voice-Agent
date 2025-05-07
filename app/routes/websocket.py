"""
WebSocket routes for audio streaming.
"""
import logging
import uuid
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Any, Optional

from app.voice.streaming import StreamManager
from app.core.streaming_agent import StreamingAgent
from database import get_db_dependency
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter()

# Singleton stream manager
stream_manager = StreamManager()

# Active agents for each connection
streaming_agents: Dict[str, StreamingAgent] = {}

@router.websocket("/ws/audio/{client_id}")
async def websocket_audio_endpoint(
    websocket: WebSocket,
    client_id: Optional[str] = None,
    db: Session = Depends(get_db_dependency)
):
    """
    WebSocket endpoint for bidirectional audio streaming.
    
    Args:
        websocket: WebSocket connection
        client_id: Optional client ID (generated if not provided)
        db: Database session
    """
    if not client_id:
        client_id = f"client_{uuid.uuid4().hex}"
    
    try:
        await stream_manager.connect(websocket, client_id)
        
        # Initialize streaming agent
        streaming_agents[client_id] = StreamingAgent(db)
        
        # Register interrupt handler
        stream_manager.register_interrupt_handler(
            client_id,
            lambda cid: streaming_agents[cid].handle_interruption()
        )
        
        # Start response task
        response_task = asyncio.create_task(
            handle_agent_responses(client_id)
        )
        
        # Main receive loop
        while True:
            data = await websocket.receive()
            
            if "bytes" in data:
                audio_chunk = data["bytes"]
                await stream_manager.receive_audio(client_id, audio_chunk)
                
                # Process accumulated audio
                if client_id in streaming_agents:
                    buffer = stream_manager.get_input_buffer(client_id)
                    if buffer:
                        audio_data = buffer.get_all()
                        if audio_data:
                            asyncio.create_task(
                                streaming_agents[client_id].process_audio(audio_data)
                            )
            
            elif "text" in data:
                # Handle text messages (e.g., commands)
                message = data["text"]
                logger.info(f"Received text from {client_id}: {message}")
                
                if message == "end_session":
                    await websocket.close()
                    break
    
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected")
    
    finally:
        # Clean up resources
        stream_manager.disconnect(client_id)
        
        if client_id in streaming_agents:
            await streaming_agents[client_id].close()
            del streaming_agents[client_id]
        
        # Cancel response task if running
        if 'response_task' in locals() and not response_task.done():
            response_task.cancel()
            try:
                await response_task
            except asyncio.CancelledError:
                pass

async def handle_agent_responses(client_id: str):
    """
    Handle streaming responses from the agent.
    
    Args:
        client_id: Client identifier
    """
    if client_id not in streaming_agents:
        return
    
    agent = streaming_agents[client_id]
    
    try:
        async for audio_chunk in agent.get_response_stream():
            await stream_manager.send_audio(client_id, audio_chunk)
    
    except asyncio.CancelledError:
        logger.info(f"Response handler for {client_id} cancelled")
    
    except Exception as e:
        logger.error(f"Error in response handler for {client_id}: {str(e)}")