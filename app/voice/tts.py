"""
Text-to-Speech module for the Voice AI Restaurant Agent.

This module handles text-to-speech synthesis.
"""
import logging
import base64
import io
import os
from typing import Optional, Dict, Any, Tuple
import tempfile

from app.config import settings
from app.core.models import VoiceSettings, TTSResponse

logger = logging.getLogger(__name__)

async def synthesize_speech(text: str, voice_settings: Optional[VoiceSettings] = None) -> TTSResponse:
    """Synthesize speech from text."""
    logger.info(f"Synthesizing speech: {text[:50]}{'...' if len(text) > 50 else ''}")
    
    if not settings.GOOGLE_CLOUD_CREDENTIALS:
        logger.warning("No Google Cloud credentials found, using mock TTS")
        return _get_mock_tts_response(text)
    
    try:
        # Use Google Cloud TTS
        return await _synthesize_with_google_cloud(text, voice_settings)
    except Exception as e:
        logger.error(f"Error synthesizing speech: {str(e)}")
        return _get_mock_tts_response("I'm sorry, I encountered an error.")

async def _synthesize_with_google_cloud(text: str, voice_settings: Optional[VoiceSettings] = None) -> TTSResponse:
    """
    Synthesize speech using Google Cloud Text-to-Speech.
    
    Args:
        text: Text to synthesize
        voice_settings: Voice settings
        
    Returns:
        TTSResponse: Synthesized speech
    """
    try:
        from google.cloud import texttospeech
        
        # Create the client
        client = texttospeech.TextToSpeechClient()
        
        # Set the text input
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # Build the voice request
        if voice_settings:
            voice = texttospeech.VoiceSelectionParams(
                language_code=voice_settings.language,
                name=voice_settings.voice_id,
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE if voice_settings.gender == "female" else texttospeech.SsmlVoiceGender.MALE
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=voice_settings.speaking_rate,
                pitch=voice_settings.pitch,
                volume_gain_db=voice_settings.volume_gain_db
            )
        else:
            # Default voice
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name="en-US-Neural2-F",
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
        
        # Perform the synthesis
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        
        # Encode the audio content to base64
        audio_content_base64 = base64.b64encode(response.audio_content).decode("utf-8")
        
        # Estimate duration (rough approximation: 1 second per 15 characters)
        duration_seconds = len(text) / 15
        
        return TTSResponse(
            audio_content_base64=audio_content_base64,
            duration_seconds=duration_seconds,
            content_type="audio/mp3"
        )
        
    except ImportError:
        logger.warning("Google Cloud TTS package not installed, using mock TTS")
        return _get_mock_tts_response(text)

def _get_mock_tts_response(text: str) -> TTSResponse:
    """
    Generate a mock TTS response for testing purposes.
    
    Args:
        text: Text to synthesize
        
    Returns:
        TTSResponse: Mock TTS response
    """
    # For development, we're using a minimal placeholder instead of actual audio data
    # In a real implementation, this would return actual audio data
    
    # Estimate duration (rough approximation: 1 second per 15 characters)
    duration_seconds = len(text) / 15
    
    # Generate a tiny audio file as a placeholder
    audio_content = b'\x00\x01\x02\x03\x04\x05'  # Not real audio data, just a placeholder
    audio_content_base64 = base64.b64encode(audio_content).decode("utf-8")
    
    return TTSResponse(
        audio_content_base64=audio_content_base64,
        duration_seconds=duration_seconds,
        content_type="audio/mp3"
    )