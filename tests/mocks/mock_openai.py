import logging
import json
import re
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)

class MockResponse:
    """Mock response for API calls."""
    def __init__(self, content: Dict[str, Any]):
        self.content = content
        self.id = "mock-response-" + datetime.now().strftime("%Y%m%d%H%M%S")
        self.choices = [MockChoice(self.content)]

class MockChoice:
    """Mock choice for API responses."""
    def __init__(self, content: Dict[str, Any]):
        self.message = MockMessage(content)
        self.index = 0
        self.finish_reason = "stop"

class MockMessage:
    """Mock message for API responses."""
    def __init__(self, content: Dict[str, Any]):
        self.content = content.get("content", "")
        self.role = content.get("role", "assistant")
        self.tool_calls = []
        
        if "tool_call" in content:
            self.tool_calls = [MockToolCall(content["tool_call"])]

class MockToolCall:
    """Mock tool call for API responses."""
    def __init__(self, tool_call: Dict[str, Any]):
        self.id = "mock-tool-call-" + datetime.now().strftime("%Y%m%d%H%M%S")
        self.type = "function"
        self.function = MockFunction(tool_call)

class MockFunction:
    """Mock function for API responses."""
    def __init__(self, tool_call: Dict[str, Any]):
        self.name = tool_call.get("name", "")
        self.arguments = json.dumps(tool_call.get("arguments", {}))

class MockChatCompletions:
    """Mock chat completions API."""
    
    def create(
        self, 
        model: str, 
        messages: List[Dict[str, str]], 
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None
    ) -> MockResponse:
        """
        Mock implementation of the chat completions API.
        
        Args:
            model: Model name
            messages: List of message dictionaries
            tools: List of tool definitions
            tool_choice: Tool choice strategy
            
        Returns:
            Mock response
        """
        logger.info(f"Mock ChatCompletions.create called with {len(messages)} messages")
        
        user_message = next((m for m in reversed(messages) if m.get("role") == "user"), None)
        
        if not user_message:
            return MockResponse({"content": "I'm not sure how to respond without a user message."})
        
        user_text = user_message.get("content", "").lower()
        
        result = self._handle_tool_calls(user_text, tools)
        if result:
            return result
        
        response_content = self._get_canned_response(user_text)
        
        return MockResponse({"content": response_content})
    
    def _handle_tool_calls(
        self, 
        user_text: str, 
        tools: Optional[List[Dict[str, Any]]]
    ) -> Optional[MockResponse]:
        """
        Handle potential tool calls based on user text.
        
        Args:
            user_text: User message text
            tools: Available tools
            
        Returns:
            Mock response with tool call or None
        """
        if not tools:
            return None
        
        if re.search(r'menu|categories|what (do you|you guys) (have|offer)|what.s on the menu', user_text):
            return MockResponse({
                "content": "Let me check our menu categories for you.",
                "tool_call": {
                    "name": "get_menu_categories",
                    "arguments": {}
                }
            })
        
        category_match = re.search(r'(what|any|show).*(starters|appetizers|main course|desserts|drinks)', user_text)
        if category_match:
            category = category_match.group(2).lower()
            category_id_map = {
                "starters": 1, 
                "appetizers": 1, 
                "main course": 2, 
                "desserts": 5,
                "drinks": 6
            }
            category_id = category_id_map.get(category, 1)
            
            return MockResponse({
                "content": f"Let me check our {category} for you.",
                "tool_call": {
                    "name": "get_menu_items_by_category",
                    "arguments": {"category_id": category_id}
                }
            })
        
        diet_match = re.search(r'(vegetarian|vegan|gluten.free|dairy.free|nut.free|halal|kosher)', user_text)
        if diet_match:
            diet_type = diet_match.group(1).lower().replace(" ", "_")
            
            return MockResponse({
                "content": f"Let me find {diet_type} options for you.",
                "tool_call": {
                    "name": "get_menu_items_by_dietary_restriction",
                    "arguments": {"restriction_type": diet_type}
                }
            })
        
        search_match = re.search(r'(do you have|is there|looking for|want|i.d like) .*?(chicken|curry|paneer|biryani|naan|tandoori|tikka)', user_text)
        if search_match:
            search_term = search_match.group(2)
            
            return MockResponse({
                "content": f"Let me search for {search_term} in our menu.",
                "tool_call": {
                    "name": "search_menu_items",
                    "arguments": {"query": search_term}
                }
            })
        
        if re.search(r'special|offer|discount|deal|promotion', user_text):
            return MockResponse({
                "content": "Let me check our current specials for you.",
                "tool_call": {
                    "name": "get_special_pricing",
                    "arguments": {}
                }
            })
        
        reservation_match = re.search(r'(book|reserve|reservation).*(table|spot|seat|reservation).*?(\d+).*?(people|person|guests?)', user_text)
        if reservation_match:
            party_size = int(reservation_match.group(3))
            
            tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = tomorrow.replace(day=tomorrow.day + 1)
            date_str = tomorrow.strftime("%Y-%m-%d")
            
            date_match = re.search(r'(today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday)', user_text)
            if date_match:
                pass
            
            time_str = "19:00"
            time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)', user_text, re.IGNORECASE)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2) or "0")
                ampm = time_match.group(3).lower()
                
                if ampm == "pm" and hour < 12:
                    hour += 12
                elif ampm == "am" and hour == 12:
                    hour = 0
                
                time_str = f"{hour:02d}:{minute:02d}"
            
            return MockResponse({
                "content": f"Let me check if we have availability for {party_size} people.",
                "tool_call": {
                    "name": "check_reservation_availability",
                    "arguments": {
                        "date": date_str,
                        "time": time_str,
                        "party_size": party_size
                    }
                }
            })
        
        return None
    
    def _get_canned_response(self, user_text: str) -> str:
        """
        Get a canned response based on user text.
        
        Args:
            user_text: User message text
            
        Returns:
            Canned response text
        """
        if re.search(r'^(hi|hello|hey|greetings|howdy)', user_text):
            return "Hello! Thank you for calling Taste of India. How can I assist you today?"
        
        if re.search(r'(hour|time|when).*(open|close|opening|closing)', user_text):
            return "We're open daily from 11:00 AM to 10:00 PM."
        
        if re.search(r'(where|location|address|direction)', user_text):
            return "We're located at 123 Culinary Street in Foodville. We're just across from Central Park, near the downtown shopping district."
        
        if re.search(r'parking', user_text):
            return "Yes, we have a parking lot behind our restaurant with free parking for customers. There's also street parking available."
        
        if re.search(r'(takeout|take.out|take.away|delivery|pick.up)', user_text):
            return "Yes, we offer both takeout and delivery services. You can place an order by phone or through our website. Delivery is available within a 5-mile radius."
        
        if re.search(r'(popular|best|recommend|signature|specialty)', user_text):
            return "Our most popular dishes include Butter Chicken, Paneer Tikka, and our special Vegetable Biryani. Our Chef's Special changes weekly, so be sure to ask about it when you visit!"
        
        if re.search(r'(spicy|spice|hot|mild|medium)', user_text):
            return "We can adjust the spice level of most dishes to your preference, from mild to very spicy. Just let us know your preference when ordering."
        
        return "Thank you for your question. As an AI assistant for Taste of India, I'm here to help with menu information, reservations, and general restaurant questions. How else can I assist you today?"

class MockOpenAIClient:
    """Mock implementation of the OpenAI client."""
    
    def __init__(self):
        """Initialize the mock client."""
        self.chat = MockChat()
        logger.info("Initialized MockOpenAIClient")

class MockChat:
    """Mock chat API."""
    
    def __init__(self):
        """Initialize the mock chat API."""
        self.completions = MockChatCompletions()