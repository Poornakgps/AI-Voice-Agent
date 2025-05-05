"""
Text-to-Speech module using OpenAI's TTS API.
"""
import logging
import base64
import tempfile
import os
from typing import Optional

from app.config import settings
from app.core.models import VoiceSettings, TTSResponse

logger = logging.getLogger(__name__)

async def synthesize_speech(text: str, voice_settings: Optional[VoiceSettings] = None) -> TTSResponse:
    """Synthesize speech from text using OpenAI TTS API."""
    logger.info(f"Synthesizing speech: {text[:50]}{'...' if len(text) > 50 else ''}")
    
    # Use OpenAI TTS if API key is available
    if settings.OPENAI_API_KEY:
        try:
            return await _synthesize_with_openai(text, voice_settings)
        except Exception as e:
            logger.error(f"Error with OpenAI TTS: {str(e)}")
            logger.info("Falling back to mock TTS")
    else:
        logger.info("No OpenAI API key, using mock TTS")
    
    # Fall back to mock implementation
    return _get_mock_tts_response(text)

async def _synthesize_with_openai(text: str, voice_settings: Optional[VoiceSettings] = None) -> TTSResponse:
    """Synthesize speech using OpenAI's TTS API."""
    import openai
    
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    # Set voice and model based on settings
    voice = "alloy"  # Default voice
    if voice_settings:
        if "female" in voice_settings.gender.lower():
            voice = "nova"  # Female voice
        else:
            voice = "echo"  # Male voice
    
    # Create a temporary file to store the audio
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        temp_file_path = temp_file.name
    
    try:
        # Generate speech
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        # Save to temporary file
        response.stream_to_file(temp_file_path)
        
        # Read the file and encode to base64
        with open(temp_file_path, "rb") as f:
            audio_content = f.read()
        
        audio_content_base64 = base64.b64encode(audio_content).decode("utf-8")
        
        # Estimate duration (roughly 150 words per minute)
        words = len(text.split())
        duration_seconds = max(1.0, words / 2.5)  # 2.5 words per second
        
        return TTSResponse(
            audio_content_base64=audio_content_base64,
            duration_seconds=duration_seconds,
            content_type="audio/mp3"
        )
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def _get_mock_tts_response(text: str) -> TTSResponse:
    """Generate a mock TTS response using gTTS."""
    try:
        from gtts import gTTS
        import io
        
        # Create gTTS object
        tts = gTTS(text=text, lang='en-us', slow=False)
        
        # Save to a buffer
        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        
        # Get audio content and encode to base64
        audio_content = buffer.getvalue()
        audio_content_base64 = base64.b64encode(audio_content).decode("utf-8")
        
        # Estimate duration based on text length
        duration_seconds = max(1.0, len(text) * 0.07)
        
        return TTSResponse(
            audio_content_base64=audio_content_base64,
            duration_seconds=duration_seconds,
            content_type="audio/mp3"
        )
    except ImportError:
        logger.warning("gTTS not installed, using silent audio")
        # Generate a simple silent MP3
        silent_mp3 = b'\xFF\xF3\x18\xC4\x00\x00\x00\x03H\x00\x00\x00\x00LAME3.100'
        audio_content_base64 = base64.b64encode(silent_mp3).decode("utf-8")
        return TTSResponse(
            audio_content_base64=audio_content_base64,
            duration_seconds=1.0,
            content_type="audio/mp3"
        )