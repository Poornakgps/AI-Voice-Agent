"""
Audio streaming module for bidirectional voice communication.
"""
import asyncio
import logging
import time
from typing import Dict, List, Optional, Callable, Any, AsyncGenerator
import numpy as np
from fastapi import WebSocket, WebSocketDisconnect

from app.voice.vad import InterruptionDetector

logger = logging.getLogger(__name__)

class AudioBuffer:
    """Buffer for audio streaming."""
    
    def __init__(self, max_size: int = 10):
        """
        Initialize the audio buffer.
        
        Args:
            max_size: Maximum buffer size in seconds
        """
        self.buffer: List[bytes] = []
        self.max_size = max_size
        self.current_size = 0
    
    def add(self, chunk: bytes):
        """Add audio chunk to buffer."""
        self.buffer.append(chunk)
        self.current_size += len(chunk)
        
        # Trim buffer if it gets too large
        while self.current_size > self.max_size and self.buffer:
            removed = self.buffer.pop(0)
            self.current_size -= len(removed)
    
    def get_all(self) -> bytes:
        """Get all audio data from buffer and clear it."""
        if not self.buffer:
            return b''
        
        result = b''.join(self.buffer)
        self.buffer = []
        self.current_size = 0
        return result
    
    def clear(self):
        """Clear the buffer."""
        self.buffer = []
        self.current_size = 0

class StreamManager:
    """Manager for audio streaming connections."""
    
    def __init__(self):
        """Initialize the stream manager."""
        self.active_connections: Dict[str, WebSocket] = {}
        self.interrupt_handlers: Dict[str, Callable] = {}
        self.vad_detectors: Dict[str, InterruptionDetector] = {}
        self.input_buffers: Dict[str, AudioBuffer] = {}
        self.last_activity: Dict[str, float] = {}
        
        logger.info("StreamManager initialized")
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """
        Accept websocket connection and set up streaming.
        
        Args:
            websocket: WebSocket connection
            client_id: Unique client identifier
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.vad_detectors[client_id] = InterruptionDetector()
        self.input_buffers[client_id] = AudioBuffer()
        self.last_activity[client_id] = time.time()
        
        logger.info(f"Client {client_id} connected")
        
        # Send initial configuration to client
        await websocket.send_json({
            "event": "connected",
            "config": {
                "sample_rate": 16000,
                "channels": 1,
                "frame_size": 480  # 30ms at 16kHz
            }
        })
    
    def disconnect(self, client_id: str):
        """
        Clean up resources when client disconnects.
        
        Args:
            client_id: Client identifier
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        
        if client_id in self.vad_detectors:
            del self.vad_detectors[client_id]
        
        if client_id in self.input_buffers:
            del self.input_buffers[client_id]
        
        if client_id in self.last_activity:
            del self.last_activity[client_id]
        
        if client_id in self.interrupt_handlers:
            del self.interrupt_handlers[client_id]
        
        logger.info(f"Client {client_id} disconnected")
    
    async def receive_audio(self, client_id: str, audio_data: bytes):
        """
        Process incoming audio from client.
        
        Args:
            client_id: Client identifier
            audio_data: Raw audio data
        """
        if client_id not in self.active_connections:
            logger.warning(f"Received audio from unknown client: {client_id}")
            return
        
        self.last_activity[client_id] = time.time()
        
        # Add to buffer
        self.input_buffers[client_id].add(audio_data)
        
        # Process with VAD for interruption detection
        if client_id in self.vad_detectors:
            is_speech, is_interruption = self.vad_detectors[client_id].process_frame(audio_data)
            
            if is_interruption and client_id in self.interrupt_handlers:
                logger.info(f"Interruption detected for client {client_id}")
                handler = self.interrupt_handlers[client_id]
                asyncio.create_task(handler(client_id))
    
    async def send_audio(self, client_id: str, audio_data: bytes):
        """
        Send audio to client.
        
        Args:
            client_id: Client identifier
            audio_data: Raw audio data
        """
        if client_id not in self.active_connections:
            logger.warning(f"Cannot send audio to unknown client: {client_id}")
            return
        
        websocket = self.active_connections[client_id]
        try:
            await websocket.send_bytes(audio_data)
            self.last_activity[client_id] = time.time()
        except WebSocketDisconnect:
            logger.info(f"Client {client_id} disconnected during send")
            self.disconnect(client_id)
        except Exception as e:
            logger.error(f"Error sending audio to {client_id}: {str(e)}")
    
    def register_interrupt_handler(self, client_id: str, handler: Callable):
        """
        Register handler for interruptions.
        
        Args:
            client_id: Client identifier
            handler: Async callback function to handle interruption
        """
        self.interrupt_handlers[client_id] = handler
        
    def get_input_buffer(self, client_id: str) -> Optional[AudioBuffer]:
        """
        Get the input buffer for a client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            AudioBuffer or None if client not found
        """
        return self.input_buffers.get(client_id)
    
    async def cleanup_inactive(self, timeout_seconds: int = 300):
        """
        Clean up inactive connections.
        
        Args:
            timeout_seconds: Inactivity timeout in seconds
        """
        now = time.time()
        inactive = [
            client_id for client_id, last_time in self.last_activity.items()
            if now - last_time > timeout_seconds
        ]
        
        for client_id in inactive:
            logger.info(f"Cleaning up inactive client: {client_id}")
            if client_id in self.active_connections:
                try:
                    await self.active_connections[client_id].close()
                except Exception:
                    pass
            self.disconnect(client_id)