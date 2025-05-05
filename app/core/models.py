"""
Core models for the Voice AI Restaurant Agent.

This module defines data models used across the application.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime

class CallStatus(str, Enum):
    """Enum for call status."""
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TRANSFERRING = "transferring"

class CallRecord(BaseModel):
    """Model for call records."""
    call_id: str = Field(..., description="Unique identifier for the call")
    customer_phone: str = Field(..., description="Customer phone number")
    start_time: datetime = Field(default_factory=datetime.now, description="Call start time")
    end_time: Optional[datetime] = Field(None, description="Call end time")
    duration_seconds: Optional[int] = Field(None, description="Call duration in seconds")
    status: CallStatus = Field(default=CallStatus.INITIATED, description="Current call status")
    transcript_url: Optional[str] = Field(None, description="URL to the call transcript")
    recording_url: Optional[str] = Field(None, description="URL to the call recording")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class TranscriptSegment(BaseModel):
    """Model for transcript segments."""
    segment_id: str = Field(..., description="Unique identifier for the segment")
    call_id: str = Field(..., description="Associated call ID")
    speaker: str = Field(..., description="Speaker identifier (user or assistant)")
    text: str = Field(..., description="Transcribed text")
    confidence: float = Field(..., description="Transcription confidence score")
    start_time: float = Field(..., description="Segment start time (seconds from call start)")
    end_time: float = Field(..., description="Segment end time (seconds from call start)")
    timestamp: datetime = Field(default_factory=datetime.now, description="Server timestamp")

class TranscriptSummary(BaseModel):
    """Model for transcript summaries."""
    call_id: str = Field(..., description="Associated call ID")
    summary: str = Field(..., description="Summary of the call")
    topics: List[str] = Field(default_factory=list, description="Topics discussed")
    action_items: List[str] = Field(default_factory=list, description="Action items from the call")
    sentiment: str = Field(..., description="Overall sentiment (positive, neutral, negative)")
    generated_at: datetime = Field(default_factory=datetime.now, description="Generation timestamp")

class AgentAction(BaseModel):
    """Model for agent actions."""
    action_id: str = Field(..., description="Unique identifier for the action")
    call_id: str = Field(..., description="Associated call ID")
    action_type: str = Field(..., description="Type of action (query_menu, check_reservation, etc.)")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    result: Optional[Dict[str, Any]] = Field(None, description="Action result")
    timestamp: datetime = Field(default_factory=datetime.now, description="Action timestamp")
    success: bool = Field(..., description="Whether the action was successful")
    error_message: Optional[str] = Field(None, description="Error message if action failed")

class VoiceSettings(BaseModel):
    """Model for voice settings."""
    voice_id: str = Field(..., description="Voice identifier")
    name: str = Field(..., description="Voice name")
    language: str = Field(..., description="Voice language")
    gender: str = Field(..., description="Voice gender")
    speaking_rate: float = Field(1.0, description="Speaking rate (0.5 to 2.0)")
    pitch: float = Field(0.0, description="Voice pitch (-10.0 to 10.0)")
    volume_gain_db: float = Field(0.0, description="Volume gain in dB (-6.0 to 6.0)")

class TTSRequest(BaseModel):
    """Model for text-to-speech requests."""
    text: str = Field(..., description="Text to synthesize")
    voice_settings: Optional[VoiceSettings] = Field(None, description="Voice settings")
    ssml: bool = Field(False, description="Whether the input is SSML")

class TTSResponse(BaseModel):
    """Model for text-to-speech responses."""
    audio_content_base64: str = Field(..., description="Base64-encoded audio content")
    duration_seconds: float = Field(..., description="Audio duration in seconds")
    content_type: str = Field(..., description="Audio content type")

class STTRequest(BaseModel):
    """Model for speech-to-text requests."""
    audio_content_base64: Optional[str] = Field(None, description="Base64-encoded audio content")
    audio_url: Optional[str] = Field(None, description="URL to audio content")
    language_code: str = Field("en-US", description="Language code")
    model: Optional[str] = Field(None, description="Speech recognition model")
    enhanced: bool = Field(False, description="Whether to use enhanced model")

class STTResponse(BaseModel):
    """Model for speech-to-text responses."""
    text: str = Field(..., description="Transcribed text")
    confidence: float = Field(..., description="Confidence score")
    is_final: bool = Field(True, description="Whether the transcription is final")
    alternatives: List[Dict[str, Any]] = Field(default_factory=list, description="Alternative transcriptions")