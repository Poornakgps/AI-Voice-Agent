"""
Streaming agent for real-time voice interactions.
"""
import asyncio
import logging
import time
import uuid
from typing import Dict, List, Any, Optional, AsyncGenerator
import json
import openai
from sqlalchemy.orm import Session

from app.config import settings
from app.core.prompt_manager import PromptManager
from app.voice.stt import transcribe_audio_stream
from app.voice.tts import synthesize_speech_stream

logger = logging.getLogger(__name__)

class StreamingAgent:
    """Agent for streaming voice interactions."""
    
    def __init__(self, db_session: Session):
        """
        Initialize the streaming agent.
        
        Args:
            db_session: Database session
        """
        self.db_session = db_session
        self.prompt_manager = PromptManager()
        
        # Streaming state
        self.conversation_id = f"conv_{uuid.uuid4().hex}"
        self.is_speaking = False
        self.should_interrupt = False
        self.partial_transcript = ""
        self.response_queue = asyncio.Queue()
        
        # OpenAI client
        self.openai_client = self._initialize_openai()
        
        # System prompt
        self.messages = [
            {"role": "system", "content": self.prompt_manager.get_system_prompt()}
        ]
        
        logger.info(f"Streaming agent initialized with conversation ID: {self.conversation_id}")
    
    def _initialize_openai(self):
        """Initialize OpenAI client."""
        if not settings.OPENAI_API_KEY:
            logger.warning("No OpenAI API key found, using mock client")
            from tests.mocks.mock_openai import MockOpenAIClient
            return MockOpenAIClient()
        
        client_params = {"api_key": settings.OPENAI_API_KEY}
        if settings.OPENAIORG_ID:
            client_params["organization"] = settings.OPENAIORG_ID
        
        return openai.OpenAI(**client_params)
    
    async def process_audio(self, audio_data: bytes) -> str:
        """
        Process audio input and generate a response.
        
        Args:
            audio_data: Raw audio data
        
        Returns:
            Transcribed text
        """
        # Transcribe audio
        transcript = await transcribe_audio_stream(audio_data, self.openai_client)
        
        if transcript:
            logger.info(f"Transcribed: {transcript}")
            self.partial_transcript = transcript
            
            # Add user message
            self.messages.append({"role": "user", "content": transcript})
            
            # Generate response (stream to queue)
            asyncio.create_task(self._generate_response())
        
        return transcript
    
    async def _generate_response(self):
        """Generate streaming response from OpenAI and convert to audio."""
        try:
            self.is_speaking = True
            
            # Generate streaming response
            stream = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.messages,
                stream=True
            )
            
            full_response = ""
            chunk_text = ""
            
            for chunk in stream:
                if self.should_interrupt:
                    logger.info("Response interrupted by user")
                    break
                
                # Extract content from chunk
                if hasattr(chunk.choices[0], 'delta') and chunk.choices[0].delta.content:
                    chunk_text += chunk.choices[0].delta.content
                    
                    # Process in sentence-sized chunks for more natural TTS
                    if '.' in chunk_text or '?' in chunk_text or '!' in chunk_text:
                        full_response += chunk_text
                        
                        # Generate audio for this chunk
                        audio_chunks = await synthesize_speech_stream(chunk_text, self.openai_client)
                        
                        # Queue audio chunks for sending
                        for audio_chunk in audio_chunks:
                            if self.should_interrupt:
                                break
                            await self.response_queue.put(audio_chunk)
                        
                        # Reset chunk text
                        chunk_text = ""
            
            # Process any remaining text
            if chunk_text and not self.should_interrupt:
                full_response += chunk_text
                audio_chunks = await synthesize_speech_stream(chunk_text, self.openai_client)
                for audio_chunk in audio_chunks:
                    await self.response_queue.put(audio_chunk)
            
            # Add assistant message to history
            if full_response:
                self.messages.append({"role": "assistant", "content": full_response})
            
            # Signal end of response
            await self.response_queue.put(None)
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            await self.response_queue.put(None)
        
        finally:
            self.is_speaking = False
            self.should_interrupt = False
    
    async def get_response_stream(self) -> AsyncGenerator[bytes, None]:
        """
        Get streaming audio response.
        
        Yields:
            Audio chunks
        """
        while True:
            chunk = await self.response_queue.get()
            
            if chunk is None:
                break
            
            yield chunk
    
    async def handle_interruption(self):
        """Handle user interruption."""
        if self.is_speaking:
            logger.info("Interruption handling triggered")
            self.should_interrupt = True
    
    async def close(self):
        """Clean up resources."""
        # Add sentinel to ensure consumers exit
        await self.response_queue.put(None)