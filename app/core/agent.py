"""
Agent orchestration module for the Voice AI Restaurant Agent.

This module handles the main agent logic, conversation management,
and integration with the OpenAI Agent SDK.
"""
import logging
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

# Import mock for development without API keys
from tests.mocks.mock_openai import MockOpenAIClient

from app.config import settings
from app.core.prompt_manager import PromptManager
from app.tools import menu_query, pricing, reservations

logger = logging.getLogger(__name__)

class Message(BaseModel):
    """Model for conversation messages."""
    role: str = Field(..., description="The role of the message sender (user, assistant, system)")
    content: str = Field(..., description="The content of the message")

class Conversation(BaseModel):
    """Model for tracking conversation state."""
    messages: List[Message] = Field(default_factory=list, description="List of messages in the conversation")
    conversation_id: Optional[str] = Field(None, description="Unique identifier for the conversation")
    user_id: Optional[str] = Field(None, description="Identifier for the user")
    
    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the conversation.
        
        Args:
            role: The role of the message sender
            content: The content of the message
        """
        self.messages.append(Message(role=role, content=content))
    
    def get_history(self) -> List[Dict[str, str]]:
        """
        Get the conversation history in the format expected by OpenAI.
        
        Returns:
            List of message dictionaries
        """
        return [msg.dict() for msg in self.messages]
    
    def clear(self) -> None:
        """Clear the conversation history but keep metadata."""
        self.messages = []

class AgentState(BaseModel):
    """Model for tracking agent state."""
    conversation: Conversation = Field(default_factory=Conversation, description="The conversation state")
    current_context: Dict[str, Any] = Field(default_factory=dict, description="Current context information")
    
    def update_context(self, key: str, value: Any) -> None:
        """
        Update a context value.
        
        Args:
            key: Context key
            value: Context value
        """
        self.current_context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """
        Get a context value.
        
        Args:
            key: Context key
            default: Default value if key not found
            
        Returns:
            Context value or default
        """
        return self.current_context.get(key, default)
    
    def clear_context(self) -> None:
        """Clear the current context."""
        self.current_context = {}

class RestaurantAgent:
    """Main agent implementation for the restaurant voice assistant."""
    
    def __init__(self, db_session: Session):
        """
        Initialize the agent.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session
        self.prompt_manager = PromptManager()
        
        # Initialize agent state
        self.state = AgentState()
        
        # Initialize OpenAI client (using mock for now)
        self.client = self._initialize_client()
        
        # Register system prompt
        self._initialize_conversation()
        
        # Define available tools
        self.tools = self._register_tools()
        
        logger.info("Restaurant agent initialized")
    
    def _initialize_client(self):
        """Initialize the OpenAI client."""
        # Use real OpenAI client when API key is available
        if settings.OPENAI_API_KEY:
            import openai
            client = openai.OpenAI(
                api_key=settings.OPENAI_API_KEY,
                organization=settings.OPENAIORG_ID
            )
            logger.info("Using real OpenAI client")
            return client
        else:
            # Fall back to mock for development without API key
            logger.warning("No OpenAI API key found, using mock client")
            return MockOpenAIClient()
    
    def _initialize_conversation(self):
        """Initialize the conversation with system prompt."""
        system_prompt = self.prompt_manager.get_system_prompt()
        self.state.conversation.add_message("system", system_prompt)
    
    def _register_tools(self):
        """
        Register available tools for the agent.
        
        Returns:
            List of tool definitions
        """
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_menu_categories",
                    "description": "Get a list of all menu categories",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_menu_items_by_category",
                    "description": "Get menu items in a specific category",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "category_id": {
                                "type": "integer",
                                "description": "The ID of the category"
                            }
                        },
                        "required": ["category_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_menu_items",
                    "description": "Search for menu items by name",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_menu_items_by_dietary_restriction",
                    "description": "Get menu items with a specific dietary restriction",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "restriction_type": {
                                "type": "string",
                                "description": "The dietary restriction type",
                                "enum": ["vegetarian", "vegan", "gluten_free", "dairy_free", "nut_free", "halal", "kosher"]
                            }
                        },
                        "required": ["restriction_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_item_price",
                    "description": "Get price information for a menu item",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "item_id": {
                                "type": "integer",
                                "description": "The ID of the menu item"
                            }
                        },
                        "required": ["item_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_special_pricing",
                    "description": "Get all active special pricing",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_order_total",
                    "description": "Calculate the total for an order",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "items": {
                                "type": "array",
                                "description": "List of items in the order",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {
                                            "type": "integer",
                                            "description": "The ID of the menu item"
                                        },
                                        "quantity": {
                                            "type": "integer",
                                            "description": "The quantity of the item"
                                        }
                                    },
                                    "required": ["id", "quantity"]
                                }
                            }
                        },
                        "required": ["items"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_reservation_availability",
                    "description": "Check if there is availability for a reservation",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {
                                "type": "string",
                                "description": "The reservation date (YYYY-MM-DD)"
                            },
                            "time": {
                                "type": "string",
                                "description": "The reservation time (HH:MM)"
                            },
                            "party_size": {
                                "type": "integer",
                                "description": "The party size"
                            }
                        },
                        "required": ["date", "time", "party_size"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_reservation",
                    "description": "Create a new reservation",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {
                                "type": "string",
                                "description": "The reservation date (YYYY-MM-DD)"
                            },
                            "time": {
                                "type": "string",
                                "description": "The reservation time (HH:MM)"
                            },
                            "party_size": {
                                "type": "integer",
                                "description": "The party size"
                            },
                            "customer_name": {
                                "type": "string",
                                "description": "The customer name"
                            },
                            "customer_phone": {
                                "type": "string",
                                "description": "The customer phone number"
                            },
                            "customer_email": {
                                "type": "string",
                                "description": "The customer email (optional)"
                            },
                            "special_requests": {
                                "type": "string",
                                "description": "Special requests (optional)"
                            }
                        },
                        "required": ["date", "time", "party_size", "customer_name", "customer_phone"]
                    }
                }
            }
        ]
        
        return tools
    
    def _execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        """
        Execute a tool function.
        
        Args:
            tool_name: The name of the tool
            tool_args: The arguments for the tool
            
        Returns:
            Tool result
        """
        logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
        
        try:
            # Menu query tools
            if tool_name == "get_menu_categories":
                return menu_query.get_menu_categories(self.db_session)
            elif tool_name == "get_menu_items_by_category":
                return menu_query.get_menu_items_by_category(self.db_session, tool_args["category_id"])
            elif tool_name == "search_menu_items":
                return menu_query.search_menu_items(self.db_session, tool_args["query"])
            elif tool_name == "get_menu_items_by_dietary_restriction":
                return menu_query.get_menu_items_by_dietary_restriction(self.db_session, tool_args["restriction_type"])
            
            # Pricing tools
            elif tool_name == "get_item_price":
                return pricing.get_item_price(self.db_session, tool_args["item_id"])
            elif tool_name == "get_special_pricing":
                return pricing.get_special_pricing(self.db_session)
            elif tool_name == "calculate_order_total":
                return pricing.calculate_order_total(self.db_session, tool_args["items"])
            
            # Reservation tools
            elif tool_name == "check_reservation_availability":
                return reservations.check_reservation_availability(
                    self.db_session, 
                    tool_args["date"], 
                    tool_args["time"], 
                    tool_args["party_size"]
                )
            elif tool_name == "create_reservation":
                return reservations.create_reservation(
                    self.db_session,
                    tool_args["date"],
                    tool_args["time"],
                    tool_args["party_size"],
                    tool_args["customer_name"],
                    tool_args["customer_phone"],
                    tool_args.get("customer_email"),
                    tool_args.get("special_requests")
                )
            
            # Unknown tool
            else:
                logger.warning(f"Unknown tool: {tool_name}")
                return {"error": f"Unknown tool: {tool_name}"}
            
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return {"error": str(e)}
    
    def process_message(self, user_input: str) -> str:
        """
        Process a user message and generate a response.
        
        Args:
            user_input: The user's input message
            
        Returns:
            Agent response
        """
        logger.info(f"Processing user message: {user_input}")
        
        # Add user message to conversation
        self.state.conversation.add_message("user", user_input)
        
        # Prepare messages for the API call
        messages = self.state.conversation.get_history()
        
        # Process with OpenAI (or mock)
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )
            
            message = response.choices[0].message

            message_content = message.content or ""
            

            if hasattr(message, 'tool_calls') and message.tool_calls:
                # Add the assistant message with tool calls to conversation
                self.state.conversation.add_message("assistant", message_content)
                
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    tool_result = self._execute_tool(function_name, function_args)
                    
                    self.state.conversation.add_message(
                        "assistant", 
                        f"Used tool {function_name} with result: {json.dumps(tool_result)}"
                    )
                
                if "menu" in user_input.lower() or "categories" in user_input.lower():
                    categories = menu_query.get_menu_categories(self.db_session)
                    category_names = [cat["name"] for cat in categories]
                    final_content = f"We have several menu categories including {', '.join(category_names)}. What would you like to know more about?"
                elif "vegetarian" in user_input.lower():
                    veg_items = menu_query.get_menu_items_by_dietary_restriction(self.db_session, "vegetarian")
                    veg_names = [item["name"] for item in veg_items[:5]]
                    final_content = f"We have several vegetarian options including {', '.join(veg_names)} and more. Would you like details on any of these?"
                else:
                    final_content = "I've looked that up for you. Is there anything specific you'd like to know about our restaurant?"
            else:
                final_content = message_content
            
            self.state.conversation.add_message("assistant", final_content)
            
            return final_content
            
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            logger.error(error_msg)
            
            error_response = "I'm sorry, I encountered an error processing your request. Please try again."
            self.state.conversation.add_message("assistant", error_response)
            
            return error_response
    
    def reset_conversation(self) -> None:
        """Reset the conversation while keeping the system prompt."""
        system_message = None
        
        for message in self.state.conversation.messages:
            if message.role == "system":
                system_message = message
                break
        
        # Clear conversation
        self.state.conversation.clear()
        
        # Restore system message
        if system_message:
            self.state.conversation.messages.append(system_message)
        else:
            # Reinitialize with system prompt if no system message was found
            self._initialize_conversation()