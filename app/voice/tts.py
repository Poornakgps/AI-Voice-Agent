"""
Text-to-Speech module with streaming support.
"""
import logging
import base64
import tempfile
import os
import asyncio
from typing import Optional, List, AsyncGenerator, Any
import openai
from app.config import settings

logger = logging.getLogger(__name__)

async def synthesize_speech_stream(
    text: str, 
    client: Optional[Any] = None,
    chunk_size: int = 4096
) -> List[bytes]:
    """
    Synthesize speech from text with streaming support.
    
    Args:
        text: Text to synthesize
        client: Optional OpenAI client instance
        chunk_size: Size of audio chunks to yield
        
    Returns:
        List of audio chunks
    """
    if not text:
        return []
    
    logger.info(f"Synthesizing speech: {text[:50]}{'...' if len(text) > 50 else ''}")
    
    if client is None:
        if not settings.OPENAI_API_KEY:
            logger.info("No OpenAI API key, using mock TTS")
            return _get_mock_tts_chunks(text, chunk_size)
            
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text
        )
        
        response.stream_to_file(temp_file_path)
        
        # Read file in chunks
        chunks = []
        with open(temp_file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                chunks.append(chunk)
        
        return chunks
    
    except Exception as e:
        logger.error(f"Error with OpenAI TTS: {str(e)}")
        logger.info("Falling back to mock TTS")
        return _get_mock_tts_chunks(text, chunk_size)
    
    finally:
        # Clean up temp file
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        except Exception:
            pass

def _get_mock_tts_chunks(text: str, chunk_size: int) -> List[bytes]:
    """Generate mock TTS audio chunks for testing."""
    try:
        from gtts import gTTS
        import io
        
        # Create gTTS object
        tts = gTTS(text=text, lang='en-us', slow=False)
        
        # Save to a buffer
        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        
        # Get audio content
        audio_content = buffer.getvalue()
        
        # Split into chunks
        chunks = []
        for i in range(0, len(audio_content), chunk_size):
            chunks.append(audio_content[i:i + chunk_size])
        
        return chunks
    
    except ImportError:
        logger.warning("gTTS not installed, using silent audio")
        # Generate a simple silent MP3
        silent_mp3 = b'\xFF\xF3\x18\xC4\x00\x00\x00\x03H\x00\x00\x00\x00LAME3.100'
        return [silent_mp3]