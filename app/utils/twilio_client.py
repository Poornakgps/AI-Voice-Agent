"""
Twilio client utilities for Voice AI Restaurant Agent.
"""
import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException, TwilioException
from app.config import settings

logger = logging.getLogger(__name__)

def create_twilio_client():
    """
    Create a properly configured Twilio client.
    
    Returns:
        Client: Configured Twilio client instance or None if configuration is missing
    """
    # Check for required configuration
    if not settings.TWILIO_API_KEY or not settings.TWILIO_API_SECRET:
        logger.warning("Missing Twilio API credentials")
        return None
    
    try:
        # Create client with API key authentication
        client = Client(settings.TWILIO_API_KEY, settings.TWILIO_API_SECRET)
        logger.info("Successfully initialized Twilio client")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Twilio client: {str(e)}")
        return None

def send_sms(to_number, from_number, message):
    """
    Send an SMS message using Twilio.
    
    Args:
        to_number: Recipient phone number
        from_number: Sender phone number
        message: Message text
        
    Returns:
        dict: Message details if successful, error details if failed
    """
    client = create_twilio_client()
    if not client:
        return {"status": "error", "message": "Twilio client initialization failed"}
    
    try:
        # Send the message
        message = client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
        
        return {
            "status": "success", 
            "message_sid": message.sid,
            "date_sent": message.date_sent
        }
    except (TwilioRestException, TwilioException) as e:
        return {
            "status": "error",
            "message": str(e),
            "code": getattr(e, "code", None),
            "status_code": getattr(e, "status", None)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }