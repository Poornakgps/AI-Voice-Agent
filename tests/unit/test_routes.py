"""
Unit tests for API routes.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "environment" in data

def test_readiness_endpoint():
    """Test the readiness check endpoint."""
    response = client.get("/readiness")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"

def test_metrics_endpoint():
    """Test the metrics endpoint."""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "uptime" in data
    assert "memory_usage" in data
    assert "cpu_usage" in data
    assert "active_connections" in data
    assert isinstance(data["uptime"], (int, float))

def test_admin_config_endpoint():
    """Test the admin config endpoint."""
    response = client.get("/admin/config")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "key" in data[0]
    assert "value" in data[0]

def test_admin_logs_endpoint():
    """Test the admin logs endpoint."""
    response = client.get("/admin/logs")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "timestamp" in data[0]
        assert "level" in data[0]
        assert "message" in data[0]

def test_admin_logs_with_params():
    """Test the admin logs endpoint with parameters."""
    response = client.get("/admin/logs?limit=2&level=INFO")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 2
    for log in data:
        assert log["level"] == "INFO"

def test_voice_webhook():
    """Test the Twilio voice webhook."""
    response = client.post("/webhook/voice")
    assert response.status_code == 200
    assert "<?xml" in response.text
    assert "<Response>" in response.text
    assert "<Say>" in response.text

def test_transcribe_webhook():
    """Test the Twilio transcribe webhook."""
    form_data = {
        "CallSid": "test-call-sid",
        "RecordingUrl": "https://example.com/recording.mp3",
        "RecordingSid": "test-recording-sid"
    }
    
    response = client.post("/webhook/transcribe", data=form_data)
    assert response.status_code == 200
    assert "<?xml" in response.text
    assert "<Response>" in response.text
    assert "<Say>" in response.text

def test_status_webhook():
    """Test the Twilio status webhook."""
    form_data = {
        "CallSid": "test-call-sid",
        "CallStatus": "completed"
    }
    
    response = client.post("/webhook/status", data=form_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "received"

def test_fallback_webhook():
    """Test the Twilio fallback webhook."""
    form_data = {
        "CallSid": "test-call-sid",
        "ErrorCode": "12345",
        "ErrorMessage": "Test error message"
    }
    
    response = client.post("/webhook/fallback", data=form_data)
    assert response.status_code == 200
    assert "<?xml" in response.text
    assert "<Response>" in response.text
    assert "<Say>" in response.text
    assert "technical difficulties" in response.text