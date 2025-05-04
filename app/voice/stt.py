"""
Speech-to-Text module for the Voice AI Restaurant Agent.

This module handles transcription of audio files.
"""
import logging
import asyncio
import os
import httpx
from typing import Optional
import tempfile
import io

from app.config import settings

logger = logging.getLogger(__name__)

async def transcribe_audio(audio_url: str) -> str:
    """
    Transcribe audio from a URL.
    
    Args:
        audio_url: URL to the audio file
        
    Returns:
        Transcribed text
    """
    logger.info(f"Transcribing audio from URL: {audio_url}")
    
    # In development/testing mode with no API keys, use mock transcriptions
    if settings.DEBUG or not settings.OPENAI_API_KEY:
        logger.info("Using mock transcription in development mode")
        return _get_mock_transcription(audio_url)
    
    try:
        # Download the audio file
        async with httpx.AsyncClient() as client:
            response = await client.get(audio_url)
            response.raise_for_status()
            audio_data = response.content
        
        # In a real implementation, we would use a speech-to-text service
        # For example, with OpenAI's Whisper API
        return await _transcribe_with_openai(audio_data)
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        return "I couldn't understand what was said."

async def _transcribe_with_openai(audio_data: bytes) -> str:
    """
    Transcribe audio using OpenAI's Whisper API.
    
    Args:
        audio_data: Audio file data
        
    Returns:
        Transcribed text
    """
    try:
        import openai
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Save audio data to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name
        
        try:
            # Transcribe with Whisper
            with open(temp_file_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-1"
                )
            
            return transcript.text
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
    except ImportError:
        logger.warning("OpenAI package not installed or misconfigured, using mock transcription")
        return _get_mock_transcription("")
    except Exception as e:
        logger.error(f"Error with OpenAI transcription: {str(e)}")
        return "I couldn't understand what was said."

def _get_mock_transcription(audio_url: str) -> str:
    """
    Generate a mock transcription for testing purposes.
    
    Args:
        audio_url: URL to the audio file (used to determine mock response)
        
    Returns:
        Mock transcribed text
    """
    # Extract keywords from the URL to generate relevant mock responses
    url_lower = audio_url.lower()
    
    # Menu-related queries
    if "menu" in url_lower:
        return "What's on your menu?"
    elif "special" in url_lower:
        return "Do you have any specials today?"
    
    # Reservation-related queries
    elif "reservation" in url_lower or "book" in url_lower or "table" in url_lower:
        return "I'd like to make a reservation for 4 people tomorrow at 7pm."
    
    # Dietary restriction queries
    elif "vegetarian" in url_lower:
        return "Do you have vegetarian options?"
    elif "vegan" in url_lower:
        return "I'm looking for vegan dishes."
    elif "gluten" in url_lower:
        return "Do you have gluten-free options?"
    
    # Food-related queries
    elif "chicken" in url_lower:
        return "Do you have any chicken dishes?"
    elif "spicy" in url_lower:
        return "How spicy is your food?"
    
    # Restaurant information queries
    elif "hour" in url_lower or "open" in url_lower:
        return "What are your opening hours?"
    elif "location" in url_lower or "address" in url_lower:
        return "Where are you located?"
    elif "parking" in url_lower:
        return "Do you have parking available?"
    
    # Farewell
    elif "bye" in url_lower or "thank" in url_lower or "goodbye" in url_lower:
        return "Thank you, goodbye!"
    
    # Default greeting
    else:
        return "Hello, I'm interested in learning more about your restaurant."