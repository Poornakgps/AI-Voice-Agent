# app/voice/twilio_streams.py
"""
Twilio Media Streams integration for real-time streaming audio.
"""
import base64
import json
import logging
from typing import Dict, Any, Callable, Optional
from fastapi import WebSocket

from app.voice.vad import InterruptionDetector
from app.voice.streaming import StreamManager
from app.core.streaming_agent import StreamingAgent

logger = logging.getLogger(__name__)

class TwilioMediaStreamHandler:
    """Handler for Twilio Media Streams."""
    
    def __init__(self, stream_manager: StreamManager):
        """Initialize the handler."""
        self.stream_manager = stream_manager
        self.active_calls: Dict[str, StreamingAgent] = {}
        self.vad_detectors: Dict[str, InterruptionDetector] = {}
        
    async def handle_connection(self, websocket: WebSocket, call_sid: str, agent: StreamingAgent):
        """
        Handle a new Media Stream connection.
        
        Args:
            websocket: WebSocket connection
            call_sid: Twilio call SID
            agent: StreamingAgent instance
        """
        await websocket.accept()
        
        # Register with stream manager
        await self.stream_manager.connect(websocket, call_sid)
        
        # Store agent reference
        self.active_calls[call_sid] = agent
        
        # Set up VAD for interruption detection
        self.vad_detectors[call_sid] = InterruptionDetector()
        
        # Register interrupt handler
        self.stream_manager.register_interrupt_handler(
            call_sid, 
            lambda cid: asyncio.create_task(self.active_calls[cid].handle_interruption())
        )
        
        # Start response streaming task
        import asyncio
        asyncio.create_task(self._handle_agent_responses(call_sid))
        
        # Send welcome message
        welcome_text = agent.prompt_manager.get_welcome_message()
        await agent.stream_response(welcome_text)
        
        logger.info(f"Media Stream established for call {call_sid}")
        
    async def handle_media(self, call_sid: str, media_chunk: Dict[str, Any]):
        """
        Handle incoming media chunk from Twilio.
        
        Args:
            call_sid: Twilio call SID
            media_chunk: Media chunk data from Twilio
        """
        if call_sid not in self.active_calls:
            logger.warning(f"Received media for unknown call: {call_sid}")
            return
        
        # Check if it's audio media
        if media_chunk.get("event") != "media" or media_chunk.get("track") != "inbound":
            return
            
        # Decode audio payload
        try:
            payload = media_chunk.get("payload", "")
            audio_data = base64.b64decode(payload)
            
            # Process with VAD for interruption detection
            if call_sid in self.vad_detectors:
                is_speech, is_interruption = self.vad_detectors[call_sid].process_frame(audio_data)
                
                if is_interruption:
                    logger.info(f"Interruption detected for call {call_sid}")
                    await self.active_calls[call_sid].handle_interruption()
            
            # Add to buffer for processing
            await self.stream_manager.receive_audio(call_sid, audio_data)
            
            # Once we have enough audio, process it
            buffer = self.stream_manager.get_input_buffer(call_sid)
            if buffer and buffer.current_size >= 16000:  # ~1 second at 16kHz mono
                audio_data = buffer.get_all()
                await self.active_calls[call_sid].process_audio(audio_data)
                
        except Exception as e:
            logger.error(f"Error processing media chunk: {str(e)}")
    
    async def handle_mark(self, call_sid: str, mark_data: Dict[str, Any]):
        """Handle mark events from Twilio."""
        if call_sid not in self.active_calls:
            return
            
        mark_name = mark_data.get("name")
        if mark_name == "end_stream":
            logger.info(f"End of stream marked for call {call_sid}")
            
    async def _handle_agent_responses(self, call_sid: str):
        """Stream agent responses back to Twilio."""
        if call_sid not in self.active_calls:
            return
            
        agent = self.active_calls[call_sid]
        
        try:
            async for audio_chunk in agent.get_response_stream():
                if audio_chunk:
                    await self.stream_manager.send_audio(call_sid, audio_chunk)
                    
        except Exception as e:
            logger.error(f"Error streaming response: {str(e)}")