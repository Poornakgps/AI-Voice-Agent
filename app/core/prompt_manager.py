"""
Prompt management module for the Voice AI Restaurant Agent.

This module handles the generation and management of prompts for the OpenAI Agent.
"""
import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.config import settings

logger = logging.getLogger(__name__)

class PromptManager:
    """Manager for agent prompts and templates."""
    
    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize the prompt manager.
        
        Args:
            template_dir: Directory containing prompt templates
        """
        if template_dir is None:
            current_dir = Path(__file__).parent
            template_dir = str(current_dir / "templates")
        
        self.template_dir = template_dir
        
        try:
            self.env = Environment(
                loader=FileSystemLoader(self.template_dir),
                autoescape=select_autoescape(['html', 'xml'])
            )
            logger.info(f"Initialized prompt manager with templates from {self.template_dir}")
        except Exception as e:
            logger.warning(f"Could not initialize templates from {self.template_dir}: {str(e)}")
            logger.warning("Using built-in default templates instead")
            self.env = None
    
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for the agent.
        
        Returns:
            System prompt text
        """
        if self.env:
            try:
                template = self.env.get_template("system_prompt.j2")
                return template.render(
                    restaurant_name="Taste of India",
                    opening_hours="11:00 AM to 10:00 PM",
                    restaurant_type="Modern Indian Cuisine",
                    restaurant_address="123 Culinary Street, Foodville",
                    restaurant_phone="(555) 123-4567"
                )
            except Exception as e:
                logger.warning(f"Error rendering system prompt template: {str(e)}")
                logger.warning("Using default system prompt")
        
        return self._get_default_system_prompt()
    
    def get_welcome_message(self) -> str:
        """
        Get the welcome message for new calls.
        
        Returns:
            Welcome message text
        """
        if self.env:
            try:
                template = self.env.get_template("welcome_message.j2")
                return template.render(
                    restaurant_name="Taste of India"
                )
            except Exception as e:
                logger.warning(f"Error rendering welcome message template: {str(e)}")
                logger.warning("Using default welcome message")
        
        return self._get_default_welcome_message()
    
    def get_goodbye_message(self) -> str:
        """
        Get the goodbye message for ending calls.
        
        Returns:
            Goodbye message text
        """
        if self.env:
            try:
                template = self.env.get_template("goodbye_message.j2")
                return template.render(
                    restaurant_name="Taste of India"
                )
            except Exception as e:
                logger.warning(f"Error rendering goodbye message template: {str(e)}")
                logger.warning("Using default goodbye message")
        
        return self._get_default_goodbye_message()
    
    def get_fallback_message(self) -> str:
        """
        Get the fallback message for when the agent cannot understand.
        
        Returns:
            Fallback message text
        """
        if self.env:
            try:
                template = self.env.get_template("fallback_message.j2")
                return template.render()
            except Exception as e:
                logger.warning(f"Error rendering fallback message template: {str(e)}")
                logger.warning("Using default fallback message")
        
        return self._get_default_fallback_message()
    
    def _get_default_system_prompt(self) -> str:
        """
        Get the default system prompt.
        
        Returns:
            Default system prompt text
        """
        return """
You are an AI assistant for "Taste of India", a modern Indian restaurant. Your name is Priya.
You are speaking to a customer on the phone. Your job is to assist with menu inquiries,
pricing information, making reservations, modifying existing reservations, and answering
general questions about the restaurant.

Restaurant Details:
- Name: Taste of India
- Type: Modern Indian Cuisine
- Address: 123 Culinary Street, Foodville
- Phone: (555) 123-4567
- Hours: Open daily from 11:00 AM to 10:00 PM

Important Guidelines:
1. Be warm, friendly, and helpful.
2. Keep responses concise and natural for a phone conversation.
3. If you don't know something, politely say so and offer to find out.
4. Use tools to look up menu items, prices, and reservation availability.
5. When taking reservations, collect the necessary information: name, phone number,
   date, time, party size, and any special requests.
6. Speak naturally as if you were having a real phone conversation.
7. Remember that the customer cannot see you, so describe things clearly.

When you need to access information or perform actions, use the available tools.
"""
    
    def _get_default_welcome_message(self) -> str:
        """
        Get the default welcome message.
        
        Returns:
            Default welcome message text
        """
        return "Thank you for calling Taste of India. This is Priya. How may I assist you today?"
    
    def _get_default_goodbye_message(self) -> str:
        """
        Get the default goodbye message.
        
        Returns:
            Default goodbye message text
        """
        return "Thank you for calling Taste of India. We look forward to serving you soon. Goodbye!"
    
    def _get_default_fallback_message(self) -> str:
        """
        Get the default fallback message.
        
        Returns:
            Default fallback message text
        """
        return "I'm sorry, I didn't quite catch that. Could you please repeat your question?"