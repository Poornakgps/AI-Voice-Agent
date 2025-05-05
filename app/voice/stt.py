"""
Speech-to-Text module with OpenAI Whisper API integration.
"""
import logging
import os
import httpx
import tempfile
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)

async def transcribe_audio(audio_url: str) -> str:
    """Transcribe audio from a URL using OpenAI Whisper API."""
    logger.info(f"Transcribing audio from URL: {audio_url}")
    
    # Use OpenAI API if key is available
    if settings.OPENAI_API_KEY:
        try:
            # Download the audio file
            audio_data = await _download_audio(audio_url)
            if not audio_data:
                logger.error(f"Failed to download audio from {audio_url}")
                return _get_mock_transcription(audio_url)
            
            # Transcribe with OpenAI Whisper
            return await _transcribe_with_openai(audio_data)
        except Exception as e:
            logger.error(f"Error transcribing with OpenAI: {str(e)}")
            logger.info("Falling back to mock transcription")
    else:
        logger.info("No OpenAI API key, using mock transcription")
    
    return _get_mock_transcription(audio_url)

async def _download_audio(audio_url: str) -> Optional[bytes]:
    """Download audio file from a URL."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(audio_url, timeout=10.0)
            response.raise_for_status()
            return response.content
    except Exception as e:
        logger.error(f"Error downloading audio: {str(e)}")
        return None

async def _transcribe_with_openai(audio_data: bytes) -> str:
    """Transcribe audio using OpenAI's Whisper API."""
    import openai
    
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        temp_file.write(audio_data)
        temp_file_path = temp_file.name
    
    try:
        # Transcribe with Whisper
        with open(temp_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        return transcript.text
    finally:
        # Clean up temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def _get_mock_transcription(audio_url: str) -> str:
    """Generate a mock transcription based on the URL."""
    url_lower = audio_url.lower()
    
    # Basic pattern matching for common restaurant queries
    if "menu" in url_lower:
        return "What's on your menu?"
    elif "special" in url_lower:
        return "Do you have any specials today?"
    elif "reservation" in url_lower or "book" in url_lower:
        return "I'd like to make a reservation for 4 people tomorrow at 7pm."
    elif "vegetarian" in url_lower:
        return "Do you have vegetarian options?"
    elif "vegan" in url_lower:
        return "I'm looking for vegan dishes."
    elif "gluten" in url_lower:
        return "Do you have gluten-free options?"
    elif "chicken" in url_lower:
        return "Do you have any chicken dishes?"
    elif "spicy" in url_lower:
        return "How spicy is your food?"
    elif "hour" in url_lower or "open" in url_lower:
        return "What are your opening hours?"
    elif "location" in url_lower or "address" in url_lower:
        return "Where are you located?"
    elif "bye" in url_lower or "thank" in url_lower:
        return "Thank you, goodbye!"
    else:
        return "Hello, I'm interested in learning more about your restaurant."