"""
Unit tests for the agent module.
"""
import pytest
import json
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.agent import RestaurantAgent, Conversation, Message, AgentState
from database.models import Base, MenuCategory
from database.mock_data import seed_database

@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    # Seed the database with test data
    seed_database(session)
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)

@pytest.fixture
def agent(db_session):
    """Create a test agent instance."""
    return RestaurantAgent(db_session)

def test_conversation_add_message():
    """Test adding messages to a conversation."""
    conversation = Conversation()
    
    conversation.add_message("user", "Hello")
    conversation.add_message("assistant", "Hi there!")
    
    assert len(conversation.messages) == 2
    assert conversation.messages[0].role == "user"
    assert conversation.messages[0].content == "Hello"
    assert conversation.messages[1].role == "assistant"
    assert conversation.messages[1].content == "Hi there!"

def test_conversation_get_history():
    """Test getting conversation history."""
    conversation = Conversation()
    
    conversation.add_message("user", "Hello")
    conversation.add_message("assistant", "Hi there!")
    
    history = conversation.get_history()
    
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Hi there!"

def test_conversation_clear():
    """Test clearing conversation history."""
    conversation = Conversation(
        messages=[
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi there!")
        ],
        conversation_id="test-conversation",
        user_id="test-user"
    )
    
    conversation.clear()
    
    assert len(conversation.messages) == 0
    assert conversation.conversation_id == "test-conversation"
    assert conversation.user_id == "test-user"

def test_agent_state_context():
    """Test agent state context operations."""
    state = AgentState()
    
    state.update_context("user_name", "John")
    state.update_context("preference", "vegetarian")
    
    assert state.get_context("user_name") == "John"
    assert state.get_context("preference") == "vegetarian"
    assert state.get_context("nonexistent") is None
    assert state.get_context("nonexistent", "default") == "default"
    
    state.clear_context()
    assert state.get_context("user_name") is None

def test_agent_initialization(agent):
    """Test agent initialization."""
    assert agent.prompt_manager is not None
    assert agent.state is not None
    assert agent.client is not None
    assert agent.tools is not None
    
    assert len(agent.state.conversation.messages) > 0
    assert agent.state.conversation.messages[0].role == "system"

def test_agent_reset_conversation(agent):
    """Test resetting the conversation."""
    agent.state.conversation.add_message("user", "Hello")
    agent.state.conversation.add_message("assistant", "Hi there!")
    
    system_prompt = agent.state.conversation.messages[0].content
    
    agent.reset_conversation()
    
    assert len(agent.state.conversation.messages) == 1
    assert agent.state.conversation.messages[0].role == "system"
    assert agent.state.conversation.messages[0].content == system_prompt

def test_agent_tools_registration(agent):
    """Test tool registration."""
    assert len(agent.tools) > 0
    
    for tool in agent.tools:
        assert "type" in tool
        assert tool["type"] == "function"
        assert "function" in tool
        assert "name" in tool["function"]
        assert "description" in tool["function"]
        assert "parameters" in tool["function"]

def test_agent_execute_tool(agent, db_session):
    """Test executing tools."""
    result = agent._execute_tool("get_menu_categories", {})
    assert isinstance(result, list)
    assert len(result) > 0
    assert "name" in result[0]
    
    category_id = result[0]["id"]
    result = agent._execute_tool("get_menu_items_by_category", {"category_id": category_id})
    assert isinstance(result, list)
    
    result = agent._execute_tool("nonexistent_tool", {})
    assert "error" in result

@patch("app.core.agent.MockOpenAIClient")
def test_agent_process_message_direct(mock_client, agent):
    """Test processing a message with a direct response (no tool calls)."""
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "This is a direct response."
    mock_message.tool_calls = None
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_client.return_value.chat.completions.create.return_value = mock_response
    
    agent.client = mock_client.return_value
    
    response = agent.process_message("Hello")
    
    assert response == "This is a direct response."
    assert len(agent.state.conversation.messages) == 3 

@patch("app.core.agent.MockOpenAIClient")
def test_agent_process_message_with_tool(mock_client, agent):
    """Test processing a message with a tool call."""
    first_response = MagicMock()
    first_choice = MagicMock()
    first_message = MagicMock()
    first_message.content = "Let me check our menu categories."
    
    mock_tool_call = MagicMock()
    mock_tool_call.function.name = "get_menu_categories"
    mock_tool_call.function.arguments = "{}"
    first_message.tool_calls = [mock_tool_call]
    
    first_choice.message = first_message
    first_response.choices = [first_choice]
    
    second_response = MagicMock()
    second_choice = MagicMock()
    second_message = MagicMock()
    second_message.content = "We have several menu categories including Starters, Main Courses, and Desserts."
    second_choice.message = second_message
    second_response.choices = [second_choice]
    
    mock_client.return_value.chat.completions.create.side_effect = [first_response, second_response]
    
    agent.client = mock_client.return_value
    
    response = agent.process_message("What's on your menu?")
    
    assert response == "We have several menu categories including Starters, Main Courses, and Desserts."
    
    messages = agent.state.conversation.messages
    assert len(messages) >= 4 
    assert any(message.role == "tool" for message in messages)

@patch("app.core.agent.MockOpenAIClient")
def test_agent_error_handling(mock_client, agent):
    """Test agent error handling."""
    mock_client.return_value.chat.completions.create.side_effect = Exception("Test error")
    
    agent.client = mock_client.return_value
    
    response = agent.process_message("Hello")
    
    assert "error" in response.lower()
    assert "sorry" in response.lower()