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
    """WebSocket endpoint for bidirectional audio streaming."""
    if not client_id:
        client_id = f"client_{uuid.uuid4().hex}"
    
    try:
        logger.info(f"Starting websocket connection for {client_id}")
        await websocket.accept()
        logger.info(f"WebSocket connection accepted for {client_id}")
        await stream_manager.connect(websocket, client_id)
        
        # Send initial configuration
        await websocket.send_json({
            "event": "connected",
            "config": {
                "sample_rate": 16000,
                "channels": 1,
                "frame_size": 480,
                "variable_frames": True
            }
        })
        
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
        
        # Create a temporary buffer for accumulating chunks
        all_audio = bytearray()
        
        # Main receive loop
        while True:
            data = await websocket.receive()
            
            if "bytes" in data:
                audio_chunk = data["bytes"]
                logger.info(f"Received {len(audio_chunk)} bytes of audio from client {client_id}")
                
                # Process with VAD for interruption detection
                await stream_manager.receive_audio(client_id, audio_chunk)
                
                # Accumulate in our temporary buffer
                all_audio.extend(audio_chunk)
                
                # After accumulating enough data (3 seconds at 16kHz mono)
                if len(all_audio) >= 16000 * 2 * 3:
                    if client_id in streaming_agents:
                        # Save input audio file
                        audio_path = stream_manager.save_audio_file(client_id, "input", bytes(all_audio))
                        logger.info(f"Saved input audio to {audio_path}")
                        
                        logger.info(f"Processing {len(all_audio)} bytes of accumulated audio")
                        asyncio.create_task(
                            streaming_agents[client_id].process_audio(bytes(all_audio))
                        )
                        # Clear the buffer
                        all_audio = bytearray()
            
            elif "text" in data:
                # Handle text messages
                message = data["text"]
                logger.info(f"Received text from {client_id}: {message}")
                
                if message == "end_session":
                    await websocket.close()
                    break
    
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", exc_info=True)
    finally:
        # Save any remaining audio
        if len(all_audio) > 0:
            stream_manager.save_audio_file(client_id, "input_final", bytes(all_audio))
            
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
                logger.info(f"Response handler for {client_id} cancelled")

async def handle_agent_responses(client_id: str):
    """Handle streaming responses from the agent."""
    if client_id not in streaming_agents:
        logger.warning(f"No agent found for client {client_id}")
        return
    
    agent = streaming_agents[client_id]
    logger.info(f"Starting response handler for {client_id}")
    
    try:
        count = 0
        all_response_audio = bytearray()
        
        async for audio_chunk in agent.get_response_stream():
            count += 1
            if audio_chunk:
                # Collect chunks for saving
                all_response_audio.extend(audio_chunk)
                logger.info(f"Sending audio chunk #{count} ({len(audio_chunk)} bytes) to {client_id}")
                await stream_manager.send_audio(client_id, audio_chunk)
        
        # Save complete response audio
        if all_response_audio:
            stream_manager.save_audio_file(client_id, "response", bytes(all_response_audio))
            
        logger.info(f"Response stream complete: sent {count} chunks to {client_id}")
    
    except asyncio.CancelledError:
        # Save partial response before cancellation
        if 'all_response_audio' in locals() and all_response_audio:
            stream_manager.save_audio_file(client_id, "response_partial", bytes(all_response_audio))
        logger.info(f"Response handler for {client_id} cancelled")
    
    except Exception as e:
        logger.error(f"Error in response handler for {client_id}: {str(e)}", exc_info=True)