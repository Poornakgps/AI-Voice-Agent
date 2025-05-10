import asyncio
import logging
import time
import uuid
from typing import Dict, List, Any, Optional, AsyncGenerator
import json
from pathlib import Path
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
            logger.info(f"Starting response generation using client type: {type(self.openai_client).__name__}")
            
            # Ensure transcript directory exists
            transcript_dir = Path("storage/transcripts")
            transcript_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate streaming response
            logger.info(f"Creating OpenAI chat completion with {len(self.messages)} messages")
            try:
                stream = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=self.messages,
                    stream=True
                )
                logger.info("Successfully created completion stream")
                
                full_response = ""
                chunk_text = ""
                
                logger.info("Processing response stream")
                for chunk in stream:
                    if self.should_interrupt:
                        logger.info("Response interrupted by user")
                        break
                    
                    # Extract content from chunk
                    if hasattr(chunk.choices[0], 'delta') and chunk.choices[0].delta.content:
                        delta_content = chunk.choices[0].delta.content
                        chunk_text += delta_content
                        logger.debug(f"Received chunk: {delta_content}")
                        
                        # Process in sentence-sized chunks for more natural TTS
                        if any(punct in chunk_text for punct in ['.', '?', '!']):
                            full_response += chunk_text
                            logger.info(f"Processing sentence: {chunk_text}")
                            
                            # Save partial transcript
                            with open(f"storage/transcripts/{self.conversation_id}_partial.txt", "a") as f:
                                f.write(f"AI: {chunk_text}\n")
                            
                            # Generate audio for this chunk
                            audio_chunks = await synthesize_speech_stream(chunk_text, self.openai_client)
                            logger.info(f"Generated {len(audio_chunks)} audio chunks")
                            
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
                    logger.info(f"Processing final chunk: {chunk_text}")
                    
                    # Save final part to transcript
                    with open(f"storage/transcripts/{self.conversation_id}_partial.txt", "a") as f:
                        f.write(f"AI: {chunk_text}\n")
                    
                    audio_chunks = await synthesize_speech_stream(chunk_text, self.openai_client)
                    logger.info(f"Generated {len(audio_chunks)} final audio chunks")
                    for audio_chunk in audio_chunks:
                        await self.response_queue.put(audio_chunk)
                
                # Add assistant message to history and save complete transcript
                if full_response:
                    self.messages.append({"role": "assistant", "content": full_response})
                    logger.info(f"Added response to conversation history: {full_response[:50]}...")
                    
                    # Save complete transcript
                    with open(f"storage/transcripts/{self.conversation_id}.txt", "a") as f:
                        f.write(f"User: {self.partial_transcript}\n")
                        f.write(f"AI: {full_response}\n\n")
                
                # Signal end of response
                logger.info("Response generation complete")
                await self.response_queue.put(None)
                
            except Exception as e:
                logger.error(f"OpenAI API error: {str(e)}", exc_info=True)
                # Fall back to a simple response for testing
                mock_text = "I'm having trouble connecting to the language model. Please try again."
                logger.info(f"Using fallback response: {mock_text}")
                
                # Save error transcript
                with open(f"storage/transcripts/{self.conversation_id}_error.txt", "a") as f:
                    f.write(f"User: {self.partial_transcript}\n")
                    f.write(f"AI ERROR: {str(e)}\n")
                    f.write(f"AI FALLBACK: {mock_text}\n\n")
                
                audio_chunks = await synthesize_speech_stream(mock_text, None)
                logger.info(f"Generated {len(audio_chunks)} fallback audio chunks")
                for chunk in audio_chunks:
                    await self.response_queue.put(chunk)
                await self.response_queue.put(None)
                
        except Exception as e:
            logger.error(f"Error in response generation: {str(e)}", exc_info=True)
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
        
    # async def process_audio(self, audio_data: bytes) -> str:
    #     """Process audio input and generate a response."""
    #     # Transcribe audio
    #     transcript = await transcribe_audio_stream(audio_data, self.openai_client)
        
    #     if transcript:
    #         logger.info(f"Transcribed: {transcript}")
    #         self.partial_transcript = transcript
            
    #         # Save transcript
    #         transcript_dir = Path("storage/transcripts")
    #         transcript_dir.mkdir(parents=True, exist_ok=True)
    #         with open(f"storage/transcripts/{self.conversation_id}.txt", "a") as f:
    #             f.write(f"User: {transcript}\n")
            
    #         # Add user message
    #         self.messages.append({"role": "user", "content": transcript})
            
    #         # Generate response
    #         logger.info("Starting response generation")
    #         asyncio.create_task(self._generate_response())
            
    #     return transcript
    
    async def stream_response(self, text: str):
        """Stream a text response to audio."""
        if not text:
            return
            
        logger.info(f"Streaming response: {text[:50]}...")
        self.messages.append({"role": "assistant", "content": text})
        
        # Generate audio chunks
        audio_chunks = await synthesize_speech_stream(text, self.openai_client)
        
        # Queue chunks for sending
        for chunk in audio_chunks:
            await self.response_queue.put(chunk)
        
        # Signal end of response
        await self.response_queue.put(None)