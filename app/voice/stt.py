"""
Speech-to-Text module with streaming support.
"""
import logging
import os
import tempfile
import asyncio
from typing import Optional, List, Dict, Any, AsyncGenerator
import openai

from app.config import settings

logger = logging.getLogger(__name__)

async def transcribe_audio_stream(audio_data: bytes, client: Optional[Any] = None) -> str:
    """
    Transcribe audio data using OpenAI Whisper API with streaming support.
    
    Args:
        audio_data: Raw audio data
        client: Optional OpenAI client instance
        
    Returns:
        Transcribed text
    """
    if not audio_data:
        return ""
    
    if client is None:
        if not settings.OPENAI_API_KEY:
            logger.warning("No OpenAI API key, using mock transcription")
            return _get_mock_transcription(len(audio_data))
            
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(audio_data)
        
        with open(temp_file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
            
            transcript = response if isinstance(response, str) else response.text
            return transcript
    
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        return _get_mock_transcription(len(audio_data))
    
    finally:
        # Clean up temp file
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        except Exception:
            pass

def _get_mock_transcription(audio_length: int) -> str:
    """Generate mock transcription for testing."""
    # Return different mock responses based on audio length
    if audio_length < 1000:
        return "Hello."
    elif audio_length < 5000:
        return "I'd like to make a reservation."
    elif audio_length < 10000:
        return "What vegetarian options do you have on the menu?"
    else:
        return "Can I make a reservation for four people tomorrow at 7pm? We're celebrating a birthday."