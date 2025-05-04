"""
TwiML response generator for the Voice AI Restaurant Agent.

This module generates TwiML responses for Twilio webhook endpoints.
"""
import logging
from typing import Optional, Dict, Any
from app.core.prompt_manager import PromptManager

logger = logging.getLogger(__name__)

class TwiMLGenerator:
    """Generator for TwiML responses."""
    
    def __init__(self):
        """Initialize the TwiML generator."""
        self.prompt_manager = PromptManager()
        logger.info("TwiML generator initialized")
    
    def welcome_response(self) -> str:
        """
        Generate TwiML for the welcome response.
        
        Returns:
            TwiML response string
        """
        welcome_message = self.prompt_manager.get_welcome_message()
        
        twiml = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="Polly.Joanna-Neural">{welcome_message}</Say>
            <Record action="/webhook/transcribe" maxLength="60" playBeep="true" />
        </Response>
        """
        
        return twiml.strip()
    
    def agent_response(self, message: str) -> str:
        """
        Generate TwiML for an agent response.
        
        Args:
            message: Agent response message
            
        Returns:
            TwiML response string
        """
        # Clean up the message for TTS
        clean_message = self._clean_message_for_tts(message)
        
        twiml = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="Polly.Joanna-Neural">{clean_message}</Say>
            <Record action="/webhook/transcribe" maxLength="60" playBeep="true" />
        </Response>
        """
        
        return twiml.strip()
    
    def goodbye_response(self) -> str:
        """
        Generate TwiML for the goodbye response.
        
        Returns:
            TwiML response string
        """
        goodbye_message = self.prompt_manager.get_goodbye_message()
        
        twiml = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="Polly.Joanna-Neural">{goodbye_message}</Say>
            <Hangup />
        </Response>
        """
        
        return twiml.strip()
    
    def error_response(self, error_message: Optional[str] = None) -> str:
        """
        Generate TwiML for an error response.
        
        Args:
            error_message: Optional custom error message
            
        Returns:
            TwiML response string
        """
        message = error_message or "I'm sorry, we're experiencing technical difficulties. Please try again later."
        
        twiml = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="Polly.Joanna-Neural">{message}</Say>
            <Hangup />
        </Response>
        """
        
        return twiml.strip()
    
    def fallback_response(self) -> str:
        """
        Generate TwiML for a fallback response.
        
        Returns:
            TwiML response string
        """
        fallback_message = self.prompt_manager.get_fallback_message()
        
        twiml = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="Polly.Joanna-Neural">{fallback_message}</Say>
            <Record action="/webhook/transcribe" maxLength="60" playBeep="true" />
        </Response>
        """
        
        return twiml.strip()
    
    def gather_digits_response(self, message: str, num_digits: int = 1, finish_on_key: str = "#") -> str:
        """
        Generate TwiML to gather DTMF input.
        
        Args:
            message: Prompt message
            num_digits: Number of digits to gather
            finish_on_key: Key to finish input
            
        Returns:
            TwiML response string
        """
        twiml = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Gather numDigits="{num_digits}" finishOnKey="{finish_on_key}" action="/webhook/dtmf" method="POST">
                <Say voice="Polly.Joanna-Neural">{message}</Say>
            </Gather>
            <Say voice="Polly.Joanna-Neural">We didn't receive any input. Goodbye!</Say>
            <Hangup />
        </Response>
        """
        
        return twiml.strip()
    
    def _clean_message_for_tts(self, message: str) -> str:
        """
        Clean up a message for text-to-speech.
        
        Args:
            message: Input message
            
        Returns:
            Cleaned message
        """
        # Replace any characters that might cause issues with TTS
        message = message.replace("&", "and")
        
        # Remove markdown formatting
        message = message.replace("*", "")
        message = message.replace("_", "")
        message = message.replace("#", "")
        message = message.replace("`", "")
        
        # Remove excessive whitespace
        message = " ".join(message.split())
        
        return message