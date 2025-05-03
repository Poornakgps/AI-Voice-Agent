"""
Pytest configuration and fixtures.
"""
import pytest
import os
import sys
from fastapi.testclient import TestClient

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import app after adjusting path
from app.main import app
from app.config import settings

@pytest.fixture
def test_client():
    """
    Create a test client for FastAPI application.
    
    Returns:
        TestClient: FastAPI test client.
    """
    with TestClient(app) as client:
        yield client

@pytest.fixture
def mock_twilio_request_data():
    """
    Create mock Twilio request data for testing.
    
    Returns:
        dict: Mock Twilio request data.
    """
    return {
        "CallSid": "FAKE_CALL_SID_TEST12345",
        "AccountSid": "FAKE_ACCOUNT_SID_TEST12345",
        "From": "+15551234567",
        "To": "+15559876543",
        "CallStatus": "in-progress",
        "ApiVersion": "2010-04-01",
        "Direction": "inbound",
        "ForwardedFrom": "",
        "CallerName": "Test Caller",
        "ParentCallSid": "",
        "RecordingUrl": "https://example.com/recordings/FAKE_RECORDING_SID_TEST12345",
        "RecordingSid": "FAKE_RECORDING_SID_TEST12345",
    }

@pytest.fixture
def mock_env_setup():
    """
    Setup test environment variables.
    
    This fixture ensures tests run with consistent configuration.
    """
    # Store original environment
    original_env = {}
    for key in ["DEBUG", "APP_ENV", "LOG_LEVEL"]:
        original_env[key] = os.environ.get(key)
    
    # Set test environment
    os.environ["DEBUG"] = "True"
    os.environ["APP_ENV"] = "development"
    os.environ["LOG_LEVEL"] = "DEBUG"
    
    # Run test
    yield
    
    # Restore original environment
    for key, value in original_env.items():
        if value is None:
            if key in os.environ:
                del os.environ[key]
        else:
            os.environ[key] = value